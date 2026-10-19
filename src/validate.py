"""
Phase 3, step 1: validate every SQL metric with an independent pandas calculation.

For each of the four SQL outputs in outputs/sql/, this script recomputes the
same numbers directly from data/processed/cookie_cats_clean.csv using pandas
- NOT by reading the SQL output and trusting it, but as a fully separate
calculation - then compares the two side by side.

Every metric gets a PASS or FAIL and a "max difference" (the biggest gap
between the SQL answer and the pandas answer across all rows for that
column), written to outputs/validation_report.md.

PASS means SQL and pandas agree within a small rounding tolerance (0.01,
since every percentage in this project is rounded to 2 decimal places).
A FAIL means they disagree by more than rounding alone could explain, which
would point to a real bug in either the SQL query or this pandas code.

Run directly with: python src/validate.py
"""

import pandas as pd
from pathlib import Path

DATA_PATH = Path("data/processed/cookie_cats_clean.csv")
SQL_OUTPUT_DIR = Path("outputs/sql")
REPORT_PATH = Path("outputs/validation_report.md")

# How far apart SQL and pandas are allowed to be and still count as a PASS.
# 0.01 because every percentage here is rounded to 2 decimal places, so a
# tiny gap from rounding is expected and not a real bug.
TOLERANCE = 0.01


def validate_01_retention_by_version(df):
    """Independently recompute: players, ret_1, ret_1_pct, ret_7, ret_7_pct per version."""
    pandas_result = df.groupby("version").agg(
        players=("userid", "count"),
        ret_1=("retention_1", "sum"),
        ret_7=("retention_7", "sum"),
    ).reset_index()
    pandas_result.loc[:, "ret_1_pct"] = (pandas_result["ret_1"] / pandas_result["players"] * 100).round(2)
    pandas_result.loc[:, "ret_7_pct"] = (pandas_result["ret_7"] / pandas_result["players"] * 100).round(2)

    sql_result = pd.read_csv(SQL_OUTPUT_DIR / "01_retention_by_version.csv")
    return pandas_result, sql_result, ["version"]


def validate_02_rounds_buckets(df):
    """Independently recompute: players, ret_1_pct, ret_7_pct per version + rounds_bucket."""
    pandas_result = df.groupby(["version", "rounds_bucket", "bucket_order"], observed=True).agg(
        players=("userid", "count"),
        ret_1_pct=("retention_1", lambda s: round(s.mean() * 100, 2)),
        ret_7_pct=("retention_7", lambda s: round(s.mean() * 100, 2)),
    ).reset_index()

    sql_result = pd.read_csv(SQL_OUTPUT_DIR / "02_rounds_buckets.csv")
    return pandas_result, sql_result, ["version", "rounds_bucket", "bucket_order"]


def validate_03_retention_by_bucket_gap(df):
    """Independently recompute: gate_30 vs gate_40 day-7 retention and the gap, per bucket."""
    pivot = df.pivot_table(
        index=["rounds_bucket", "bucket_order"], columns="version",
        values="retention_7", aggfunc="mean", observed=True,
    ).reset_index()

    pandas_result = pd.DataFrame({
        "rounds_bucket": pivot["rounds_bucket"],
        "bucket_order": pivot["bucket_order"],
        "gate_30_ret_7_pct": (pivot["gate_30"] * 100).round(2),
        "gate_40_ret_7_pct": (pivot["gate_40"] * 100).round(2),
        # Round the RAW difference once, same as the SQL does - rounding
        # each side first and then subtracting can be off by 0.01 from
        # rounding twice instead of once.
        "gate_40_minus_gate_30_pp": ((pivot["gate_40"] - pivot["gate_30"]) * 100).round(2),
    })

    sql_result = pd.read_csv(SQL_OUTPUT_DIR / "03_retention_by_bucket_gap.csv")
    return pandas_result, sql_result, ["rounds_bucket", "bucket_order"]


def validate_04_summary(df):
    """Independently recompute: players, avg_rounds, max_rounds, zero-round count, pct 30+ rounds."""
    pandas_result = df.groupby("version").agg(
        players=("userid", "count"),
        avg_rounds=("sum_gamerounds", lambda s: round(s.mean(), 2)),
        max_rounds=("sum_gamerounds", "max"),
        players_zero_rounds=("sum_gamerounds", lambda s: int((s == 0).sum())),
        pct_players_30plus_rounds=("sum_gamerounds", lambda s: round((s >= 30).mean() * 100, 2)),
    ).reset_index()

    sql_result = pd.read_csv(SQL_OUTPUT_DIR / "04_summary.csv")
    return pandas_result, sql_result, ["version"]


def compare(name, pandas_result, sql_result, key_cols):
    """
    Merge the pandas and SQL results on their shared key columns, then for
    every other column compute the biggest absolute difference between the
    two. Returns one (metric_name, PASS/FAIL, max_diff) tuple per column.
    """
    # Keys are cast to string on both sides so a dtype mismatch (e.g.
    # "category" from pandas vs plain text read back from a CSV) can't
    # cause rows to fail to match up.
    # .assign() builds a new DataFrame with the key columns cast to str,
    # instead of modifying pandas_result/sql_result's columns in place -
    # this avoids the dtype-change warnings in-place assignment causes.
    left = pandas_result.assign(**{c: pandas_result[c].astype(str) for c in key_cols})
    right = sql_result.assign(**{c: sql_result[c].astype(str) for c in key_cols})

    merged = left.merge(right, on=key_cols, suffixes=("_pandas", "_sql"))
    value_cols = [c for c in pandas_result.columns if c not in key_cols]

    results = []
    for col in value_cols:
        diff = (merged[f"{col}_pandas"] - merged[f"{col}_sql"]).abs()
        max_diff = diff.max()
        status = "PASS" if max_diff <= TOLERANCE else "FAIL"
        results.append((f"{name}.{col}", status, round(float(max_diff), 4)))
    return results


def run():
    df = pd.read_csv(DATA_PATH)

    checks = [
        ("01_retention_by_version", validate_01_retention_by_version),
        ("02_rounds_buckets", validate_02_rounds_buckets),
        ("03_retention_by_bucket_gap", validate_03_retention_by_bucket_gap),
        ("04_summary", validate_04_summary),
    ]

    all_results = []
    for name, func in checks:
        pandas_result, sql_result, key_cols = func(df)
        all_results.extend(compare(name, pandas_result, sql_result, key_cols))

    print("\n--- Validation results (SQL vs independent pandas) ---")
    lines = [
        "# Validation Report",
        "",
        "Every SQL metric below was recomputed independently in pandas directly from",
        "data/processed/cookie_cats_clean.csv (not by reading the SQL output), then",
        f"compared to the SQL result. Tolerance = {TOLERANCE} (rounding allowance).",
        "",
        "| Metric | Status | Max difference |",
        "|---|---|---|",
    ]

    any_fail = False
    for metric, status, max_diff in all_results:
        print(f"{status}: {metric} (max diff = {max_diff})")
        lines.append(f"| {metric} | {status} | {max_diff} |")
        if status == "FAIL":
            any_fail = True

    lines.append("")
    if any_fail:
        lines.append("**At least one metric FAILED - see the table above for which one(s).**")
    else:
        lines.append(f"**All {len(all_results)} metrics PASSED.**")

    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text("\n".join(lines) + "\n")
    print(f"\nSaved {REPORT_PATH}")

    return any_fail


if __name__ == "__main__":
    run()
