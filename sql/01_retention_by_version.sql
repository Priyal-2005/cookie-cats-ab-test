-- Goal: for each version, how many players, and what % came back on day 1 and day 7?
SELECT
    version,
    COUNT(*) AS players,
    
    -- Players who came back on day 1
    SUM(retention_1) AS ret_1,
    
    -- Day-1 retention % (rounded to 2 decimals)
    ROUND(AVG(retention_1) * 100.0, 2) AS ret_1_pct,
    
    -- Players who came back on day 7
    SUM(retention_7) AS ret_7,
    
    -- Day-7 retention % (rounded to 2 decimals)
    ROUND(AVG(retention_7) * 100.0, 2) AS ret_7_pct

FROM players
GROUP BY version;