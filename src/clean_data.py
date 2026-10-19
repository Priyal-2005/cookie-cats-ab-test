"""
Phase 1: Audit and clean the raw Cookie Cats data.

What this script does, in order:
1. Load the raw CSV and print basic facts about it (shape, dtypes, nulls,
   duplicate userids, version split).
2. Audit the sum_gamerounds column in detail (min/max/mean/median,
   percentiles, biggest values, how many zero-round players).
3. Make sure retention_1 / retention_7 are real booleans.
4. Clean the data in small, logged steps (see CLAUDE.md rule 2):
   - drop duplicate userids
   - keep (not drop) players with 0 rounds
   - flag extreme outliers instead of deleting them
   - add a rounds_bucket column for easier grouping in charts
5. Save the cleaned data and two report files so every number in the
   README can be traced back to a file we produced.

Run directly with:  python src/clean_data.py
(It is also called from src/run_all.py so the whole pipeline can be
rebuilt from raw data with one command, per CLAUDE.md rule 5.)
"""

import pandas as pd
import numpy as np
from pathlib import Path

# ---- File locations -------------------------------------------------
# Paths are relative to the project root, not this file, so the script
# only works correctly when run from the project root (python src/clean_data.py).
RAW_PATH = Path("data/raw/cookie_cats.csv")
PROCESSED_PATH = Path("data/processed/cookie_cats_clean.csv")
CLEANING_LOG_PATH = Path("outputs/cleaning_log.csv")
QUALITY_REPORT_PATH = Path("outputs/data_quality_report.md")

# The percentile we use to flag (not delete) extreme outliers in sum_gamerounds.
OUTLIER_PERCENTILE = 0.9999

# The upper edges of each rounds_bucket. "inf" catches everything above 199.
BUCKET_EDGES = [-1, 0, 4, 9, 19, 29, 39, 49, 99, 199, np.inf]
BUCKET_LABELS = ["0", "1-4", "5-9", "10-19", "20-29", "30-39", "40-49", "50-99", "100-199", "200+"]


def load_raw_data(path):
    """Read the raw CSV into a DataFrame and print the row count."""
    df = pd.read_csv(path)
    print(f"Loaded {len(df):,} rows from {path}")
    return df


def print_initial_audit(df):
    """Print shape, dtypes, nulls, duplicate userids, and version split."""
    print("\n--- Initial audit ---")
    print(f"Shape (rows, columns): {df.shape}")

    print("\nColumn dtypes:")
    print(df.dtypes)

    print("\nNull counts per column:")
    print(df.isnull().sum())

    # A userid is a duplicate if it appears more than once anywhere in the file.
    duplicate_mask = df["userid"].duplicated(keep=False)
    n_duplicate_rows = duplicate_mask.sum()
    # This is how many ROWS we'd remove if we kept only the first occurrence
    # of each userid - the number that matters for cleaning.
    n_extra_rows_if_deduped = df["userid"].duplicated(keep="first").sum()
    print(f"\nRows involved in a duplicate userid: {n_duplicate_rows}")
    print(f"Extra rows that would be removed by de-duplicating (keep first): {n_extra_rows_if_deduped}")

    print("\nversion value counts:")
    version_counts = df["version"].value_counts()
    version_pct = df["version"].value_counts(normalize=True) * 100
    for v in version_counts.index:
        print(f"  {v}: {version_counts[v]:,} rows ({version_pct[v]:.2f}%)")

    return {
        "n_rows": len(df),
        "n_duplicate_rows": int(n_duplicate_rows),
        "n_extra_rows_if_deduped": int(n_extra_rows_if_deduped),
        "version_counts": version_counts.to_dict(),
        "version_pct": version_pct.to_dict(),
    }


def audit_sum_gamerounds(df):
    """Print detailed stats on sum_gamerounds: spread, percentiles, top values, zeros."""
    print("\n--- sum_gamerounds audit ---")
    s = df["sum_gamerounds"]

    stats = {
        "min": s.min(),
        "max": s.max(),
        "mean": s.mean(),
        "median": s.median(),
        "p50": s.quantile(0.50),
        "p90": s.quantile(0.90),
        "p99": s.quantile(0.99),
        "p99_9": s.quantile(0.999),
    }
    for name, value in stats.items():
        print(f"  {name}: {value:,.2f}")

    n_zero = (s == 0).sum()
    pct_zero = n_zero / len(df) * 100
    print(f"\nPlayers with 0 rounds played: {n_zero:,} ({pct_zero:.2f}%)")

    top10 = df.nlargest(10, "sum_gamerounds")[["userid", "version", "sum_gamerounds"]]
    print("\n10 largest sum_gamerounds values:")
    print(top10.to_string(index=False))

    stats["n_zero"] = int(n_zero)
    stats["pct_zero"] = pct_zero
    stats["top10"] = top10
    return stats


def ensure_boolean_columns(df):
    """Make sure retention_1 and retention_7 are real booleans, not strings."""
    print("\n--- Checking retention column types ---")
    for col in ["retention_1", "retention_7"]:
        before_dtype = df[col].dtype
        if df[col].dtype != bool:
            # If pandas read them in as text ("True"/"False"), convert explicitly.
            df[col] = df[col].astype(str).map({"True": True, "False": False}).astype(bool)
        print(f"  {col}: was {before_dtype}, now {df[col].dtype}")
    return df


def drop_duplicate_userids(df, log_rows):
    """Cleaning step 1: drop duplicate userids, keeping the first occurrence."""
    rows_before = len(df)
    df_clean = df.drop_duplicates(subset="userid", keep="first")
    rows_after = len(df_clean)
    removed = rows_before - rows_after

    if removed == 0:
        note = "No duplicate userids found - nothing removed."
    else:
        note = f"Removed {removed} duplicate-userid rows, kept first occurrence of each."
    print(f"\n[Cleaning] drop_duplicate_userids: {rows_before} -> {rows_after} rows. {note}")

    log_rows.append({
        "step": "drop_duplicate_userids",
        "rows_before": rows_before,
        "rows_after": rows_after,
        "rows_removed": removed,
        "notes": note,
    })
    return df_clean


def note_zero_round_players(df, log_rows):
    """Cleaning step 2: do NOT drop 0-round players, just log how many there are."""
    rows_before = len(df)
    n_zero = (df["sum_gamerounds"] == 0).sum()
    note = f"Kept {n_zero} players with 0 rounds (installed but never played) - not dropped, per project rule."
    print(f"\n[Cleaning] note_zero_round_players: {rows_before} -> {rows_before} rows. {note}")

    log_rows.append({
        "step": "keep_zero_round_players",
        "rows_before": rows_before,
        "rows_after": rows_before,
        "rows_removed": 0,
        "notes": note,
    })
    return df


def flag_outliers(df, log_rows):
    """Cleaning step 3: flag (don't delete) extreme sum_gamerounds outliers."""
    rows_before = len(df)
    threshold = df["sum_gamerounds"].quantile(OUTLIER_PERCENTILE)
    df = df.copy()
    df.loc[:, "is_outlier"] = df["sum_gamerounds"] > threshold

    n_outliers = df["is_outlier"].sum()
    outlier_values = sorted(df.loc[df["is_outlier"], "sum_gamerounds"].tolist(), reverse=True)
    note = (
        f"Flagged {n_outliers} rows with sum_gamerounds above the "
        f"{OUTLIER_PERCENTILE*100:.2f}th percentile (threshold={threshold:.1f}). "
        f"Flagged values: {outlier_values}. Rows were NOT deleted."
    )
    print(f"\n[Cleaning] flag_outliers: {rows_before} -> {rows_before} rows (no rows removed). {note}")

    log_rows.append({
        "step": "flag_outliers",
        "rows_before": rows_before,
        "rows_after": rows_before,
        "rows_removed": 0,
        "notes": note,
    })
    return df, n_outliers, threshold, outlier_values


def add_rounds_bucket(df, log_rows):
    """Cleaning step 4: add rounds_bucket (readable label) and bucket_order (sort key)."""
    rows_before = len(df)
    df = df.copy()
    df.loc[:, "rounds_bucket"] = pd.cut(
        df["sum_gamerounds"], bins=BUCKET_EDGES, labels=BUCKET_LABELS, right=True
    )
    # bucket_order is just 1..10 following the same order as BUCKET_LABELS,
    # so charts can sort buckets correctly instead of alphabetically.
    order_map = {label: i + 1 for i, label in enumerate(BUCKET_LABELS)}
    df.loc[:, "bucket_order"] = df["rounds_bucket"].map(order_map)

    note = f"Added rounds_bucket (categories: {BUCKET_LABELS}) and bucket_order (1-10) columns."
    print(f"\n[Cleaning] add_rounds_bucket: {rows_before} -> {rows_before} rows (no rows removed). {note}")

    log_rows.append({
        "step": "add_rounds_bucket",
        "rows_before": rows_before,
        "rows_after": rows_before,
        "rows_removed": 0,
        "notes": note,
    })
    return df


def write_cleaning_log(log_rows):
    """Save every cleaning step (before/after row counts) to outputs/cleaning_log.csv."""
    log_df = pd.DataFrame(log_rows, columns=["step", "rows_before", "rows_after", "rows_removed", "notes"])
    log_df.to_csv(CLEANING_LOG_PATH, index=False)
    print(f"\nSaved cleaning log to {CLEANING_LOG_PATH}")


def write_quality_report(initial_stats, rounds_stats, n_outliers, outlier_threshold, outlier_values, n_zero_kept):
    """Write a plain-English summary of the data quality checks, using only real numbers."""
    version_lines = "\n".join(
        f"- **{v}**: {initial_stats['version_counts'][v]:,} rows ({initial_stats['version_pct'][v]:.2f}%)"
        for v in initial_stats["version_counts"]
    )

    report = f"""# Data Quality Report - Cookie Cats Raw Data

## Basic facts
- Total rows loaded: {initial_stats['n_rows']:,}
- Rows involved in a duplicate userid: {initial_stats['n_duplicate_rows']}
- Extra rows removed when de-duplicating (keep first occurrence): {initial_stats['n_extra_rows_if_deduped']}

## A/B group split
{version_lines}

## sum_gamerounds distribution
- Min: {rounds_stats['min']}
- Max: {rounds_stats['max']:,}
- Mean: {rounds_stats['mean']:.2f}
- Median: {rounds_stats['median']}
- 50th percentile: {rounds_stats['p50']}
- 90th percentile: {rounds_stats['p90']}
- 99th percentile: {rounds_stats['p99']}
- 99.9th percentile: {rounds_stats['p99_9']:.2f}
- Players with 0 rounds played: {rounds_stats['n_zero']:,} ({rounds_stats['pct_zero']:.2f}%) - kept in the cleaned data (see docs/assumptions.md)

## Outliers
- {n_outliers} row(s) flagged as outliers (sum_gamerounds above the 99.99th percentile, threshold = {outlier_threshold:.1f})
- Flagged values: {outlier_values}
- These rows were NOT deleted. They have `is_outlier = True` in the cleaned data so they can be
  included or excluded from any analysis as needed.

## What changed between raw and cleaned data
See outputs/cleaning_log.csv for the exact row counts before and after every step.
"""
    QUALITY_REPORT_PATH.write_text(report)
    print(f"Saved data quality report to {QUALITY_REPORT_PATH}")


def write_assumptions_doc():
    """Write docs/assumptions.md with the assumptions behind this analysis."""
    assumptions = """# Assumptions

This file records assumptions made during data cleaning and analysis, per CLAUDE.md rule 3.

1. **sum_gamerounds is only a proxy for the level a player reached**, not the level itself.
   The dataset does not record which level a player is on - only how many rounds they have
   played in total. A player could replay earlier levels many times, so a high round count
   does not guarantee they passed the gate. We treat sum_gamerounds as an approximate signal,
   not an exact measurement of progress.

2. **Players with fewer than about 30 rounds very likely never reached either gate.**
   Since gate_30 is the earlier of the two gates being tested, a player who has played fewer
   than ~30 rounds total almost certainly has not reached gate_30 yet, let alone gate_40.
   This is an approximation, not a guarantee, for the same reason as assumption 1.

3. **There is no date/time information in this dataset.**
   Every row is a snapshot of a player's lifetime totals (sum_gamerounds, retention_1,
   retention_7) with no timestamps. This means we cannot analyze trends over time (e.g.
   whether retention changed week over week during the test) - only aggregate differences
   between the gate_30 and gate_40 groups.

4. **Outliers in sum_gamerounds are flagged, not removed.**
   A small number of players have extremely high round counts (see outputs/data_quality_report.md
   for exact values). These could be real highly-engaged players or bots/testers. Since we can't
   tell which from this data alone, we keep them in the dataset with an `is_outlier` flag so later
   analysis can choose to include or exclude them and see if it changes the conclusion.

5. **Players with 0 rounds played are kept, not dropped.**
   A 0-round player installed the app but never played a single round. This is a valid outcome
   (not missing/bad data) and matters for retention analysis, so these rows are kept.
"""
    Path("docs/assumptions.md").write_text(assumptions)
    print("Saved docs/assumptions.md")


def run():
    """Run the full Phase 1 audit + cleaning pipeline, start to finish."""
    log_rows = []

    df = load_raw_data(RAW_PATH)
    initial_stats = print_initial_audit(df)
    rounds_stats = audit_sum_gamerounds(df)
    df = ensure_boolean_columns(df)

    # Log the very first "step" so cleaning_log.csv shows where we started.
    log_rows.append({
        "step": "load_raw_data",
        "rows_before": "",
        "rows_after": len(df),
        "rows_removed": 0,
        "notes": f"Initial load from {RAW_PATH}",
    })

    df = drop_duplicate_userids(df, log_rows)
    df = note_zero_round_players(df, log_rows)
    df, n_outliers, outlier_threshold, outlier_values = flag_outliers(df, log_rows)
    df = add_rounds_bucket(df, log_rows)

    n_zero_kept = (df["sum_gamerounds"] == 0).sum()

    # Save all outputs.
    PROCESSED_PATH.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(PROCESSED_PATH, index=False)
    print(f"\nSaved cleaned data to {PROCESSED_PATH} ({len(df):,} rows)")

    write_cleaning_log(log_rows)
    write_quality_report(initial_stats, rounds_stats, n_outliers, outlier_threshold, outlier_values, n_zero_kept)
    write_assumptions_doc()

    print("\nPhase 1 complete.")


if __name__ == "__main__":
    run()
