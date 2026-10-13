"""Central configuration. Every value can be overridden through environment variables or `.env`."""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[2]
load_dotenv(PROJECT_ROOT / ".env")


def _env_list(name: str, default: str) -> list[str]:
    return [t.strip().upper() for t in os.getenv(name, default).split(",") if t.strip()]


@dataclass(frozen=True)
class Settings:
    tickers: list[str] = field(default_factory=lambda: _env_list("EDGAR_RAG_TICKERS", "AAPL,MSFT,NVDA"))
    sec_user_agent: str = os.getenv("SEC_USER_AGENT", "")

    ollama_host: str = os.getenv("OLLAMA_HOST", "http://localhost:11434")
    chat_model: str = os.getenv("EDGAR_RAG_CHAT_MODEL", "qwen2.5:7b")
    embed_model: str = os.getenv("EDGAR_RAG_EMBED_MODEL", "nomic-embed-text")

    # Chunk sizes are in words (roughly 0.75 words per token, so 300 words is about 400 tokens).
    # 300 beat 600 on evidence hit rate@6 (100% vs 95%); see README "Evaluation".
    chunk_words: int = int(os.getenv("EDGAR_RAG_CHUNK_WORDS", "300"))
    chunk_overlap_words: int = int(os.getenv("EDGAR_RAG_CHUNK_OVERLAP_WORDS", "50"))
    top_k: int = int(os.getenv("EDGAR_RAG_TOP_K", "6"))
    num_ctx: int = int(os.getenv("EDGAR_RAG_NUM_CTX", "16384"))

    data_dir: Path = PROJECT_ROOT / "data"
    collection_name: str = "tenk_chunks"

    @property
    def raw_dir(self) -> Path:
        return self.data_dir / "raw"

    @property
    def chroma_dir(self) -> Path:
        return self.data_dir / "chroma"


settings = Settings()
