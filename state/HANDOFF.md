# Handoff

For someone (person or agent) taking over the project. Update when ownership or context changes.

**Owner:** sparkk29 (GitHub)
**Last updated:** 2026-10-13

## In one paragraph

edgar-rag is a local RAG assistant over SEC 10-K filings. It downloads filings from EDGAR, splits
them by 10-K Item, embeds ~300-word chunks with `nomic-embed-text` into Chroma, retrieves with a
company filter, and answers with `qwen2.5:7b` through Ollama, citing numbered sources. Two
automatic checks flag invented figures and bad citations. Retrieval scores 100% on a 24-question
eval set. Read [`../AGENTS.md`](../AGENTS.md), then [`../PROJECT_CONTEXT.md`](../PROJECT_CONTEXT.md).

## What works

- `ingest`, `ask`, `eval` CLI commands and the Streamlit UI
- All 18 unit tests
- Eval: section and evidence hit rate@6 both 100%

## What is in flight

- The documentation system is written but uncommitted (T-020); the logo is already pushed.
- Phase 2 items remaining: license, screenshot, social preview, CI ([`../planning/NEXT.md`](../planning/NEXT.md)).

## Things that will surprise you

- `data/` is git-ignored. A fresh clone has no index; run `uv run edgar-rag ingest` first
  (needs `SEC_USER_AGENT` in `.env` and Ollama running).
- `EdgarClient` refuses a `User-Agent` containing `example.com`, so the `.env.example` value must be replaced.
- NVIDIA puts its financial statements under Item 15, not Item 8.
- Microsoft's 10-K HTML is 8.6 MB and its Item 8 is over 17,000 words.
- Company detection is a keyword match. "The iPhone maker" only works because of an alias in `retrieve.py`.
- `qwen2.5:7b` sometimes appends "Not found in the indexed filings." after a complete answer (T-033).
- The grounding check cannot catch a real number attached to the wrong claim.

## Where to look

| Need | File |
|---|---|
| Rules you must follow | [`../RULES.md`](../RULES.md) |
| How data flows | [`../FLOW.md`](../FLOW.md) |
| Why it is built this way | [`../architecture/DECISIONS.md`](../architecture/DECISIONS.md) |
| Known failure cases | [`../knowledge/FAILURES.md`](../knowledge/FAILURES.md) |
| Fixing a problem | [`../knowledge/DEBUGGING.md`](../knowledge/DEBUGGING.md) |
