"""Retrieval evaluation against labeled questions.

Two levels of strictness:
- section level: a top-k chunk comes from the expected company and 10-K Item (hit rate@k, MRR);
- evidence level: a top-k chunk contains a specific fact string, e.g. "42,000 employees".
  Items like Item 8 are long, so a section-level hit does not guarantee the answer was retrieved.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

import yaml

from .retrieve import Hit, retrieve


@dataclass
class EvalCase:
    question: str
    ticker: str
    items: list[str]
    evidence: str | None = None


@dataclass
class EvalResult:
    case: EvalCase
    hits: list[Hit]
    rank: int | None  # 1-based rank of the first chunk from the expected section
    evidence_rank: int | None  # 1-based rank of the first chunk containing the evidence string
    answer: str = ""
    unsupported: list[str] = field(default_factory=list)
    citation_issues: list[str] = field(default_factory=list)


def load_cases(path: Path) -> list[EvalCase]:
    raw = yaml.safe_load(path.read_text())
    return [
        EvalCase(
            question=r["question"],
            ticker=r["ticker"].upper(),
            items=[str(i).upper() for i in r["items"]],
            evidence=r.get("evidence"),
        )
        for r in raw
    ]


def is_relevant(hit: Hit, case: EvalCase) -> bool:
    return hit.metadata["ticker"] == case.ticker and hit.metadata["item"] in case.items


def first_rank(hits: list[Hit], predicate) -> int | None:
    return next((n for n, h in enumerate(hits, start=1) if predicate(h)), None)


def evaluate_case(case: EvalCase, k: int, company_filter: bool = True) -> EvalResult:
    hits = retrieve(case.question, k=k, tickers=None if company_filter else [])
    evidence_rank = None
    if case.evidence:
        evidence_rank = first_rank(
            hits, lambda h: h.metadata["ticker"] == case.ticker and case.evidence in h.text
        )
    return EvalResult(
        case=case,
        hits=hits,
        rank=first_rank(hits, lambda h: is_relevant(h, case)),
        evidence_rank=evidence_rank,
    )


def summarize(results: list[EvalResult]) -> dict[str, float]:
    n = len(results)
    with_evidence = [r for r in results if r.case.evidence]
    return {
        "questions": n,
        "hit_rate": sum(r.rank is not None for r in results) / n,
        "mrr": sum(1 / r.rank for r in results if r.rank) / n,
        "evidence_questions": len(with_evidence),
        "evidence_hit_rate": (
            sum(r.evidence_rank is not None for r in with_evidence) / len(with_evidence) if with_evidence else 0.0
        ),
    }
