# Failures

Things that went wrong, why, and what we changed. Add an entry whenever something fails in a way
that taught you something. Never delete entries; they explain why the code looks the way it does.

## F-001: NVIDIA headcount not retrieved with 600-word chunks

- **What happened:** "How many employees does NVIDIA have?" was answered "Not found in the indexed filings."
- **Why:** The "Human Capital Management" paragraph with `42,000 employees` sat inside a long Item 1
  chunk; its embedding was dominated by unrelated business text and never reached the top 6.
- **Fix:** Chunk size cut to 300 words (ADR-005). Evidence hit rate@6 went from 95% to 100%.
- **Lesson:** Section-level metrics hid this; the evidence metric caught it. Always label evidence strings.

## F-002: `llama3.1:8b` invented Microsoft product-revenue figures

- **What happened:** In an early run, before the prompt forbade calculations, the model stated three
  Microsoft product-revenue figures that appear nowhere in the filing.
- **Fix:** "Never calculate, convert, or estimate numbers" rule in the prompt (ADR-010) and the
  automatic grounding check (ADR-009).
- **Lesson:** Small models fill gaps with plausible numbers. Check numbers mechanically.

## F-003: Model arithmetic on Apple's Services share

- **What happened:** Asked to compare Apple's and Microsoft's revenue drivers, the model wrote that
  Services were "26.5% of total net sales". The filing gives only dollar amounts
  ($109,158M of $416,161M, which is 26.2%).
- **Caught by:** Grounding check: `these figures were not found in the sources: 26.5, 24.4, 22.2`.
- **Lesson:** Even with the no-calculation rule, models compute shares. The check is essential.

## F-004: `qwen2.5:7b` made up half of a buyback split

- **What happened:** It split Microsoft's "$10.2 billion returned in Q4" into "$6.759 billion in
  dividends and $3.451 billion in share repurchases". The dividend was a unit conversion of $6,759
  million; the buyback figure was invented (10.2 - 6.759 would be 3.441).
- **Caught by:** Grounding check (the 1/24 flagged answer in the qwen report).
- **Open:** Unit conversions (million to billion) still slip through the prompt rule.

## F-005: `llama3.1:8b` computed growth and mixed fiscal years

- **What happened:** It computed NVIDIA's Data Center growth ($78,551 million; correct arithmetic,
  not stated in the filing) and added dividends and buybacks from two fiscal years into a misleading
  "$56.7 billion" total.
- **Caught by:** Grounding check (2/24 flagged answers in the llama report).
- **Lesson:** The check cannot tell correct arithmetic from wrong; both are flagged because neither
  is in the source. That is the intended behavior.

## F-006: Trailing "Not found" after a complete answer

- **What happened:** `qwen2.5:7b` occasionally ends a correct, cited answer with
  "Not found in the indexed filings."
- **Status:** Cosmetic, open as T-033.

## F-007: `uv sync` run before the project existed in the folder

- **What happened:** `uv sync` failed with "No `pyproject.toml` found in current directory or any parent directory".
- **Why:** It was run in `~/Documents/AIproj` before the project files were there.
- **Fix:** Run uv commands from the repo root; the README now says so.

## F-008: Stray heading appended to the README

- **What happened:** GitHub's quick-start (`echo "# edgar-rag-ollama" >> README.md`) appended a
  heading to the end of the existing README.
- **Fix:** Removed on 2026-10-13. When connecting an existing project to a new GitHub repo, skip the
  `echo` step.
