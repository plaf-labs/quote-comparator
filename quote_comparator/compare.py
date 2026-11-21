"""Pure functions that turn extracted quotes into tables and files (no API calls)."""

from __future__ import annotations

import io

import pandas as pd

from .i18n import t

SUMMARY_FIELDS = [
    "quote_number",
    "quote_date",
    "valid_until",
    "currency",
    "item_count",
    "subtotal",
    "taxes",
    "taxes_included",
    "total",
    "delivery_time",
    "payment_terms",
    "warranty",
    "notes",
    "missing_fields",
]


def _format_value(field: str, quote: dict, language: str):
    if field == "item_count":
        return len(quote.get("items") or [])
    value = quote.get(field)
    if field == "missing_fields":
        return ", ".join(value) if value else "—"
    if field == "taxes_included" and value is not None:
        return t(language, "yes") if value else t(language, "no")
    if value is None or value == "":
        return "—"
    return value


def supplier_labels(quotes: list[dict]) -> list[str]:
    """Unique column names, even if two quotes come from the same supplier."""
    labels, seen = [], {}
    for i, q in enumerate(quotes, start=1):
        name = (q.get("supplier_name") or f"#{i}").strip()
        seen[name] = seen.get(name, 0) + 1
        labels.append(name if seen[name] == 1 else f"{name} ({seen[name]})")
    return labels


def comparison_table(quotes: list[dict], language: str = "en") -> pd.DataFrame:
    """One row per attribute, one column per supplier."""
    labels = supplier_labels(quotes)
    data = {
        label: [_format_value(f, q, language) for f in SUMMARY_FIELDS]
        for label, q in zip(labels, quotes)
    }
    index = [t(language, f) for f in SUMMARY_FIELDS]
    return pd.DataFrame(data, index=index)


def items_table(quotes: list[dict], language: str = "en") -> pd.DataFrame:
    """All quoted line items, with the supplier in the first column."""
    rows = []
    for label, q in zip(supplier_labels(quotes), quotes):
        for item in q.get("items") or []:
            rows.append(
                {
                    t(language, "supplier"): label,
                    t(language, "description"): item.get("description"),
                    t(language, "quantity"): item.get("quantity"),
                    t(language, "unit"): item.get("unit"),
                    t(language, "unit_price"): item.get("unit_price"),
                    t(language, "item_total"): item.get("total"),
                    t(language, "currency"): q.get("currency"),
                }
            )
    return pd.DataFrame(rows)


def currencies(quotes: list[dict]) -> list[str]:
    return sorted({q["currency"] for q in quotes if q.get("currency")})


def cheapest(quotes: list[dict]) -> str | None:
    """Supplier with the lowest total, only when all quotes share one currency and have totals."""
    if len(currencies(quotes)) != 1 or any(q.get("total") is None for q in quotes):
        return None
    labels = supplier_labels(quotes)
    best = min(range(len(quotes)), key=lambda i: quotes[i]["total"])
    return labels[best]


def to_excel(quotes: list[dict], language: str = "en", recommendation: dict | None = None) -> bytes:
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        comparison_table(quotes, language).to_excel(writer, sheet_name=t(language, "comparison")[:31])
        items_table(quotes, language).to_excel(writer, sheet_name=t(language, "items")[:31], index=False)
        if recommendation:
            rec_rows = [(t(language, "recommended"), recommendation.get("recommended_supplier") or "—"),
                        (t(language, "recommendation"), recommendation.get("summary", ""))]
            for key in ("reasons", "risks", "questions_for_suppliers"):
                label = t(language, "questions" if key == "questions_for_suppliers" else key)
                rec_rows += [(label, line) for line in recommendation.get(key, [])]
            pd.DataFrame(rec_rows).to_excel(
                writer, sheet_name=t(language, "recommendation")[:31], index=False, header=False
            )
    return buffer.getvalue()


def to_csv(quotes: list[dict], language: str = "en") -> bytes:
    return comparison_table(quotes, language).to_csv().encode("utf-8-sig")
