"""Command-line interface: `edgar-rag ingest | ask | eval`."""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console
from rich.table import Table

from .config import PROJECT_ROOT, settings

app = typer.Typer(add_completion=False, help="Local RAG assistant over SEC 10-K filings.")
console = Console()


def _tickers(value: str | None) -> list[str]:
    return [t.strip().upper() for t in value.split(",")] if value else settings.tickers


@app.command()
def ingest(
    tickers: Annotated[str | None, typer.Option(help="Comma-separated tickers, e.g. AAPL,MSFT")] = None,
    refresh: Annotated[bool, typer.Option(help="Re-check EDGAR for newer 10-K filings")] = False,
) -> None:
    """Download the latest 10-K for each ticker, split it by Item, chunk, embed and index it."""
    from .chunk import chunk_sections
    from .edgar import EdgarClient
    from .index import index_chunks
    from .parse import split_items

    client = EdgarClient()
    summary = Table(title="Ingest summary")
    for col in ("Ticker", "Company", "FY", "Filed", "Items", "Chunks", "Seconds"):
        summary.add_column(col)

    try:
        for ticker in _tickers(tickers):
            started = time.monotonic()
            with console.status(f"[bold]{ticker}[/]: fetching 10-K from EDGAR"):
                filing = client.latest_10k(ticker, refresh=refresh)
                html_path = client.download(filing)
            meta = json.loads(html_path.with_suffix(".json").read_text()) | {"fiscal_year": filing.fiscal_year}

            sections = split_items(html_path.read_bytes())
            chunks = chunk_sections(sections, meta, settings.chunk_words, settings.chunk_overlap_words)
            with console.status(f"[bold]{ticker}[/]: embedding {len(chunks)} chunks") as status:
                index_chunks(chunks, on_progress=lambda d, t: status.update(f"[bold]{ticker}[/]: embedded {d}/{t}"))

            summary.add_row(
                ticker, filing.company, filing.fiscal_year, filing.filing_date,
                str(len(sections)), str(len(chunks)), f"{time.monotonic() - started:.1f}",
            )
    finally:
        client.close()
    console.print(summary)


@app.command()
def ask(
    question: Annotated[str, typer.Argument(help="Your question about the indexed filings")],
    k: Annotated[int, typer.Option(help="Number of chunks to retrieve")] = settings.top_k,
    show_context: Annotated[bool, typer.Option(help="Print the retrieved chunk text")] = False,
) -> None:
    """Answer a question with citations to 10-K sections."""
    from .answer import citation_problems, stream_answer, unsupported_numbers
    from .retrieve import detect_companies, retrieve

    companies = detect_companies(question)
    with console.status("Retrieving"):
        hits = retrieve(question, k=k, tickers=companies)
    if companies:
        console.print(f"[dim]Filtered to: {', '.join(companies)}[/]")

    console.print()
    text = ""
    for token in stream_answer(question, hits):
        text += token
        console.print(token, end="", markup=False, highlight=False)
    console.print("\n")

    missing = unsupported_numbers(text, hits)
    if missing:
        console.print(f"[yellow]Grounding check: these figures were not found in the sources: {', '.join(missing)}[/]\n")
    for problem in citation_problems(text, hits):
        console.print(f"[yellow]Citation check: {problem}[/]\n")

    table = Table(title="Sources", show_lines=show_context)
    for col in ("#", "Section", "Distance", "Filing"):
        table.add_column(col, overflow="fold")
    for n, hit in enumerate(hits, start=1):
        section = hit.label + (f"\n\n{hit.text[:1200]}" if show_context else "")
        table.add_row(str(n), section, f"{hit.distance:.3f}", hit.metadata["url"])
    console.print(table)


@app.command("eval")
def eval_cmd(
    k: Annotated[int, typer.Option(help="Retrieval depth")] = settings.top_k,
    questions: Annotated[Path, typer.Option(help="YAML file of labeled questions")] = PROJECT_ROOT / "eval" / "questions.yaml",
    answers: Annotated[bool, typer.Option(help="Also generate answers and run the grounding check")] = False,
    company_filter: Annotated[bool, typer.Option(help="Apply the company metadata filter (disable for an ablation)")] = True,
    output: Annotated[Path | None, typer.Option(help="Write a Markdown report here")] = None,
) -> None:
    """Measure retrieval quality: hit rate@k and MRR. Optionally generate answers too."""
    from .answer import answer, citation_problems, unsupported_numbers
    from .evaluate import evaluate_case, load_cases, summarize

    cases = load_cases(questions)
    results = []
    for n, case in enumerate(cases, start=1):
        with console.status(f"[{n}/{len(cases)}] {case.question}"):
            result = evaluate_case(case, k, company_filter)
            if answers:
                result.answer = answer(case.question, result.hits)
                result.unsupported = unsupported_numbers(result.answer, result.hits)
                result.citation_issues = citation_problems(result.answer, result.hits)
        results.append(result)

    table = Table(title=f"Retrieval eval (k={k}, company filter {'on' if company_filter else 'off'})")
    for col in ("Question", "Expected", "Section rank", "Evidence rank", "Top hit"):
        table.add_column(col, overflow="fold")
    if answers:
        table.add_column("Answer checks", overflow="fold")
    for r in results:
        top = r.hits[0].metadata if r.hits else {}
        row = [
            r.case.question,
            f"{r.case.ticker} {'/'.join(r.case.items)}",
            str(r.rank) if r.rank else "[red]miss[/]",
            _evidence_cell(r, rich=True),
            f"{top.get('ticker', '')} {top.get('item', '')}",
        ]
        if answers:
            row.append(_answer_checks(r))
        table.add_row(*row)
    console.print(table)

    stats = summarize(results)
    console.print(
        f"[bold]Section hit rate@{k}: {stats['hit_rate']:.0%}   MRR: {stats['mrr']:.3f}   "
        f"Evidence hit rate@{k}: {stats['evidence_hit_rate']:.0%}[/]  "
        f"({stats['questions']} questions, {stats['evidence_questions']} with evidence)"
    )
    if answers:
        flagged = sum(bool(r.unsupported) for r in results)
        uncited = sum(bool(r.citation_issues) for r in results)
        console.print(f"[bold]Answers with ungrounded figures: {flagged}/{len(results)}[/]")
        console.print(f"[bold]Answers with citation problems: {uncited}/{len(results)}[/]")
        for r in results:
            console.rule(r.case.question)
            console.print(r.answer, markup=False, highlight=False)

    if output:
        output.write_text(_markdown_report(results, stats, k, answers))
        console.print(f"Report written to {output}")


def _answer_checks(r) -> str:
    problems = [f"ungrounded: {', '.join(r.unsupported)}"] if r.unsupported else []
    problems += r.citation_issues
    return "; ".join(problems) or "-"


def _evidence_cell(r, rich: bool = False) -> str:
    if not r.case.evidence:
        return "-"
    if r.evidence_rank:
        return str(r.evidence_rank)
    return "[red]miss[/]" if rich else "miss"


def _markdown_report(results, stats, k: int, answers: bool) -> str:
    lines = [
        f"# Eval report (k={k}, chat model `{settings.chat_model}`, embeddings `{settings.embed_model}`, "
        f"chunk {settings.chunk_words} words)",
        "",
        f"- Questions: {stats['questions']} ({stats['evidence_questions']} with an evidence string)",
        f"- Section hit rate@{k}: {stats['hit_rate']:.0%}",
        f"- Section MRR: {stats['mrr']:.3f}",
        f"- Evidence hit rate@{k}: {stats['evidence_hit_rate']:.0%}",
    ]
    if answers:
        flagged = sum(bool(r.unsupported) for r in results)
        uncited = sum(bool(r.citation_issues) for r in results)
        lines.append(f"- Answers with ungrounded figures: {flagged}/{len(results)}")
        lines.append(f"- Answers with citation problems: {uncited}/{len(results)}")
    lines += [
        "",
        "| Question | Expected | Section rank | Evidence rank | Top hit |",
        "|---|---|---|---|---|",
    ]
    for r in results:
        top = r.hits[0].metadata if r.hits else {}
        lines.append(
            f"| {r.case.question} | {r.case.ticker} {'/'.join(r.case.items)} | {r.rank or 'miss'} "
            f"| {_evidence_cell(r)} | {top.get('ticker', '')} {top.get('item', '')} |"
        )
    if answers:
        lines += ["", "## Answers", ""]
        for r in results:
            lines += [f"### {r.case.question}", "", r.answer.strip(), ""]
            if r.unsupported or r.citation_issues:
                lines += [f"> Answer checks: {_answer_checks(r)}", ""]
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    app()
