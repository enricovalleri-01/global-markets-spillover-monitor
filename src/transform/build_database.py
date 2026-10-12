"""Read the raw files and build the DuckDB database from scratch.

The database is always rebuilt from data/raw, never edited by hand, so it can
be deleted and recreated at any time.

Run:  python -m src.transform.build_database
"""

from pathlib import Path

import duckdb
import pandas as pd

RAW = Path("data/raw")
DB_FILE = Path("data/processed/monitor.duckdb")

# series: (description, unit, source, source code, change type)
SERIES = {
    "eurusd": ("EUR/USD, ECB reference rate (US dollars per euro)", "USD per EUR", "ECB", "EXR.D.USD.EUR.SP00.A", "log_pct"),
    "bund_10y": ("German 10-year government bond yield", "percent", "Bundesbank", "BBSIS.D.I.ZAR.ZI.EUR.S1311.B.A604.R10XX.R.A.A._Z._Z.A", "diff_bp"),
    "ciss_ea": ("Composite Indicator of Systemic Stress, euro area", "index 0-1", "ECB", "CISS.D.U2.Z0Z.4F.EC.SS_CIN.IDX", "diff"),
    "us_10y": ("US 10-year Treasury yield, constant maturity", "percent", "FRED", "DGS10", "diff_bp"),
    "vix": ("CBOE volatility index", "index", "FRED", "VIXCLS", "diff"),
    "brent": ("Brent crude oil price", "USD per barrel", "FRED", "DCOILBRENTEU", "log_pct"),
    "usd_broad": ("Nominal broad US dollar index", "index", "FRED", "DTWEXBGS", "log_pct"),
}


def read_ecb(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path, usecols=["TIME_PERIOD", "OBS_VALUE"])
    return df.rename(columns={"TIME_PERIOD": "date", "OBS_VALUE": "value"})


def read_fred(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path, na_values=["."])
    df.columns = ["date", "value"]
    return df


def read_bundesbank(path: Path) -> pd.DataFrame:
    # The file starts with a few description lines; data rows start with a date.
    df = pd.read_csv(path, header=None, usecols=[0, 1], names=["date", "value"], na_values=["."])
    return df[df["date"].str.match(r"\d{4}-\d{2}-\d{2}", na=False)]


READERS = {
    "eurusd": (read_ecb, RAW / "ecb/eurusd.csv"),
    "ciss_ea": (read_ecb, RAW / "ecb/ciss_ea.csv"),
    "bund_10y": (read_bundesbank, RAW / "bundesbank/bund_10y.csv"),
    "us_10y": (read_fred, RAW / "fred/us_10y.csv"),
    "vix": (read_fred, RAW / "fred/vix.csv"),
    "brent": (read_fred, RAW / "fred/brent.csv"),
    "usd_broad": (read_fred, RAW / "fred/usd_broad.csv"),
}


def load_observations() -> pd.DataFrame:
    frames = []
    for name, (reader, path) in READERS.items():
        df = reader(path)
        df["date"] = pd.to_datetime(df["date"]).dt.date
        df["value"] = pd.to_numeric(df["value"])
        df = df.dropna(subset=["value"])  # days without a value are simply not stored
        df.insert(0, "series", name)
        frames.append(df)
    return pd.concat(frames, ignore_index=True)


def load_announcements() -> pd.DataFrame:
    raw = pd.read_excel(RAW / "frbsf/monetary-policy-surprises-data.xlsx", sheet_name="FOMC (update 2023)")
    return pd.DataFrame({
        "date": pd.to_datetime(raw["Date"]).dt.date,
        "time_et": raw["Time"].astype(str),
        "unscheduled": raw["Unscheduled"].astype(bool),
        # the file is in percentage points: times 100 gives basis points
        "mps_bp": raw["MPS"] * 100,
        "mps_orth_bp": raw["MPS_ORTH"] * 100,
        "us10y_30min_bp": raw["TNOTE10"] * 100,
    })


def build() -> None:
    DB_FILE.parent.mkdir(parents=True, exist_ok=True)
    DB_FILE.unlink(missing_ok=True)
    con = duckdb.connect(str(DB_FILE))
    con.execute(Path("sql/schema.sql").read_text())

    # The DataFrames get a "_df" suffix so that their names cannot be confused
    # with the database tables in the SQL below.
    series_df = pd.DataFrame(
        [(name, *info) for name, info in SERIES.items()],
        columns=["series", "description", "unit", "source", "source_code", "change_type"],
    )
    observations_df = load_observations()
    announcements_df = load_announcements()

    con.execute("INSERT INTO series SELECT * FROM series_df")
    con.execute("INSERT INTO observations SELECT * FROM observations_df")
    con.execute("INSERT INTO fomc_announcements SELECT * FROM announcements_df")
    con.execute(Path("sql/event_windows.sql").read_text())

    for table in ["series", "observations", "fomc_announcements"]:
        rows = con.execute(f"SELECT count(*) FROM {table}").fetchone()[0]
        print(f"{table:20s} {rows:>8,} rows")
    con.close()


if __name__ == "__main__":
    build()
