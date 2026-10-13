"""Embeddings via Ollama and storage in a persistent Chroma collection."""

from __future__ import annotations

from collections.abc import Callable, Sequence

import chromadb
import ollama

from .chunk import Chunk
from .config import settings

# nomic-embed-text was trained with task prefixes; using them noticeably improves retrieval.
DOC_PREFIX = "search_document: "
QUERY_PREFIX = "search_query: "

_ollama: ollama.Client | None = None


def ollama_client() -> ollama.Client:
    global _ollama
    if _ollama is None:
        _ollama = ollama.Client(host=settings.ollama_host)
    return _ollama


def embed(texts: Sequence[str], prefix: str = DOC_PREFIX) -> list[list[float]]:
    resp = ollama_client().embed(
        model=settings.embed_model,
        input=[prefix + t for t in texts],
        truncate=True,
        options={"num_ctx": 8192},
    )
    return [list(v) for v in resp.embeddings]


def embed_query(text: str) -> list[float]:
    return embed([text], prefix=QUERY_PREFIX)[0]


def get_collection() -> chromadb.Collection:
    settings.chroma_dir.mkdir(parents=True, exist_ok=True)
    client = chromadb.PersistentClient(
        path=str(settings.chroma_dir),
        settings=chromadb.Settings(anonymized_telemetry=False),
    )
    return client.get_or_create_collection(
        name=settings.collection_name,
        configuration={"hnsw": {"space": "cosine"}},
        embedding_function=None,
    )


def index_chunks(
    chunks: list[Chunk],
    batch_size: int = 32,
    on_progress: Callable[[int, int], None] | None = None,
) -> int:
    """Replace all chunks belonging to the same filings, then upsert the new ones.

    Deleting first keeps the index exact if a re-parse produces fewer chunks than before;
    stable chunk IDs make the upsert itself idempotent.
    """
    if not chunks:
        return 0
    collection = get_collection()
    for ticker, year in {(c.metadata["ticker"], c.metadata["fiscal_year"]) for c in chunks}:
        collection.delete(where={"$and": [{"ticker": ticker}, {"fiscal_year": year}]})

    for start in range(0, len(chunks), batch_size):
        batch = chunks[start : start + batch_size]
        collection.upsert(
            ids=[c.id for c in batch],
            documents=[c.text for c in batch],
            metadatas=[c.metadata for c in batch],
            embeddings=embed([c.embedding_text() for c in batch]),
        )
        if on_progress:
            on_progress(min(start + batch_size, len(chunks)), len(chunks))
    return len(chunks)
