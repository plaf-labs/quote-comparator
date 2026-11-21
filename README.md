# Supplier Quote Comparator

**An open-source AI agent that reads supplier quotes (PDF) and turns them into a side-by-side comparison with a recommendation.**
Built for purchasing teams at SMEs and industrial companies. Works in English and Spanish.

![Python](https://img.shields.io/badge/Python-3.10+-3776AB?logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?logo=streamlit&logoColor=white)
![Claude](https://img.shields.io/badge/Claude-API-D97757?logo=anthropic&logoColor=white)
![License: MIT](https://img.shields.io/badge/License-MIT-green)

---

## The problem

Every purchase means comparing quotes that look nothing alike: different formats, currencies, tax treatment,
delivery times and payment terms — and some information is simply missing. Doing it by hand in a spreadsheet
is slow and easy to get wrong.

## What it does

1. **Upload 2 to 5 quotes** in PDF, in any layout.
2. **Claude reads each one** and extracts supplier, items, prices, currency, taxes, delivery, payment terms,
   validity and warranty.
3. **Flags what's missing** in each quote (e.g. no validity date, taxes not specified).
4. **Builds a comparison table** and a line-item view.
5. **Recommends a supplier** with reasons, risks and questions to send to suppliers before deciding.
6. **Exports** the result to Excel or CSV.

It never converts currencies or invents data: when quotes aren't directly comparable, it tells you why.

## Quick start

You need Python 3.10+ and an [Anthropic API key](https://console.anthropic.com/).

```bash
git clone https://github.com/plaf-labs/quote-comparator.git
cd quote-comparator
pip install -r requirements.txt

# Optional: create three fictional quotes to try it
python scripts/make_samples.py

streamlit run app.py
```

Open the URL Streamlit prints, paste your API key in the sidebar, choose the language and upload the PDFs
(or the ones in `samples/`).

You can also set the key as an environment variable instead of typing it:

```bash
export ANTHROPIC_API_KEY=your-api-key-here
```

## How it works

```
PDF quotes ──► Claude (PDF input + structured output) ──► normalized JSON per quote
                                                              │
                         comparison table ◄───────────────────┤
                         recommendation  ◄── Claude ◄─────────┘
                         Excel / CSV export
```

- `quote_comparator/llm.py` — API calls. Each quote is sent as a PDF document and Claude must answer through
  a JSON schema (tool use), so the output is always structured.
- `quote_comparator/compare.py` — pure functions that build tables and exports (no API calls, fully tested).
- `quote_comparator/schema.py` — the data the agent extracts.
- `app.py` — the Streamlit interface.

## Privacy

Files are sent to the Anthropic API for processing and are not stored by the app. Your API key is only used
during your session. Don't commit your `.env` file.

## Tests

```bash
pytest
```

Tests use a mocked client, so they don't need an API key and don't consume credits.

## Limitations

- Scanned quotes with poor image quality may extract less accurately.
- Totals in different currencies are flagged, not converted.
- The recommendation is a starting point: always review the original quotes before deciding.

## Contributing

Ideas, bug reports and pull requests are welcome — in English or Spanish.
Open an [issue](https://github.com/plaf-labs/quote-comparator/issues) or read [CONTRIBUTING.md](CONTRIBUTING.md).

## License

MIT — see [LICENSE](LICENSE).

---

Made by [PLAF Labs](https://github.com/plaf-labs) · Software, automation and web development for SMEs and
industrial companies · [plaf.agency](https://plaf.agency)
