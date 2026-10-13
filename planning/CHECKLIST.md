# Checklists

## Before every commit

- [ ] `uv run pytest` passes
- [ ] No `.env`, `data/` or cache files staged (`git status --short`)
- [ ] New settings are in `config.py`, `.env.example` and the README
- [ ] Docs describe the new behavior (README, and `architecture/` if the design changed)
- [ ] Commit message says why, not only what

## Before changing parsing, chunking, embedding, retrieval or the prompt

- [ ] Record the current `uv run edgar-rag eval` numbers
- [ ] Make the change
- [ ] Re-ingest if chunks or embeddings changed: `uv run edgar-rag ingest`
- [ ] Re-run `uv run edgar-rag eval` and compare
- [ ] For prompt or model changes: `uv run edgar-rag eval --answers --output eval/reports/<model>.md`
- [ ] Record the result in [`../knowledge/EXPERIMENTS.md`](../knowledge/EXPERIMENTS.md)
- [ ] If a default changed: update `config.py`, the README tables and [`../architecture/DECISIONS.md`](../architecture/DECISIONS.md)

## Adding a company

- [ ] `uv run edgar-rag ingest --tickers XYZ` succeeds and the summary shows a sensible number of Items
- [ ] Ask a question that names the company and check `Filtered to: XYZ` appears
- [ ] If people refer to it by another name, add aliases to `EXTRA_ALIASES` in `retrieve.py`
- [ ] Add at least two labeled questions to `eval/questions.yaml`
- [ ] To make it a default, add it to `EDGAR_RAG_TICKERS` in `config.py` and `.env.example`

## Before a release (version bump)

- [ ] Everything in "Before every commit"
- [ ] Full eval with answers; numbers meet [`../REQUIREMENTS.md`](../REQUIREMENTS.md) acceptance criteria
- [ ] Version bumped in `pyproject.toml`, `uv sync` run so `uv.lock` matches
- [ ] [`ROADMAP.md`](ROADMAP.md) and [`../state/STATUS.md`](../state/STATUS.md) updated
- [ ] Tag pushed: `git tag v0.x.0 && git push --tags`

## Starting a session

- [ ] Read [`../state/RESUME.md`](../state/RESUME.md), [`../state/STATUS.md`](../state/STATUS.md), [`../state/BLOCKERS.md`](../state/BLOCKERS.md), [`NEXT.md`](NEXT.md)
- [ ] `git pull` and `uv sync`
- [ ] `brew services start ollama` (or `ollama serve`) if you need answers or ingest

## Ending a session

- [ ] Update [`../state/SESSION.md`](../state/SESSION.md), [`../state/PROGRESS.md`](../state/PROGRESS.md), [`../state/RESUME.md`](../state/RESUME.md)
- [ ] Update [`TASKS.md`](TASKS.md) and [`NEXT.md`](NEXT.md)
- [ ] Record new lessons in `knowledge/`
