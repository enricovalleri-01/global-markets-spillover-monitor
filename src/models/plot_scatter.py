"""Plot the idea of the regression with the real data: one dot per announcement.

The fitted line is the ordinary least squares line of the change in the German
10-year yield at h = 1 on the surprise, so its slope (times 10) is the baseline
coefficient in outputs/tables/lp_baseline.csv.

Run:  python -m src.models.plot_scatter
"""

from pathlib import Path

import duckdb
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from src.models.local_projections import DB_FILE, build_panel, load


def main() -> None:
    con = duckdb.connect(DB_FILE, read_only=True)
    panel = build_panel(*load(con))
    data = panel[(panel["series"] == "bund_10y") & (panel["h"] == 1)].dropna(subset=["mps_orth_bp"])
    x = data["mps_orth_bp"].to_numpy()
    y = data["change"].to_numpy()
    slope, intercept = np.polyfit(x, y, 1)

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.scatter(x, y, s=40, color="#1f4e9c", alpha=0.45, edgecolors="none")
    line_x = np.array([x.min() - 1, x.max() + 1])
    ax.plot(line_x, intercept + slope * line_x, color="#d1793b", linewidth=3,
            label=f"Average relationship: {10 * slope:+.1f} bp per 10 bp of surprise")
    ax.axhline(0, color="#9aa0a8", linewidth=0.8)
    ax.axvline(0, color="#9aa0a8", linewidth=0.8)
    ax.set_xlabel("Fed surprise (basis points)", fontsize=11)
    ax.set_ylabel("Change in German 10-year yield (bp)", fontsize=11)
    ax.legend(frameon=False, fontsize=10, loc="upper left")
    ax.spines[["top", "right"]].set_visible(False)
    ax.set_title("Each dot is one FOMC announcement, 1999-2023", fontsize=12, loc="left")
    fig.text(0.01, 0.01, f"{len(data)} announcements. Change from the last observation before the announcement day "
             "to the first one after (h = 1). Shock: Bauer-Swanson orthogonalised surprise.",
             fontsize=7.5, color="#444444")
    fig.tight_layout(rect=(0, 0.03, 1, 1))
    Path("outputs/figures").mkdir(parents=True, exist_ok=True)
    fig.savefig("outputs/figures/scatter_bund_h1.png", dpi=160)


if __name__ == "__main__":
    main()
