# Status

Snapshot of the project's health. Update whenever any of these numbers change.

**Last updated:** 2026-10-13

## Summary

Working end to end. Phase 1 is complete; Phase 2 (presentable repository) is in progress. The logo
is pushed; the documentation system is written but not committed.

## Code

| Item | State |
|---|---|
| Version | 0.1.0 (`pyproject.toml`) |
| Unit tests | 18 passed (`uv run pytest`, 0.3 s) |
| Python | 3.12 (`.python-version`), managed by uv |
| Linter | None configured yet (T-025) |
| CI | None yet (T-024) |

## Data and index

| Item | State |
|---|---|
| Filings in `data/raw/` | AAPL 10-K FY2025, MSFT 10-K FY2026, NVDA 10-K FY2026 |
| Chroma collection | `tenk_chunks`, 572 chunks (AAPL 136, MSFT 209, NVDA 227), cosine distance, 768-dim |
| Items detected | 23 of 23 in each filing |
| Chunking | 300 words, 50-word overlap |

## Models (Ollama)

| Model | Role | Pulled |
|---|---|---|
| `qwen2.5:7b` | Default chat model | Yes |
| `llama3.1:8b` | Alternative chat model | Yes |
| `nomic-embed-text` | Embeddings | Yes |

## Latest evaluation (k=6, 300-word chunks)

| Metric | Value |
|---|---|
| Section hit rate@6 | 100% |
| Section MRR | 1.000 |
| Evidence hit rate@6 | 100% (20 evidence questions) |
| Answers with ungrounded figures (`qwen2.5:7b`) | 1/24 |
| Answers with citation problems (`qwen2.5:7b`) | 0/24 |
| Time for 24 answers (`qwen2.5:7b`) | 313 s |

Full reports: [`eval/reports/qwen2.5-7b.md`](../eval/reports/qwen2.5-7b.md),
[`eval/reports/llama3.1-8b.md`](../eval/reports/llama3.1-8b.md).

## Git

| Item | State |
|---|---|
| Remote | `origin` = <https://github.com/sparkk29/edgar-rag-ollama> |
| Branch | `main`, in sync with `origin/main` at `32a4b01` (logo, README header, config updates) |
| Uncommitted | README "Project documentation" section and all documentation files |
