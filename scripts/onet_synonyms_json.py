"""Convert ONET scraped synonyms CSV to a compact JSON file.

Reads ``ONET-Scrapped-Data/onet_data_scraped.csv`` and writes
``ONET-Scrapped-Data/onet_synonyms.json`` containing records of the form::
    {"soc": "43-3021", "synonyms": "Billing Clerk, ..."}

This separation keeps the scraping step isolated from downstream
processing.
"""
from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

CSV_FILE = Path("ONET-Scrapped-Data/onet_data_scraped.csv")
OUT_FILE = Path("ONET-Scrapped-Data/onet_synonyms.json")


def main() -> None:
    df = pd.read_csv(CSV_FILE, dtype=str)
    if df.empty:
        raise SystemExit(f"No rows found in {CSV_FILE}")

    df["soc"] = df["onet_soc_code"].str.replace(r"\.\d+$", "", regex=True)
    df = df[["soc", "synonyms"]].fillna("")

    rows = df.to_dict(orient="records")
    OUT_FILE.write_text(json.dumps(rows, indent=2))
    print(f"\u2713 Wrote {OUT_FILE}")


if __name__ == "__main__":
    main()
