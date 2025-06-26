"""Merge Frey-Osborne automation risk scores with SOC 2018 codes and employment.

This script performs three steps:
1. Join the automation risk table (indexed by SOC 2010) with a
   SOC2010–SOC2018 crosswalk and save ``automation_risk_soc2018.csv``.
2. Merge the result with ``national_employment_2024.csv`` to append ``TOT_EMP``
   and save ``automation_risk_with_employment.csv``.
3. Compute the employment-weighted percentile rank of the automation probability
   and write ``automation_risk_percentiles.csv`` containing the SOC code,
   occupation label, probability, employment count and percentile rank.
"""

from pathlib import Path
import pandas as pd

# ------------------------------------------------------------
# File locations
# ------------------------------------------------------------
ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data_tables"
FREY_DIR = ROOT / "frey_and_osborne18_data"

FREY_FILE = FREY_DIR / "frey_osborne_automation_risk_index_clean.csv"
CROSSWALK_FILE = FREY_DIR / "crosswalk_soc2010_to_soc2018.csv"
EMP_FILE = DATA_DIR / "national_employment_2024.csv"

OUT_SOC2018 = DATA_DIR / "automation_risk_soc2018.csv"
OUT_EMPLOY = DATA_DIR / "automation_risk_with_employment.csv"
OUT_PERCENTILES = DATA_DIR / "automation_risk_percentiles.csv"


def merge_soc2018() -> pd.DataFrame:
    """Attach 2018 SOC codes to the automation risk table."""
    frey = pd.read_csv(FREY_FILE, dtype={"SOC code": str})
    cw = pd.read_csv(
        CROSSWALK_FILE,
        dtype={"2010 SOC Code": str, "2018 SOC Code": str},
    )
    merged = frey.merge(cw, left_on="SOC code", right_on="2010 SOC Code", how="left")
    merged.to_csv(OUT_SOC2018, index=False)
    print(f"\u2713 Wrote {OUT_SOC2018}")
    return merged


def merge_employment(df: pd.DataFrame) -> pd.DataFrame:
    """Append national employment totals."""
    emp = pd.read_csv(EMP_FILE, dtype={"OCC_CODE": str, "TOT_EMP": "Int64"})
    result = df.merge(emp, left_on="2018 SOC Code", right_on="OCC_CODE", how="left")
    result.to_csv(OUT_EMPLOY, index=False)
    print(f"\u2713 Wrote {OUT_EMPLOY}")
    return result


def add_percentile(df: pd.DataFrame) -> pd.DataFrame:
    """Compute employment-weighted percentile ranks."""
    df = df.copy()
    df["TOT_EMP"] = df["TOT_EMP"].fillna(0).astype("Int64")
    df = df.sort_values("Probability").reset_index(drop=True)
    df["cum_emp"] = df["TOT_EMP"].cumsum()
    total_emp = df["TOT_EMP"].sum()
    df["percentile_rank"] = df["cum_emp"] / total_emp * 100
    final = df[[
        "2018 SOC Code",
        "Occupation",
        "Probability",
        "TOT_EMP",
        "percentile_rank",
    ]]
    final.to_csv(OUT_PERCENTILES, index=False)
    print(f"\u2713 Wrote {OUT_PERCENTILES}")
    return final


def main() -> None:
    step1 = merge_soc2018()
    step2 = merge_employment(step1)
    add_percentile(step2)


if __name__ == "__main__":
    main()
