"""Dense retrieval with company-aware metadata filtering."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from functools import lru_cache

from .config import settings
from .index import embed_query, get_collection

# Extra names people use for the default companies; any other ingested ticker is matched by its
# ticker symbol and the first word of its SEC company name.
EXTRA_ALIASES = {
    "AAPL": ["apple", "iphone maker", "cupertino"],
    "MSFT": ["microsoft", "redmond"],
    "NVDA": ["nvidia", "jensen"],
}


@dataclass
class Hit:
    id: str
    text: str
    metadata: dict
    distance: float

    @property
    def label(self) -> str:
        m = self.metadata
        return f"{m['company']} ({m['ticker']}) 10-K FY{m['fiscal_year']}, Item {m['item']}: {m['item_title']}"


@lru_cache(maxsize=1)
def company_aliases() -> dict[str, list[str]]:
    aliases: dict[str, list[str]] = {}
    for path in settings.raw_dir.glob("*_10K.json"):
        meta = json.loads(path.read_text())
        ticker = meta["ticker"].upper()
        first_word = re.sub(r"[^a-z]", "", meta["company"].lower().split()[0])
        aliases[ticker] = sorted({ticker.lower(), first_word, *EXTRA_ALIASES.get(ticker, [])})
    return aliases


def detect_companies(question: str) -> list[str]:
    """Return tickers mentioned in the question, in order of first mention."""
    q = question.lower()
    found: list[tuple[int, str]] = []
    for ticker, names in company_aliases().items():
        positions = [m.start() for name in names for m in re.finditer(rf"\b{re.escape(name)}\b", q)]
        if positions:
            found.append((min(positions), ticker))
    return [t for _, t in sorted(found)]


def _query(embedding: list[float], k: int, where: dict | None) -> list[Hit]:
    res = get_collection().query(
        query_embeddings=[embedding],
        n_results=k,
        where=where,
        include=["documents", "metadatas", "distances"],
    )
    return [
        Hit(id=i, text=d, metadata=m, distance=dist)
        for i, d, m, dist in zip(res["ids"][0], res["documents"][0], res["metadatas"][0], res["distances"][0])
    ]


def retrieve(question: str, k: int | None = None, tickers: list[str] | None = None) -> list[Hit]:
    """Retrieve the most relevant chunks.

    - No company mentioned: search everything.
    - One company: restrict to that company's filing.
    - Several companies (comparisons): retrieve separately per company so each one is represented,
      then interleave the results so the strongest hit for each company comes first.
    """
    k = k or settings.top_k
    tickers = tickers if tickers is not None else detect_companies(question)
    embedding = embed_query(question)

    if len(tickers) <= 1:
        where = {"ticker": tickers[0]} if tickers else None
        return _query(embedding, k, where)

    per_company = max(3, k // len(tickers))
    groups = [_query(embedding, per_company, {"ticker": t}) for t in tickers]
    interleaved: list[Hit] = []
    for rank in range(per_company):
        interleaved.extend(g[rank] for g in groups if rank < len(g))
    return interleaved
