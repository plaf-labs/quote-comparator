"""Streamlit UI for the Supplier Quote Comparator.

Run with:  streamlit run app.py
"""

import os

import anthropic
import streamlit as st

from quote_comparator import compare, llm
from quote_comparator.i18n import t

MAX_FILES = 5
MAX_FILE_MB = 20

st.set_page_config(page_title="Quote Comparator · PLAF Labs", page_icon="📊", layout="wide")

# --- Sidebar: settings ---------------------------------------------------------
with st.sidebar:
    language = st.radio(
        "Language / Idioma", options=["es", "en"], format_func=lambda x: {"es": "Español", "en": "English"}[x],
        horizontal=True,
    )
    api_key = st.text_input(
        t(language, "api_key"),
        value=os.getenv("ANTHROPIC_API_KEY", ""),
        type="password",
        help=t(language, "api_key_help"),
    )
    model = st.text_input(t(language, "model"), value=llm.DEFAULT_MODEL)
    st.caption(t(language, "privacy"))
    st.markdown("---")
    st.caption("Built by [PLAF Labs](https://github.com/plaf-labs)")

# --- Main ------------------------------------------------------------------------
st.title(t(language, "title"))
st.write(t(language, "subtitle"))

files = st.file_uploader(t(language, "upload"), type=["pdf"], accept_multiple_files=True)

if st.button(t(language, "compare"), type="primary"):
    if not api_key:
        st.warning(t(language, "need_key"))
        st.stop()
    if not files or not 2 <= len(files) <= MAX_FILES:
        st.warning(t(language, "need_files"))
        st.stop()

    client = anthropic.Anthropic(api_key=api_key)
    quotes = []
    for f in files:
        if f.size > MAX_FILE_MB * 1024 * 1024:
            st.error(t(language, "error", name=f.name, error=f"> {MAX_FILE_MB} MB"))
            continue
        with st.spinner(t(language, "extracting", name=f.name)):
            try:
                quote = llm.extract_quote(client, f.getvalue(), language=language, model=model)
                quote["_source_file"] = f.name
                quotes.append(quote)
            except Exception as exc:  # show the error and keep going with the other files
                st.error(t(language, "error", name=f.name, error=exc))

    if len(quotes) < 2:
        st.stop()

    with st.spinner(t(language, "recommending")):
        try:
            clean = [{k: v for k, v in q.items() if not k.startswith("_")} for q in quotes]
            recommendation = llm.recommend(client, clean, language=language, model=model)
        except Exception as exc:
            st.error(t(language, "error", name="recommendation", error=exc))
            recommendation = None

    st.session_state["result"] = {"quotes": quotes, "recommendation": recommendation, "language": language}

# --- Results (kept across reruns, e.g. when downloading) -------------------------
result = st.session_state.get("result")
if result:
    quotes, recommendation, lang = result["quotes"], result["recommendation"], result["language"]

    mixed = compare.currencies(quotes)
    if len(mixed) > 1:
        st.warning(t(lang, "mixed_currencies", currencies=", ".join(mixed)))

    if recommendation:
        st.subheader(t(lang, "recommendation"))
        chosen = recommendation.get("recommended_supplier")
        if chosen:
            st.success(f"**{t(lang, 'recommended')}:** {chosen}")
        else:
            st.info(t(lang, "no_clear_choice"))
        st.write(recommendation.get("summary", ""))
        col1, col2, col3 = st.columns(3)
        for col, key, label in (
            (col1, "reasons", "reasons"),
            (col2, "risks", "risks"),
            (col3, "questions_for_suppliers", "questions"),
        ):
            with col:
                st.markdown(f"**{t(lang, label)}**")
                for line in recommendation.get(key, []):
                    st.markdown(f"- {line}")

    st.subheader(t(lang, "comparison"))
    st.dataframe(compare.comparison_table(quotes, lang).astype(str), width="stretch")

    st.subheader(t(lang, "items"))
    st.dataframe(compare.items_table(quotes, lang), width="stretch", hide_index=True)

    col_a, col_b = st.columns(2)
    col_a.download_button(
        t(lang, "download_xlsx"),
        data=compare.to_excel(quotes, lang, recommendation),
        file_name="quote-comparison.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
    col_b.download_button(
        t(lang, "download_csv"),
        data=compare.to_csv(quotes, lang),
        file_name="quote-comparison.csv",
        mime="text/csv",
    )
