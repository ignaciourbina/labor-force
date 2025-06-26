"""
state_labor_force_table.py — State‑level labor‑force totals with labels
======================================================================
Reads the *wide* CPS table (`results/cps_state_occ_nat_emp_wide.csv`) and
writes `results/cps_state_labor_force_totals.csv` with five columns:

* **state_abbr** – two‑letter USPS abbreviation
* **state_name** – full official state name
* **total_lf**   – total civilian labor force (employed + unemployed)
* **native**     – native‑born share of the labor force
* **foreign**    – foreign‑born (non‑citizen) share

Just run the file directly—no command‑line arguments:
    python state_labor_force_table.py
"""

from __future__ import annotations

import pandas as pd
from pathlib import Path
import os

# ---------------------------------------------------------------------------
# File locations
# ---------------------------------------------------------------------------
os.chdir(r'/content/drive/MyDrive/cps_occup_data')
wide_path = Path("results/cps_state_occ_nat_emp_wide.csv")
out_path  = Path("results/cps_state_labor_force_totals.csv")

# ---------------------------------------------------------------------------
# FIPS → (abbreviation, full name) lookup (2‑digit, zero‑padded keys)
# ---------------------------------------------------------------------------
STATE_INFO: dict[str, tuple[str, str]] = {
    "01": ("AL", "Alabama"),         "02": ("AK", "Alaska"),          "04": ("AZ", "Arizona"),
    "05": ("AR", "Arkansas"),        "06": ("CA", "California"),      "08": ("CO", "Colorado"),
    "09": ("CT", "Connecticut"),     "10": ("DE", "Delaware"),        "11": ("DC", "District of Columbia"),
    "12": ("FL", "Florida"),         "13": ("GA", "Georgia"),          "15": ("HI", "Hawaii"),
    "16": ("ID", "Idaho"),           "17": ("IL", "Illinois"),        "18": ("IN", "Indiana"),
    "19": ("IA", "Iowa"),            "20": ("KS", "Kansas"),          "21": ("KY", "Kentucky"),
    "22": ("LA", "Louisiana"),       "23": ("ME", "Maine"),           "24": ("MD", "Maryland"),
    "25": ("MA", "Massachusetts"),   "26": ("MI", "Michigan"),        "27": ("MN", "Minnesota"),
    "28": ("MS", "Mississippi"),     "29": ("MO", "Missouri"),        "30": ("MT", "Montana"),
    "31": ("NE", "Nebraska"),        "32": ("NV", "Nevada"),          "33": ("NH", "New Hampshire"),
    "34": ("NJ", "New Jersey"),      "35": ("NM", "New Mexico"),       "36": ("NY", "New York"),
    "37": ("NC", "North Carolina"),  "38": ("ND", "North Dakota"),    "39": ("OH", "Ohio"),
    "40": ("OK", "Oklahoma"),        "41": ("OR", "Oregon"),          "42": ("PA", "Pennsylvania"),
    "44": ("RI", "Rhode Island"),    "45": ("SC", "South Carolina"),  "46": ("SD", "South Dakota"),
    "47": ("TN", "Tennessee"),       "48": ("TX", "Texas"),           "49": ("UT", "Utah"),
    "50": ("VT", "Vermont"),        "51": ("VA", "Virginia"),        "53": ("WA", "Washington"),
    "54": ("WV", "West Virginia"),   "55": ("WI", "Wisconsin"),       "56": ("WY", "Wyoming"),
}

# ---------------------------------------------------------------------------
# Load wide table and build state‑level totals
# ---------------------------------------------------------------------------
wide_tbl = pd.read_csv(wide_path)

# Compute labor‑force count per record (employed + unemployed).
wide_tbl["lf"] = wide_tbl["EMPLOYED"] + wide_tbl["UNEMPLOYED"]

# Make sure that the occupation codes are zero-padded, 4-character strings.
wide_tbl["occ2018"] = wide_tbl["occ2018"].astype(str).str.zfill(4)

# Sum across occupations, split by nativity flag.
state_nat = (
    wide_tbl.groupby(["state_fips", "nativity_flag"], as_index=False)["lf"].sum()
)

# Pivot: native (0) vs foreign (1) into columns.
state_tbl = (
    state_nat.pivot(index="state_fips", columns="nativity_flag", values="lf")
    .fillna(0.0)
    .rename(columns={0: "native", 1: "foreign"})
)
state_tbl["total_lf"] = state_tbl["native"] + state_tbl["foreign"]
state_tbl = state_tbl[["total_lf", "native", "foreign"]].reset_index()

# ---------------------------------------------------------------------------
# Attach state abbreviation & full‑name labels
# ---------------------------------------------------------------------------
state_tbl["state_abbr"] = (
    state_tbl["state_fips"].astype(str).str.zfill(2).map(lambda k: STATE_INFO[k][0])
)
state_tbl["state_name"] = (
    state_tbl["state_fips"].astype(str).str.zfill(2).map(lambda k: STATE_INFO[k][1])
)

# Move label columns to front and sort rows by full state name.
state_tbl = state_tbl[["state_abbr", "state_name", "total_lf", "native", "foreign"]]
state_tbl = state_tbl.sort_values("state_name")

# ---------------------------------------------------------------------------
# Write output
# ---------------------------------------------------------------------------
out_path.parent.mkdir(parents=True, exist_ok=True)
state_tbl.to_csv(out_path, index=False)
print(f"✓ Wrote {out_path}")

