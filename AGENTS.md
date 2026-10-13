# AGENTS.md

Instructions for AI coding agents (and humans) working on **edgar-rag**, a local RAG assistant over
SEC 10-K filings. Read this file first, then follow the session protocol below.

## Start of every session

1. [`state/RESUME.md`](state/RESUME.md): where the last session stopped and the first thing to do.
2. [`state/STATUS.md`](state/STATUS.md): current health of the code, index, models and git.
3. [`state/BLOCKERS.md`](state/BLOCKERS.md): anything that must be resolved before other work.
4. [`planning/NEXT.md`](planning/NEXT.md): the short list of what to work on now.
5. [`RULES.md`](RULES.md): non-negotiable constraints. Skim it even if you have read it before.

For background, [`PROJECT_CONTEXT.md`](PROJECT_CONTEXT.md) explains what the project is and why, and
[`architecture/ARCHITECTURE.md`](architecture/ARCHITECTURE.md) explains how it is built.

## Commands

Run everything from the repository root (the folder with `pyproject.toml`).

```bash
uv sync                                   # install / update the environment
uv run pytest                             # unit tests (fast, no network, no Ollama)
uv run edgar-rag ingest                   # download + index the default filings (needs Ollama and .env)
uv run edgar-rag ask "question"           # one answer with citations and checks
uv run edgar-rag eval                     # retrieval metrics on eval/questions.yaml (seconds)
uv run edgar-rag eval --answers           # also generate and check all 24 answers (~6 min)
uv run streamlit run app.py               # chat UI on http://localhost:8501
```

Prerequisites: Ollama running (`brew services start ollama`) with `qwen2.5:7b` and
`nomic-embed-text` pulled, and `SEC_USER_AGENT` set in `.env`.

## Where things live

| Path | What it is |
|---|---|
| `src/edgar_rag/` | The pipeline: `edgar`, `parse`, `chunk`, `index`, `retrieve`, `answer`, `evaluate`, `cli`, `config` |
| `app.py` | Streamlit UI |
| `tests/` | Unit tests and the `mini_10k.htm` fixture |
| `eval/` | Labeled questions and saved eval reports |
| `data/` | Downloaded filings and the Chroma index (git-ignored, rebuild with `ingest`) |
| Root `*.md`, `planning/`, `state/`, `architecture/`, `quality/`, `knowledge/` | Project documentation (this system) |

## How to make a change

1. Pick a task from [`planning/TASKS.md`](planning/TASKS.md) and mark it in progress.
2. Follow [`quality/CODING_STANDARDS.md`](quality/CODING_STANDARDS.md).
3. Add or update tests ([`quality/TESTING.md`](quality/TESTING.md)).
4. If the change touches parsing, chunking, retrieval or the prompt, run the eval and compare with
   the numbers in [`state/STATUS.md`](state/STATUS.md) ([`quality/VALIDATION.md`](quality/VALIDATION.md)).
5. Go through [`planning/CHECKLIST.md`](planning/CHECKLIST.md) before committing.

## End of every session

Update these before you stop, even if the work is unfinished:

- [`state/SESSION.md`](state/SESSION.md): what this session did, decided and left open.
- [`state/PROGRESS.md`](state/PROGRESS.md): one dated entry summarizing the session.
- [`state/STATUS.md`](state/STATUS.md): if test counts, eval numbers, index or git state changed.
- [`state/RESUME.md`](state/RESUME.md): the exact next step for whoever starts next.
- [`state/HANDOFF.md`](state/HANDOFF.md): if someone else will continue the work.
- [`planning/TASKS.md`](planning/TASKS.md) and [`planning/NEXT.md`](planning/NEXT.md): task status.

When you learn something durable, record it in `knowledge/`: facts in
[`MEMORY.md`](knowledge/MEMORY.md), things that went wrong in [`FAILURES.md`](knowledge/FAILURES.md),
measured comparisons in [`EXPERIMENTS.md`](knowledge/EXPERIMENTS.md), and design choices in
[`architecture/DECISIONS.md`](architecture/DECISIONS.md).

## Do not

- Commit `.env` or anything under `data/`.
- Add a cloud LLM, an API key, or an orchestration framework (LangChain, LlamaIndex).
- Loosen the grounding or citation checks to make an eval look better.
- Change defaults in `config.py` without eval numbers that justify it.
