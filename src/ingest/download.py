"""Download the raw files, one per series, and log every download.

Raw files are saved exactly as the source serves them and are never edited.
Each download adds one line to data/raw/download_log.csv with the URL, the
UTC time, the file size and a sha256 fingerprint, so that any number in the
project can be traced back to the file it came from.

Run:  python -m src.ingest.download
"""

import csv
import hashlib
from datetime import datetime, timezone
from pathlib import Path

import requests

RAW_DIR = Path("data/raw")
LOG_FILE = RAW_DIR / "download_log.csv"

ECB = "https://data-api.ecb.europa.eu/service/data/{}?format=csvdata"
FRED = "https://fred.stlouisfed.org/graph/fredgraph.csv?id={}"
BUNDESBANK = "https://api.statistiken.bundesbank.de/rest/download/{}?format=csv&lang=en"

# name: (source folder, file name, URL)
SERIES = {
    "fed_shocks": (
        "frbsf",
        "monetary-policy-surprises-data.xlsx",
        "https://www.frbsf.org/wp-content/uploads/monetary-policy-surprises-data.xlsx",
    ),
    "eurusd": ("ecb", "eurusd.csv", ECB.format("EXR/D.USD.EUR.SP00.A")),
    "ciss_ea": ("ecb", "ciss_ea.csv", ECB.format("CISS/D.U2.Z0Z.4F.EC.SS_CIN.IDX")),
    "bund_10y": (
        "bundesbank",
        "bund_10y.csv",
        BUNDESBANK.format("BBSIS/D.I.ZAR.ZI.EUR.S1311.B.A604.R10XX.R.A.A._Z._Z.A"),
    ),
    "us_10y": ("fred", "us_10y.csv", FRED.format("DGS10")),
    "vix": ("fred", "vix.csv", FRED.format("VIXCLS")),
    "brent": ("fred", "brent.csv", FRED.format("DCOILBRENTEU")),
    "usd_broad": ("fred", "usd_broad.csv", FRED.format("DTWEXBGS")),
    # ECB Governing Council meeting dates and decisions, from the data of my
    # master's thesis (the "%28" is a stray "(" in the file name on GitHub).
    "ecb_meetings": (
        "thesis",
        "ecb_policy_decisions_1999_2025.csv",
        "https://raw.githubusercontent.com/enricovalleri-01/ECB-monetary-surprises-extraction-llm-"
        "/main/data/ecb_policy_decisions_FULL_1999_2025.csv%28",
    ),
}


def download(name: str) -> Path:
    folder, filename, url = SERIES[name]
    response = requests.get(url, timeout=120)
    response.raise_for_status()

    path = RAW_DIR / folder / filename
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(response.content)

    new_log = not LOG_FILE.exists()
    with LOG_FILE.open("a", newline="") as f:
        writer = csv.writer(f)
        if new_log:
            writer.writerow(["series", "file", "url", "downloaded_utc", "bytes", "sha256"])
        writer.writerow([
            name,
            str(path),
            url,
            datetime.now(timezone.utc).isoformat(timespec="seconds"),
            len(response.content),
            hashlib.sha256(response.content).hexdigest(),
        ])
    return path


if __name__ == "__main__":
    import sys

    # with no arguments download everything; otherwise only the names given
    for name in sys.argv[1:] or SERIES:
        path = download(name)
        print(f"{name:12s} -> {path}  ({path.stat().st_size:,} bytes)")
