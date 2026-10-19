-- Goal: for each rounds_bucket, compare day-7 retention % between gate_30 and
-- gate_40 side by side, and show the gap between them in percentage points.
--
-- How this works: AVG(retention_7) is the day-7 retention rate (since
-- retention_7 is 0/1, its average is the fraction of players retained).
-- A CASE expression inside AVG() turns that into a *conditional* average:
-- "only average retention_7 for rows where version = 'gate_30'". Rows from
-- the other version return NULL from the CASE, and SQLite's AVG() ignores
-- NULLs, so each AVG() only looks at its own version's players even though
-- we never filtered rows out with WHERE. This lets both versions' numbers
-- sit in the same output row per bucket, ready to compare side by side.
SELECT
    rounds_bucket,
    bucket_order,

    -- gate_30's day-7 retention %, for players in this rounds_bucket only.
    ROUND(AVG(CASE WHEN version = 'gate_30' THEN retention_7 END) * 100.0, 2) AS gate_30_ret_7_pct,

    -- gate_40's day-7 retention %, for players in this rounds_bucket only.
    ROUND(AVG(CASE WHEN version = 'gate_40' THEN retention_7 END) * 100.0, 2) AS gate_40_ret_7_pct,

    -- The gap: gate_40's retention minus gate_30's retention, in percentage
    -- points. Positive means gate_40 retained better in this bucket.
    ROUND(
        (AVG(CASE WHEN version = 'gate_40' THEN retention_7 END)
         - AVG(CASE WHEN version = 'gate_30' THEN retention_7 END)) * 100.0,
    2) AS gate_40_minus_gate_30_pp

FROM players
GROUP BY rounds_bucket, bucket_order
ORDER BY bucket_order;
