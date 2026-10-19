# Data Quality Report - Cookie Cats Raw Data

## Basic facts
- Total rows loaded: 90,189
- Rows involved in a duplicate userid: 0
- Extra rows removed when de-duplicating (keep first occurrence): 0

## A/B group split
- **gate_40**: 45,489 rows (50.44%)
- **gate_30**: 44,700 rows (49.56%)

## sum_gamerounds distribution
- Min: 0
- Max: 49,854
- Mean: 51.87
- Median: 16.0
- 50th percentile: 16.0
- 90th percentile: 134.0
- 99th percentile: 493.0
- 99.9th percentile: 1073.62
- Players with 0 rounds played: 3,994 (4.43%) - kept in the cleaned data (see docs/assumptions.md)

## Outliers
- 10 row(s) flagged as outliers (sum_gamerounds above the 99.99th percentile, threshold = 2013.0)
- Flagged values: [49854, 2961, 2640, 2438, 2294, 2251, 2156, 2124, 2063, 2015]
- These rows were NOT deleted. They have `is_outlier = True` in the cleaned data so they can be
  included or excluded from any analysis as needed.

## What changed between raw and cleaned data
See outputs/cleaning_log.csv for the exact row counts before and after every step.
