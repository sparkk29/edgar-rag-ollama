from pathlib import Path

from edgar_rag.parse import find_headings, html_to_lines, split_items

FIXTURE = (Path(__file__).parent / "fixtures" / "mini_10k.htm").read_text()


def test_hidden_and_noise_lines_removed():
    lines = html_to_lines(FIXTURE)
    joined = "\n".join(lines)
    assert "hidden xbrl facts" not in joined
    assert "color: red" not in joined
    assert "1" not in lines
    assert "PART I Item 1A" not in lines


def test_split_span_heading_is_joined():
    assert "ITEM 1. BUSINESS" in html_to_lines(FIXTURE)


def test_tables_become_pipe_rows_with_units_attached():
    lines = html_to_lines(FIXTURE)
    assert "Net sales | $1,000 | $893" in lines
    assert "Gross margin | 36.8% | ( 12)" in lines


def test_headings_skip_table_of_contents():
    lines = html_to_lines(FIXTURE)
    headings = find_headings(lines)
    assert list(headings) == ["1", "1A", "7", "8"]
    assert lines[headings["1"]] == "ITEM 1. BUSINESS"


def test_split_items_assigns_text_to_correct_section():
    sections = {s.item: s for s in split_items(FIXTURE)}
    assert sections["1"].title == "Business"
    assert "roadrunner" in sections["1"].text
    assert "anvils" in sections["1A"].text
    assert "Gravity" in sections["1A"].text
    assert "rocket skate" in sections["7"].text
    assert "anvils" not in sections["7"].text
    assert sections["8"].text == "Consolidated statements of operations follow."
