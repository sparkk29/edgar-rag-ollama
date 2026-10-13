# Testing

Two layers: **unit tests** for deterministic logic (fast, offline) and the **eval** for retrieval
and answer quality (needs Ollama and the index). End-to-end checks are in [`VALIDATION.md`](VALIDATION.md).

## Running

```bash
uv run pytest            # all unit tests, about 0.3 s
uv run pytest -q tests/test_parse.py
uv run pytest -k grounded
```

Pytest is configured in `pyproject.toml` (`testpaths = ["tests"]`, `pythonpath = ["src"]`).

## What is covered (18 tests)

| File | Tests | Covers |
|---|---|---|
| `test_parse.py` | 5 | Hidden XBRL and page noise removed; split-span heading joined; tables to pipe rows with `$`/`%` attached; headings skip the table of contents; text lands in the right Item |
| `test_chunk.py` | 5 | Short text stays one chunk; max words respected; overlap repeats the trailing paragraph; long paragraphs split on sentences; metadata and IDs on chunks |
| `test_answer.py` | 5 | Grounded numbers pass; invented numbers flagged; a number inside a larger number is flagged; citation problems; sources numbered in the prompt |
| `test_evaluate.py` | 3 | Relevance needs ticker and Item; 1-based ranks; hit rate, MRR and evidence hit rate |

The fixture `tests/fixtures/mini_10k.htm` is a tiny fake 10-K (company "Acme") containing the
tricky patterns from real filings: a table of contents, a heading split across spans, hidden XBRL,
page numbers, running headers and unit cells.

## What is not unit tested, and why

| Area | Reason | Covered by |
|---|---|---|
| `edgar.py` | Needs network and the SEC | `edgar-rag ingest` |
| `index.py` | Needs Ollama and Chroma | `edgar-rag ingest`, `edgar-rag eval` |
| `retrieve.py` | Needs embeddings and the index | `edgar-rag eval` (section and evidence metrics) |
| `stream_answer` | Needs a chat model | `edgar-rag eval --answers` |
| `app.py`, `cli.py` | UI glue | Manual smoke test in [`VALIDATION.md`](VALIDATION.md) |

`detect_companies` is pure logic once `company_aliases()` is known, so it is a good candidate for a
unit test with a patched alias table.

## Writing tests

- One behavior per test, named `test_<what_should_happen>`.
- No network, Ollama or Chroma. Build `Hit`, `Section` and `EvalCase` objects directly (see the `HIT`
  and `_hit` helpers in existing tests).
- For parser changes, add the problematic HTML pattern to `mini_10k.htm` (or a new fixture) and assert
  on the cleaned lines.
- For a bug fix, first write a test that fails, then fix.
- Keep the whole suite under a few seconds.

## The eval as a regression test

`eval/questions.yaml` holds 24 labeled questions. Treat the current numbers in
[`../state/STATUS.md`](../state/STATUS.md) as the baseline: any drop must be explained before merging.
How to add questions is in [`VALIDATION.md`](VALIDATION.md).
