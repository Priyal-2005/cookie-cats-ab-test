# AI Mistakes Log

Per CLAUDE.md rule 12: every time an error I (the AI) made is caught, it's logged here -
what went wrong, how it was caught, what changed.

## 2026-10-19: run_all.py didn't rebuild the SQLite database

**What went wrong:** When I wrote `src/load_to_sqlite.py` (loading the cleaned CSV into
`data/processed/cookie_cats.db`), I never added a call to it from `src/run_all.py`.
`run_all.py` only ran Phase 1 (`clean_data.run()`), so `python src/run_all.py` silently
did not rebuild the database - violating CLAUDE.md rule 5 ("run_all.py must rebuild
everything from raw data").

**How it was caught:** During a full code review, I deleted `cookie_cats.db` and re-ran
`python src/run_all.py` to verify rule 5 actually held. The file did not come back.

**What changed:** Added `import load_to_sqlite` and `load_to_sqlite.run()` to
`src/run_all.py`, as "Phase 2", right after Phase 1. Re-tested by deleting the `.db` file
and re-running `run_all.py` - it now rebuilds correctly.
