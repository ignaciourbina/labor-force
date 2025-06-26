"""Merge full SOC 2018 list with CPS occupation totals.

This script reads the master mapping of detailed 2018 SOC codes to 2018
Census occupation codes and attaches the CPS labor‑force totals for each
Census code. The resulting table contains one row for every six‑digit
SOC code (~800 codes).

The output is written to ``data_tables/soc2018_codes_mergedWith_cps_occ_labor_force_totals.csv``.
"""
from __future__ import annotations

import pandas as pd
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data_tables"
MAP_FILE = ROOT / "SOC2018codes_MAIN_INDEX_files" / "soc2018_to_census2018_mapping (1).csv"
CPS_TOTALS = DATA_DIR / "cps_occ_labor_force_totals.csv"
CROSSWALK = DATA_DIR / "csv_crosswalk_census18codes_to_soc18codes.csv"
OUT_FILE = DATA_DIR / "soc2018_codes_mergedWith_cps_occ_labor_force_totals.csv"


def main() -> None:
    mapping = pd.read_csv(MAP_FILE, dtype=str)
    cps = pd.read_csv(CPS_TOTALS, dtype=str)
    cross = pd.read_csv(CROSSWALK, dtype=str)

    mapping["Census_2018_Code"] = mapping["Census_2018_Code"].str.zfill(4)
    cps["occ2018"] = cps["occ2018"].str.zfill(4)
    cross["2018 Census Code"] = cross["2018 Census Code"].str.zfill(4)

    merged = mapping.merge(cps, left_on="Census_2018_Code", right_on="occ2018", how="left")
    merged = merged.merge(
        cross[["2018 Census Code", "2018 Census Title "]],
        left_on="Census_2018_Code",
        right_on="2018 Census Code",
        how="left",
    )
    merged = merged.drop(columns=["2018 Census Code"])

    merged = merged.rename(
        columns={
            "SOC_2018_Code": "2018 SOC Code",
            "SOC_Title": "2018 SOC Title",
            "Census_2018_Code": "2018 Census Code",
            "2018 Census Title ": "2018 Census Title ",
        }
    )[
        [
            "2018 SOC Code",
            "2018 SOC Title",
            "2018 Census Code",
            "2018 Census Title ",
            "occ2018",
            "total_lf",
            "native",
            "foreign",
        ]
    ]

    merged.to_csv(OUT_FILE, index=False)
    print(f"\u2713 Wrote {OUT_FILE}")


if __name__ == "__main__":
    main()
