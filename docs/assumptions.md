# Assumptions

This file records assumptions made during data cleaning and analysis, per CLAUDE.md rule 3.

1. **sum_gamerounds is only a proxy for the level a player reached**, not the level itself.
   The dataset does not record which level a player is on - only how many rounds they have
   played in total. A player could replay earlier levels many times, so a high round count
   does not guarantee they passed the gate. We treat sum_gamerounds as an approximate signal,
   not an exact measurement of progress.

2. **Players with fewer than about 30 rounds very likely never reached either gate.**
   Since gate_30 is the earlier of the two gates being tested, a player who has played fewer
   than ~30 rounds total almost certainly has not reached gate_30 yet, let alone gate_40.
   This is an approximation, not a guarantee, for the same reason as assumption 1.

3. **There is no date/time information in this dataset.**
   Every row is a snapshot of a player's lifetime totals (sum_gamerounds, retention_1,
   retention_7) with no timestamps. This means we cannot analyze trends over time (e.g.
   whether retention changed week over week during the test) - only aggregate differences
   between the gate_30 and gate_40 groups.

4. **Outliers in sum_gamerounds are flagged, not removed.**
   A small number of players have extremely high round counts (see outputs/data_quality_report.md
   for exact values). These could be real highly-engaged players or bots/testers. Since we can't
   tell which from this data alone, we keep them in the dataset with an `is_outlier` flag so later
   analysis can choose to include or exclude them and see if it changes the conclusion.

5. **Players with 0 rounds played are kept, not dropped.**
   A 0-round player installed the app but never played a single round. This is a valid outcome
   (not missing/bad data) and matters for retention analysis, so these rows are kept.
