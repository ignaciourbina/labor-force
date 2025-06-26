
"""
extract_detailed_soc_2018.py
----------------------------
Extract the list of “detailed” 2018 SOC occupation codes from the
BLS definition workbook and save them to a CSV.

Usage (from the command line):
    python extract_detailed_soc_2018.py         --excel "soc_2018_definitions (1).xlsx"         --csv soc_2018_detailed_codes.csv
"""

import pandas as pd
import argparse
from pathlib import Path

DEFAULT_EXCEL = "soc_2018_definitions (1).xlsx"
DEFAULT_CSV   = "soc_2018_detailed_codes.csv"

def extract_detailed_soc(excel_path: str = DEFAULT_EXCEL,
                         csv_path: str = DEFAULT_CSV,
                         header_row: int = 7) -> pd.DataFrame:
    """
    Parameters
    ----------
    excel_path : str
        Path to the SOC 2018 definitions workbook.
    csv_path : str
        Where to write the resulting CSV with detailed SOC codes.
    header_row : int, default 7
        Row index (0‑based) where the true header starts in the workbook.
    """
    df = pd.read_excel(excel_path, sheet_name=0, header=header_row)
    df.columns = df.columns.str.strip()
    detailed_df = df[df["SOC Group"] == "Detailed"].copy()
    detailed_df.to_csv(csv_path, index=False)
    print(f"Saved {detailed_df['SOC Code'].nunique()} unique detailed SOC codes to '{csv_path}'.")
    return detailed_df

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Extract detailed SOC 2018 codes to CSV.")
    parser.add_argument("--excel", default=DEFAULT_EXCEL,
                        help="Path to the SOC 2018 definitions workbook (default: %(default)s)")
    parser.add_argument("--csv",   default=DEFAULT_CSV,
                        help="Output CSV path (default: %(default)s)")
    args = parser.parse_args()
    extract_detailed_soc(args.excel, args.csv)
