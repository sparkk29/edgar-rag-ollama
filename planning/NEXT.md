# Next

The few things to do now, in order. Keep this list short (five items at most); everything else
belongs in [`TASKS.md`](TASKS.md).

1. **T-020: Commit and push** the documentation system and the README section that links it.
   Run `uv run pytest` first; it should report 18 passed.
2. **T-021: Choose a license** (owner decision). MIT is the usual choice for a portfolio project.
3. **T-022: Add a UI screenshot.** Run `uv run streamlit run app.py`, ask one of the example
   questions, capture the answer with its source cards, save it as `assets/screenshot.png` and
   embed it under the README intro.
4. **T-024: Add CI** that runs the unit tests on every push.
5. **T-023: Upload the social preview** (`assets/logo.png`) in the GitHub repository settings.

After these, Phase 2 is complete and Phase 3 (hybrid search, T-030) starts.
