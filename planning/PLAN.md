# Plan

The overall plan, in phases. Each phase has a goal and an exit criterion. Individual work items
live in [`TASKS.md`](TASKS.md); versions and dates live in [`ROADMAP.md`](ROADMAP.md).

## Phase 1: Working pipeline (done, v0.1.0)

Goal: answer questions about three real 10-Ks with citations, fully locally.

- EDGAR client with caching and rate limiting
- HTML parser that handles inline XBRL, split headings, page noise and unit cells
- Item-aware chunking, Ollama embeddings, Chroma index
- Company-aware retrieval, grounded prompt, grounding and citation checks
- CLI and Streamlit UI
- 24-question eval set; chunk size and chat model chosen from the numbers

Exit criterion (met): section hit rate@6 100%, evidence hit rate@6 100%, 1/24 answers with
ungrounded figures, 0/24 citation problems.

## Phase 2: Presentable repository (in progress)

Goal: someone landing on the GitHub repo understands, installs and trusts it within minutes.

- Logo, badges, clone instructions in the README (done, pushed in `32a4b01`)
- Documentation system: root docs plus `planning/`, `state/`, `architecture/`, `quality/`, `knowledge/` (written, uncommitted)
- License, UI screenshot or GIF, GitHub social preview
- CI that runs `uv run pytest` on every push

Exit criterion: all of the above merged on `main`, CI green.

## Phase 3: Better retrieval

Goal: stay at 100% on the current eval while handling harder questions and more companies.

- Hybrid search: BM25 alongside dense retrieval for exact terms and figures
- Cross-encoder reranking of the top 20 candidates
- Expand the eval set (more companies, more questions without a company name)

Exit criterion: evidence hit rate holds at 100% on the current set and improves on the expanded set.

## Phase 4: Structured financial data

Goal: numeric questions answered from XBRL facts rather than flattened table text.

- Parse inline XBRL facts into a table (concept, period, value, unit)
- Route numeric questions to the facts table and cite the fact

Exit criterion: zero ungrounded figures on the numeric eval questions.

## Phase 5: Several fiscal years

Goal: year-over-year questions beyond what a single filing's tables contain.

- Index the last N 10-Ks per company
- Fiscal-year detection and filter in retrieval and the UI

Exit criterion: new eval questions that need two filings pass.
