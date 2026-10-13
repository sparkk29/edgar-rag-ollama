# Tasks

Status values: `todo`, `doing`, `done`, `blocked`. Keep IDs stable; never reuse one.
Phase numbers refer to [`PLAN.md`](PLAN.md).

## Doing

| ID | Task | Phase | Notes |
|---|---|---|---|
| T-020 | Commit and push the documentation system | 2 | All files are written; logo already pushed in `32a4b01` |

## Todo

| ID | Task | Phase | Notes |
|---|---|---|---|
| T-021 | Add a `LICENSE` (owner to choose; MIT suggested) | 2 | Blocked on owner decision, see [`../state/BLOCKERS.md`](../state/BLOCKERS.md) |
| T-022 | Screenshot or GIF of the Streamlit UI in `assets/`, embedded in the README | 2 | |
| T-023 | Upload `assets/logo.png` as the GitHub social preview | 2 | Manual step in GitHub Settings |
| T-024 | GitHub Actions workflow: `uv sync` + `uv run pytest` on push and PR | 2 | Unit tests need no Ollama |
| T-025 | Add a linter/formatter (ruff) and a `[tool.ruff]` section | 2 | Match current style, line length 120 |
| T-030 | Hybrid retrieval: BM25 next to dense search, merged with reciprocal rank fusion | 3 | |
| T-031 | Cross-encoder reranker over the top 20 candidates | 3 | Must run locally |
| T-032 | Expand eval set: 2 more companies, 10 more questions without a company name | 3 | |
| T-033 | Strip the trailing "Not found in the indexed filings." after a complete answer | 3 | Known qwen2.5 quirk |
| T-034 | Less brittle company detection (aliases from SEC former names, fuzzy match) | 3 | |
| T-040 | Parse inline XBRL facts into a structured table | 4 | |
| T-041 | Answer numeric questions from XBRL facts with fact-level citations | 4 | |
| T-050 | Index the last N 10-Ks per company | 5 | Chunk IDs already include fiscal year |
| T-051 | Fiscal-year detection and filter in retrieval and UI | 5 | |
| T-060 | LLM-as-judge answer scoring to complement the rule-based checks | 3 | Local judge model |

## Done

| ID | Task | Phase |
|---|---|---|
| T-001 | EDGAR client: ticker to CIK, latest 10-K, cached rate-limited download | 1 |
| T-002 | HTML to clean lines, tables to pipe rows with units re-attached | 1 |
| T-003 | Item heading detection that skips the table of contents | 1 |
| T-004 | Paragraph-aware chunking with overlap and metadata | 1 |
| T-005 | Ollama embeddings with nomic task prefixes; idempotent Chroma upsert | 1 |
| T-006 | Company-aware retrieval with per-company interleaving for comparisons | 1 |
| T-007 | Grounded prompt, streaming answers, numeric grounding check, citation check | 1 |
| T-008 | CLI: `ingest`, `ask`, `eval` | 1 |
| T-009 | Streamlit UI with examples, k slider, company filter, source cards | 1 |
| T-010 | 24-question labeled eval set with section and evidence labels | 1 |
| T-011 | Chunk size experiment (600 vs 300 words); 300 chosen | 1 |
| T-012 | Chat model comparison (qwen2.5:7b vs llama3.1:8b); qwen2.5 chosen | 1 |
| T-013 | Unit tests for parse, chunk, answer checks and eval metrics (18 tests) | 1 |
| T-014 | README with architecture, setup, usage, evaluation, limitations | 1 |
| T-015 | Push to GitHub as `sparkk29/edgar-rag-ollama` | 2 |
| T-016 | Logo (`assets/logo.svg`, `assets/logo.png`) and README header with badges | 2 |
| T-017 | Clone step, repo-root note, `EDGAR_RAG_NUM_CTX` in `.env.example`, project URLs in `pyproject.toml` | 2 |
| T-018 | Logo as the Streamlit page icon | 2 |
| T-019 | Documentation system (root docs, planning, state, architecture, quality, knowledge) | 2 |
