# Database

The project stores data in two places, both under `data/` and both git-ignored: a **Chroma vector
store** and a **file cache** of raw EDGAR downloads. Everything can be rebuilt with
`uv run edgar-rag ingest`.

## Chroma vector store

| Property | Value |
|---|---|
| Client | `chromadb.PersistentClient`, embedded (no server) |
| Path | `data/chroma/` |
| Collection | `tenk_chunks` |
| Distance | Cosine (`configuration={"hnsw": {"space": "cosine"}}`) |
| Embedding function | None; embeddings are computed with Ollama and passed in |
| Telemetry | Disabled (`anonymized_telemetry=False`) |
| Current size | 572 records (AAPL FY2025, MSFT FY2026, NVDA FY2026) |

### Record schema

| Field | Type | Example | Notes |
|---|---|---|---|
| `id` | str | `NVDA-2026-1A-0003` | `{ticker}-{fiscal_year}-{item}-{chunk_index:04d}`; stable across re-ingests |
| `document` | str | chunk text | Without the header; the header is only in the embedded text |
| `embedding` | float[768] | | `nomic-embed-text` of `search_document: {header}\n{text}` |
| `metadata.ticker` | str | `NVDA` | Used for company filters |
| `metadata.company` | str | `NVIDIA CORP` | SEC company name |
| `metadata.fiscal_year` | str | `2026` | First four characters of the report date |
| `metadata.filing_date` | str | `2026-02-25` | |
| `metadata.item` | str | `1A` | 10-K Item id |
| `metadata.item_title` | str | `Risk Factors` | |
| `metadata.url` | str | `https://www.sec.gov/Archives/...` | Link shown in citations |
| `metadata.chunk_index` | int | `3` | Position within the Item |

### Writes

`index_chunks` runs per ingest:

1. For each (ticker, fiscal year) in the new chunks, delete all records matching both.
2. Upsert the new chunks in batches of 32 with their embeddings.

Deleting first means a re-parse that produces fewer chunks leaves nothing stale; stable IDs make the
upsert itself idempotent. Another fiscal year of the same company is not touched.

### Reads

`retrieve._query` calls `collection.query` with the query embedding, `n_results=k`, an optional
`where` filter (`{"ticker": "NVDA"}`), and returns documents, metadatas and distances as `Hit`s.

## File cache (`data/raw/`)

| File | Content | Refreshed |
|---|---|---|
| `company_tickers.json` | SEC ticker-to-CIK table | Never automatically; delete to refresh |
| `submissions_{cik}.json` | Company filing history | With `ingest --refresh` |
| `{TICKER}_{FY}_10K.htm` | Primary 10-K document | Downloaded once per fiscal year |
| `{TICKER}_{FY}_10K.json` | `Filing` fields plus `url` | Rewritten on every ingest |

`retrieve.company_aliases()` reads the `*_10K.json` files to know which companies are indexed.
It is cached for the life of the process, so restart the Streamlit app after ingesting a new company.

## Maintenance

```bash
rm -rf data/chroma && uv run edgar-rag ingest     # rebuild the index (e.g. after changing embed model or chunk size)
rm -rf data && uv run edgar-rag ingest            # start completely fresh (re-downloads ~12 MB)
uv run python -c "from edgar_rag.index import get_collection; print(get_collection().count())"
```

Changing `EDGAR_RAG_EMBED_MODEL` requires rebuilding the index: old and new vectors are not comparable.
