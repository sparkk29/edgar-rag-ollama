from edgar_rag.evaluate import EvalCase, EvalResult, first_rank, is_relevant, summarize
from edgar_rag.retrieve import Hit


def _hit(ticker: str, item: str, text: str = "") -> Hit:
    return Hit(id=f"{ticker}-{item}", text=text, metadata={"ticker": ticker, "item": item}, distance=0.1)


CASE = EvalCase(question="q", ticker="NVDA", items=["1A", "7"], evidence="42,000 employees")


def test_relevance_requires_ticker_and_item():
    assert is_relevant(_hit("NVDA", "7"), CASE)
    assert not is_relevant(_hit("AAPL", "7"), CASE)
    assert not is_relevant(_hit("NVDA", "8"), CASE)


def test_first_rank_is_one_based():
    hits = [_hit("NVDA", "8"), _hit("NVDA", "1A")]
    assert first_rank(hits, lambda h: is_relevant(h, CASE)) == 2
    assert first_rank(hits[:1], lambda h: is_relevant(h, CASE)) is None


def test_summarize_hit_rate_mrr_and_evidence():
    no_evidence = EvalCase(question="q2", ticker="NVDA", items=["1"])
    results = [
        EvalResult(case=CASE, hits=[], rank=1, evidence_rank=None),
        EvalResult(case=CASE, hits=[], rank=2, evidence_rank=3),
        EvalResult(case=no_evidence, hits=[], rank=None, evidence_rank=None),
    ]
    stats = summarize(results)
    assert stats["hit_rate"] == 2 / 3
    assert stats["mrr"] == (1 + 0.5) / 3
    assert stats["evidence_questions"] == 2
    assert stats["evidence_hit_rate"] == 0.5
