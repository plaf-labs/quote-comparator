"""Tests that run without an API key (the Claude client is mocked)."""

import io
from types import SimpleNamespace

import openpyxl

from quote_comparator import compare, llm

QUOTE_A = {
    "supplier_name": "Aceros del Sur",
    "currency": "ARS",
    "items": [{"description": "Bearing 6205", "quantity": 40, "unit_price": 4850, "total": 194000}],
    "total": 600000,
    "taxes_included": True,
    "missing_fields": [],
}
QUOTE_B = {
    "supplier_name": "Industrias Norte",
    "currency": "ARS",
    "items": [{"description": "Bearing 6205", "quantity": 40, "unit_price": 5600, "total": 224000}],
    "total": 550000,
    "taxes_included": False,
    "missing_fields": ["validity", "warranty"],
}


class FakeClient:
    """Mimics anthropic.Anthropic().messages.create and records the last call."""

    def __init__(self, tool_input):
        self.tool_input = tool_input
        self.last_call = None
        self.messages = self

    def create(self, **kwargs):
        self.last_call = kwargs
        block = SimpleNamespace(type="tool_use", name=kwargs["tool_choice"]["name"], input=self.tool_input)
        return SimpleNamespace(content=[block])


def test_extract_quote_sends_pdf_and_forces_tool():
    client = FakeClient(QUOTE_A)
    result = llm.extract_quote(client, b"%PDF-1.4 fake", language="es", model="test-model")

    assert result == QUOTE_A
    call = client.last_call
    assert call["model"] == "test-model"
    assert call["tool_choice"] == {"type": "tool", "name": "record_quote"}
    doc = call["messages"][0]["content"][0]
    assert doc["type"] == "document" and doc["source"]["media_type"] == "application/pdf"
    assert "Spanish" in call["messages"][0]["content"][1]["text"]


def test_recommend_includes_quotes_in_prompt():
    rec = {"recommended_supplier": "Industrias Norte", "summary": "ok", "reasons": [], "risks": [],
           "questions_for_suppliers": []}
    client = FakeClient(rec)
    assert llm.recommend(client, [QUOTE_A, QUOTE_B]) == rec
    assert "Aceros del Sur" in client.last_call["messages"][0]["content"][0]["text"]


def test_comparison_table_shape_and_translation():
    df = compare.comparison_table([QUOTE_A, QUOTE_B], "es")
    assert list(df.columns) == ["Aceros del Sur", "Industrias Norte"]
    assert df.loc["Total", "Industrias Norte"] == 550000
    assert df.loc["Impuestos incluidos", "Aceros del Sur"] == "Sí"
    assert df.loc["Información faltante", "Industrias Norte"] == "validity, warranty"
    assert df.loc["Validez", "Aceros del Sur"] == "—"


def test_duplicate_supplier_names_get_unique_columns():
    assert compare.supplier_labels([QUOTE_A, QUOTE_A]) == ["Aceros del Sur", "Aceros del Sur (2)"]


def test_cheapest_only_with_single_currency():
    assert compare.cheapest([QUOTE_A, QUOTE_B]) == "Industrias Norte"
    usd = {**QUOTE_B, "currency": "USD"}
    assert compare.cheapest([QUOTE_A, usd]) is None


def test_excel_export_has_three_sheets():
    rec = {"recommended_supplier": "X", "summary": "s", "reasons": ["r"], "risks": [], "questions_for_suppliers": []}
    data = compare.to_excel([QUOTE_A, QUOTE_B], "en", rec)
    wb = openpyxl.load_workbook(io.BytesIO(data))
    assert wb.sheetnames == ["Comparison", "Items by supplier", "Recommendation"]
