# Risks

Things that could go wrong in the future. Likelihood and impact are Low, Medium or High.
Review when planning a new phase; move a risk to [`../state/BLOCKERS.md`](../state/BLOCKERS.md) if it happens.

| ID | Risk | Likelihood | Impact | Mitigation | Trigger to watch |
|---|---|---|---|---|---|
| R-001 | Filers change HTML structure; Item detection breaks for some companies | Medium | High | Unit fixture of tricky patterns; ingest summary shows Item counts | A filing with fewer than 23 Items |
| R-002 | SEC blocks requests or changes the API | Low | High | Real `User-Agent`, throttling, local cache | HTTP 403 or schema errors on ingest |
| R-003 | Small models state wrong figures that pass the grounding check (real number, wrong claim) | Medium | High | Citations and source cards; prompt rules; future LLM-as-judge (T-060) | User reports; manual review of eval answers |
| R-004 | Eval set too small and author-labeled; overfitting defaults to 24 questions | High | Medium | Treat as regression test; expand set (T-032) | Real questions failing while eval is 100% |
| R-005 | Keyword company detection misfires as more companies are added | Medium | Medium | UI company multiselect; better detector (T-034) | Wrong `Filtered to:` |
| R-006 | Chroma or Ollama client APIs change across versions | Medium | Medium | Versions pinned in `uv.lock`; unit tests; eval after upgrades | Errors after `uv lock --upgrade` |
| R-007 | Data goes stale when new 10-Ks are filed | High | Low | `ingest --refresh`; filing date shown in sources | A new fiscal year on EDGAR |
| R-008 | Context window too small for larger k or longer chunks; sources silently cut | Low | Medium | `num_ctx` 16384 with k=6 of 300-word chunks leaves headroom | Raising k or chunk size |
| R-009 | Hardware: users with 8 GB RAM cannot run a 7B model comfortably | Medium | Medium | Document requirements; allow smaller models via `EDGAR_RAG_CHAT_MODEL` | Setup complaints |
| R-010 | Without a license, nobody can legally reuse the code | High (until fixed) | Medium | Choose a license (T-021) | Already true |
| R-011 | Streamlit UI exposed on a shared network | Low | Medium | Run with `--server.address localhost` ([`../quality/SECURITY.md`](../quality/SECURITY.md)) | Using the app on public Wi-Fi |
| R-012 | Personal details committed (`.env`, eval reports) | Low | Medium | `.gitignore`; pre-commit checklist | `git status` shows `.env` |
