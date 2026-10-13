# Decisions

Architecture decision records, newest last. Each says what was decided, why, and what it costs.
Add a new record instead of editing an old one; mark superseded ones.

## ADR-001: Run everything locally

- **Decision:** Ollama for chat and embeddings, embedded Chroma for vectors. No cloud services.
- **Why:** Privacy, zero cost, no API keys, works offline after ingest.
- **Cost:** 7-8B models are weaker at reasoning and arithmetic than frontier models (mitigated by ADR-009).

## ADR-002: No orchestration framework

- **Decision:** Plain Python functions instead of LangChain or LlamaIndex.
- **Why:** Each step is short, readable and testable; behavior is obvious when debugging.
- **Cost:** Features like hybrid search or reranking must be written by hand.

## ADR-003: Split by 10-K Item before chunking

- **Decision:** Detect Item headings and chunk within each Item; store the Item in metadata.
- **Why:** Citations can name the section (e.g. *Item 1A: Risk Factors*), and chunks never mix two sections.
- **Cost:** Depends on heading detection, which must skip the table of contents (last-occurrence rule).

## ADR-004: Chroma as the vector store

- **Decision:** `chromadb.PersistentClient` with cosine distance and metadata filters.
- **Why:** Embedded, persistent, supports `where` filters, no server to run.
- **Cost:** No built-in BM25; hybrid search needs a separate index.

## ADR-005: 300-word chunks with 50-word overlap

- **Decision:** `EDGAR_RAG_CHUNK_WORDS=300`, `EDGAR_RAG_CHUNK_OVERLAP_WORDS=50`.
- **Why:** Evidence hit rate@6 was 100% vs 95% for 600-word chunks; the NVIDIA headcount fact was
  diluted in long chunks. Prompts also became half as long, so answers are faster.
- **Cost:** About twice as many chunks (572 vs 287).
- **Evidence:** [`../knowledge/EXPERIMENTS.md`](../knowledge/EXPERIMENTS.md), EXP-001.

## ADR-006: Context header and nomic task prefixes in embeddings

- **Decision:** Embed `search_document: {company} ({ticker}) 10-K FY{year}, Item {item}: {title}\n{text}`;
  queries use `search_query:`.
- **Why:** The header makes each chunk self-describing (even with the company filter off, every top
  hit came from the right company and Item); nomic was trained with these prefixes.
- **Cost:** Changing the header format requires re-ingesting.

## ADR-007: Keyword company detection with metadata filter

- **Decision:** Match tickers, the first word of the SEC name and hand-written aliases; filter retrieval to those tickers.
  Comparisons retrieve per company and interleave.
- **Why:** Cheap, deterministic, and guarantees each named company appears in the sources.
- **Cost:** Brittle for indirect references ("the iPhone maker" needs an alias) and possible false
  positives (the word "apple" in another sense). Tracked as T-034.

## ADR-008: `qwen2.5:7b` as the default chat model

- **Decision:** Default `EDGAR_RAG_CHAT_MODEL=qwen2.5:7b`; `llama3.1:8b` remains supported.
- **Why:** 1/24 answers with ungrounded figures vs 2/24, more complete answers (e.g. reported the 25%
  OpenAI stake), slightly faster (313 s vs 324 s for 24 answers).
- **Evidence:** [`../knowledge/EXPERIMENTS.md`](../knowledge/EXPERIMENTS.md), EXP-002.

## ADR-009: Automatic grounding and citation checks

- **Decision:** After every answer, flag numbers absent from the sources and missing or invalid citations, in both CLI and UI.
- **Why:** In an early run `llama3.1:8b` invented three Microsoft product-revenue figures. Small models
  also do their own arithmetic and get it wrong.
- **Cost:** Cannot detect a real number attached to the wrong claim; users still need to read the sources.

## ADR-010: Forbid calculations in the prompt; temperature 0

- **Decision:** The prompt says never calculate, convert or estimate; copy figures exactly. Temperature 0.
- **Why:** Most flagged figures came from model arithmetic. Temperature 0 makes eval runs repeatable.
- **Cost:** The model will not answer questions that need arithmetic (e.g. growth rates not stated in the filing).

## ADR-011: Delete-then-upsert per filing

- **Decision:** Before indexing a filing, delete all chunks with the same ticker and fiscal year.
- **Why:** Keeps the index exact if a parser change produces fewer chunks.
- **Cost:** A brief window during ingest where that filing has no chunks.

## ADR-012: uv for environment and dependencies

- **Decision:** `uv sync` / `uv run`, lockfile committed.
- **Why:** Fast, reproducible, installs the right Python automatically.

## ADR-013: Repo named `edgar-rag-ollama`, package stays `edgar-rag`

- **Decision (2026-10-13):** GitHub repository `sparkk29/edgar-rag-ollama`; package, CLI and import names unchanged.
- **Why:** The repo name signals "local, Ollama" on GitHub; renaming the package would touch code,
  the CLI command and every doc for no functional gain.

## ADR-014: Documentation system in topic folders at the repo root

- **Decision (2026-10-13):** Root docs plus `planning/`, `state/`, `architecture/`, `quality/`, `knowledge/`.
- **Why:** Gives humans and AI agents a predictable place for plans, current state and lessons;
  `AGENTS.md` at the root is where agent tools look first.
