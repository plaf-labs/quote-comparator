"""Generate three fictional supplier quotes (PDF) to try the app.

Usage:  python scripts/make_samples.py
Output: samples/*.pdf

All companies, people and numbers are invented.
"""

from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

OUT = Path(__file__).resolve().parent.parent / "samples"

QUOTES = [
    {
        "file": "quote_aceros_del_sur.pdf",
        "supplier": "Aceros del Sur S.A. (fictional)",
        "header": ["Cotización N.º 2026-0412", "Fecha: 10/11/2026", "Validez de la oferta: 15 días"],
        "items": [
            ("Rodamiento rígido de bolas 6205-2RS", 40, "u.", 4850.00),
            ("Correa en V tipo B-52", 25, "u.", 7200.00),
            ("Grasa de litio EP2 x 18 kg", 2, "balde", 96500.00),
        ],
        "currency": "ARS",
        "vat": 0.21,
        "conditions": [
            "Precios en pesos argentinos. IVA 21% no incluido en precios unitarios.",
            "Plazo de entrega: 7 días hábiles desde la orden de compra.",
            "Forma de pago: 50% anticipo, 50% contra entrega.",
            "Garantía: 6 meses por defectos de fabricación.",
        ],
    },
    {
        "file": "quote_industrias_norte.pdf",
        "supplier": "Industrias Norte SRL (fictional)",
        "header": ["Presupuesto 88731", "Fecha: 12/11/2026"],
        "items": [
            ("Rodamiento 6205-2RS (marca premium)", 40, "u.", 5600.00),
            ("Correa en V B-52", 25, "u.", 6400.00),
            ("Grasa EP2 balde 18 kg", 2, "u.", 89900.00),
        ],
        "currency": "ARS",
        "vat": 0.21,
        "conditions": [
            "Precios en pesos argentinos más IVA.",
            "Entrega inmediata sujeta a stock; resto en 20 días.",
            "Pago a 30 días fecha de factura.",
        ],
    },
    {
        "file": "quote_global_parts.pdf",
        "supplier": "Global Parts Supply LLC (fictional)",
        "header": ["Quotation Q-55102", "Date: 2026-11-13", "Valid for 30 days"],
        "items": [
            ("Deep groove ball bearing 6205-2RS", 40, "pcs", 4.10),
            ("V-belt B52", 25, "pcs", 5.90),
            ("Lithium EP2 grease 18 kg pail", 2, "pcs", 78.00),
        ],
        "currency": "USD",
        "vat": 0.0,
        "conditions": [
            "Prices in US dollars, EXW Miami. Freight, duties and local taxes not included.",
            "Lead time: 4-6 weeks.",
            "Payment: 100% wire transfer in advance.",
            "Warranty: 12 months.",
        ],
    },
]


def money(value: float, currency: str) -> str:
    return f"{currency} {value:,.2f}"


def build(quote: dict) -> None:
    styles = getSampleStyleSheet()
    doc = SimpleDocTemplate(str(OUT / quote["file"]), pagesize=A4)
    story = [Paragraph(quote["supplier"], styles["Title"])]
    story += [Paragraph(line, styles["Normal"]) for line in quote["header"]]
    story.append(Spacer(1, 16))

    cur = quote["currency"]
    rows = [["Description", "Qty", "Unit", "Unit price", "Total"]]
    subtotal = 0.0
    for desc, qty, unit, price in quote["items"]:
        line = qty * price
        subtotal += line
        rows.append([desc, str(qty), unit, money(price, cur), money(line, cur)])
    rows.append(["", "", "", "Subtotal", money(subtotal, cur)])
    if quote["vat"]:
        vat = subtotal * quote["vat"]
        rows.append(["", "", "", f"IVA {int(quote['vat'] * 100)}%", money(vat, cur)])
        rows.append(["", "", "", "TOTAL", money(subtotal + vat, cur)])
    else:
        rows.append(["", "", "", "TOTAL", money(subtotal, cur)])

    table = Table(rows, colWidths=[200, 40, 45, 95, 105])
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#222222")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("GRID", (0, 0), (-1, len(quote["items"])), 0.5, colors.grey),
                ("ALIGN", (1, 1), (-1, -1), "RIGHT"),
                ("FONTNAME", (3, -1), (-1, -1), "Helvetica-Bold"),
            ]
        )
    )
    story += [table, Spacer(1, 16)]
    story += [Paragraph(f"• {c}", styles["Normal"]) for c in quote["conditions"]]
    doc.build(story)


if __name__ == "__main__":
    OUT.mkdir(exist_ok=True)
    for q in QUOTES:
        build(q)
        print(f"Created samples/{q['file']}")
