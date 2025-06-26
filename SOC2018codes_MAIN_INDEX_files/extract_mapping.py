
import pandas as pd
import re

def build_soc_to_census_mapping(
    excel_path="2018-occupation-code-list-and-crosswalk.xlsx",
    csv_output_path="2018_soc_to_census_mapping.csv",
    sheet_name="2018 Census Occ Code List",
):
    """
    Extracts the 2018 SOC‑to‑Census occupation code mapping from the specified Excel file
    and writes it to *csv_output_path*.

    Parameters
    ----------
    excel_path : str, default "2018-occupation-code-list-and-crosswalk.xlsx"
        Path to the Excel file that contains the Census occupation code list.
    csv_output_path : str, default "2018_soc_to_census_mapping.csv"
        Where to write the resulting CSV file.
    sheet_name : str, default "2018 Census Occ Code List"
        The sheet in *excel_path* that holds the data.
    """
    df = pd.read_excel(excel_path, sheet_name=sheet_name, header=4)
    df = df.rename(columns=lambda c: c.strip() if isinstance(c, str) else c)
    df = df[df["2018 Census Code"].notna() & df["2018 SOC Code"].notna()]
    df = df[
        ~df["2018 Census Code"].astype(str).str.contains(r"-")
        & ~df["2018 SOC Code"].astype(str).str.contains(r"\s-\s")
    ]
    df = df[df["2018 SOC Code"].astype(str).str.fullmatch(r"\d{2}-\d{4}")]
    df["2018 Census Code"] = df["2018 Census Code"].astype(str).str.zfill(4).str.strip()
    df["2018 SOC Code"] = df["2018 SOC Code"].astype(str).str.strip()
    mapping_df = (
        df[["2018 SOC Code", "2018 Census Code"]]
        .drop_duplicates()
        .rename(
            columns={
                "2018 SOC Code": "2018_SOC_Code",
                "2018 Census Code": "2018_Census_Code",
            }
        )
        .reset_index(drop=True)
    )
    mapping_df.to_csv(csv_output_path, index=False)
    return mapping_df

if __name__ == "__main__":
    build_soc_to_census_mapping()
