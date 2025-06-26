
"""
soc2018_to_census2018_mapping.py
--------------------------------
Create a one‑to‑one mapping between every *detailed* 2018 SOC code and a 2018
Census occupation code using the official cross‑walk workbook:

    2018-occupation-code-list-and-crosswalk.xlsx   (sheet "2018 Census Occ Code List")

Strategy
--------
1. Load the cross‑walk worksheet.
2. Build a lookup table of (SOC code → Census code) that includes:
   • exact matches (e.g., 13‑2052 → 0850);
   • wildcard rows that contain an X placeholder (e.g., 15‑124X);
   • aggregated codes where the final digit(s) are zero (e.g., 11‑2030).
3. Read the master list of detailed SOC 2018 occupations from
   "soc_2018_definitions (1).xlsx" (header row at index 7).
4. Resolve every detailed SOC code following the hierarchy:
   * exact match,
   * wildcard match,
   * roll‑up (replace one or more trailing digits with 0 until a match is found).
5. Write the resulting mapping to CSV.

The script prints how many SOC codes were mapped and where the file was saved.
"""

from __future__ import annotations

import argparse
import re
from pathlib import Path

import pandas as pd

DEFAULT_CROSSWALK = "2018-occupation-code-list-and-crosswalk.xlsx"
DEFAULT_ANCHOR    = "soc_2018_definitions (1).xlsx"
DEFAULT_OUTPUT    = "soc2018_to_census2018_mapping.csv"

def load_crosswalk(crosswalk_path: str, sheet: str = "2018 Census Occ Code List") -> pd.DataFrame:
    df = pd.read_excel(crosswalk_path, sheet_name=sheet, header=4)
    df.columns = df.columns.str.strip()
    df = df[["2018 Census Code", "2018 SOC Code"]].dropna()
    df["2018 Census Code"] = df["2018 Census Code"].astype(str).str.strip()
    df["2018 SOC Code"]    = df["2018 SOC Code"].astype(str).str.strip()
    return df

def build_lookup(df: pd.DataFrame) -> tuple[dict[str, str], list[tuple[re.Pattern, str]]]:
    """Return a (exact_dict, wildcard_list)."""
    exact = {}
    wildcards = []
    for soc, census in zip(df["2018 SOC Code"], df["2018 Census Code"]):
        if "X" in soc:
            regex = re.compile("^" + soc.replace("X", r"\d") + "$")
            wildcards.append((regex, census))
        else:
            exact[soc] = census
    # sort wildcards by specificity (fewer X means more specific)
    wildcards.sort(key=lambda t: t[0].pattern.count("\d"), reverse=True)
    return exact, wildcards

def resolve_soc(soc: str, exact: dict[str, str], wildcards: list[tuple[re.Pattern, str]]) -> str | None:
    """Return the Census code for a detailed SOC code or None if not found."""
    # 1. exact
    if soc in exact:
        return exact[soc]
    # 2. wildcard
    for regex, census in wildcards:
        if regex.match(soc):
            return census
    # 3. roll‑up: progressively replace trailing digits with 0
    prefix, digits = soc.split("-")
    digits = list(digits)
    for i in range(1, len(digits) + 1):
        rolled = prefix + "-" + "".join(digits[:-i] + ["0"] * i)
        if rolled in exact:
            return exact[rolled]
        # consider wildcard with X in the first replaced digit
        rolled_wild = prefix + "-" + "".join(digits[:-i] + ["X"] + ["0"] * (i - 1))
        for regex, census in wildcards:
            if regex.pattern.startswith("^" + rolled_wild.replace("X", r"\d")):
                return census
    return None

def extract_detailed_soc(anchor_path: str) -> pd.DataFrame:
    df = pd.read_excel(anchor_path, sheet_name=0, header=7)
    df.columns = df.columns.str.strip()
    detailed = df[df["SOC Group"] == "Detailed"][["SOC Code", "SOC Title"]].copy()
    detailed["SOC Code"] = detailed["SOC Code"].astype(str).str.strip()
    return detailed

def build_mapping(
    crosswalk_path: str = DEFAULT_CROSSWALK,
    anchor_path: str = DEFAULT_ANCHOR,
    csv_output: str = DEFAULT_OUTPUT,
) -> pd.DataFrame:
    crosswalk_df = load_crosswalk(crosswalk_path)
    exact, wildcards = build_lookup(crosswalk_df)
    detailed_soc_df = extract_detailed_soc(anchor_path)

    detailed_soc_df["Census_2018_Code"] = detailed_soc_df["SOC Code"].apply(
        lambda x: resolve_soc(x, exact, wildcards)
    )

    unmapped = detailed_soc_df["Census_2018_Code"].isna().sum()
    if unmapped:
        print(f"Warning: {unmapped} SOC codes could not be mapped.")

    detailed_soc_df.rename(columns={"SOC Code": "SOC_2018_Code", "SOC Title": "SOC_Title"}, inplace=True)
    detailed_soc_df.to_csv(csv_output, index=False)
    print(f"Wrote {len(detailed_soc_df)} SOC → Census mappings to '{csv_output}'.")
    return detailed_soc_df

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Build SOC 2018 → Census 2018 occupation-code mapping.")
    parser.add_argument("--crosswalk", default=DEFAULT_CROSSWALK,
                        help="Path to the 2018 occupation crosswalk workbook (default: %(default)s)")
    parser.add_argument("--anchor", default=DEFAULT_ANCHOR,
                        help="Path to the SOC 2018 definitions workbook (default: %(default)s)")
    parser.add_argument("--csv", default=DEFAULT_OUTPUT,
                        help="Output CSV path (default: %(default)s)")
    args = parser.parse_args()
    build_mapping(args.crosswalk, args.anchor, args.csv)
