# Experiments

Measured comparisons that informed decisions. Every experiment records its setup, numbers and
conclusion, so results can be reproduced and defaults defended. Use the template at the bottom.

## EXP-001: Chunk size (600 vs 300 words)

- **Date:** 2026-10-11
- **Question:** Which chunk size retrieves the exact evidence most reliably?
- **Setup:** 3 filings, 24 questions (20 with evidence), `nomic-embed-text`, company filter on.

| Chunk size | Chunks | k | Section hit rate | Section MRR | Evidence hit rate |
|---|---|---|---|---|---|
| 600 words | 287 | 3 | 100% | 1.000 | 90% |
| 600 words | 287 | 6 | 100% | 1.000 | 95% |
| 300 words | 572 | 3 | 100% | 1.000 | 85% |
| **300 words** | **572** | **6** | **100%** | **1.000** | **100%** |

- **Conclusion:** 300 words with k=6 is the only setting at 100% evidence hit rate, and halves prompt
  size. Adopted as default (ADR-005). Section-level metrics could not distinguish the settings.

## EXP-002: Chat model (`qwen2.5:7b` vs `llama3.1:8b`)

- **Date:** 2026-10-11
- **Setup:** k=6, 300-word chunks, 24 questions, temperature 0, `eval --answers`.

| Model | Ungrounded figures | Citation problems | Time for 24 answers |
|---|---|---|---|
| **`qwen2.5:7b`** | 1/24 | 0/24 | 313 s (about 13 s each) |
| `llama3.1:8b` | 2/24 | 0/24 | 324 s |

- **Observations:** Both answered all 20 evidence questions with the right figure. qwen2.5 gave more
  complete answers (e.g. reported the 25% OpenAI stake and funding commitments llama left out).
- **Conclusion:** `qwen2.5:7b` as default (ADR-008). Reports: `eval/reports/qwen2.5-7b.md`, `eval/reports/llama3.1-8b.md`.

## EXP-003: Company filter ablation

- **Date:** 2026-10-11
- **Setup:** `uv run edgar-rag eval --no-company-filter`, 300-word chunks, k=6.
- **Result:** Every question's top hit still came from the correct company and Item.
- **Conclusion:** At three filings the embedding header carries most of the company signal. The filter
  still matters for comparisons (guarantees each company is represented) and will matter more as the
  index grows. Re-run this ablation after adding companies.

## EXP-004: "Never calculate" prompt rule

- **Date:** 2026-10-11
- **Setup:** An observation across runs, not a controlled before/after comparison.
- **Result:** In an early run without the rule, `llama3.1:8b` invented three Microsoft product-revenue
  figures. With the rule, the flagged answers are the ones in EXP-002, all arithmetic or unit conversions.
- **Conclusion:** Keep the rule (ADR-010) and the grounding check (ADR-009); neither alone is enough.

## Template

```markdown
## EXP-00N: <short title>

- **Date:** YYYY-MM-DD
- **Question:** What are we trying to learn?
- **Hypothesis:** What do we expect and why?
- **Setup:** Data, settings, commands (exact, so it can be re-run).

| Variant | Metric 1 | Metric 2 |
|---|---|---|

- **Conclusion:** What changes (link the ADR), or why nothing changes.
```
