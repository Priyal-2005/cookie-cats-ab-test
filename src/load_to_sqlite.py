"""
Loads the cleaned CSV into a SQLite database so the SQL metrics in /sql
can run against it.

This does ONE thing: read data/processed/cookie_cats_clean.csv and write
it to data/processed/cookie_cats.db as a table called "players".
"""

import sqlite3
import pandas as pd
from pathlib import Path

CSV_PATH = Path("data/processed/cookie_cats_clean.csv")
DB_PATH = Path("data/processed/cookie_cats.db")


def run():
    df = pd.read_csv(CSV_PATH)

    conn = sqlite3.connect(DB_PATH)
    # if_exists="replace" so re-running this script rebuilds the table
    # instead of erroring out or duplicating rows.
    df.to_sql("players", conn, if_exists="replace", index=False)
    conn.close()

    print(f"Loaded {len(df):,} rows from {CSV_PATH} into {DB_PATH} (table: players)")


if __name__ == "__main__":
    run()
