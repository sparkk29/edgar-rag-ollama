"""Turn a 10-K HTML document into clean text split by Item (1, 1A, 7, 7A, 8, ...)."""

from __future__ import annotations

import re
import warnings
from dataclasses import dataclass

from bs4 import BeautifulSoup, NavigableString, XMLParsedAsHTMLWarning

warnings.filterwarnings("ignore", category=XMLParsedAsHTMLWarning)

ITEM_TITLES: dict[str, str] = {
    "1": "Business",
    "1A": "Risk Factors",
    "1B": "Unresolved Staff Comments",
    "1C": "Cybersecurity",
    "2": "Properties",
    "3": "Legal Proceedings",
    "4": "Mine Safety Disclosures",
    "5": "Market for Registrant's Common Equity, Related Stockholder Matters and Issuer Purchases of Equity Securities",
    "6": "[Reserved]",
    "7": "Management's Discussion and Analysis of Financial Condition and Results of Operations",
    "7A": "Quantitative and Qualitative Disclosures About Market Risk",
    "8": "Financial Statements and Supplementary Data",
    "9": "Changes in and Disagreements with Accountants on Accounting and Financial Disclosure",
    "9A": "Controls and Procedures",
    "9B": "Other Information",
    "9C": "Disclosure Regarding Foreign Jurisdictions that Prevent Inspections",
    "10": "Directors, Executive Officers and Corporate Governance",
    "11": "Executive Compensation",
    "12": "Security Ownership of Certain Beneficial Owners and Management and Related Stockholder Matters",
    "13": "Certain Relationships and Related Transactions, and Director Independence",
    "14": "Principal Accountant Fees and Services",
    "15": "Exhibits and Financial Statement Schedules",
    "16": "Form 10-K Summary",
}
ITEM_ORDER = list(ITEM_TITLES)

# "Item 1A. Risk Factors", "ITEM 7. MANAGEMENT'S ...", "Item 1A. | Risk Factors | 12" (table rows).
# The title must start with a letter or "[" so running headers like "Item 1B, 1C" are ignored.
HEADING_RE = re.compile(r"^item\s+(\d{1,2}[a-c]?)\s*[.:]?\s*(?:\|\s*)?([A-Za-z\[].*)$", re.IGNORECASE)

BLOCK_TAGS = ["p", "div", "br", "li", "h1", "h2", "h3", "h4", "h5", "h6", "section"]
_PAGE_NOISE = [
    re.compile(r"^\d{1,3}$"),
    re.compile(r"^page \d+$", re.IGNORECASE),
    re.compile(r"\|\s*\d{4} Form 10-K\s*\|", re.IGNORECASE),
    re.compile(r"^(part\s+[iv]+\s*)?item\s+[\d,\sa-c]+$", re.IGNORECASE),
    re.compile(r"^table of contents$", re.IGNORECASE),
    re.compile(r"^part\s+[iv]+$", re.IGNORECASE),
]


@dataclass
class Section:
    item: str
    title: str
    text: str

    @property
    def word_count(self) -> int:
        return len(self.text.split())


def _clean(text: str) -> str:
    return re.sub(r"\s+", " ", text.replace("\xa0", " ")).strip()


def _merge_unit_cells(cells) -> list[str]:
    """Filers put '$', '%' and closing ')' in their own cells; glue them back onto the number."""
    out: list[str] = []
    prefix = ""
    for cell in cells:
        if not cell:
            continue
        if cell == "$":
            prefix = "$"
        elif cell in {"%", ")", "%)"} and out:
            out[-1] += cell
        else:
            out.append(prefix + cell)
            prefix = ""
    return out


def html_to_lines(html: str | bytes) -> list[str]:
    """Flatten the document into one line per block element; tables become ' | '-joined rows."""
    soup = BeautifulSoup(html, "lxml")
    for tag in soup(["script", "style", "head"]):
        tag.decompose()
    for tag in soup.find_all(lambda t: t.name in ("ix:header",)):
        tag.decompose()
    for tag in soup.find_all(style=re.compile(r"display:\s*none", re.IGNORECASE)):
        tag.decompose()

    for table in soup.find_all("table"):
        rows = []
        for tr in table.find_all("tr"):
            cells = _merge_unit_cells(_clean(td.get_text(" ")) for td in tr.find_all(["td", "th"]))
            if cells:
                rows.append(" | ".join(cells))
        table.replace_with(NavigableString("\n" + "\n".join(rows) + "\n"))

    for tag in soup.find_all(BLOCK_TAGS):
        tag.insert_after(NavigableString("\n"))

    lines = (_clean(line) for line in soup.get_text("").split("\n"))
    return [line for line in lines if line and not any(p.search(line) for p in _PAGE_NOISE)]


def find_headings(lines: list[str]) -> dict[str, int]:
    """Map item id -> line index of its real heading.

    Each heading appears at least twice (table of contents, then the section itself), so we keep
    the last occurrence of each item and then drop any that break document order.
    """
    last: dict[str, int] = {}
    for i, line in enumerate(lines):
        if len(line) > 250:
            continue
        m = HEADING_RE.match(line)
        if m and m.group(1).upper() in ITEM_TITLES:
            last[m.group(1).upper()] = i

    ordered: dict[str, int] = {}
    prev = -1
    for item in ITEM_ORDER:
        if item in last and last[item] > prev:
            ordered[item] = last[item]
            prev = last[item]
    return ordered


def split_items(html: str | bytes) -> list[Section]:
    lines = html_to_lines(html)
    headings = find_headings(lines)
    starts = sorted(headings.items(), key=lambda kv: kv[1])
    sections = []
    for n, (item, start) in enumerate(starts):
        end = starts[n + 1][1] if n + 1 < len(starts) else len(lines)
        body = "\n".join(lines[start + 1 : end]).strip()
        sections.append(Section(item=item, title=ITEM_TITLES[item], text=body))
    return sections
