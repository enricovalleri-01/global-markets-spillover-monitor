"""Daily local projections around FOMC announcements.

For each series and each horizon h (in trading days of that series):

    y(h days after the announcement) - y(last day before) = a + b * shock + e

The shock is the Bauer-Swanson surprise divided by 10, so b is the response
to a 10 basis point surprise. One regression per series and horizon, with
heteroskedasticity-robust (HC1) standard errors.

Run:  python -m src.models.local_projections
"""

from pathlib import Path

import duckdb
import numpy as np
import pandas as pd
import statsmodels.api as sm

DB_FILE = "data/processed/monitor.duckdb"
HORIZONS = range(1, 21)
RESPONSES = ["us_10y", "bund_10y", "eurusd", "ciss_ea"]
START = "1999-01-01"


def load(con) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    series = con.execute("SELECT series, change_type FROM series").df().set_index("series")
    observations = con.execute("SELECT series, date, value FROM observations ORDER BY series, date").df()
    events = con.execute(
        """
        SELECT a.date, a.time_et, a.unscheduled, a.mps_bp, a.mps_orth_bp,
               w.ecb_meeting_in_window
        FROM fomc_announcements a
        JOIN event_windows w
          ON w.announcement_date = a.date AND w.time_et = a.time_et AND w.series = 'bund_10y'
        WHERE a.date >= ?
        ORDER BY a.date
        """,
        [START],
    ).df()
    return series, observations, events


def change(before: float, after: float, change_type: str) -> float:
    if change_type == "diff_bp":
        return (after - before) * 100
    if change_type == "log_pct":
        return 100 * np.log(after / before)
    return after - before


def build_panel(series: pd.DataFrame, observations: pd.DataFrame, events: pd.DataFrame) -> pd.DataFrame:
    """One row per announcement, series and horizon, with the change in the series."""
    rows = []
    for name in RESPONSES:
        obs = observations[observations["series"] == name]
        dates = obs["date"].to_numpy()
        values = obs["value"].to_numpy()
        change_type = series.loc[name, "change_type"]
        for event_date in events["date"]:
            day = np.datetime64(event_date)
            i_before = np.searchsorted(dates, day, side="left") - 1   # last observation before the day
            i_after = np.searchsorted(dates, day, side="right")       # first observation after the day
            for h in HORIZONS:
                i = i_after + h - 1
                if i_before < 0 or i >= len(values):
                    continue
                rows.append((event_date, name, h, change(values[i_before], values[i], change_type)))
    panel = pd.DataFrame(rows, columns=["date", "series", "h", "change"])
    return panel.merge(events, on="date")


def estimate(panel: pd.DataFrame, shock: str = "mps_orth_bp") -> pd.DataFrame:
    """Response to a 10 basis point surprise, by series and horizon."""
    results = []
    for (name, h), group in panel.dropna(subset=[shock]).groupby(["series", "h"]):
        x = sm.add_constant(group[shock] / 10)
        fit = sm.OLS(group["change"], x).fit(cov_type="HC1")
        low, high = fit.conf_int(alpha=0.10).loc[shock]
        results.append({
            "series": name,
            "h": h,
            "beta": fit.params[shock],
            "se": fit.bse[shock],
            "ci90_low": low,
            "ci90_high": high,
            "p_value": fit.pvalues[shock],
            "n": int(fit.nobs),
        })
    return pd.DataFrame(results)


def main() -> None:
    con = duckdb.connect(DB_FILE, read_only=True)
    series, observations, events = load(con)
    panel = build_panel(series, observations, events)
    baseline = estimate(panel)

    Path("outputs/tables").mkdir(parents=True, exist_ok=True)
    baseline.round(4).to_csv("outputs/tables/lp_baseline.csv", index=False)
    print(baseline[baseline["h"].isin([1, 2, 5, 10, 20])].round(3).to_string(index=False))


if __name__ == "__main__":
    main()
