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

## 2026-10-19: no sample ratio mismatch (SRM) check until a skeptical audit caught it

**What went wrong:** The pipeline computed retention metrics, a bootstrap significance
test, and a sensitivity check, but never checked the one thing that comes before all of
that in a real A/B test: whether the gate_30/gate_40 split is actually close to 50/50. A
badly skewed split (a "sample ratio mismatch") is a classic sign that random assignment
didn't work cleanly, which would undermine every retention number built on top of it -
and this project reported all of those numbers without ever running that check.

**How it was caught:** Asked to act as a skeptical senior analyst reviewing the project
and check the methodology for weak points. Manually computed a chi-square goodness-of-fit
test on the 44,700 (gate_30) vs 45,489 (gate_40) split: chi2 = 6.9024, p = 0.008608 -
below the conventional 0.05 threshold, meaning the split is unlikely under true random
assignment. This had not been checked or reported anywhere before that review.

**What changed:** Added `src/srm_check.py`, which computes this same chi-square test
(using only `math`/`pandas`, no stats library) and saves the result to
`outputs/srm_check.csv`. Wired it into `src/run_all.py` as "Phase 1b", right after data
cleaning. Added the real numbers and a plain-language caveat to `README.md` (at the top
of Key Findings) and `docs/assumptions.md` (assumption 6), stating that random assignment
may not have been clean and the cause cannot be determined from this dataset alone.

## 2026-10-19: docs/assumptions.md edits got silently wiped by a full rebuild

**What went wrong:** `src/clean_data.py` has a `write_assumptions_doc()` function that
overwrites `docs/assumptions.md` with a hardcoded string every time `clean_data.run()`
runs - which happens on every `python src/run_all.py`. After manually editing
`docs/assumptions.md` to add assumptions 6 (SRM) and 7 (rounds played as a gate-affected
confound), I ran a full clean rebuild to verify the pipeline still worked end to end. That
rebuild silently overwrote my edits back to the original 5-assumption version, because
`write_assumptions_doc()`'s hardcoded string hadn't been updated to match.

**How it was caught:** After the rebuild, `git status` showed `docs/assumptions.md` as
unmodified even though I had just edited it - a sign something had reverted the file.
`git diff docs/assumptions.md` confirmed the working tree matched the last commit, with
assumptions 6 and 7 missing.

**What changed:** Added assumptions 6 and 7 directly into `write_assumptions_doc()`'s
hardcoded string in `src/clean_data.py`, so they now survive every rebuild instead of only
existing until the next `run_all.py` run. Followed the same pattern already used for
assumption 4 (point to the relevant `outputs/*` file for exact numbers instead of
hardcoding them in the prose) to avoid the numbers drifting out of sync if the underlying
data ever changes. Re-ran the full pipeline and confirmed `docs/assumptions.md` now comes
out with all 7 assumptions intact.
