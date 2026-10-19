"""
Phase 2: run the SQL metrics against the cleaned data.

What this script does:
1. Load data/processed/cookie_cats_clean.csv into a SQLite database
   (data/processed/cookie_cats.db, table "players") by reusing
   load_to_sqlite.py - so there is only one place that does the loading.
2. Run every .sql file in /sql, in order, against that database.
3. Save each query's result to outputs/sql/<same_name>.csv.
4. Print the first few rows of each result so they can be spot-checked.

Run directly with:  python src/run_sql.py
(Also called from src/run_all.py so the whole pipeline rebuilds from raw
data with one command, per CLAUDE.md rule 5.)
"""

import sqlite3
import pandas as pd
from pathlib import Path

import load_to_sqlite

DB_PATH = Path("data/processed/cookie_cats.db")
SQL_DIR = Path("sql")
OUTPUT_DIR = Path("outputs/sql")

# Listed explicitly (instead of just globbing the folder) so the order is
# clear and predictable, and so a stray .sql file in the folder can't
# silently get run.
SQL_FILES = [
    "01_retention_by_version.sql",
    "02_rounds_buckets.sql",
    "03_retention_by_bucket_gap.sql",
    "04_summary.sql",
]


def run():
    # Step 1: make sure the database is fresh and matches the cleaned CSV.
    load_to_sqlite.run()

    conn = sqlite3.connect(DB_PATH)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    for filename in SQL_FILES:
        sql_path = SQL_DIR / filename
        query = sql_path.read_text()

        result = pd.read_sql_query(query, conn)

        # outputs/sql/01_retention_by_version.csv, etc.
        out_path = OUTPUT_DIR / (sql_path.stem + ".csv")
        result.to_csv(out_path, index=False)

        print(f"\n=== {filename} -> {out_path} ({len(result)} rows) ===")
        print(result.head().to_string(index=False))

    conn.close()


if __name__ == "__main__":
    run()
