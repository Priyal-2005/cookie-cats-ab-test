"""
Rebuilds the entire project output from raw data, start to finish.

Per CLAUDE.md rule 5: running `python src/run_all.py` from the project root
must regenerate every file in data/processed/ and outputs/ from scratch, so
nothing in this project depends on files that aren't tracked in code.

As more phases are added (SQL metrics, pandas validation, dashboard CSVs),
their run() functions get called here too, in order.
"""

import clean_data
import run_sql

if __name__ == "__main__":
    print("=== Phase 1: Clean and audit raw data ===")
    clean_data.run()

    print("\n=== Phase 2: Load into SQLite and run SQL metrics ===")
    run_sql.run()
