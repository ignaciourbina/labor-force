"""Merge national employment counts onto CPS occupation totals.

This script assigns TOT_EMP from the May 2024 OEWS release to
the CPS occupation totals table. Some rows in the CPS table use
SOC codes with trailing "X" placeholders (e.g. ``51-20XX``) to
group multiple six-digit occupations under a single Census code.
Those rows receive the sum of all matching SOC codes from the
national employment table.
"""
import pandas as pd
import re
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parents[1] / "data_tables"
OEWS_FILE = DATA_DIR / "national_employment_2024.csv"
CPS_FILE = DATA_DIR / "cps_occ_labor_force_totals_soc2018_xwalk.csv"
OUT_FILE = DATA_DIR / "cps_occ_labor_force_with_employment.csv"


def load_data():
    """Read the two input CSVs with codes preserved as strings."""
    oews = pd.read_csv(OEWS_FILE, dtype={"OCC_CODE": str})
    cps = pd.read_csv(CPS_FILE, dtype={"2018 SOC Code": str})
    oews["OCC_CODE"] = oews["OCC_CODE"].str.strip()
    cps["2018 SOC Code"] = cps["2018 SOC Code"].str.strip()
    return oews, cps


def employment_for_pattern(oews: pd.DataFrame, pattern: str):
    """Return TOT_EMP for a specific or wildcard SOC code."""
    if not pattern or str(pattern).lower() == "nan":
        return pd.NA

    pattern = str(pattern)

    # direct lookup first
    exact = oews[oews["OCC_CODE"] == pattern]
    if not exact.empty:
        return exact["TOT_EMP"].iloc[0]

    # remove any trailing X placeholders
    prefix = re.sub(r"X+$", "", pattern)
    if prefix != pattern:
        return oews[oews["OCC_CODE"].str.startswith(prefix)]["TOT_EMP"].sum()

    # handle 5-digit SOC group codes that end in zero
    if pattern.endswith("0"):
        return oews[oews["OCC_CODE"].str.startswith(pattern[:-1])]["TOT_EMP"].sum()

    return pd.NA


def main() -> None:
    oews, cps = load_data()
    cps["TOT_EMP"] = cps["2018 SOC Code"].apply(lambda c: employment_for_pattern(oews, c))
    cps.to_csv(OUT_FILE, index=False)
    print(f"\u2713 Merged file written to {OUT_FILE}")


if __name__ == "__main__":
    main()
