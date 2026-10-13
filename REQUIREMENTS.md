# Requirements

## Functional requirements

| ID | Requirement | Where it is met |
|---|---|---|
| FR-1 | Download the most recent 10-K for a given ticker from SEC EDGAR | `edgar.py` `EdgarClient.latest_10k`, `download` |
| FR-2 | Convert filing HTML to clean text, with tables flattened to readable rows | `parse.py` `html_to_lines` |
| FR-3 | Split each filing by 10-K Item, skipping the table of contents | `parse.py` `find_headings`, `split_items` |
| FR-4 | Chunk each Item with overlap and attach ticker, company, fiscal year, Item and URL | `chunk.py` `chunk_sections` |
| FR-5 | Embed chunks locally and store them persistently; re-ingesting must not duplicate data | `index.py` `index_chunks` |
| FR-6 | Retrieve the top-k chunks, filtered to companies named in the question | `retrieve.py` `retrieve`, `detect_companies` |
| FR-7 | For comparison questions, represent every named company in the retrieved set | `retrieve.py` per-company retrieval and interleaving |
| FR-8 | Generate an answer that uses only the sources and cites them as `[n]` | `answer.py` `SYSTEM_PROMPT`, `stream_answer` |
| FR-9 | Answer exactly "Not found in the indexed filings." when the sources lack the answer | `answer.py` `NOT_FOUND` |
| FR-10 | Flag figures in an answer that do not appear in the sources | `answer.py` `unsupported_numbers` |
| FR-11 | Flag answers with no citations or with out-of-range citations | `answer.py` `citation_problems` |
| FR-12 | Show sources with section labels and sec.gov links in both CLI and UI | `cli.py` `ask`, `app.py` `render_sources` |
| FR-13 | Measure retrieval with section hit rate@k, MRR and evidence hit rate@k | `evaluate.py`, `cli.py` `eval` |
| FR-14 | Optionally generate all eval answers and write a Markdown report | `edgar-rag eval --answers --output` |
| FR-15 | Every setting is overridable by environment variable or `.env` | `config.py` |

## Non-functional requirements

| ID | Requirement | Target |
|---|---|---|
| NFR-1 | Privacy: no data leaves the machine except SEC downloads | No cloud LLM or API keys |
| NFR-2 | SEC compliance | Descriptive `User-Agent`, at most 10 requests/s (client waits 0.15 s between requests) |
| NFR-3 | Ingest time for the three default filings | About 30 s on an Apple M4 Pro |
| NFR-4 | Answer latency with `qwen2.5:7b`, k=6 | About 13 s per answer |
| NFR-5 | Determinism | Chat temperature 0 |
| NFR-6 | Readability | No orchestration framework; small, typed functions |
| NFR-7 | Reproducibility | Dependencies pinned in `uv.lock`; Python 3.12 via `.python-version` |
| NFR-8 | Offline re-runs | Filings and EDGAR indexes cached in `data/raw/` |

## Environment

- macOS or Linux
- Python 3.12 or newer (managed by `uv`)
- Ollama with `qwen2.5:7b` (4.7 GB) and `nomic-embed-text` (274 MB); `llama3.1:8b` optional
- About 6 GB free disk; 16 GB RAM or more recommended (developed on 24 GB)
- `SEC_USER_AGENT="Your Name you@example.com"` in `.env`

## Acceptance criteria

A change is acceptable when:

1. `uv run pytest` passes.
2. `uv run edgar-rag eval` keeps section hit rate@6 at 100% and evidence hit rate@6 at 100%
   (or the regression is explained and recorded in [`knowledge/EXPERIMENTS.md`](knowledge/EXPERIMENTS.md)).
3. With `--answers`, no more than 1 of 24 answers has ungrounded figures and none has citation problems.
4. The README still describes the actual behavior and defaults.
