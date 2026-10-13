# Project context

## What it is

**edgar-rag** answers natural-language questions about real SEC Form 10-K annual reports and cites
the exact filing section each fact came from, with a link to the original document on sec.gov.
Everything runs locally: Ollama serves the chat and embedding models, Chroma stores the vectors.

- Repository: <https://github.com/sparkk29/edgar-rag-ollama>
- Package and CLI name: `edgar-rag` (Python package `edgar_rag`)
- Version: 0.1.0

## Why it exists

It is a portfolio-grade demonstration of retrieval-augmented generation done carefully:

- on **real, messy data** (EDGAR HTML with inline XBRL and broken-up headings), not a toy corpus;
- with **structure-aware chunking** so citations point to a 10-K Item, not just "page 47";
- with **measured choices**: chunk size and chat model were picked from eval numbers;
- with **guardrails** that catch the most common small-model failure, invented figures.

## Who uses it

- The author, as a learning and portfolio project.
- Reviewers or recruiters reading the repo, who should understand it from the README in minutes.
- Anyone who wants a private, offline way to query 10-K filings.

## Scope

In scope:

- Latest 10-K for any SEC-registered ticker (defaults: AAPL, MSFT, NVDA).
- Questions answered from filing text, with numbered citations and sec.gov links.
- CLI (`ingest`, `ask`, `eval`) and a Streamlit chat UI.
- Retrieval and answer evaluation on a labeled question set.

Out of scope (for now):

- Other form types (10-Q, 8-K, proxy statements).
- Several fiscal years per company (only the most recent 10-K is indexed).
- Hosted deployment, multi-user access, authentication.
- Investment advice. The tool reports what filings say; it does not interpret them.

## Current indexed data

| Ticker | Company (SEC name) | Filing | Period end | Filed | Raw HTML |
|---|---|---|---|---|---|
| AAPL | Apple Inc. | 10-K FY2025 | 2025-09-27 | 2025-10-31 | 1.5 MB |
| MSFT | MICROSOFT CORP | 10-K FY2026 | 2026-06-30 | 2026-07-29 | 8.6 MB |
| NVDA | NVIDIA CORP | 10-K FY2026 | 2026-01-25 | 2026-02-25 | 2.0 MB |

572 chunks of about 300 words each in the Chroma collection `tenk_chunks`.

## Glossary

| Term | Meaning |
|---|---|
| 10-K | Annual report every US public company files with the SEC |
| Item | Standard 10-K section, e.g. Item 1 Business, 1A Risk Factors, 7 MD&A, 8 Financial Statements |
| EDGAR | The SEC's public filing system and API |
| CIK | Central Index Key, the SEC's numeric company identifier |
| Accession number | Unique ID of one filing, part of its archive URL |
| Inline XBRL | Machine-readable financial tags embedded in the filing HTML |
| Chunk | A ~300-word piece of one Item, stored with metadata and an embedding |
| Hit | A retrieved chunk plus its cosine distance |
| Section hit | A retrieved chunk comes from the expected company and Item |
| Evidence string | A fact (e.g. `42,000 employees`) that must appear verbatim in a retrieved chunk |
| Grounding check | Flags numbers in an answer that do not appear in the retrieved sources |
| Citation check | Flags answers without `[n]` citations or with citations to nonexistent sources |
