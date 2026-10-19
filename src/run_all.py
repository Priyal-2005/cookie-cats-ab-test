"""
Rebuilds the entire project output from raw data, start to finish.

Per CLAUDE.md rule 5: running `python src/run_all.py` from the project root
must regenerate every file in data/processed/ and outputs/ from scratch, so
nothing in this project depends on files that aren't tracked in code.

As more phases are added (SQL metrics, pandas validation, dashboard CSVs),
their run() functions get called here too, in order.
"""

import clean_data
import srm_check
import run_sql
import validate
import ab_test
import sensitivity
import charts
import dashboard_exports

if __name__ == "__main__":
    print("=== Phase 1: Clean and audit raw data ===")
    clean_data.run()

    print("\n=== Phase 1b: Sample ratio mismatch (SRM) check ===")
    srm_check.run()

    print("\n=== Phase 2: Load into SQLite and run SQL metrics ===")
    run_sql.run()

    print("\n=== Phase 3a: Validate SQL metrics against independent pandas ===")
    validate.run()

    print("\n=== Phase 3b: A/B test (bootstrap confidence intervals) ===")
    ab_test_result = ab_test.run()
    ab_test.OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    ab_test_result.to_csv(ab_test.OUTPUT_PATH, index=False)
    print(f"Saved {ab_test.OUTPUT_PATH}")

    print("\n=== Phase 3c: Sensitivity check (excluding outliers) ===")
    sensitivity.run()

    print("\n=== Phase 3d: Build charts ===")
    charts.run()

    print("\n=== Phase 3e: Build dashboard-ready CSVs ===")
    dashboard_exports.run()
