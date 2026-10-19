-- Goal: for each version AND each rounds_bucket: players, day-1 retention %, day-7 retention %.
SELECT
    version,
    rounds_bucket,
    bucket_order,
    COUNT(*) AS players,
    
    -- Day-1 retention % (rounded to 2 decimals)
    ROUND(AVG(retention_1) * 100.0, 2) AS ret_1_pct,
    
    -- Day-7 retention % (rounded to 2 decimals)
    ROUND(AVG(retention_7) * 100.0, 2) AS ret_7_pct

FROM players
GROUP BY
    version,
    rounds_bucket,
    bucket_order
ORDER BY
    version,
    bucket_order;