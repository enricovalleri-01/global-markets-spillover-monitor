"""The event windows are computed twice, in SQL and in Python. They must agree."""

import duckdb
import numpy as np

from src.models.local_projections import DB_FILE, build_panel, load


def test_python_horizon_1_matches_sql_view():
    con = duckdb.connect(DB_FILE, read_only=True)
    series, observations, events = load(con)
    panel = build_panel(series, observations, events)
    python = panel[panel["h"] == 1].set_index(["date", "series"])["change"]

    sql = con.execute(
        "SELECT announcement_date AS date, series, change FROM event_windows WHERE announcement_date >= '1999-01-01'"
    ).df().set_index(["date", "series"])["change"]

    common = python.index.intersection(sql.index)
    assert len(common) == len(python)  # every Python window exists in SQL
    assert np.allclose(python.loc[common], sql.loc[common])


def test_one_known_window():
    # 13 December 2023: Bund 10-year yield 2.25% on the 12th, 2.09% on the 14th.
    con = duckdb.connect(DB_FILE, read_only=True)
    change = con.execute(
        "SELECT change FROM event_windows WHERE announcement_date = '2023-12-13' AND series = 'bund_10y'"
    ).fetchone()[0]
    assert round(change, 6) == -16.0
