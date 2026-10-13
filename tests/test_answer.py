from edgar_rag.answer import NOT_FOUND, build_messages, citation_problems, unsupported_numbers
from edgar_rag.retrieve import Hit

HIT = Hit(
    id="ACME-2025-7-0000",
    text="Net sales | 209,586 | 201,183\nCloud revenue increased 27% to $214.4 billion in 2025.",
    metadata={"company": "Acme Corp", "ticker": "ACME", "fiscal_year": "2025", "item": "7", "item_title": "MD&A"},
    distance=0.2,
)


def test_grounded_numbers_pass():
    text = "Net sales were $209,586 million [1] and cloud revenue rose 27% to $214.4 billion in FY2025 [1]."
    assert unsupported_numbers(text, [HIT]) == []


def test_invented_numbers_are_flagged():
    text = "Azure revenue was $41.4 billion [1] and net sales were 209,587 [1]."
    assert unsupported_numbers(text, [HIT]) == ["41.4", "209,587"]


def test_partial_match_inside_larger_number_is_flagged():
    assert unsupported_numbers("Revenue grew 14.4 percent [1].", [HIT]) == ["14.4"]


def test_citation_problems():
    assert citation_problems("Sales grew [1][2].", [HIT, HIT]) == []
    assert citation_problems("Sales grew.", [HIT]) == ["answer has no [n] citations"]
    assert citation_problems("Sales grew [3].", [HIT]) == ["cites nonexistent source [3]"]
    assert citation_problems(NOT_FOUND, [HIT]) == []


def test_sources_are_numbered_in_prompt():
    messages = build_messages("What drove sales?", [HIT, HIT])
    user = messages[1]["content"]
    assert "[1] Acme Corp (ACME) 10-K FY2025, Item 7: MD&A" in user
    assert "[2] Acme Corp" in user
    assert user.rstrip().endswith("Answer with citations:")
