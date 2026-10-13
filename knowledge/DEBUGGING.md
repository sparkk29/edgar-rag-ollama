# Debugging

Symptom, likely cause, fix. Add a row whenever you solve a problem that could happen again.

## Setup and environment

| Symptom | Likely cause | Fix |
|---|---|---|
| `No pyproject.toml found in current directory or any parent directory` | Running uv outside the repo | `cd` to the folder that contains `pyproject.toml` |
| `RuntimeError: Set SEC_USER_AGENT in .env ...` | `.env` missing, or still `you@example.com` | `cp .env.example .env` and set `SEC_USER_AGENT="Your Name you@yourmail.com"` |
| `httpx.ConnectError` to `localhost:11434` | Ollama not running | `brew services start ollama` or `ollama serve` |
| `model "qwen2.5:7b" not found` | Model not pulled | `ollama pull qwen2.5:7b` (or set `EDGAR_RAG_CHAT_MODEL` to a pulled model) |
| `ModuleNotFoundError: edgar_rag` | Environment not synced or not using uv | `uv sync`, then run through `uv run ...` |

## Ingest

| Symptom | Likely cause | Fix |
|---|---|---|
| HTTP 403 from sec.gov | Missing or generic User-Agent, or too many requests | Real name and email in `SEC_USER_AGENT`; keep `_MIN_INTERVAL_S` at 0.15 or more |
| `KeyError: Ticker 'XYZ' not found` | Typo, or ticker newer than the cached table | Check the symbol; delete `data/raw/company_tickers.json` to refresh |
| `LookupError: No 10-K found in recent filings` | Company files 20-F/40-F (foreign) or is new | Not supported; pick a US 10-K filer |
| Newer 10-K not picked up | Submissions JSON is cached | `uv run edgar-rag ingest --refresh` |
| Fewer than 23 Items in the summary | A heading format the regex misses, or a heading in a table row | Inspect lines: see "Inspecting a filing" below; adjust `HEADING_RE` or `_PAGE_NOISE` and add a fixture case |
| An Item has text from the next section | Heading of the next Item not detected, or broke document order | Same as above; check `find_headings` output |

## Retrieval and answers

| Symptom | Likely cause | Fix |
|---|---|---|
| "Not found" for a fact that is in the filing | Fact diluted in a chunk, or wrong company filter | `ask ... --show-context`; check `Filtered to:`; try a higher `--k`; check chunk size |
| `Filtered to:` missing for a named company | Name not in aliases | Add to `EXTRA_ALIASES` in `retrieve.py` |
| Wrong company filtered (e.g. "apple" as fruit) | Keyword detection false positive | Rephrase, or use the UI company multiselect; T-034 tracks a better detector |
| New company not recognized in the UI | `company_aliases()` cached for the process | Restart Streamlit |
| Grounding warning on a correct answer | Model converted units or did arithmetic | Read the cited source; this is the check working. Tighten the prompt only with eval evidence |
| `cites nonexistent source [n]` | Model hallucinated a citation number | Usually rare at temperature 0; re-run, and record in `FAILURES.md` if it repeats |
| Answers truncated or ignore later sources | Prompt exceeds `num_ctx` | Raise `EDGAR_RAG_NUM_CTX` or lower `--k` |
| Very slow answers | Model running on CPU or memory pressure | Close other apps; check `ollama ps`; try a smaller `--k` |
| Results changed after switching embed model | Old vectors from a different model | `rm -rf data/chroma && uv run edgar-rag ingest` |

## Inspecting a filing

```bash
uv run python - <<'EOF'
from pathlib import Path
from edgar_rag.parse import html_to_lines, find_headings, split_items
html = Path("data/raw/NVDA_2026_10K.htm").read_bytes()
lines = html_to_lines(html)
heads = find_headings(lines)
for item, i in heads.items():
    print(item, i, lines[i][:80])
for s in split_items(html):
    print(s.item, s.word_count)
EOF
```

## Inspecting retrieval

```bash
uv run edgar-rag ask "your question" --show-context --k 10
uv run edgar-rag eval --no-company-filter     # is the filter helping or hiding a problem?
```
