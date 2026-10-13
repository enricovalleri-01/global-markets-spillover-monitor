"""Plot the baseline responses with 90% confidence bands.

Run:  python -m src.models.plot_baseline
"""

from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

TITLES = {
    "us_10y": ("US 10-year Treasury yield", "basis points"),
    "bund_10y": ("German 10-year yield (Bundesbank term structure)", "basis points"),
    "eurusd": ("EUR/USD (negative = weaker euro)", "percent"),
    "ciss_ea": ("Euro area systemic stress (CISS)", "index points"),
}


def main() -> None:
    results = pd.read_csv("outputs/tables/lp_baseline.csv")
    fig, axes = plt.subplots(2, 2, figsize=(10, 6.5), sharex=True)
    for ax, (name, (title, unit)) in zip(axes.flat, TITLES.items()):
        r = results[results["series"] == name]
        ax.fill_between(r["h"], r["ci90_low"], r["ci90_high"], color="#1f4e9c", alpha=0.18, linewidth=0)
        ax.plot(r["h"], r["beta"], color="#1f4e9c", linewidth=1.8)
        ax.axhline(0, color="black", linewidth=0.6)
        ax.set_title(title, fontsize=10, loc="left")
        ax.set_ylabel(unit, fontsize=9)
        ax.tick_params(labelsize=8)
        ax.spines[["top", "right"]].set_visible(False)
    for ax in axes[1]:
        ax.set_xlabel("Observations after the FOMC announcement day", fontsize=9)
        ax.set_xticks([1, 5, 10, 15, 20])
    n = int(results["n"].max())
    fig.suptitle("Cumulative response to a 10 basis point US monetary policy surprise", fontsize=12, x=0.02, ha="left")
    fig.text(
        0.02, 0.005,
        f"Local projections on {n} FOMC announcements, 1999-2023; 2020 and 17 September 2001 are excluded because the orthogonalised\n"
        "surprise is missing. Change from the last observation before the announcement day; horizons are counted in each series' own\n"
        "calendar. Shaded area: pointwise 90% intervals, Newey-West standard errors (2 announcement lags).\n"
        "Shock: Bauer-Swanson orthogonalised surprise. Sources: FRBSF, ECB, Bundesbank, FRED.",
        fontsize=7.5, color="#444444", va="bottom",
    )
    fig.tight_layout(rect=(0, 0.10, 1, 0.96))
    Path("outputs/figures").mkdir(parents=True, exist_ok=True)
    fig.savefig("outputs/figures/lp_baseline.png", dpi=160)


if __name__ == "__main__":
    main()
