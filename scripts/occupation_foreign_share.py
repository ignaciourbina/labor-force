from __future__ import annotations
"""Build foreign-born labor-force percentages by occupation.

Reads ``data_tables/soc2018_codes_mergedWith_cps_occ_labor_force_totals.csv`` and
writes ``API_database_laborforce/data_occup_foreign.json`` with records like::
    {
        "soc": "11-1011",
        "occ_label": "Chief executives",
        "foreign_pct": 17.1,
        "soc3": "11-1",
        "foreign_pct_soc3": 15.95,
        "major": "11",
    }
"""

import json
from pathlib import Path

import pandas as pd

DATA_FILE = Path(
    "data_tables/soc2018_codes_mergedWith_cps_occ_labor_force_totals.csv"
)
OUT_FILE = Path("API_database_laborforce/data_occup_foreign.json")


def soc3(code: str) -> str:
    """Return the 3-digit SOC prefix for ``code``.

    Examples
    --------
    >>> soc3("15-1252")
    '15-1'
    >>> soc3("41-2010")
    '41-2'
    """
    if "-" in code:
        major, minor = code.split("-", 1)
        return f"{major}-{minor[0]}"
    return code[:3]


def main() -> None:
    df = pd.read_csv(DATA_FILE)

    # Drop rows without a SOC code (e.g. "Occupation not reported").
    df = df[df["2018 SOC Code"].notna()].copy()

    df["occ_label"] = df["2018 SOC Title"].str.strip()
    df["foreign_pct"] = (df["foreign"] / df["total_lf"] * 100).round(2)
    df["soc3"] = df["2018 SOC Code"].astype(str).apply(soc3)
    df["major"] = df["2018 SOC Code"].astype(str).str.split("-").str[0]

    grp = df.groupby("soc3").agg({"foreign": "sum", "total_lf": "sum"})
    grp["foreign_pct_soc3"] = (grp["foreign"] / grp["total_lf"] * 100).round(2)

    df = df.merge(grp["foreign_pct_soc3"], on="soc3", how="left")

    rows = df[
        [
            "2018 SOC Code",
            "occ_label",
            "foreign_pct",
            "soc3",
            "foreign_pct_soc3",
            "major",
        ]
    ].rename(columns={"2018 SOC Code": "soc"})

    OUT_FILE.write_text(json.dumps(rows.to_dict(orient="records"), indent=2))
    print(f"\u2713 Wrote {OUT_FILE}")


if __name__ == "__main__":
    main()
