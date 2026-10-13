from edgar_rag.chunk import chunk_sections, chunk_text
from edgar_rag.parse import Section

META = {
    "ticker": "ACME",
    "company": "Acme Corp",
    "fiscal_year": "2025",
    "filing_date": "2025-11-01",
    "url": "https://www.sec.gov/Archives/edgar/data/1/2/acme.htm",
}


def _para(word: str, n: int) -> str:
    return " ".join([word] * n)


def test_short_text_is_single_chunk():
    assert chunk_text("one two three\nfour five", max_words=50) == ["one two three\nfour five"]


def test_chunks_respect_max_words():
    text = "\n".join(_para(f"w{i}", 40) for i in range(20))
    chunks = chunk_text(text, max_words=100, overlap_words=0)
    assert all(len(c.split()) <= 100 for c in chunks)
    assert sum(len(c.split()) for c in chunks) == 800


def test_overlap_repeats_trailing_paragraph():
    text = "\n".join(_para(f"p{i}", 30) for i in range(6))
    chunks = chunk_text(text, max_words=90, overlap_words=30)
    assert len(chunks) > 1
    last_para_of_first = chunks[0].split("\n")[-1]
    assert chunks[1].startswith(last_para_of_first)


def test_long_paragraph_split_on_sentences():
    sentence = _para("word", 20) + "."
    paragraph = " ".join([sentence] * 10)
    chunks = chunk_text(paragraph, max_words=50, overlap_words=0)
    assert all(len(c.split()) <= 50 for c in chunks)
    assert all(c.endswith(".") for c in chunks)


def test_chunk_sections_metadata_and_ids():
    sections = [
        Section("1", "Business", _para("rockets", 30)),
        Section("1B", "Unresolved Staff Comments", "None."),
        Section("1A", "Risk Factors", "\n".join(_para("anvil", 50) for _ in range(3))),
    ]
    chunks = chunk_sections(sections, META, max_words=60, overlap_words=0)
    items = [c.metadata["item"] for c in chunks]
    assert "1B" not in items
    assert items.count("1A") == 3
    assert chunks[0].id == "ACME-2025-1-0000"
    assert len({c.id for c in chunks}) == len(chunks)
    assert chunks[0].metadata["url"] == META["url"]
    assert chunks[0].embedding_text().startswith("Acme Corp (ACME) 10-K FY2025, Item 1: Business")
