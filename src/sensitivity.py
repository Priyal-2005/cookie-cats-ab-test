"""
Phase 3, step 3: sensitivity check - does excluding the flagged outliers
(see docs/assumptions.md, assumption 4) change the A/B test conclusion?

This re-runs the exact same A/B test as ab_test.py (same bootstrap function,
same settings), but on the subset of players where is_outlier is False.
If the conclusion (significant / not significant) stays the same with or
without the outliers, that's reassuring - it means a handful of extreme
players aren't secretly driving the result.

Run directly with: python src/sensitivity.py
"""

import pandas as pd
from pathlib import Path

import ab_test

DATA_PATH = Path("data/processed/cookie_cats_clean.csv")
OUTPUT_PATH = Path("outputs/sensitivity.csv")


def run():
    df = pd.read_csv(DATA_PATH)
    df_no_outliers = df[~df["is_outlier"]]

    n_removed = len(df) - len(df_no_outliers)
    print(f"Excluding {n_removed} outlier row(s) out of {len(df):,} "
          f"({len(df_no_outliers):,} players remain).")

    full_result = ab_test.run(df, label="full dataset")
    no_outlier_result = ab_test.run(df_no_outliers, label="excluding outliers")

    # Put both side by side so it's easy to see if anything changed.
    comparison = full_result.merge(
        no_outlier_result, on="metric", suffixes=("_full", "_no_outliers")
    )

    print("\n--- Does the conclusion change without outliers? ---")
    for _, row in comparison.iterrows():
        same_conclusion = row["ci_includes_zero_full"] == row["ci_includes_zero_no_outliers"]
        print(f"{row['metric']}: significant with outliers = "
              f"{not row['ci_includes_zero_full']}, significant without outliers = "
              f"{not row['ci_includes_zero_no_outliers']} "
              f"-> conclusion {'UNCHANGED' if same_conclusion else 'CHANGED'}")

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    comparison.to_csv(OUTPUT_PATH, index=False)
    print(f"\nSaved {OUTPUT_PATH}")

    return comparison


if __name__ == "__main__":
    run()
