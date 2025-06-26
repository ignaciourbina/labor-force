"""Merge automation risk scores with employment totals and compute percentiles.

This version of the pipeline starts with the national employment table indexed by
SOC 2018 codes.  We attach the corresponding SOC 2010 codes, then merge in the
Frey–Osborne automation probabilities (indexed by SOC 2010).  Finally we compute
an employment‑weighted percentile rank of the automation risk.

The script writes three intermediate files:

1. ``employment_with_soc2010.csv`` – national employment totals annotated with
   the matching 2010 SOC code(s).
2. ``automation_risk_with_employment.csv`` – the above table merged with the
   automation risk scores.
3. ``automation_risk_percentiles.csv`` – final table containing the percentile
   rank for each SOC 2018 occupation.
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

OUT_EMP_SOC2010 = DATA_DIR / "employment_with_soc2010.csv"
OUT_MERGED = DATA_DIR / "automation_risk_with_employment.csv"
OUT_PERCENTILES = DATA_DIR / "automation_risk_percentiles.csv"


def attach_soc2010() -> pd.DataFrame:
    """Append SOC 2010 codes to the national employment table."""
    emp = pd.read_csv(EMP_FILE, dtype={"OCC_CODE": str, "TOT_EMP": "Int64"})
    cw = pd.read_csv(
        CROSSWALK_FILE,
        dtype={"2010 SOC Code": str, "2018 SOC Code": str},
    )
    merged = emp.merge(cw, left_on="OCC_CODE", right_on="2018 SOC Code", how="left")
    merged.to_csv(OUT_EMP_SOC2010, index=False)
    print(f"\u2713 Wrote {OUT_EMP_SOC2010}")
    return merged


def merge_frey(df: pd.DataFrame) -> pd.DataFrame:
    """Merge the employment table with Frey–Osborne automation scores."""
    frey = pd.read_csv(FREY_FILE, dtype={"SOC code": str})
    result = df.merge(frey, left_on="2010 SOC Code", right_on="SOC code", how="left")
    result.to_csv(OUT_MERGED, index=False)
    print(f"\u2713 Wrote {OUT_MERGED}")
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
    step1 = attach_soc2010()
    step2 = merge_frey(step1)
    add_percentile(step2)


if __name__ == "__main__":
    main()
