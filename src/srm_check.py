"""
Sample ratio mismatch (SRM) check.

Goal: confirm the gate_30/gate_40 split is close enough to 50/50 to trust
that version assignment was actually random. If it isn't, that's a red
flag for the whole experiment - a broken random assignment can't be fixed
after the fact with statistics on the retention numbers.

How the test works: if assignment were truly 50/50 random, we'd expect
roughly half the players in each group. A chi-square goodness-of-fit test
with 1 degree of freedom measures how far the OBSERVED split is from that
EXPECTED 50/50 split, as a single chi2 number - bigger means less likely
to be chance.

Why math.erfc instead of a stats library: a chi-square statistic with 1
degree of freedom is mathematically just a squared standard normal value.
That means its p-value can be computed directly from the normal
distribution's complementary error function - no scipy/statsmodels
needed, just the standard library's math module:
    p_value = math.erfc(sqrt(chi2 / 2))

A small p-value (conventionally < 0.05) means this split is unlikely to
have happened by chance under true 50/50 random assignment - what A/B
testing calls a "sample ratio mismatch" (SRM).

Run directly with: python src/srm_check.py
"""

import math
import pandas as pd
from pathlib import Path

DATA_PATH = Path("data/processed/cookie_cats_clean.csv")
OUTPUT_PATH = Path("outputs/srm_check.csv")

SIGNIFICANCE_LEVEL = 0.05


def run():
    df = pd.read_csv(DATA_PATH)

    n_gate_30 = int((df["version"] == "gate_30").sum())
    n_gate_40 = int((df["version"] == "gate_40").sum())
    total = n_gate_30 + n_gate_40

    # This check's entire job is to catch data-integrity problems, so it
    # shouldn't silently ignore rows that aren't "gate_30"/"gate_40" - a
    # NaN, typo, or a future third test arm should be reported, not dropped.
    n_other = len(df) - total
    if n_other > 0:
        print(f"WARNING: {n_other} row(s) have a version value other than "
              f"'gate_30'/'gate_40' and are excluded from this chi-square test.")

    if total == 0:
        raise ValueError(
            f"No rows with version 'gate_30' or 'gate_40' found in {DATA_PATH} - "
            f"cannot run the sample ratio mismatch check."
        )

    expected = total / 2  # what each group "should" have under a true 50/50 split

    chi2 = ((n_gate_30 - expected) ** 2) / expected + ((n_gate_40 - expected) ** 2) / expected
    p_value = math.erfc(math.sqrt(chi2 / 2))  # chi-square p-value, df=1

    srm_detected = p_value < SIGNIFICANCE_LEVEL

    print(f"gate_30: {n_gate_30:,} players, gate_40: {n_gate_40:,} players "
          f"(expected {expected:,.1f} each under a true 50/50 split)")
    print(f"chi-square = {chi2:.4f}, p-value = {p_value:.6f}")
    if srm_detected:
        print(f"-> p < {SIGNIFICANCE_LEVEL}: this split is UNLIKELY under random 50/50 "
              f"assignment. Possible sample ratio mismatch (SRM) - treat downstream "
              f"retention numbers with caution.")
    else:
        print(f"-> p >= {SIGNIFICANCE_LEVEL}: this split is consistent with random 50/50 "
              f"assignment.")

    result = pd.DataFrame([{
        "n_gate_30": n_gate_30,
        "n_gate_40": n_gate_40,
        "n_other_version": n_other,
        "total": total,
        "expected_per_group": expected,
        "chi2": round(chi2, 4),
        "p_value": round(p_value, 6),
        "significance_level": SIGNIFICANCE_LEVEL,
        "srm_detected": bool(srm_detected),
    }])

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    result.to_csv(OUTPUT_PATH, index=False)
    print(f"\nSaved {OUTPUT_PATH}")

    return result


if __name__ == "__main__":
    run()
