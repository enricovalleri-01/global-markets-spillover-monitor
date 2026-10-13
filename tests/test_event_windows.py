"""Tests for the event windows and the sample."""

import datetime as dt

import duckdb
import numpy as np
import pandas as pd
import pytest

from src.models.local_projections import DB_FILE, build_panel, change, load


def test_python_horizon_1_matches_sql_view():
    # The windows are computed twice, in SQL and in Python. They must agree,
    # on the same set of announcements, in both the change and the ECB flag.
    con = duckdb.connect(DB_FILE, read_only=True)
    panel = build_panel(*load(con))
    python = panel[panel["h"] == 1].set_index(["date", "series"])[["change", "ecb_in_window"]].sort_index()

    sql = con.execute(
        """
        SELECT announcement_date AS date, series, change, ecb_meeting_in_h1_window
        FROM event_windows
        WHERE announcement_date >= '1999-01-01' AND series IN ('us_10y', 'bund_10y', 'eurusd', 'ciss_ea')
        """
    ).df().set_index(["date", "series"]).sort_index()

    assert len(python) == len(sql) == 214 * 4
    assert np.allclose(python["change"], sql["change"])
    assert (python["ecb_in_window"] == sql["ecb_meeting_in_h1_window"]).all()


def test_one_known_window():
    # 13 December 2023: German 10-year yield 2.25% on the 12th, 2.09% on the 14th.
    con = duckdb.connect(DB_FILE, read_only=True)
    value = con.execute(
        "SELECT change FROM event_windows WHERE announcement_date = '2023-12-13' AND series = 'bund_10y'"
    ).fetchone()[0]
    assert round(value, 6) == -16.0


def test_sample_size():
    con = duckdb.connect(DB_FILE, read_only=True)
    events = load(con)[2]
    assert len(events) == 214                         # announcements from 1999
    assert events["mps_orth_bp"].notna().sum() == 201  # with the orthogonalised surprise


def test_change_types():
    assert change(2.25, 2.09, "diff_bp") == pytest.approx(-16.0)       # yields in percent -> basis points
    assert change(1.100, 1.089, "log_pct") == pytest.approx(-1.00503, abs=1e-5)
    assert change(0.20, 0.21, "diff") == pytest.approx(0.01)


def make_small_case(event_dates):
    # A made-up series observed Monday 1 to Friday 12 January 2024, with no
    # value on Wednesday 3 (a holiday) and none at the weekend.
    days = [d for d in pd.date_range("2024-01-01", "2024-01-12") if d.weekday() < 5 and d.day != 3]
    observations = pd.DataFrame({"series": "x", "date": days, "value": [float(d.day) for d in days]})
    series = pd.DataFrame({"change_type": ["diff"]}, index=["x"])
    events = pd.DataFrame({"date": pd.to_datetime(event_dates)})
    ecb_dates = np.array([np.datetime64("2024-01-09")])
    return series, observations, events, ecb_dates


def test_windows_on_a_small_made_up_calendar():
    # announcements on a normal day (Tue 2), on the holiday (Wed 3) and on a Sunday (7)
    case = make_small_case(["2024-01-02", "2024-01-03", "2024-01-07"])
    panel = build_panel(*case, responses=["x"], horizons=[1, 2]).set_index(["date", "h"])

    def window(day, h):
        row = panel.loc[(pd.Timestamp(day), h)]
        return row["date_before"].date(), row["date_end"].date(), row["change"], row["ecb_in_window"]

    d = dt.date
    assert window("2024-01-02", 1) == (d(2024, 1, 1), d(2024, 1, 4), 3.0, False)   # skips the holiday
    assert window("2024-01-03", 1) == (d(2024, 1, 2), d(2024, 1, 4), 2.0, False)
    assert window("2024-01-07", 1) == (d(2024, 1, 5), d(2024, 1, 8), 3.0, False)   # Friday to Monday
    assert window("2024-01-07", 2) == (d(2024, 1, 5), d(2024, 1, 9), 4.0, True)    # ECB meeting on the 9th


def test_two_announcements_on_one_day_are_rejected():
    case = make_small_case(["2024-01-02", "2024-01-02"])
    with pytest.raises(AssertionError):
        build_panel(*case, responses=["x"], horizons=[1])
