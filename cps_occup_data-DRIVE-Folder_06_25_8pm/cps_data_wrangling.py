"""cps_pipeline.py — Population counts by State × Occupation × Nativity × Employment


====================================================================================
This script builds CPS-style population estimates by
  • State (FIPS)             – GESTFIPS
  • Occupation (2018 SOC, primary job) – PTIO1OCD
  • Foreign-born, not a U.S. citizen   – derived from PRCITSHP
  • Employment status (Employed vs. Unemployed) – PREMPNOT
for civilians age ≥ 16 who are **in** the civilian labor force.

This version is simplified for use in a Google Colab or Jupyter notebook.
Set the file paths in the "Analysis Execution" section at the bottom of the
script, then run the entire script.

Key features
------------
* **Case-insensitive import** – Reads your CSV without assuming upper- or lower-case
  headers; all names are coerced to UPPER-CASE right after ingest, so the script
  works no matter what your extraction software produced.
* **Listwise deletion** before any transformations (on the analysis variable set)
  to avoid weight distortions from missing values.
* Outputs three CSVs: a variable dictionary, a long table, and a wide table.

Dependencies: pandas ≥ 1.5.
"""
import pathlib
import sys
import pandas as pd
import os

# -----------------------------------------------------------------------------
# Configuration
# -----------------------------------------------------------------------------
# These are the raw variable names required from the input CSV.
RAW_COLS = [
    "GESTFIPS", "PRPERTYP", "PRTAGE", "PWCMPWGT", "PWORWGT", "PTIO1OCD",
    "PRCITSHP", "PENATVTY", "PRINUYER", "PEMLR", "PRCIVLF", "PREMPNOT",
]

# This map provides human-readable names for the raw CPS variables.
RENAME_MAP = {
    "GESTFIPS": "state_fips",
    "PRPERTYP": "person_type",
    "PRTAGE": "age",
    "PWCMPWGT": "weight_cmp",
    "PWORWGT": "weight_or",
    "PTIO1OCD": "occ2018",
    "PRCITSHP": "citizenship",
    "PENATVTY": "nativity_country",
    "PRINUYER": "year_of_entry",
    "PEMLR": "mlr_status",
    "PRCIVLF": "in_civ_lf",
    "PREMPNOT": "emp_recode",
}

# This list provides content for the output variable dictionary CSV.
DICTIONARY_ROWS = [
    ("state_fips", "GESTFIPS", "FIPS state code (household geography)"),
    ("person_type", "PRPERTYP", "Person record type (should be 2 for civilians)"),
    ("age", "PRTAGE", "Age in years"),
    ("weight_cmp", "PWCMPWGT", "Composited person weight (4 implied decimals)"),
    ("weight_or", "PWORWGT", "Outgoing-rotation weight (earnings analyses)"),
    ("occ2018", "PTIO1OCD", "Primary job occupation — 2018 SOC cross-walked"),
    ("citizenship", "PRCITSHP", "Citizenship/nativity recode"),
    ("nativity_country", "PENATVTY", "Country of birth (nativity)"),
    ("year_of_entry", "PRINUYER", "Year of entry into the U.S."),
    ("mlr_status", "PEMLR", "Monthly labor-force recode (7 categories)"),
    ("in_civ_lf", "PRCIVLF", "Civilian labor force flag (1=in LF, 2=not in LF)"),
    ("emp_recode", "PREMPNOT", "Employed/Unemployed/NILF recode"),
]

# These are the variables used in the final analysis. Any record with a missing
# value in one of these columns will be dropped (listwise deletion).
ANALYSIS_VARS = [
    "state_fips", "occ2018", "age", "citizenship", "emp_recode",
    "in_civ_lf", "weight_cmp",
]

# -----------------------------------------------------------------------------
# Helper functions
# -----------------------------------------------------------------------------

def read_cps(path: pathlib.Path) -> pd.DataFrame:
    """Read CPS CSV and force all column names to upper-case."""
    print("→ Reading CPS extract…", file=sys.stderr)
    try:
        df = pd.read_csv(path, low_memory=False)
    except FileNotFoundError:
        print(f"Error: Input file not found at {path}", file=sys.stderr)
        # In a notebook, it's better to raise an error than to exit.
        raise
        
    # Standardise header case to prevent case sensitivity issues.
    df.columns = df.columns.str.upper()
    print(f"  Loaded {len(df):,} rows × {df.shape[1]} cols", file=sys.stderr)
    # Check that all required columns are present in the dataframe.
    missing = sorted(set(RAW_COLS) - set(df.columns))
    if missing:
        raise KeyError(
            f"Input file lacks required column(s): {', '.join(missing)}.\n"
            "Ensure your extract includes those variables."
        )
    # Subset to only the raw variables needed for the pipeline.
    return df[RAW_COLS].copy()


def rename_vars(df: pd.DataFrame) -> pd.DataFrame:
    """Rename raw CPS variables to short, human-readable names."""
    return df.rename(columns=RENAME_MAP)


def write_dictionary(outdir: pathlib.Path):
    """Save variable dictionary as a CSV file."""
    outdir.mkdir(parents=True, exist_ok=True)
    dict_df = pd.DataFrame(DICTIONARY_ROWS, columns=["name", "source", "description"])
    dict_path = outdir / "variable_dictionary.csv"
    dict_df.to_csv(dict_path, index=False)
    print(f"✓ Wrote {dict_path}")


def derive_flags(df: pd.DataFrame) -> pd.DataFrame:
    """Add analysis flags and recodes based on existing variables."""
    # Foreign-born & not a U.S. citizen: PRCITSHP code '5' only.
    df["non_cit_foreign"] = (df["citizenship"].astype(str).str.strip() == "5").astype(int)
    # Employment status 1/0 via PREMPNOT.
    df["emp_status"] = df["emp_recode"].astype(str).str.strip().map({"1": "EMPLOYED", "2": "UNEMPLOYED"})
    return df


def listwise_delete(df: pd.DataFrame, cols: list[str]) -> pd.DataFrame:
    """Drop any record with a missing value in *any* of the given columns."""
    before = len(df)
    df2 = df.dropna(subset=cols)
    after = len(df2)
    if (before - after) > 0:
        print(f"→ Listwise deletion: dropped {before - after:,} rows with missing values", file=sys.stderr)
    return df2


def filter_to_universe(df: pd.DataFrame) -> pd.DataFrame:
    """Keep only civilians aged 16+ who are in the civilian labor force."""
    # The universe is defined by age and civilian labor force status (PRCIVLF == 1).
    mask = (df["age"] >= 16) & (df["in_civ_lf"].astype(str).str.strip() == "1")
    filtered = df[mask].copy()
    print(f"→ Subset to civilians 16+ in LF: {len(filtered):,} rows remain", file=sys.stderr)
    return filtered


def get_weighted_counts(df: pd.DataFrame) -> pd.DataFrame:
    """Collapse to weighted counts by state × occupation × citizenship × employment."""
    # PWCMPWGT has 4 implied decimal places, so we divide by 10,000.
    df["weight"] = df["weight_cmp"] / 1e4
    group_cols = ["state_fips", "occ2018", "non_cit_foreign", "emp_status"]
    
    # Group by the analysis dimensions and sum the person weights.
    grp = df.groupby(group_cols, dropna=False)
    out = grp["weight"].sum().reset_index(name="population")
    print("→ Collapsed to weighted counts", file=sys.stderr)
    return out


def pivot_wide(df: pd.DataFrame) -> pd.DataFrame:
    """Convert long EMPLOYED/UNEMPLOYED rows into wide columns."""
    wide = df.pivot_table(
        index=["state_fips", "occ2018", "non_cit_foreign"],
        columns="emp_status",
        values="population",
        fill_value=0,
    ).reset_index()
    wide.columns.name = None
    return wide

# -----------------------------------------------------------------------------
# Analysis Execution
# -----------------------------------------------------------------------------
# TODO: Set your file paths here
# -----------------------------------------------------------------------------
# Path to your input CPS CSV file.
# For Colab, you might upload this or access it from Google Drive.
# Example: cps_csv_path = pathlib.Path('/content/cps_data.csv')
os.chdir(r'F:\Dropbox\PhD SBU\01_Research_Pipeline\coding-projects\us-occupations')
cps_csv_path = pathlib.Path(r"Data-Sources\cps_microdata_may2025\basic_cps.csv")

# Path to the directory where you want to save the output files.
# Example: output_dir = pathlib.Path('/content/results/')
output_dir = pathlib.Path("Results/")
# -----------------------------------------------------------------------------

# Create the output directory if it doesn't exist.
output_dir.mkdir(parents=True, exist_ok=True)

# --- Run the pipeline by calling the functions in order ---
df_raw = read_cps(cps_csv_path)
df_renamed = rename_vars(df_raw)

# Save variable dictionary (once per run).
write_dictionary(output_dir)

# Listwise deletion on analysis variables (before LF filters).
df_clean = listwise_delete(df_renamed, ANALYSIS_VARS)

# Derive flags & subset to the analysis universe.
df_derived = derive_flags(df_clean)
df_lf = filter_to_universe(df_derived)

# Collapse to a long table of weighted counts.
long_tbl = get_weighted_counts(df_lf)
long_path = output_dir / "cps_state_occ_nat_emp_long.csv"
long_tbl.to_csv(long_path, index=False)
print(f"✓ Wrote {long_path}")

# Pivot the long table into a wide format.
wide_tbl = pivot_wide(long_tbl)
wide_path = output_dir / "cps_state_occ_nat_emp_wide.csv"
wide_tbl.to_csv(wide_path, index=False)
print(f"✓ Wrote {wide_path}")

print("\nPipeline finished successfully.", file=sys.stderr)

