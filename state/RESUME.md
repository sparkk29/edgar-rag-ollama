# Resume

Read this to pick up exactly where work stopped.

**Last session:** 2026-10-13 (see [`SESSION.md`](SESSION.md))

## Where we are

The pipeline works and is evaluated. The logo and README header are pushed (`32a4b01`). The full
documentation system is written but **not committed**.

## First thing to do

```bash
cd edgar-rag-ollama            # the repo root, where pyproject.toml is
git status --short             # expect README.md, the root docs and the five docs folders
uv run pytest                  # expect 18 passed
git add -A && git commit -m "Add project documentation system for planning, state and knowledge"
git push
```

Then continue with [`../planning/NEXT.md`](../planning/NEXT.md).

## Quick health check (optional)

```bash
brew services start ollama
ollama list                                   # qwen2.5:7b, nomic-embed-text present
uv run edgar-rag eval                         # expect 100% / 1.000 / 100%
uv run edgar-rag ask "How many employees does NVIDIA have?"
```

If anything differs, look in [`../knowledge/DEBUGGING.md`](../knowledge/DEBUGGING.md).
