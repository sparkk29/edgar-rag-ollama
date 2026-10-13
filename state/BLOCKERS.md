# Blockers

Anything that stops progress. Add an entry as soon as you are blocked; move it to "Resolved" with
the fix when it is cleared.

## Open

| ID | Blocker | Blocks | Needs | Since |
|---|---|---|---|---|
| B-001 | No license chosen. Without one the code is "all rights reserved" and others cannot legally reuse it. | T-021 | Owner decision (MIT suggested) | 2026-10-13 |
| B-002 | GitHub social preview can only be uploaded through the repository settings page. | T-023 | Owner does it manually | 2026-10-13 |

## Resolved

| ID | Blocker | Fix | Resolved |
|---|---|---|---|
| B-000 | `uv sync` failed with "No `pyproject.toml` found in current directory or any parent directory" | It was run before the project files were in the folder. Run uv commands from the repo root. | 2026-10-11 |
