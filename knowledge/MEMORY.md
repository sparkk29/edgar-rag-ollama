# Memory

Durable facts worth remembering across sessions. Short, factual, dated when they may go stale.
Lessons from mistakes go in [`FAILURES.md`](FAILURES.md); measured comparisons in [`EXPERIMENTS.md`](EXPERIMENTS.md).

## Project identity

- GitHub repo: `sparkk29/edgar-rag-ollama`. Package, CLI and import name: `edgar-rag` / `edgar_rag`.
- Local folder on the owner's machine: `~/Documents/AIproj`.
- Logo: `assets/logo.svg` (source) and `assets/logo.png` (512 px). Colors: navy gradient
  `#0F2A4A` to `#1E4D8C`, amber highlight `#FDE68A` / `#D97706`, emerald badge `#10B981`.

## Defaults (from `config.py`)

| Setting | Default |
|---|---|
| Tickers | AAPL, MSFT, NVDA |
| Chat model | `qwen2.5:7b` |
| Embedding model | `nomic-embed-text` (768 dimensions) |
| Chunk size / overlap | 300 / 50 words |
| top-k | 6 |
| Chat context window | 16384 tokens (embedding calls use 8192) |
| Collection | `tenk_chunks` in `data/chroma/` |

## Data facts (as of 2026-10-13)

- Indexed: Apple 10-K FY2025 (period end 2025-09-27), Microsoft FY2026 (2026-06-30), NVIDIA FY2026 (2026-01-25).
- 572 chunks: AAPL 136, MSFT 209, NVDA 227. Each filing yields all 23 Items.
- NVIDIA puts its financial statements under **Item 15**, not Item 8.
- Microsoft's 10-K HTML is 8.6 MB; its Item 8 is over 17,000 words.
- SEC company names are as filed: `Apple Inc.`, `MICROSOFT CORP`, `NVIDIA CORP`.
- Facts used as eval evidence: NVIDIA ~42,000 employees in 38 countries; NVIDIA Data Center revenue
  `193,737` (million, FY2026); Apple iPhone net sales `209,586` (million, FY2025); Microsoft holds
  about 25% of OpenAI on an as-converted basis.

## Behavior facts

- `EdgarClient` rejects a `User-Agent` that is empty or contains `example.com`.
- `company_aliases()` is cached per process: restart Streamlit after ingesting a new company.
- With the company filter off, every eval question's top hit still comes from the right company and
  Item; the embedding header does most of that work.
- `qwen2.5:7b` sometimes appends "Not found in the indexed filings." after a complete answer.
- The grounding check ignores numbers with fewer than three significant characters and four-digit years
  starting with 19 or 20.

## Environment facts

- Developed on an Apple M4 Pro with 24 GB RAM, macOS, Python 3.12.15, uv 0.13.0, Ollama 0.40.3.
- macOS QuickLook can rasterize SVG without extra tools:
  `qlmanage -t -s 512 -o /tmp file.svg` (set the SVG's width and height to the target size first).
