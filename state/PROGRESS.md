# Progress

A dated log, newest first. One entry per working session: what changed and why it matters.

## 2026-10-13

- Created the logo (`assets/logo.svg` and a 512 px `assets/logo.png`): a filing page with a
  highlighted passage and a `[1]` citation badge. It is also the Streamlit page icon.
- README: centered logo header, badges, clone step for `sparkk29/edgar-rag-ollama`, a note to run
  commands from the repo root, how to switch to `llama3.1:8b`, `assets/` in the project layout;
  removed a stray `# edgar-rag-ollama` line appended during git setup.
- `.env.example` now documents `EDGAR_RAG_NUM_CTX`; `pyproject.toml` has project URLs.
- Added the documentation system: root docs (`AGENTS`, `FLOW`, `PROJECT_CONTEXT`, `REQUIREMENTS`,
  `RULES`) and the `planning/`, `state/`, `architecture/`, `quality/`, `knowledge/` folders.
- Tests: 18 passed. Logo and config changes pushed as `32a4b01`; the docs are not committed yet.

## 2026-10-11

- Built the full pipeline: EDGAR client, HTML parser, Item splitter, chunker, Ollama embeddings,
  Chroma index, company-aware retrieval, grounded answers, CLI and Streamlit UI.
- Wrote 24 labeled eval questions and the section and evidence metrics.
- Chunk size experiment: 300-word chunks reached 100% evidence hit rate@6 (600 words: 95%).
- Chat model comparison: `qwen2.5:7b` chosen over `llama3.1:8b` (1 vs 2 flagged answers, more
  complete, slightly faster).
- Added the "never calculate" prompt rule and the grounding check after `llama3.1:8b` invented
  Microsoft product-revenue figures in an early run.
- Wrote the README and unit tests; pushed to GitHub (`26fd5be`, `c9c8edc`).
