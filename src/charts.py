"""
Phase 3, step 4: build the three matplotlib charts for the README/dashboard.

All three charts read from the SQL outputs in outputs/sql/ (already
validated against pandas in validate.py), so the charts and the numbers in
the README are guaranteed to come from the same source.

1. retention_by_version.png: day-1 and day-7 retention, one bar pair per version.
2. rounds_distribution_by_bucket.png: how many players fall in each rounds_bucket, by version.
3. day7_retention_by_bucket.png: day-7 retention % by rounds_bucket, by version.

Run directly with: python src/charts.py
"""

import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

SQL_OUTPUT_DIR = Path("outputs/sql")
CHARTS_DIR = Path("outputs/charts")

# Bucket order as a list, so charts show buckets in a sensible order
# (0, 1-4, 5-9, ...) instead of alphabetical order.
BUCKET_ORDER = ["0", "1-4", "5-9", "10-19", "20-29", "30-39", "40-49", "50-99", "100-199", "200+"]


def chart_retention_by_version():
    """Grouped bar chart: day-1 vs day-7 retention %, one group per version."""
    df = pd.read_csv(SQL_OUTPUT_DIR / "01_retention_by_version.csv")
    df = df.sort_values("version")

    x = range(len(df))
    width = 0.35

    fig, ax = plt.subplots(figsize=(7, 5))
    ax.bar([i - width / 2 for i in x], df["ret_1_pct"], width, label="Day 1 retention")
    ax.bar([i + width / 2 for i in x], df["ret_7_pct"], width, label="Day 7 retention")

    ax.set_xticks(list(x))
    ax.set_xticklabels(df["version"])
    ax.set_xlabel("Version")
    ax.set_ylabel("Retention (%)")
    ax.set_title("Day-1 and Day-7 Retention by Version")
    ax.legend()

    fig.tight_layout()
    out_path = CHARTS_DIR / "retention_by_version.png"
    fig.savefig(out_path, dpi=150)
    plt.close(fig)
    print(f"Saved {out_path}")


def chart_rounds_distribution_by_bucket():
    """Grouped bar chart: number of players per rounds_bucket, one group per version."""
    df = pd.read_csv(SQL_OUTPUT_DIR / "02_rounds_buckets.csv")
    pivot = df.pivot(index="rounds_bucket", columns="version", values="players").reindex(BUCKET_ORDER)

    x = range(len(pivot))
    width = 0.35

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.bar([i - width / 2 for i in x], pivot["gate_30"], width, label="gate_30")
    ax.bar([i + width / 2 for i in x], pivot["gate_40"], width, label="gate_40")

    ax.set_xticks(list(x))
    ax.set_xticklabels(pivot.index, rotation=45, ha="right")
    ax.set_xlabel("Rounds played (bucket)")
    ax.set_ylabel("Number of players")
    ax.set_title("Distribution of Rounds Played, by Bucket and Version")
    ax.legend()

    fig.tight_layout()
    out_path = CHARTS_DIR / "rounds_distribution_by_bucket.png"
    fig.savefig(out_path, dpi=150)
    plt.close(fig)
    print(f"Saved {out_path}")


def chart_day7_retention_by_bucket():
    """Line chart: day-7 retention % by rounds_bucket, one line per version."""
    df = pd.read_csv(SQL_OUTPUT_DIR / "02_rounds_buckets.csv")
    pivot = df.pivot(index="rounds_bucket", columns="version", values="ret_7_pct").reindex(BUCKET_ORDER)

    x = range(len(pivot))

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(x, pivot["gate_30"], marker="o", label="gate_30")
    ax.plot(x, pivot["gate_40"], marker="o", label="gate_40")

    ax.set_xticks(list(x))
    ax.set_xticklabels(pivot.index, rotation=45, ha="right")
    ax.set_xlabel("Rounds played (bucket)")
    ax.set_ylabel("Day-7 retention (%)")
    ax.set_title("Day-7 Retention by Rounds Bucket and Version")
    ax.legend()

    fig.tight_layout()
    out_path = CHARTS_DIR / "day7_retention_by_bucket.png"
    fig.savefig(out_path, dpi=150)
    plt.close(fig)
    print(f"Saved {out_path}")


def run():
    CHARTS_DIR.mkdir(parents=True, exist_ok=True)
    chart_retention_by_version()
    chart_rounds_distribution_by_bucket()
    chart_day7_retention_by_bucket()


if __name__ == "__main__":
    run()
