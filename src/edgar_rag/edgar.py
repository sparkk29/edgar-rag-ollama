"""Minimal SEC EDGAR client: ticker lookup, latest 10-K discovery, cached download.

EDGAR rules (https://www.sec.gov/os/accessing-edgar-data):
- every request must send a descriptive User-Agent ("Name email"),
- at most 10 requests per second.
"""

from __future__ import annotations

import json
import time
from dataclasses import asdict, dataclass
from pathlib import Path

import httpx

from .config import settings

TICKERS_URL = "https://www.sec.gov/files/company_tickers.json"
SUBMISSIONS_URL = "https://data.sec.gov/submissions/CIK{cik:010d}.json"
ARCHIVE_URL = "https://www.sec.gov/Archives/edgar/data/{cik}/{accession}/{document}"

_MIN_INTERVAL_S = 0.15


@dataclass
class Filing:
    ticker: str
    company: str
    cik: int
    form: str
    accession: str
    filing_date: str
    report_date: str
    primary_document: str

    @property
    def fiscal_year(self) -> str:
        return self.report_date[:4]

    @property
    def url(self) -> str:
        return ARCHIVE_URL.format(
            cik=self.cik, accession=self.accession.replace("-", ""), document=self.primary_document
        )


class EdgarClient:
    def __init__(self, user_agent: str | None = None, cache_dir: Path | None = None):
        user_agent = user_agent or settings.sec_user_agent
        if not user_agent or "example.com" in user_agent:
            raise RuntimeError(
                "Set SEC_USER_AGENT in .env to 'Your Name your@email.com' (required by the SEC)."
            )
        self.cache_dir = cache_dir or settings.raw_dir
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self._http = httpx.Client(
            headers={"User-Agent": user_agent, "Accept-Encoding": "gzip, deflate"},
            timeout=60,
            follow_redirects=True,
        )
        self._last_request = 0.0

    def _get(self, url: str) -> httpx.Response:
        wait = _MIN_INTERVAL_S - (time.monotonic() - self._last_request)
        if wait > 0:
            time.sleep(wait)
        resp = self._http.get(url)
        self._last_request = time.monotonic()
        resp.raise_for_status()
        return resp

    def _cached_json(self, url: str, name: str, refresh: bool = False) -> dict:
        path = self.cache_dir / name
        if path.exists() and not refresh:
            return json.loads(path.read_text())
        data = self._get(url).json()
        path.write_text(json.dumps(data))
        return data

    def ticker_to_cik(self, ticker: str) -> tuple[int, str]:
        """Return (cik, company title) for a ticker symbol."""
        table = self._cached_json(TICKERS_URL, "company_tickers.json")
        for row in table.values():
            if row["ticker"].upper() == ticker.upper():
                return int(row["cik_str"]), row["title"]
        raise KeyError(f"Ticker {ticker!r} not found in SEC ticker list")

    def latest_10k(self, ticker: str, refresh: bool = False) -> Filing:
        """Most recent 10-K. With refresh=True the filing index is re-fetched to catch new filings."""
        cik, title = self.ticker_to_cik(ticker)
        subs = self._cached_json(SUBMISSIONS_URL.format(cik=cik), f"submissions_{cik}.json", refresh)
        recent = subs["filings"]["recent"]
        for i, form in enumerate(recent["form"]):
            if form == "10-K":
                return Filing(
                    ticker=ticker.upper(),
                    company=subs.get("name") or title,
                    cik=cik,
                    form=form,
                    accession=recent["accessionNumber"][i],
                    filing_date=recent["filingDate"][i],
                    report_date=recent["reportDate"][i],
                    primary_document=recent["primaryDocument"][i],
                )
        raise LookupError(f"No 10-K found in recent filings for {ticker}")

    def download(self, filing: Filing) -> Path:
        """Download the filing's primary HTML document (cached) and write its metadata alongside."""
        stem = f"{filing.ticker}_{filing.fiscal_year}_10K"
        html_path = self.cache_dir / f"{stem}.htm"
        meta_path = self.cache_dir / f"{stem}.json"
        if not html_path.exists():
            html_path.write_bytes(self._get(filing.url).content)
        meta_path.write_text(json.dumps(asdict(filing) | {"url": filing.url}, indent=2))
        return html_path

    def close(self) -> None:
        self._http.close()
