"""JSON schemas used as tools to get structured output from Claude."""

QUOTE_TOOL = {
    "name": "record_quote",
    "description": "Record the structured data extracted from one supplier quote.",
    "input_schema": {
        "type": "object",
        "properties": {
            "supplier_name": {"type": "string", "description": "Supplier / vendor company name."},
            "quote_number": {"type": ["string", "null"]},
            "quote_date": {"type": ["string", "null"], "description": "ISO date (YYYY-MM-DD) if available."},
            "valid_until": {"type": ["string", "null"], "description": "ISO date or free text (e.g. '15 days')."},
            "currency": {"type": ["string", "null"], "description": "ISO 4217 code, e.g. ARS, USD, EUR."},
            "items": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "description": {"type": "string"},
                        "quantity": {"type": ["number", "null"]},
                        "unit": {"type": ["string", "null"]},
                        "unit_price": {"type": ["number", "null"]},
                        "total": {"type": ["number", "null"]},
                    },
                    "required": ["description"],
                },
            },
            "subtotal": {"type": ["number", "null"]},
            "taxes": {"type": ["number", "null"], "description": "Total taxes (VAT, etc.)."},
            "taxes_included": {
                "type": ["boolean", "null"],
                "description": "True if the total already includes taxes.",
            },
            "total": {"type": ["number", "null"], "description": "Final amount to pay."},
            "delivery_time": {"type": ["string", "null"], "description": "Delivery time as written."},
            "delivery_days": {
                "type": ["integer", "null"],
                "description": "Delivery time converted to calendar days, if possible.",
            },
            "payment_terms": {"type": ["string", "null"]},
            "warranty": {"type": ["string", "null"]},
            "notes": {"type": ["string", "null"], "description": "Other relevant conditions or exclusions."},
            "missing_fields": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Important information NOT present in the quote "
                "(e.g. validity, delivery time, taxes, payment terms, warranty).",
            },
        },
        "required": ["supplier_name", "items", "missing_fields"],
    },
}

RECOMMENDATION_TOOL = {
    "name": "record_recommendation",
    "description": "Record the comparison result and recommendation.",
    "input_schema": {
        "type": "object",
        "properties": {
            "recommended_supplier": {
                "type": ["string", "null"],
                "description": "Supplier name, or null if no clear choice is possible.",
            },
            "summary": {"type": "string", "description": "2-4 sentence recommendation."},
            "reasons": {"type": "array", "items": {"type": "string"}},
            "risks": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Caveats, missing data or things to confirm with suppliers.",
            },
            "questions_for_suppliers": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Concrete questions to send to suppliers before deciding.",
            },
        },
        "required": ["summary", "reasons", "risks", "questions_for_suppliers"],
    },
}
