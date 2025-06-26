import pandas as pd
from pathlib import Path

# ---------------------------------------------------------------
# 1.  FILE LOCATIONS
# ---------------------------------------------------------------
crosswalk_path = Path(r"F:\Dropbox\PhD SBU\01_Research_Pipeline\coding-projects\server-backend\data_tables/csv_crosswalk_census18codes_to_soc18codes.csv")
totals_path    = Path(r"F:\Dropbox\PhD SBU\01_Research_Pipeline\coding-projects\server-backend\data_tables\cps_occ_labor_force_totals.csv")
out_path       = Path(r"F:\Dropbox\PhD SBU\01_Research_Pipeline\coding-projects\server-backend\data_tables/cps_occ_labor_force_totals_soc2018_xwalk.csv")

# ---------------------------------------------------------------
# 2.  READ  – force both columns to STRING, then zero-pad to 4
# ---------------------------------------------------------------
crosswalk = pd.read_csv(
    crosswalk_path,
    dtype={"2018 Census Code": "string", "2018 SOC Code": "string"},
)

totals = pd.read_csv(
    totals_path,
    dtype={"occ2018": "string"},
)

crosswalk["2018 Census Code"] = crosswalk["2018 Census Code"].str.zfill(4)
totals["occ2018"]             = totals["occ2018"].str.zfill(4)

# ---------------------------------------------------------------
# 3.  ONE-TO-ONE MERGE  (Census-code key)
# ---------------------------------------------------------------
merged = totals.merge(
    crosswalk,
    left_on="occ2018",
    right_on="2018 Census Code",
    how="left",
    validate="1:1",        # ← will raise if either file has duplicates
)

missing = merged["2018 SOC Code"].isna().sum()
if missing == 0:
    f"{missing} occupation codes not found in the cross-walk!"

# ---------------------------------------------------------------
# 3a.  What’s missing?
# ---------------------------------------------------------------
if missing:
    # Which occ2018 codes were *not* found in the cross-walk?
    not_found = set(totals["occ2018"]) - set(crosswalk["2018 Census Code"])
    print(f"⚠  {len(not_found)} codes absent from cross-walk:", ", ".join(sorted(not_found)))

    if not_found:
        # show a few offending rows so you can inspect them
        sample = totals[totals["occ2018"].isin(not_found)].head()
        print("\nSample rows with missing codes:")
        print(sample.to_string(index=False))

# define labels up front
special_map = {
    "-001": {"2018 SOC Code": pd.NA,
             "2018 SOC Title": pd.NA,
             "2018 Census Title": "Occupation not reported"},
    "9840": {"2018 SOC Code": pd.NA,
             "2018 SOC Title": pd.NA,
             "2018 Census Title": "Armed Forces (military)"},
}

'''
| code     | what it really is                                                                                                                                                                         | shows up because…                                                                                                          | typical treatment                                                                                                      |
| -------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------- |
| **-001** | “Not applicable / no occupation reported.”  It’s the placeholder that IPUMS and Census use when a respondent is *in* the labour-force universe but did not give a usable occupation code. | The CPS record passed your filters (aged ≥ 16, in the civilian LF), but the occupation question was blank or inconsistent. | **Drop** (there’s no SOC equivalent; analyses of occupation should exclude it).                                        |
| **9840** | “Armed Forces” catch-all.  Military personnel are counted in the labour force, but their work is outside the civilian SOC structure, so BLS leaves it unmapped.                           | Some service members appear in the CPS, especially in states with large bases.                                             | Either drop *or* relabel to something like “Military (no SOC)”.  Almost everyone lumps it into an “Other / NA” bucket. |

'''

# fill the cross-walk columns for those codes
for code, cols in special_map.items():
    mask = merged["occ2018"] == code
    for col, value in cols.items():
        merged.loc[mask, col] = value

merged.to_csv(out_path, index=False)
print(f"✓ Wrote file with special rows preserved to {out_path}")

# ---------------------------------------------------------------
# 4.  SAVE
# ---------------------------------------------------------------
merged.to_csv(out_path, index=False)
print(f"✓ Merged file written to {out_path}")



