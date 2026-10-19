"""
Phase 3, step 5: copy the key result tables into outputs/dashboard/ as flat,
Tableau-friendly CSVs.

"Tableau-friendly" here means: one header row, snake_case column names,
no merged/multi-level headers, one row per record. All three source files
already look like this - this script just gathers them into one folder
under clear, stable names so a dashboard tool can point at a single
directory instead of outputs/sql/ + outputs/.

Run directly with: python src/dashboard_exports.py
"""

import pandas as pd
from pathlib import Path

DASHBOARD_DIR = Path("outputs/dashboard")

# (source file, destination filename) pairs.
EXPORTS = [
    (Path("outputs/sql/01_retention_by_version.csv"), "retention_by_version.csv"),
    (Path("outputs/sql/02_rounds_buckets.csv"), "rounds_buckets.csv"),
    (Path("outputs/ab_test_result.csv"), "ab_test_result.csv"),
]


def run():
    DASHBOARD_DIR.mkdir(parents=True, exist_ok=True)

    for source_path, dest_name in EXPORTS:
        df = pd.read_csv(source_path)
        dest_path = DASHBOARD_DIR / dest_name
        df.to_csv(dest_path, index=False)
        print(f"Saved {dest_path} ({len(df)} rows, columns: {list(df.columns)})")


if __name__ == "__main__":
    run()
