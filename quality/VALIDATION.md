# Validation

How to confirm the whole system works, not just its parts. Unit tests are in [`TESTING.md`](TESTING.md).

## 1. Environment

```bash
uv sync
ollama list          # qwen2.5:7b and nomic-embed-text must be listed
grep SEC_USER_AGENT .env   # must be a real "Name email", not example.com
```

## 2. Ingest

```bash
uv run edgar-rag ingest
```

Expected: a summary table with three rows, about 30 s in total. With default settings:

| Ticker | FY | Items | Chunks |
|---|---|---|---|
| AAPL | 2025 | 23 | 136 |
| MSFT | 2026 | 23 | 209 |
| NVDA | 2026 | 23 | 227 |

Fewer than 23 Items usually means a heading was missed (see
[`../knowledge/DEBUGGING.md`](../knowledge/DEBUGGING.md)). Total chunks should be 572:

```bash
uv run python -c "from edgar_rag.index import get_collection; print(get_collection().count())"
```

## 3. Retrieval eval

```bash
uv run edgar-rag eval
```

| Metric | Must be |
|---|---|
| Section hit rate@6 | 100% |
| Section MRR | 1.000 |
| Evidence hit rate@6 | 100% (20 questions with evidence) |

Ablation (should also be 100% section hit rate at this scale):

```bash
uv run edgar-rag eval --no-company-filter
```

## 4. Answer eval (for prompt or model changes)

```bash
uv run edgar-rag eval --answers --output eval/reports/qwen2.5-7b.md
```

| Metric | Must be |
|---|---|
| Answers with ungrounded figures | 1/24 or fewer |
| Answers with citation problems | 0/24 |
| Evidence questions answered with the right figure | 20/20 (read the report) |

Read every flagged answer in the report and decide whether it is a real error or a false alarm.

## 5. Manual smoke test

| Question | Expect |
|---|---|
| `uv run edgar-rag ask "How many employees does NVIDIA have?"` | `Filtered to: NVDA`; about 42,000 employees with a citation to Item 1 |
| `uv run edgar-rag ask "Compare Apple's and Microsoft's revenue drivers."` | Both companies in the sources (interleaved); each addressed separately |
| `uv run edgar-rag ask "What was Tesla's revenue last year?"` | Exactly "Not found in the indexed filings." |
| `uv run edgar-rag ask "Which company is headquartered in Santa Clara, California?"` | NVIDIA, from Item 2, with no company filter applied |

UI: `uv run streamlit run app.py`, then click an example question. Check the answer streams, source
cards expand and show text, the sec.gov link opens the filing, and the browser tab shows the logo.

## 6. Adding eval questions

Add an entry to `eval/questions.yaml`:

```yaml
- question: What is Apple's dividend policy?
  ticker: AAPL
  items: [5, 7]              # every Item where the answer legitimately lives
  evidence: "per share"      # optional: exact text that must be in a retrieved chunk
```

Prefer evidence strings that are short, distinctive and copied verbatim from the filing. Re-run
the eval and update the counts in the README and [`../state/STATUS.md`](../state/STATUS.md).
