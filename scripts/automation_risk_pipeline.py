"""Merge automation risk scores with employment totals and compute percentiles.

This pipeline attaches SOC 2010 codes to the national employment table,
merges the Frey–Osborne automation probabilities, and calculates an
employment‑weighted percentile rank of the automation risk.

The script writes three intermediate files:
1. ``employment_with_soc2010.csv`` – national employment totals annotated
   with the matching 2010 SOC code.
2. ``automation_risk_with_employment.csv`` – the above table merged with the
   automation risk scores.
3. ``automation_risk_percentiles.csv`` – final table containing the
   percentile rank for each SOC 2018 occupation.
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

    emp = pd.read_csv(
        EMP_FILE,
        dtype={"OCC_CODE": str, "OCC_TITLE": str, "TOT_EMP": "Int64"},
    )
    cw = pd.read_csv(
        CROSSWALK_FILE,
        dtype={"2010 SOC Code": str, "2018 SOC Code": str},
    )
    # The crosswalk is designed so that every 2018 code maps to exactly one
    # 2010 code. In case of accidental duplicates we keep the first occurrence.
    cw_unique = cw.drop_duplicates(subset="2018 SOC Code")

    merged = emp.merge(
        cw_unique,
        left_on="OCC_CODE",
        right_on="2018 SOC Code",
        how="left",
    )

    # Flag rows lacking a 2010 mapping but keep them for auditing
    merged["missing_soc2010"] = merged["2010 SOC Code"].isna()
    merged.to_csv(OUT_EMP_SOC2010, index=False)
    print(f"\u2713 Wrote {OUT_EMP_SOC2010}")
    return merged


def merge_frey(df: pd.DataFrame) -> pd.DataFrame:
    """Merge the employment table with Frey–Osborne automation scores."""

    frey = pd.read_csv(FREY_FILE, dtype={"SOC code": str})

    merged = df.merge(
        frey,
        left_on="2010 SOC Code",
        right_on="SOC code",
        how="left",
    )

    merged.to_csv(OUT_MERGED, index=False)
    print(f"\u2713 Wrote {OUT_MERGED}")
    return merged


def add_percentile(df: pd.DataFrame) -> pd.DataFrame:
    """Compute employment-weighted percentile ranks.

    Percentiles are calculated only for rows that have a probability
    value. Unmatched occupations are kept with ``NaN`` percentiles."""

    df = df.copy()

    df["TOT_EMP"] = df["TOT_EMP"].fillna(0).astype("Int64")

    prob_df = df.dropna(subset=["Probability"]).sort_values("Probability")
    prob_df["cum_emp"] = prob_df["TOT_EMP"].cumsum()
    total_emp = prob_df["TOT_EMP"].sum()
    prob_df["percentile_rank"] = prob_df["cum_emp"] / total_emp * 100

    df = df.merge(
        prob_df[["OCC_CODE", "percentile_rank"]],
        on="OCC_CODE",
        how="left",
    )

    final = df[
        [
            "OCC_CODE",
            "OCC_TITLE",
            "2010 SOC Code",
            "2010 SOC Title",
            "Probability",
            "TOT_EMP",
            "percentile_rank",
            "missing_soc2010",
        ]
    ]
    final.to_csv(OUT_PERCENTILES, index=False)
    print(f"\u2713 Wrote {OUT_PERCENTILES}")
    return final


def main() -> None:
    step1 = attach_soc2010()
    step2 = merge_frey(step1)
    add_percentile(step2)


if __name__ == "__main__":
    main()
