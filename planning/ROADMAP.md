# Roadmap

Versions map to the phases in [`PLAN.md`](PLAN.md). Dates are targets, not promises.

| Version | Theme | Status | Highlights |
|---|---|---|---|
| 0.1.0 | Working pipeline | Built 2026-10-11 (not tagged yet) | EDGAR ingest, Item-aware chunks, cited answers, grounding checks, eval |
| 0.2.0 | Presentable repository | In progress | Logo, docs system, license, screenshot, CI |
| 0.3.0 | Better retrieval | Planned | Hybrid BM25 + dense search, reranker, larger eval set |
| 0.4.0 | Structured financial data | Planned | XBRL facts table, numeric answers from facts |
| 0.5.0 | Several fiscal years | Planned | Multi-year index, fiscal-year filter |

## Ideas not yet scheduled

- Other filing types: 10-Q quarterly reports, 8-K current reports
- LLM-as-judge scoring of answer faithfulness and completeness
- Export an answer with its sources as Markdown
- Larger local models as an option for users with more memory
- Docker image or a one-command setup script
- Publishing these docs as a site (MkDocs Material on GitHub Pages)
