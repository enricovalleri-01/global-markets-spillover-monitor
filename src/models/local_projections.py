"""Daily local projections around FOMC announcements.

For each series and each horizon h:

    y(h-th observation after the announcement day) - y(last observation before it)
        = a + b * shock + e

The shock is the Bauer-Swanson surprise divided by 10, so b is the cumulative
response to a 10 basis point surprise. One regression per series and horizon.

Horizons are counted in the observations of each series, so the same h can end
on different calendar days for different series (holidays differ).

Standard errors: the windows of announcements that are close in time overlap,
so their errors are correlated. The baseline uses Newey-West (HAC) standard
errors with two lags, where a lag is one announcement, not one day. The
simpler heteroskedasticity-robust errors (HC1) are saved next to them.

Run:  python -m src.models.local_projections
"""

from pathlib import Path

import duckdb
import numpy as np
import pandas as pd
import statsmodels.api as sm

DB_FILE = "data/processed/monitor.duckdb"
START = "1999-01-01"
HORIZONS = range(1, 21)
RESPONSES = ["us_10y", "bund_10y", "eurusd", "ciss_ea"]

# The horizons on which conclusions are based. Fixed on 13 October 2026, after
# the first baseline run and before any robustness check was run.
MAIN_HORIZONS = [1, 2, 5]

# 8 October 2008: rate cut coordinated between the Fed, the ECB and other
# central banks. It cannot identify a US-only surprise.
COORDINATED_CUT = pd.Timestamp("2008-10-08")


def load(con) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, np.ndarray]:
    series = con.execute("SELECT series, change_type FROM series").df().set_index("series")
    observations = con.execute("SELECT series, date, value FROM observations ORDER BY series, date").df()
    events = con.execute(
        "SELECT date, time_et, unscheduled, mps_bp, mps_orth_bp FROM fomc_announcements WHERE date >= ? ORDER BY date",
        [START],
    ).df()
    ecb_dates = con.execute("SELECT date FROM ecb_meetings ORDER BY date").df()["date"].to_numpy()
    return series, observations, events, ecb_dates


def change(before: float, after: float, change_type: str) -> float:
    if change_type == "diff_bp":
        return (after - before) * 100
    if change_type == "log_pct":
        return 100 * np.log(after / before)
    return after - before


def build_panel(series, observations, events, ecb_dates, responses=RESPONSES, horizons=HORIZONS) -> pd.DataFrame:
    """One row per announcement, series and horizon, with the change in the series."""
    # The daily design needs one announcement per day. Two on the same day
    # would be counted twice below.
    assert events["date"].is_unique, "two announcements on the same day"

    rows = []
    for name in responses:
        obs = observations[observations["series"] == name]
        dates = obs["date"].to_numpy()
        values = obs["value"].to_numpy()
        change_type = series.loc[name, "change_type"]
        for event_date in events["date"]:
            day = np.datetime64(event_date)
            i_before = np.searchsorted(dates, day, side="left") - 1   # last observation before the day
            i_after = np.searchsorted(dates, day, side="right")       # first observation after the day
            for h in horizons:
                i = i_after + h - 1
                if i_before < 0 or i >= len(values):
                    continue
                # Is there an ECB meeting after the starting observation and up
                # to the final one? This is a calendar match, by date only.
                ecb_in_window = bool(((ecb_dates > dates[i_before]) & (ecb_dates <= dates[i])).any())
                # The meeting calendar starts in March 1999: before that, "no
                # meeting" cannot be told apart from "no data".
                calendar_covers = bool(dates[i_before] >= ecb_dates.min())
                rows.append((
                    event_date, name, h, dates[i_before], dates[i],
                    change(values[i_before], values[i], change_type), ecb_in_window, calendar_covers,
                ))
    panel = pd.DataFrame(
        rows,
        columns=["date", "series", "h", "date_before", "date_end", "change", "ecb_in_window", "calendar_covers"],
    )
    return panel.merge(events, on="date")


def estimate(panel: pd.DataFrame, shock: str = "mps_orth_bp") -> pd.DataFrame:
    """Response to a 10 basis point surprise, by series and horizon."""
    results = []
    for (name, h), group in panel.dropna(subset=[shock]).groupby(["series", "h"]):
        group = group.sort_values("date")  # HAC needs the announcements in time order
        x = sm.add_constant(group[shock] / 10)
        model = sm.OLS(group["change"], x)
        hac = model.fit(cov_type="HAC", cov_kwds={"maxlags": 2, "use_correction": True})
        hc1 = model.fit(cov_type="HC1")
        low, high = hac.conf_int(alpha=0.10).loc[shock]
        results.append({
            "series": name,
            "h": h,
            "beta": hac.params[shock],
            "se": hac.bse[shock],
            "ci90_low": low,
            "ci90_high": high,
            "p_value": hac.pvalues[shock],
            "se_hc1": hc1.bse[shock],
            "p_value_hc1": hc1.pvalues[shock],
            "n": int(hac.nobs),
        })
    return pd.DataFrame(results)


def robustness(panel: pd.DataFrame) -> pd.DataFrame:
    """The baseline and four variations, at the main horizons only."""
    main = panel[panel["h"].isin(MAIN_HORIZONS)]
    specifications = {
        "baseline": estimate(main),
        # windows with no recorded ECB meeting, among those the calendar covers
        "no_ecb_meeting": estimate(main[~main["ecb_in_window"] & main["calendar_covers"]]),
        # raw surprise instead of the orthogonalised one: brings back March-December 2020
        "raw_shock": estimate(main, shock="mps_bp"),
        # scheduled announcements only
        "scheduled_only": estimate(main[~main["unscheduled"]]),
        # without the coordinated cut of 8 October 2008
        "no_coordinated_cut": estimate(main[main["date"] != COORDINATED_CUT]),
    }
    tables = [table.assign(specification=name) for name, table in specifications.items()]
    columns = ["specification", "series", "h", "beta", "se", "ci90_low", "ci90_high", "p_value", "n"]
    return pd.concat(tables, ignore_index=True)[columns]


def main() -> None:
    con = duckdb.connect(DB_FILE, read_only=True)
    panel = build_panel(*load(con))
    baseline = estimate(panel)
    checks = robustness(panel)

    Path("outputs/tables").mkdir(parents=True, exist_ok=True)
    baseline.round(4).to_csv("outputs/tables/lp_baseline.csv", index=False)
    checks.round(4).to_csv("outputs/tables/lp_robustness.csv", index=False)

    print("BASELINE, main horizons")
    print(baseline[baseline["h"].isin(MAIN_HORIZONS)].round(3).to_string(index=False))
    print("\nROBUSTNESS (beta, p-value, n)")
    wide = checks.assign(cell=checks.apply(lambda r: f"{r.beta:6.2f} ({r.p_value:.2f}) n={r.n}", axis=1))
    print(wide.pivot(index=["series", "h"], columns="specification", values="cell")[
        ["baseline", "no_ecb_meeting", "raw_shock", "scheduled_only", "no_coordinated_cut"]
    ].to_string())


if __name__ == "__main__":
    main()
