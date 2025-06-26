from __future__ import annotations

"""Generate automation risk percentile JSON for the API.

Reads ``data_tables/automation_risk_percentiles.csv`` and writes
``API_database_laborforce/data_occup_automation.json`` containing
records of the form::
    {
        "soc": "15-1256",
        "occupation": "Software Developers",
        "automation_pctile": 12.34,
        "major": "15",
        "minor": "15-1",
    }
"""

import json
from pathlib import Path

import pandas as pd

CSV_FILE = Path("data_tables/automation_risk_percentiles.csv")
OUT_FILE = Path("API_database_laborforce/data_occup_automation.json")


def main() -> None:
    df = pd.read_csv(CSV_FILE, dtype=str)
    df = df[["OCC_CODE", "OCC_TITLE", "percentile_rank"]]
    df = df.rename(
        columns={
            "OCC_CODE": "soc",
            "OCC_TITLE": "occupation",
            "percentile_rank": "automation_pctile",
        }
    )

    df = df.dropna(subset=["soc", "occupation", "automation_pctile"])
    df["automation_pctile"] = pd.to_numeric(df["automation_pctile"], errors="coerce")
    df = df.dropna(subset=["automation_pctile"])  # drop if percentile missing

    # SOC major (two-digit) and minor (three-digit) prefixes
    df["major"] = df["soc"].str.split("-").str[0]
    df["minor"] = df["soc"].apply(
        lambda c: f"{c.split('-')[0]}-{c.split('-')[1][0]}" if "-" in c else c[:3]
    )

    df = df.drop_duplicates(subset="soc")
    rows = df.to_dict(orient="records")
    OUT_FILE.write_text(json.dumps(rows, indent=2))
    print(f"\u2713 Wrote {OUT_FILE}")


if __name__ == "__main__":
    main()
