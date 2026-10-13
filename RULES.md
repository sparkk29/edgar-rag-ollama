# Rules

Hard constraints for anyone changing this project. If a rule blocks you, record it in
[`state/BLOCKERS.md`](state/BLOCKERS.md) and ask the owner instead of working around it.

## Product rules

1. **Local only.** Models run through Ollama on the user's machine. No cloud LLMs, no API keys.
2. **Answers come from sources.** The prompt forbids outside knowledge, calculations and unit
   conversions. Do not relax those instructions.
3. **Every claim is cited.** Answers cite `[n]` source numbers; the UI and CLI show what each
   number refers to, with a link to the filing.
4. **Checks stay on.** The grounding check and citation check run in both the CLI and the UI.
   Never weaken them to make results look better; fix the cause instead.
5. **Admit gaps.** If the sources do not answer the question, the model says exactly
   "Not found in the indexed filings."

## SEC EDGAR rules

6. Every request sends `SEC_USER_AGENT` ("Name email"). `EdgarClient` refuses to start without it.
7. Stay under 10 requests per second. Keep the minimum interval in `edgar.py` at 0.15 s or more.
8. Cache downloads in `data/raw/`; only re-fetch with `--refresh`.

## Code rules

9. No LangChain, LlamaIndex or similar frameworks. Each pipeline step is a small, readable function.
10. All tunables live in `config.py` and are overridable through environment variables. Document
    new ones in `.env.example` and the README.
11. Library modules do not print. Only `cli.py` and `app.py` talk to the user.
12. Keep the CLI and the Streamlit UI behaviorally equivalent (same retrieval, same checks).
13. New behavior comes with unit tests that run without network, Ollama or Chroma.

## Evaluation rules

14. Run `uv run edgar-rag eval` before and after any change to parsing, chunking, embedding,
    retrieval or the prompt. Record the before and after numbers.
15. Defaults in `config.py` change only with eval evidence, recorded in
    [`architecture/DECISIONS.md`](architecture/DECISIONS.md) and [`knowledge/EXPERIMENTS.md`](knowledge/EXPERIMENTS.md).
16. If eval numbers change, update the README tables and [`state/STATUS.md`](state/STATUS.md).
17. Do not edit `eval/questions.yaml` to make a failing question pass. Add questions freely;
    change labels only when the label itself is wrong, and say why in the commit message.

## Repository rules

18. Never commit `.env`, `data/`, `.venv/` or caches (they are in `.gitignore`).
19. Keep the docs current: update `state/` at the end of every session (see [`AGENTS.md`](AGENTS.md)).
20. One logical change per commit, with a message that says why.
