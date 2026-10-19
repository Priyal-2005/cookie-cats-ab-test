# Cookie Cats A/B Test — Player Retention Analysis

## Business question

Cookie Cats is a mobile puzzle game. Early in the game, players hit a "gate" that forces
them to wait (or pay) before continuing. This analysis asks: **if you move the first gate
from level 30 (`gate_30`) to level 40 (`gate_40`), does that change how many players come
back the next day (day-1 retention) or a week later (day-7 retention), and does it change
how much they play?**

## Dataset and source

This is a public dataset from Kaggle ("Cookie Cats A/B Testing"). **I did not run this
experiment myself** — I'm analyzing data that was already collected. Each row is one
player who was randomly assigned to `gate_30` or `gate_40`, with their total rounds played
and whether they returned on day 1 / day 7.

- 90,189 players total, 44,700 in `gate_30` (49.56%) and 45,489 in `gate_40` (50.44%) [outputs/data_quality_report.md]
- Raw file: `data/raw/cookie_cats.csv`

## Approach

1. **Clean** the raw data: check for duplicates, nulls, and bad types; flag (not delete)
   extreme outliers; bucket players by rounds played. (`src/clean_data.py`)
2. **Load** the cleaned data into SQLite and compute retention metrics in SQL.
   (`src/load_to_sqlite.py`, `src/run_sql.py`, `sql/*.sql`)
3. **Validate** every SQL metric with an independent pandas calculation, so no number in
   this README is trusted without a second, separate check. (`src/validate.py`)
4. **Test**: compute the retention gap between versions and a 95% bootstrap confidence
   interval for that gap, to see if the difference could just be random chance.
   (`src/ab_test.py`)
5. **Sensitivity check**: repeat the test excluding flagged outliers, to make sure a
   handful of extreme players aren't driving the result. (`src/sensitivity.py`)
6. **Charts and dashboard exports** for a Tableau Public dashboard. (`src/charts.py`,
   `src/dashboard_exports.py`)

## Folder structure

```
data/raw/              - the original, unmodified Kaggle CSV
data/processed/        - cleaned CSV + SQLite database (both rebuilt by code, not edited by hand)
sql/                   - SQL metric queries (01 and 02 written by me, 03 and 04 by Claude Code)
src/                   - all Python scripts (the actual pipeline)
outputs/               - every generated file: reports, CSVs, charts (nothing here is hand-edited)
outputs/sql/           - the result of running each query in sql/
outputs/charts/        - matplotlib PNG charts
outputs/dashboard/     - flat CSVs for the Tableau Public dashboard
docs/assumptions.md    - every assumption made during cleaning/analysis, with reasons
docs/ai_mistakes_log.md - AI mistakes caught during this project, and how they were fixed
```

## How to run

```
python src/run_all.py
```

Run from the project root. This rebuilds everything — cleaned data, SQLite database, SQL
metrics, validation report, A/B test result, sensitivity check, charts, and dashboard CSVs
— from the raw CSV in `data/raw/`. Nothing in `outputs/` or `data/processed/` is edited by
hand; if a number looks wrong, the fix belongs in the code, not the output file.

Requires: `pandas`, `numpy`, `matplotlib`, `sqlite3` (Python standard library), `openpyxl`.

## Key findings

- **Day-1 retention**: `gate_30` = 44.82%, `gate_40` = 44.23%, a difference of -0.59
  percentage points (gate_40 minus gate_30), 95% bootstrap CI = [-1.23, 0.05] percentage
  points [outputs/ab_test_result.csv]. The interval includes 0, so **this difference is
  not statistically significant** at the 95% level.
- **Day-7 retention**: `gate_30` = 19.02%, `gate_40` = 18.20%, a difference of -0.82
  percentage points, 95% bootstrap CI = [-1.33, -0.31] percentage points
  [outputs/ab_test_result.csv]. The interval excludes 0, so **this difference IS
  statistically significant** — players retain worse at day 7 under `gate_40`.
- **Sensitivity check**: excluding the 10 flagged outlier players [outputs/data_quality_report.md],
  the day-7 gap is still -0.82 percentage points with CI [-1.33, -0.31] [outputs/sensitivity.csv]
  — the conclusion **does not change**.
- Average rounds played: `gate_30` = 52.46, `gate_40` = 51.30 rounds per player
  [outputs/sql/04_summary.csv].
- Every one of the 16 SQL metrics checked against an independent pandas calculation
  **passed** with zero difference [outputs/validation_report.md].

### Tableau Public dashboard

> _Screenshot placeholder: paste your Tableau Public dashboard screenshot(s) here._
>
> _Dashboard link placeholder: add your published Tableau Public URL here._
>
> Built from the flat CSVs in `outputs/dashboard/` (`retention_by_version.csv`,
> `rounds_buckets.csv`, `ab_test_result.csv`).

## Assumptions and limitations

- **No dates in this dataset.** Every row is a lifetime snapshot — there are no
  timestamps, so trends over time (e.g. did retention change week by week during the
  test?) cannot be analyzed, only the aggregate difference between groups.
- **`sum_gamerounds` is only a proxy for level reached**, not the level itself — a player
  could replay earlier levels many times, so a high round count doesn't guarantee they
  passed a gate (see `docs/assumptions.md` for the full reasoning).
- **This is one dataset from one run of the experiment.** The bootstrap confidence
  intervals describe sampling uncertainty within this dataset, not uncertainty about
  whether the game, player population, or time period generalize to other contexts.
- **This A/B test only covers the first gate.** It compares moving one early gate from
  level 30 to level 40 — it says nothing about later gates, other game mechanics, or
  interactions between multiple changes at once.
- Full list of assumptions, each with its reasoning: `docs/assumptions.md`.

## How I used AI

Claude Code drafted the data cleaning, validation, and charting code
(`src/clean_data.py`, `src/validate.py`, `src/ab_test.py`, `src/sensitivity.py`,
`src/charts.py`, `src/dashboard_exports.py`, `src/run_all.py`, and SQL files `sql/03` and
`sql/04`). **I wrote `sql/01_retention_by_version.sql` and `sql/02_rounds_buckets.sql`
myself** — Claude Code reviewed them for bugs but did not rewrite them. Every metric in
this project was cross-checked against an independent pandas calculation before being
reported (`outputs/validation_report.md`). Mistakes Claude Code made during this project,
how they were caught, and what changed are logged in `docs/ai_mistakes_log.md`.
