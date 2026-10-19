-- Goal: one summary row per version with overall engagement stats:
-- how many players, how much they played on average, the heaviest player,
-- how many never played at all, and what share played enough rounds to
-- plausibly have reached gate_30 (see docs/assumptions.md, assumption 2).
SELECT
    version,

    -- Total players in this version.
    COUNT(*) AS players,

    -- Average rounds played per player, rounded to 2 decimals.
    ROUND(AVG(sum_gamerounds), 2) AS avg_rounds,

    -- The single highest sum_gamerounds value in this version.
    MAX(sum_gamerounds) AS max_rounds,

    -- How many players never played a single round (sum_gamerounds = 0).
    -- CASE...THEN 1 ELSE 0 turns a yes/no condition into a 1/0 we can SUM.
    SUM(CASE WHEN sum_gamerounds = 0 THEN 1 ELSE 0 END) AS players_zero_rounds,

    -- Share of players who played 30+ rounds, as a percentage.
    -- COUNT(*) here is "players" again, just recomputed inside this row's
    -- group so the division happens per-version, not across the whole table.
    ROUND(
        SUM(CASE WHEN sum_gamerounds >= 30 THEN 1 ELSE 0 END) * 100.0 / COUNT(*),
    2) AS pct_players_30plus_rounds

FROM players
GROUP BY version;
