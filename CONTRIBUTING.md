# Contributing

Thanks for your interest in improving the Supplier Quote Comparator! Contributions in English or Spanish are welcome.
¡Las contribuciones en español también son bienvenidas!

## Ways to contribute

- **Report a bug** — open an issue with the *Bug report* template.
- **Suggest an improvement** — open an issue with the *Feature request* template.
- **Send a pull request** — for small fixes go ahead; for bigger changes, open an issue first so we can agree on the approach.

## Development setup

```bash
git clone https://github.com/plaf-labs/quote-comparator.git
cd quote-comparator
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
pytest
```

## Pull request checklist

- [ ] `pytest` passes.
- [ ] New logic in `quote_comparator/compare.py` has tests.
- [ ] UI texts are added in both languages in `quote_comparator/i18n.py`.
- [ ] No API keys, real supplier data or customer documents are included.

## Privacy

Never attach real quotes from your company or your suppliers to issues or pull requests.
Use the fictional samples (`python scripts/make_samples.py`) or anonymize the documents first.

## Code of conduct

Be respectful and constructive. Maintainers may remove comments or contributions that aren't.
