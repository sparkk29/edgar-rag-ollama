# Flow

How data and work move through the project. For component design see
[`architecture/ARCHITECTURE.md`](architecture/ARCHITECTURE.md).

## 1. Ingest flow (`edgar-rag ingest`)

```mermaid
flowchart TD
    T["Ticker, e.g. NVDA"] --> CIK["Look up CIK in company_tickers.json (cached)"]
    CIK --> Subs["Fetch submissions JSON, find the latest 10-K (cached unless --refresh)"]
    Subs --> HTML["Download primary HTML document to data/raw/ (cached)"]
    HTML --> Lines["html_to_lines: drop hidden XBRL, scripts, page noise; tables to 'a | b | c' rows"]
    Lines --> Items["find_headings + split_items: one Section per 10-K Item"]
    Items --> Chunks["chunk_sections: ~300-word chunks, 50-word overlap, metadata attached"]
    Chunks --> Embed["Ollama nomic-embed-text with 'search_document:' prefix"]
    Embed --> Store["Chroma: delete this ticker + fiscal year, then upsert"]
```

Per ticker, the CLI prints a summary row: company, fiscal year, filing date, number of Items,
number of chunks and seconds taken.

## 2. Question flow (`edgar-rag ask` and the Streamlit UI)

```mermaid
flowchart TD
    Q["Question"] --> Detect["detect_companies: match tickers, company names, aliases"]
    Detect --> Embed["Embed question with 'search_query:' prefix"]
    Embed --> Branch{"Companies named?"}
    Branch -->|None| All["Top-k over all chunks"]
    Branch -->|One| One["Top-k filtered to that ticker"]
    Branch -->|Several| Many["Top max(3, k / n) per ticker, interleaved"]
    All --> Prompt
    One --> Prompt
    Many --> Prompt["Grounded prompt with numbered sources [1]..[k]"]
    Prompt --> LLM["Ollama chat model, temperature 0, streamed"]
    LLM --> Checks["unsupported_numbers + citation_problems"]
    Checks --> Out["Answer, warnings, source table or cards with sec.gov links"]
```

In the UI, the sidebar multiselect overrides automatic company detection, and the slider sets k.

## 3. Evaluation flow (`edgar-rag eval`)

1. Load labeled cases from `eval/questions.yaml` (question, ticker, acceptable Items, optional evidence).
2. Retrieve top-k for each question (company filter on, or off with `--no-company-filter`).
3. Record the rank of the first chunk from the right section and the first chunk containing the evidence.
4. Summarize section hit rate@k, MRR and evidence hit rate@k.
5. With `--answers`, generate every answer and run both checks.
6. With `--output`, write a Markdown report (see `eval/reports/`).

## 4. Work flow (people and agents)

```mermaid
flowchart LR
    Start["Start session"] --> Read["Read state/RESUME, STATUS, BLOCKERS, planning/NEXT"]
    Read --> Pick["Pick a task in planning/TASKS"]
    Pick --> Build["Code + tests"]
    Build --> Validate["pytest; eval if retrieval or prompt changed"]
    Validate --> Check["planning/CHECKLIST"]
    Check --> Commit["Commit"]
    Commit --> Record["Update state/ and knowledge/"]
    Record --> Start
```

The detailed protocol is in [`AGENTS.md`](AGENTS.md).
