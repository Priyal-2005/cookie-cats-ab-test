# Validation Report

Every SQL metric below was recomputed independently in pandas directly from
data/processed/cookie_cats_clean.csv (not by reading the SQL output), then
compared to the SQL result. Tolerance = 0.01 (rounding allowance).

| Metric | Status | Max difference |
|---|---|---|
| 01_retention_by_version.players | PASS | 0.0 |
| 01_retention_by_version.ret_1 | PASS | 0.0 |
| 01_retention_by_version.ret_7 | PASS | 0.0 |
| 01_retention_by_version.ret_1_pct | PASS | 0.0 |
| 01_retention_by_version.ret_7_pct | PASS | 0.0 |
| 02_rounds_buckets.players | PASS | 0.0 |
| 02_rounds_buckets.ret_1_pct | PASS | 0.0 |
| 02_rounds_buckets.ret_7_pct | PASS | 0.0 |
| 03_retention_by_bucket_gap.gate_30_ret_7_pct | PASS | 0.0 |
| 03_retention_by_bucket_gap.gate_40_ret_7_pct | PASS | 0.0 |
| 03_retention_by_bucket_gap.gate_40_minus_gate_30_pp | PASS | 0.0 |
| 04_summary.players | PASS | 0.0 |
| 04_summary.avg_rounds | PASS | 0.0 |
| 04_summary.max_rounds | PASS | 0.0 |
| 04_summary.players_zero_rounds | PASS | 0.0 |
| 04_summary.pct_players_30plus_rounds | PASS | 0.0 |

**All 16 metrics PASSED.**
