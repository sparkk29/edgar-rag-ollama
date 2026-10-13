"""Paragraph-aware chunking with per-chunk filing metadata."""

from __future__ import annotations

import re
from dataclasses import dataclass, field

from .parse import Section

_SENTENCE_RE = re.compile(r"(?<=[.!?])\s+")


@dataclass
class Chunk:
    id: str
    text: str
    metadata: dict = field(default_factory=dict)

    @property
    def header(self) -> str:
        m = self.metadata
        return f"{m['company']} ({m['ticker']}) 10-K FY{m['fiscal_year']}, Item {m['item']}: {m['item_title']}"

    def embedding_text(self) -> str:
        """Text sent to the embedding model: a context header makes chunks self-describing."""
        return f"{self.header}\n{self.text}"


def _split_long(paragraph: str, max_words: int) -> list[str]:
    """Break a paragraph longer than max_words on sentence boundaries (or hard word limits)."""
    pieces, current, count = [], [], 0
    for sentence in _SENTENCE_RE.split(paragraph):
        words = sentence.split()
        while len(words) > max_words:
            if current:
                pieces.append(" ".join(current))
                current, count = [], 0
            pieces.append(" ".join(words[:max_words]))
            words = words[max_words:]
        if not words:
            continue
        if count + len(words) > max_words and current:
            pieces.append(" ".join(current))
            current, count = [], 0
        current.append(" ".join(words))
        count += len(words)
    if current:
        pieces.append(" ".join(current))
    return [p for p in pieces if p.strip()]


def chunk_text(text: str, max_words: int = 600, overlap_words: int = 80) -> list[str]:
    """Greedily pack paragraphs into chunks of at most max_words.

    Consecutive chunks share up to overlap_words of trailing paragraphs so that a fact
    straddling a boundary still appears whole in at least one chunk.
    """
    paragraphs: list[str] = []
    for para in (p.strip() for p in text.split("\n")):
        if not para:
            continue
        paragraphs.extend(_split_long(para, max_words) if len(para.split()) > max_words else [para])

    chunks: list[str] = []
    current: list[str] = []
    count = 0
    for para in paragraphs:
        n = len(para.split())
        if current and count + n > max_words:
            chunks.append("\n".join(current))
            tail: list[str] = []
            tail_count = 0
            for prev in reversed(current):
                prev_n = len(prev.split())
                if tail_count + prev_n > overlap_words:
                    break
                tail.insert(0, prev)
                tail_count += prev_n
            if tail_count + n > max_words:
                tail, tail_count = [], 0
            current, count = tail, tail_count
        current.append(para)
        count += n
    if current:
        chunks.append("\n".join(current))
    return chunks


def chunk_sections(
    sections: list[Section],
    filing_meta: dict,
    max_words: int = 600,
    overlap_words: int = 80,
    min_words: int = 15,
) -> list[Chunk]:
    """Chunk every section and attach metadata. Very short sections (e.g. 'None.') are skipped."""
    out: list[Chunk] = []
    for section in sections:
        if section.word_count < min_words:
            continue
        for i, text in enumerate(chunk_text(section.text, max_words, overlap_words)):
            meta = {
                "ticker": filing_meta["ticker"],
                "company": filing_meta["company"],
                "fiscal_year": str(filing_meta["fiscal_year"]),
                "filing_date": filing_meta.get("filing_date", ""),
                "item": section.item,
                "item_title": section.title,
                "url": filing_meta["url"],
                "chunk_index": i,
            }
            chunk_id = f"{meta['ticker']}-{meta['fiscal_year']}-{section.item}-{i:04d}"
            out.append(Chunk(id=chunk_id, text=text, metadata=meta))
    return out
