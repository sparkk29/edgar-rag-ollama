# Tech stack

Versions are what is installed as of 2026-10-13; the minimums are in `pyproject.toml` and exact
pins in `uv.lock`.

## Runtime

| Component | Version | Role | Why this one |
|---|---|---|---|
| Python | 3.12.15 | Language | Modern typing, stable ecosystem; pinned in `.python-version` |
| Ollama | 0.40.3 | Local model server | One command to pull and serve models; simple HTTP API |
| `qwen2.5:7b` | 4.7 GB | Chat model (default) | Fewer ungrounded figures and more complete answers than `llama3.1:8b` in our eval |
| `llama3.1:8b` | 4.9 GB | Chat model (alternative) | Benchmark comparison; works via `EDGAR_RAG_CHAT_MODEL` |
| `nomic-embed-text` | 274 MB | Embeddings | Strong small embedding model; 8k context; task prefixes |

## Python dependencies

| Package | Installed | Used for |
|---|---|---|
| `httpx` | 0.28.1 | EDGAR HTTP client (timeouts, redirects, gzip) |
| `beautifulsoup4` | 4.15.0 | HTML traversal and cleanup |
| `lxml` | 6.1.3 | Fast, tolerant HTML parser backend |
| `chromadb` | 1.5.9 | Embedded persistent vector store with metadata filters |
| `ollama` | 0.6.3 | Python client for embeddings and streaming chat |
| `python-dotenv` | 1.2.4 | Load `.env` into the environment |
| `pyyaml` | 6.0.3 | Read `eval/questions.yaml` |
| `typer` | 0.27.3 | CLI commands and options |
| `rich` | 15.0.0 | Tables, spinners and colored warnings in the CLI |
| `streamlit` | 1.65.0 | Chat UI |

## Development

| Tool | Version | Used for |
|---|---|---|
| `uv` | 0.13.0 | Environment, dependency resolution, lockfile, running commands |
| `hatchling` | (build backend) | Builds the `edgar_rag` package from `src/` |
| `pytest` | 9.1.1 | Unit tests (`[dependency-groups] dev`) |

## Deliberately not used

| Not used | Reason |
|---|---|
| LangChain, LlamaIndex | Every step stays a small, readable function; easier to explain and debug |
| Cloud LLMs (OpenAI, Anthropic, ...) | Privacy, cost, no API keys; the point is a fully local system |
| A separate vector database server | Chroma runs embedded; nothing extra to start |
| A web backend (FastAPI, ...) | The CLI and Streamlit call the library directly |
