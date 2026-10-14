"""Plot the five specifications side by side at the main horizons.

Run:  python -m src.models.plot_robustness
"""

from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

SERIES = {
    "us_10y": "US 10-year yield (bp)",
    "bund_10y": "German 10-year yield (bp)",
    "eurusd": "EUR/USD (%)",
}
SPECIFICATIONS = {
    "baseline": ("Baseline", "#1f4e9c"),
    "no_ecb_meeting": ("No ECB meeting in window", "#d1793b"),
    "raw_shock": ("Raw surprise (incl. 2020)", "#5a9e6f"),
    "scheduled_only": ("Scheduled meetings only", "#8b5fa8"),
    "no_coordinated_cut": ("Without 8 Oct 2008", "#7a7a7a"),
}


def main() -> None:
    results = pd.read_csv("outputs/tables/lp_robustness.csv")
    horizons = sorted(results["h"].unique())
    fig, axes = plt.subplots(1, 3, figsize=(11, 3.8))
    width = 0.14
    for ax, (name, title) in zip(axes, SERIES.items()):
        for k, (spec, (label, color)) in enumerate(SPECIFICATIONS.items()):
            r = results[(results["series"] == name) & (results["specification"] == spec)].sort_values("h")
            x = [i + (k - 2) * width for i in range(len(horizons))]
            ax.errorbar(x, r["beta"], yerr=[r["beta"] - r["ci90_low"], r["ci90_high"] - r["beta"]],
                        fmt="o", color=color, markersize=4, elinewidth=1.2, capsize=0, label=label)
        ax.axhline(0, color="black", linewidth=0.6)
        ax.set_xticks(range(len(horizons)), [f"h = {h}" for h in horizons])
        ax.set_title(title, fontsize=10, loc="left")
        ax.tick_params(labelsize=8)
        ax.spines[["top", "right"]].set_visible(False)
    handles, labels = axes[0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="lower center", ncol=5, fontsize=7.5, frameon=False, bbox_to_anchor=(0.5, 0.06))
    fig.suptitle("Response to a 10 basis point US surprise: baseline and four variations", fontsize=11, x=0.01, ha="left")
    fig.text(0.01, 0.01, "Points: estimates; bars: pointwise 90% intervals, Newey-West standard errors (2 announcement lags). "
             "Sample 1999-2023.", fontsize=7.5, color="#444444")
    fig.tight_layout(rect=(0, 0.13, 1, 0.94))
    Path("outputs/figures").mkdir(parents=True, exist_ok=True)
    fig.savefig("outputs/figures/lp_robustness.png", dpi=160)


if __name__ == "__main__":
    main()
