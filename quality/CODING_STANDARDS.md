# Coding standards

These describe how the existing code is written. Match them so the codebase stays consistent.

## Python style

- Python 3.12+. Start every module with a one-line docstring, then `from __future__ import annotations`.
- Type-hint every function signature. Use built-in generics (`list[str]`, `dict[str, int]`) and `X | None`.
- Model data with `@dataclass`; add derived values as `@property` (e.g. `Filing.url`, `Hit.label`).
- Keep functions short and single-purpose. If a function needs a long comment to explain, split it.
- Module-level constants in `UPPER_CASE` (`HEADING_RE`, `ITEM_TITLES`); private helpers and constants
  start with `_` (`_clean`, `_MIN_INTERVAL_S`).
- Compile regular expressions once at module level.
- Lines up to about 120 characters (no formatter is enforced yet; T-025 adds ruff).
- Imports: standard library, third-party, then local (`from .config import settings`), separated by blank lines.

## Structure

- One responsibility per module (see [`../architecture/ARCHITECTURE.md`](../architecture/ARCHITECTURE.md)).
  Keep the dependency direction: `parse` and `chunk` must not import `index`, `retrieve` or `answer`.
- Configuration comes only from `config.settings`. Do not read environment variables elsewhere.
- Library modules return values and raise exceptions; they do not print. Only `cli.py` (Rich) and
  `app.py` (Streamlit) produce output.
- In `cli.py`, import pipeline modules inside the command function so `--help` stays fast.
- Paths are built from `config.PROJECT_ROOT` or `settings.*_dir`, never from the current directory.

## Docstrings and comments

- Docstrings say what a function returns or guarantees, in one or two lines; add a short second
  paragraph only for non-obvious behavior (see `find_headings`, `index_chunks`).
- Comments explain *why* something is done when the code cannot show it, e.g. why the title in
  `HEADING_RE` must start with a letter. Do not narrate what the next line does.

## Errors

- Fail early with a clear, actionable message (`EdgarClient` refuses to start without `SEC_USER_AGENT`).
- Raise specific exceptions (`KeyError`, `LookupError`, `RuntimeError`) with the offending value in the message.
- Let HTTP errors surface (`raise_for_status`); do not swallow exceptions in library code.

## External services

- SEC requests go through `EdgarClient._get` only, so throttling and the `User-Agent` always apply.
- Ollama access goes through `index.ollama_client()`, so `OLLAMA_HOST` is honored everywhere.
- Chroma access goes through `index.get_collection()`.

## Naming

- Tickers are upper-case strings everywhere (`"NVDA"`); Items are upper-case strings (`"1A"`).
- Chunk IDs follow `{ticker}-{fiscal_year}-{item}-{index:04d}`. Do not change the format without re-ingesting.
- CLI options use kebab-case (`--show-context`, `--no-company-filter`); Python names use snake_case.
