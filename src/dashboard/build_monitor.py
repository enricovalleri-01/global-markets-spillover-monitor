"""Build the monitor: a summary table, a chart page and an Excel file.

The monitor describes where markets stand today. It estimates nothing: every
number comes from sql/monitor_summary.sql or from the observations table.

Run:  python -m src.dashboard.build_monitor
"""

from pathlib import Path

import duckdb
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

DB_FILE = "data/processed/monitor.duckdb"
OUT = Path("outputs/monitor")
CHART_START = "2019-01-01"

# order of the rows, label, unit of the level, unit of the changes
ROWS = {
    "eurusd": ("EUR/USD", "USD per EUR", "%"),
    "usd_broad": ("US dollar, broad index", "index", "%"),
    "us_10y": ("US 10-year yield", "%", "bp"),
    "bund_10y": ("German 10-year yield", "%", "bp"),
    "us_bund_spread": ("US minus German 10-year yield", "pp", "bp"),
    "brent": ("Brent crude oil", "USD per barrel", "%"),
    "vix": ("VIX", "index", "points"),
    "ciss_ea": ("Euro area systemic stress (CISS)", "index 0-1", "points"),
}


def summary(con) -> pd.DataFrame:
    table = con.execute(Path("sql/monitor_summary.sql").read_text()).df().set_index("series").loc[list(ROWS)]
    table["last_date"] = pd.to_datetime(table["last_date"]).dt.date  # a plain date, not a timestamp
    table.insert(0, "label", [ROWS[s][0] for s in table.index])
    table.insert(1, "level_unit", [ROWS[s][1] for s in table.index])
    table.insert(2, "change_unit", [ROWS[s][2] for s in table.index])
    return table.drop(columns="change_type")


def markdown_table(table: pd.DataFrame) -> str:
    lines = [
        "| Series | Last date | Level | 1 week | 1 month | 1 year | Change unit | Percentile since 1999* |",
        "| --- | --- | ---: | ---: | ---: | ---: | --- | ---: |",
    ]
    for _, r in table.iterrows():
        digits = 4 if r.change_unit == "points" and r.last_value < 1 else 2
        lines.append(
            f"| {r.label} | {r.last_date:%d %b %Y} | {r.last_value:.{digits}f} {r.level_unit} "
            f"| {r.change_1w:+.{digits}f} | {r.change_1m:+.{digits}f} | {r.change_1y:+.{digits}f} "
            f"| {r.change_unit} | {r.percentile_since_1999:.0f} |"
        )
    return "\n".join(lines)


def charts(con) -> None:
    obs = con.execute("SELECT series, date, value FROM observations WHERE date >= ?", [CHART_START]).df()
    wide = obs.pivot(index="date", columns="series", values="value")
    panels = [
        ("EUR/USD", ["eurusd"], "USD per EUR"),
        ("10-year government bond yields", ["us_10y", "bund_10y"], "percent"),
        ("US minus German 10-year yield", ["spread"], "percentage points"),
        ("Brent crude oil", ["brent"], "USD per barrel"),
        ("VIX", ["vix"], "index"),
        ("Euro area systemic stress (CISS)", ["ciss_ea"], "index"),
    ]
    wide["spread"] = wide["us_10y"] - wide["bund_10y"]
    names = {"us_10y": "United States", "bund_10y": "Germany"}
    fig, axes = plt.subplots(3, 2, figsize=(10, 9), sharex=True)
    for ax, (title, columns, unit) in zip(axes.flat, panels):
        for column, color in zip(columns, ["#1f4e9c", "#d1793b"]):
            s = wide[column].dropna()
            ax.plot(s.index, s.values, color=color, linewidth=1.1, label=names.get(column))
            ax.annotate(f"{s.iloc[-1]:.2f}", (s.index[-1], s.iloc[-1]), xytext=(4, 0),
                        textcoords="offset points", fontsize=7.5, color=color, va="center")
        if len(columns) > 1:
            ax.legend(fontsize=7.5, frameon=False, loc="upper left")
        ax.set_title(title, fontsize=10, loc="left")
        ax.set_ylabel(unit, fontsize=8.5)
        ax.tick_params(labelsize=8)
        ax.spines[["top", "right"]].set_visible(False)
    last = obs["date"].max()
    fig.suptitle(f"Global markets monitor, {pd.Timestamp(CHART_START):%Y} to {pd.Timestamp(last):%d %B %Y}",
                 fontsize=12, x=0.02, ha="left")
    fig.text(0.02, 0.005, "Daily data. Sources: ECB (EUR/USD, CISS), Bundesbank (German yield), "
             "FRED (US yield, Brent, VIX).", fontsize=7.5, color="#444444")
    fig.tight_layout(rect=(0, 0.02, 1, 0.96))
    fig.savefig(OUT / "monitor_charts.png", dpi=150)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    con = duckdb.connect(DB_FILE, read_only=True)
    table = summary(con)
    charts(con)

    downloaded = pd.read_csv("data/raw/download_log.csv")["downloaded_utc"].str[:10].max()
    page = f"""# Global markets monitor

Data downloaded on {downloaded}. Each series shows its latest observation; the
dates differ because sources publish with different delays. Changes are in
basis points for yields and the spread, in percent for exchange rates and oil
(log changes), and in index points for the VIX and the CISS. The percentile is
the share of daily observations since 1999 below the latest level (since 2006
for the broad dollar index).

{markdown_table(table)}

\* Since 2006 for the broad dollar index, the first year of the series.

![Monitor charts](monitor_charts.png)

Rebuild with `make monitor`. To update the data first, run `make download`;
the event-study results in the README and the note would change too.
"""
    (OUT / "monitor.md").write_text(page)

    Path("outputs/excel").mkdir(parents=True, exist_ok=True)
    with pd.ExcelWriter("outputs/excel/global_markets_monitor.xlsx") as xl:
        table.round(4).to_excel(xl, sheet_name="monitor")
        pd.read_csv("outputs/tables/lp_baseline.csv").to_excel(xl, sheet_name="lp_baseline", index=False)
        pd.read_csv("outputs/tables/lp_robustness.csv").to_excel(xl, sheet_name="lp_robustness", index=False)
    print(table.round(3).to_string())


if __name__ == "__main__":
    main()
