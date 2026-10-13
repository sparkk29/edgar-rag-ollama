# Review

Checklist for reviewing a change (your own before committing, or someone else's pull request).

## Correctness

- [ ] Does the change do what the task in [`../planning/TASKS.md`](../planning/TASKS.md) says?
- [ ] Edge cases: empty results, a company with no 10-K, a section under 15 words, a question naming three companies
- [ ] Are errors raised with a clear message rather than swallowed?

## Rules

- [ ] Nothing violates [`../RULES.md`](../RULES.md): local only, checks intact, no framework, SEC limits respected
- [ ] The prompt still forbids outside knowledge and calculations
- [ ] CLI and UI still behave the same way

## Code

- [ ] Follows [`CODING_STANDARDS.md`](CODING_STANDARDS.md): types, dataclasses, small functions, no prints in library code
- [ ] Settings go through `config.py`; new ones are in `.env.example` and the README
- [ ] Module dependency direction is unchanged
- [ ] No dead code, debug prints or commented-out blocks

## Tests and evidence

- [ ] Unit tests added or updated; `uv run pytest` passes
- [ ] For retrieval, chunking, embedding or prompt changes: before and after eval numbers are in the description
- [ ] If a default changed: a new ADR in [`../architecture/DECISIONS.md`](../architecture/DECISIONS.md)

## Data and security

- [ ] No `.env`, `data/` or personal details committed
- [ ] New dependencies are justified, maintained and added through `uv add`
- [ ] See [`SECURITY.md`](SECURITY.md) for anything touching network access or the UI's exposure

## Documentation

- [ ] README still matches behavior (commands, defaults, numbers)
- [ ] `state/` and `planning/` updated
- [ ] Lessons recorded in `knowledge/` if something surprising came up

## Giving feedback

Say what to change and why, point to the line, and separate "must fix" from "suggestion".
Approve when the must-fix items are done.
