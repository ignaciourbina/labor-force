"""Append 4-digit Census occupation codes to national employment totals.

This script reads ``data_tables/national_employment_2024.csv`` and matches each
six-digit 2018 SOC code to its corresponding four-digit 2018 Census occupation
code using ``csv_crosswalk_census18codes_to_soc18codes.csv``. The mapping
handles wildcard SOC codes in the crosswalk such as ``15-124X`` or group codes
like ``13-2070`` by treating them as prefixes. The original employment rows are
not aggregated; a new ``census_code`` column is appended and the result is
written to ``data_tables/national_employment_2024_with_census.csv``.
"""
from __future__ import annotations

import pandas as pd
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parents[1] / "data_tables"
EMP_FILE = DATA_DIR / "national_employment_2024.csv"
CROSSWALK_FILE = DATA_DIR / "csv_crosswalk_census18codes_to_soc18codes.csv"
OUT_FILE = DATA_DIR / "national_employment_2024_with_census.csv"


def load_tables() -> tuple[pd.DataFrame, pd.DataFrame]:
    """Load employment totals and Census-SOC crosswalk."""
    emp = pd.read_csv(EMP_FILE, dtype={"OCC_CODE": str})
    cw = pd.read_csv(CROSSWALK_FILE, dtype={"2018 Census Code": str, "2018 SOC Code": str})
    cw["2018 Census Code"] = cw["2018 Census Code"].str.zfill(4)
    cw["2018 SOC Code"] = cw["2018 SOC Code"].str.strip()
    return emp, cw


def census_for_soc(crosswalk: pd.DataFrame, soc: str) -> str | pd.NA:
    """Return the 4-digit Census code for a SOC code using wildcard logic."""
    soc = str(soc)
    # exact match
    exact = crosswalk[crosswalk["2018 SOC Code"] == soc]
    if not exact.empty:
        return exact["2018 Census Code"].iloc[0]

    # wildcard patterns with X placeholders
    mask_x = crosswalk["2018 SOC Code"].str.contains("X")
    for _, row in crosswalk[mask_x].iterrows():
        prefix = row["2018 SOC Code"].replace("X", "")
        if soc.startswith(prefix):
            return row["2018 Census Code"]

    # 5-digit SOC group codes ending in zero
    mask_zero = crosswalk["2018 SOC Code"].str.endswith("0") & ~mask_x
    for _, row in crosswalk[mask_zero].iterrows():
        cw_soc = row["2018 SOC Code"]
        if soc.startswith(cw_soc[:-1]):
            return row["2018 Census Code"]

    return pd.NA


def main() -> None:
    emp, cw = load_tables()
    emp["census_code"] = emp["OCC_CODE"].apply(lambda c: census_for_soc(cw, c))
    emp.to_csv(OUT_FILE, index=False)
    print(f"\u2713 Wrote {OUT_FILE}")


if __name__ == "__main__":
    main()
