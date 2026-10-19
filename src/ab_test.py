"""
Phase 3, step 2: the actual A/B test - is the retention difference real,
or could it just be random noise?

For retention_1 and retention_7:
1. Compute the retention rate for each version.
2. Compute the difference (gate_40 minus gate_30) in percentage points.
3. Bootstrap a 95% confidence interval for that difference.
4. Say in plain words whether the interval includes 0.

What "bootstrap" means here: we don't know the TRUE retention rate for all
possible players, only the rate in this sample. To see how much that
difference could plausibly wobble just by chance, we resample each group
WITH REPLACEMENT (same size as the original group) 10,000 times, recompute
the difference each time, and look at the spread of those 10,000
differences. The middle 95% of that spread is our 95% confidence interval.
If 0 falls inside it, "no difference" is a plausible explanation and we
can't call the result significant. If 0 falls outside it, the difference
is unlikely to be due to chance alone.

Run directly with: python src/ab_test.py
"""

import numpy as np
import pandas as pd
from pathlib import Path

DATA_PATH = Path("data/processed/cookie_cats_clean.csv")
OUTPUT_PATH = Path("outputs/ab_test_result.csv")

N_RESAMPLES = 10_000
RANDOM_SEED = 42  # fixed so re-running this script gives the exact same CI every time


def bootstrap_diff_ci(group_a_values, group_b_values, n_resamples, rng):
    """
    Bootstrap a 95% CI for (mean of group_b - mean of group_a).

    group_a_values / group_b_values: 1D arrays of 0s and 1s (e.g. retention_1
    for gate_30 and gate_40). Returns (ci_lower, ci_upper) as fractions
    (0.0-1.0), not percentages.
    """
    n_a = len(group_a_values)
    n_b = len(group_b_values)
    diffs = np.empty(n_resamples)

    for i in range(n_resamples):
        resample_a = rng.choice(group_a_values, size=n_a, replace=True)
        resample_b = rng.choice(group_b_values, size=n_b, replace=True)
        diffs[i] = resample_b.mean() - resample_a.mean()

    ci_lower, ci_upper = np.percentile(diffs, [2.5, 97.5])
    return ci_lower, ci_upper


def run(df=None, label="full dataset"):
    """
    Run the A/B test on `df` (defaults to the full cleaned dataset).
    `label` is just used in the printed messages, so this same function can
    be reused for the sensitivity check (Phase 3, step 3) on a filtered df.
    """
    if df is None:
        df = pd.read_csv(DATA_PATH)

    rng = np.random.default_rng(RANDOM_SEED)

    rows = []
    for metric in ["retention_1", "retention_7"]:
        g30 = df.loc[df["version"] == "gate_30", metric].to_numpy()
        g40 = df.loc[df["version"] == "gate_40", metric].to_numpy()

        rate_30 = g30.mean() * 100
        rate_40 = g40.mean() * 100
        diff_pp = rate_40 - rate_30

        ci_lower, ci_upper = bootstrap_diff_ci(g30, g40, N_RESAMPLES, rng)
        ci_lower_pp = ci_lower * 100
        ci_upper_pp = ci_upper * 100

        includes_zero = ci_lower_pp <= 0 <= ci_upper_pp

        rows.append({
            "metric": metric,
            "gate_30_rate_pct": round(rate_30, 2),
            "gate_40_rate_pct": round(rate_40, 2),
            "diff_pp_gate40_minus_gate30": round(diff_pp, 2),
            "ci_95_lower_pp": round(ci_lower_pp, 2),
            "ci_95_upper_pp": round(ci_upper_pp, 2),
            "ci_includes_zero": bool(includes_zero),
        })

        print(f"\n[{label}] {metric}:")
        print(f"  gate_30 = {rate_30:.2f}%, gate_40 = {rate_40:.2f}%, "
              f"diff = {diff_pp:+.2f}pp (gate_40 - gate_30)")
        print(f"  95% bootstrap CI for the difference: [{ci_lower_pp:.2f}, {ci_upper_pp:.2f}]pp")
        if includes_zero:
            print("  -> The interval INCLUDES 0, so 'no real difference' is still plausible - "
                  "this is NOT a statistically significant result at the 95% level.")
        else:
            print("  -> The interval does NOT include 0 - this difference is unlikely to be "
                  "random chance, so it IS statistically significant at the 95% level.")

    return pd.DataFrame(rows)


if __name__ == "__main__":
    result_df = run()
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    result_df.to_csv(OUTPUT_PATH, index=False)
    print(f"\nSaved {OUTPUT_PATH}")
