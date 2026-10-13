"""Streamlit chat UI. Run with: uv run streamlit run app.py"""

from __future__ import annotations

import streamlit as st

from edgar_rag.answer import citation_problems, stream_answer, unsupported_numbers
from edgar_rag.config import settings
from edgar_rag.index import get_collection
from edgar_rag.retrieve import Hit, company_aliases, detect_companies, retrieve

st.set_page_config(page_title="10-K Assistant", page_icon=None, layout="wide")

EXAMPLES = [
    "What supply chain risks does NVIDIA disclose?",
    "Compare Apple's and Microsoft's revenue drivers.",
    "How does Microsoft describe its cybersecurity risk management?",
    "What were Apple's iPhone net sales in fiscal 2025?",
]


def render_sources(hits: list[Hit], missing: list[str], citation_issues: list[str]) -> None:
    if missing:
        st.warning(f"Grounding check: these figures were not found in the sources: {', '.join(missing)}")
    for problem in citation_issues:
        st.warning(f"Citation check: {problem}")
    st.caption("Sources")
    for n, hit in enumerate(hits, start=1):
        with st.expander(f"[{n}] {hit.label}  (distance {hit.distance:.3f})"):
            st.markdown(f"[Open filing on sec.gov]({hit.metadata['url']})")
            st.text(hit.text)


with st.sidebar:
    st.header("10-K Assistant")
    st.write("Local RAG over SEC 10-K filings. Answers cite the exact filing section.")
    try:
        count = get_collection().count()
    except Exception as exc:
        count = 0
        st.error(f"Could not open the index: {exc}")
    indexed = sorted(company_aliases())
    st.metric("Indexed chunks", count)
    st.write("Companies: " + (", ".join(indexed) if indexed else "none, run `edgar-rag ingest`"))
    st.write(f"Chat model: `{settings.chat_model}`  \nEmbeddings: `{settings.embed_model}`")
    k = st.slider("Chunks to retrieve (k)", 2, 12, settings.top_k)
    company_filter = st.multiselect("Restrict to companies (default: auto-detect)", indexed)
    if st.button("Clear chat"):
        st.session_state.messages = []

if "messages" not in st.session_state:
    st.session_state.messages = []

if not st.session_state.messages:
    st.write("Try one of these:")
    cols = st.columns(len(EXAMPLES))
    for col, example in zip(cols, EXAMPLES):
        if col.button(example, width="stretch"):
            st.session_state.pending = example

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if msg["role"] == "assistant":
            render_sources(msg["hits"], msg["missing"], msg["citation_issues"])

question = st.chat_input("Ask about the indexed 10-K filings") or st.session_state.pop("pending", None)

if question:
    st.session_state.messages.append({"role": "user", "content": question})
    with st.chat_message("user"):
        st.markdown(question)

    with st.chat_message("assistant"):
        tickers = company_filter or detect_companies(question)
        with st.spinner("Retrieving relevant filing sections"):
            hits = retrieve(question, k=k, tickers=tickers)
        if tickers:
            st.caption(f"Filtered to: {', '.join(tickers)}")
        text = st.write_stream(stream_answer(question, hits))
        missing = unsupported_numbers(text, hits)
        issues = citation_problems(text, hits)
        render_sources(hits, missing, issues)

    st.session_state.messages.append(
        {"role": "assistant", "content": text, "hits": hits, "missing": missing, "citation_issues": issues}
    )
