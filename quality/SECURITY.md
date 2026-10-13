# Security

edgar-rag is a single-user tool that runs on a laptop. The main concerns are keeping personal
details out of git, not exposing local services to the network, and treating downloaded documents
as untrusted input.

## Assets

| Asset | Where | Sensitivity |
|---|---|---|
| `SEC_USER_AGENT` (your name and email) | `.env` | Personal data; git-ignored |
| Downloaded filings and index | `data/` | Public SEC data; git-ignored for size |
| Questions you ask | In memory, Streamlit session | Private; never sent off the machine |

## Threats and mitigations

| Threat | Mitigation | Status |
|---|---|---|
| Committing `.env` | `.env` is in `.gitignore`; `.env.example` has placeholders only | In place |
| Streamlit reachable from the local network | Streamlit listens on all interfaces by default. On shared networks run `uv run streamlit run app.py --server.address localhost` | Document only |
| Ollama exposed to the network | Ollama binds to `localhost:11434` by default. Do not set `OLLAMA_HOST=0.0.0.0` unless you mean to | Default is safe |
| Malicious or malformed HTML | Parsed with lxml through BeautifulSoup; text only, nothing executed; scripts and styles removed | In place |
| Prompt injection inside a filing | The model has no tools and cannot take actions; the worst case is a wrong answer, which citations and checks help expose | Accepted risk |
| Hallucinated figures presented as fact | Grounding and citation checks; sources shown with every answer | In place |
| Being blocked by the SEC | Descriptive `User-Agent`, 0.15 s between requests, caching | In place |
| Vulnerable dependencies | Pinned in `uv.lock`; update with `uv lock --upgrade` and re-run tests | Manual |
| Chroma telemetry | Disabled in `get_collection` | In place |

## Practices

- Never paste real names, emails or tokens into code, docs or eval reports.
- Add dependencies only with `uv add`, and prefer well-maintained packages.
- Review `git status` before every commit (see [`../planning/CHECKLIST.md`](../planning/CHECKLIST.md)).
- If you deploy the UI anywhere beyond your own machine, add authentication first; the app has none.

## Reporting a problem

Open an issue on <https://github.com/sparkk29/edgar-rag-ollama/issues>. For anything sensitive,
contact the owner privately through their GitHub profile instead of filing a public issue.
