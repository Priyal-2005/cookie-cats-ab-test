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

6. **We cannot confirm random assignment was clean, and this limits how much the retention
   results can be trusted.** A sample ratio mismatch (SRM) check (src/srm_check.py,
   outputs/srm_check.csv) compares the actual gate_30/gate_40 split to a true 50/50 split
   using a chi-square goodness-of-fit test (see outputs/srm_check.csv for the exact counts,
   chi2, and p-value). If that check shows a p-value below 0.05, the split is unlikely to
   have happened under genuinely random 50/50 assignment, and the cause cannot be determined
   from this dataset alone (it could be a logging gap, a crash affecting one arm, or
   something else entirely). Every retention number in this project should be read with that
   caveat: the dataset gives no way to rule out the version groups differing in some way
   unrelated to the gate itself.

7. **Rounds played (sum_gamerounds) can itself be affected by the gate being tested**, not
   just by a player's general engagement. A player who hits gate_30 may stop progressing
   (or churn) earlier than a player who doesn't hit a gate until level 40, simply because
   the gate is in their way sooner. That means sum_gamerounds is not a clean, gate-independent
   measure of engagement to control for - it's partly a *consequence* of which version a
   player was assigned to, so bucketing or comparing by rounds played (sql/02, sql/03) can
   partially reflect the gate's effect rather than a confound separate from it.
