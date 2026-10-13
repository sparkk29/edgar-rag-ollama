"""Grounded answer generation with numbered citations and a numeric grounding check."""

from __future__ import annotations

import re
from collections.abc import Iterator

from .config import settings
from .index import ollama_client
from .retrieve import Hit

NOT_FOUND = "Not found in the indexed filings."

SYSTEM_PROMPT = f"""You are a financial research assistant answering questions about SEC Form 10-K filings.

Rules:
- Use ONLY the numbered sources provided. Do not use outside knowledge.
- Cite every factual claim with its source number in square brackets, e.g. [1] or [2][4].
  Every sentence and every bullet point must end with at least one citation.
- Copy figures exactly as written in the sources, with their units and fiscal years.
- Never calculate, convert, or estimate numbers. A growth percentage is not a dollar amount.
- If a figure is not in the sources, describe the item without a number instead of guessing.
- When comparing companies, address each company separately and then summarize the difference.
- If the sources do not contain the answer, reply exactly: "{NOT_FOUND}"
- Be concise: a short paragraph or a few bullet points."""

_NUMBER_RE = re.compile(r"(?<![\w\[])\d[\d,]*(?:\.\d+)?")
_CITATION_RE = re.compile(r"\[(\d+)\]")


def format_sources(hits: list[Hit]) -> str:
    return "\n\n".join(f"[{n}] {hit.label}\n{hit.text}" for n, hit in enumerate(hits, start=1))


def build_messages(question: str, hits: list[Hit]) -> list[dict]:
    user = f"Sources:\n\n{format_sources(hits)}\n\nQuestion: {question}\n\nAnswer with citations:"
    return [{"role": "system", "content": SYSTEM_PROMPT}, {"role": "user", "content": user}]


def stream_answer(question: str, hits: list[Hit]) -> Iterator[str]:
    """Yield the answer token by token."""
    if not hits:
        yield NOT_FOUND
        return
    stream = ollama_client().chat(
        model=settings.chat_model,
        messages=build_messages(question, hits),
        stream=True,
        options={"temperature": 0, "num_ctx": settings.num_ctx},
    )
    for part in stream:
        yield part.message.content or ""


def answer(question: str, hits: list[Hit]) -> str:
    return "".join(stream_answer(question, hits))


def citation_problems(answer_text: str, hits: list[Hit]) -> list[str]:
    """Describe citation issues: no citations at all, or citations to sources that don't exist."""
    if answer_text.strip() == NOT_FOUND:
        return []
    cited = {int(n) for n in _CITATION_RE.findall(answer_text)}
    if not cited:
        return ["answer has no [n] citations"]
    invalid = sorted(n for n in cited if not 1 <= n <= len(hits))
    return [f"cites nonexistent source [{n}]" for n in invalid]


def unsupported_numbers(answer_text: str, hits: list[Hit]) -> list[str]:
    """Return figures in the answer that never appear in the sources.

    Small 8B models occasionally invent or "convert" numbers. This cheap check catches that:
    every number with 3+ significant characters (ignoring years and citation markers like [3])
    must appear verbatim, modulo thousands separators, in at least one retrieved chunk.
    """
    sources = " ".join(h.text for h in hits).replace(",", "")
    missing: list[str] = []
    for raw in _NUMBER_RE.findall(answer_text):
        value = raw.rstrip(".,").replace(",", "")
        if len(value.replace(".", "")) < 3 or re.fullmatch(r"(19|20)\d\d", value):
            continue
        if not re.search(rf"(?<![\d.]){re.escape(value)}(?![\d]|\.\d)", sources):
            if raw not in missing:
                missing.append(raw.rstrip(".,"))
    return missing
