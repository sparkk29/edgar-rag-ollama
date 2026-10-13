# API

edgar-rag has no web API. Its interfaces are the **CLI**, the **Python library** that the CLI and
UI share, and the **external APIs** it calls (SEC EDGAR and Ollama).

## CLI

Run with `uv run edgar-rag <command>`; `--help` works on every command.

### `ingest`

Download, parse, chunk, embed and index the latest 10-K for each ticker.

| Option | Default | Meaning |
|---|---|---|
| `--tickers TEXT` | `EDGAR_RAG_TICKERS` (AAPL,MSFT,NVDA) | Comma-separated tickers |
| `--refresh` | off | Re-fetch the EDGAR filing index to catch newer 10-Ks |

Prints a summary table: ticker, company, fiscal year, filing date, Items, chunks, seconds.

### `ask QUESTION`

Answer one question with citations, run the checks and list the sources.

| Option | Default | Meaning |
|---|---|---|
| `--k INTEGER` | `EDGAR_RAG_TOP_K` (6) | Number of chunks to retrieve |
| `--show-context` | off | Print the first 1,200 characters of each retrieved chunk |

Output: `Filtered to: ...` (if companies were detected), the streamed answer, any
`Grounding check:` or `Citation check:` warnings, and a sources table with distance and URL.

### `eval`

Score retrieval on the labeled questions; optionally generate and check answers.

| Option | Default | Meaning |
|---|---|---|
| `--k INTEGER` | 6 | Retrieval depth |
| `--questions PATH` | `eval/questions.yaml` | Labeled question file |
| `--answers` | off | Also generate answers and run both checks |
| `--company-filter / --no-company-filter` | on | Disable the filter for an ablation |
| `--output PATH` | none | Write a Markdown report |

## Python library

Import from `edgar_rag.<module>`. Signatures as implemented:

```python
# edgar.py
EdgarClient(user_agent: str | None = None, cache_dir: Path | None = None)
EdgarClient.ticker_to_cik(ticker: str) -> tuple[int, str]
EdgarClient.latest_10k(ticker: str, refresh: bool = False) -> Filing
EdgarClient.download(filing: Filing) -> Path          # writes <TICKER>_<FY>_10K.htm and .json
EdgarClient.close() -> None

# parse.py
html_to_lines(html: str | bytes) -> list[str]
find_headings(lines: list[str]) -> dict[str, int]     # item id -> line index
split_items(html: str | bytes) -> list[Section]

# chunk.py
chunk_text(text: str, max_words: int = 600, overlap_words: int = 80) -> list[str]
chunk_sections(sections, filing_meta: dict, max_words=600, overlap_words=80, min_words=15) -> list[Chunk]

# index.py
embed(texts: Sequence[str], prefix: str = "search_document: ") -> list[list[float]]
embed_query(text: str) -> list[float]
get_collection() -> chromadb.Collection
index_chunks(chunks: list[Chunk], batch_size: int = 32, on_progress=None) -> int

# retrieve.py
company_aliases() -> dict[str, list[str]]             # cached; built from data/raw/*_10K.json
detect_companies(question: str) -> list[str]          # tickers in order of first mention
retrieve(question: str, k: int | None = None, tickers: list[str] | None = None) -> list[Hit]

# answer.py
build_messages(question: str, hits: list[Hit]) -> list[dict]
stream_answer(question: str, hits: list[Hit]) -> Iterator[str]
answer(question: str, hits: list[Hit]) -> str
unsupported_numbers(answer_text: str, hits: list[Hit]) -> list[str]
citation_problems(answer_text: str, hits: list[Hit]) -> list[str]

# evaluate.py
load_cases(path: Path) -> list[EvalCase]
evaluate_case(case: EvalCase, k: int, company_filter: bool = True) -> EvalResult
summarize(results: list[EvalResult]) -> dict[str, float]
```

The CLI passes `settings.chunk_words` (300) and `settings.chunk_overlap_words` (50) to
`chunk_sections`; the function defaults (600/80) apply only when it is called directly.

Example:

```python
from edgar_rag.retrieve import retrieve
from edgar_rag.answer import answer, unsupported_numbers

hits = retrieve("How many employees does NVIDIA have?")
text = answer("How many employees does NVIDIA have?", hits)
print(text, unsupported_numbers(text, hits))
```

## External APIs

### SEC EDGAR

| Endpoint | Used for | Cached as |
|---|---|---|
| `https://www.sec.gov/files/company_tickers.json` | Ticker to CIK and company title | `data/raw/company_tickers.json` |
| `https://data.sec.gov/submissions/CIK{cik:010d}.json` | Recent filings list, latest 10-K | `data/raw/submissions_{cik}.json` |
| `https://www.sec.gov/Archives/edgar/data/{cik}/{accession}/{document}` | Filing HTML | `data/raw/{TICKER}_{FY}_10K.htm` |

Requirements: `User-Agent: Name email` on every request, at most 10 requests per second.

### Ollama (`OLLAMA_HOST`, default `http://localhost:11434`)

| Call | Model | Options |
|---|---|---|
| `embed` | `nomic-embed-text` | `truncate=True`, `num_ctx` 8192 |
| `chat` (streamed) | `qwen2.5:7b` | `temperature` 0, `num_ctx` 16384 |
