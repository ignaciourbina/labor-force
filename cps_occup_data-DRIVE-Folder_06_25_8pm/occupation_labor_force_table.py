"""
occupation_labor_force_table.py — Occupation‑level labor‑force totals
====================================================================
Reads the *wide* CPS table (`results/cps_state_occ_nat_emp_wide.csv`) and
writes `results/cps_occ_labor_force_totals.csv` listing every 2018 SOC
occupation code with:

* **occ2018**  – six‑digit 2018 SOC code (string)
* **total_lf** – total civilian labor force in that occupation
* **native**   – native‑born portion of the labor force
* **foreign**  – foreign‑born, non‑citizen portion of the labor force

No command‑line arguments are required—simply run:
    python occupation_labor_force_table.py
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
out_path  = Path("results/cps_occ_labor_force_totals.csv")

# ---------------------------------------------------------------------------
# Load wide table and build occupation‑level totals
# ---------------------------------------------------------------------------
wide_tbl = pd.read_csv(wide_path)

# Make sure that the occupation codes are zero-padded, 4-character strings.
wide_tbl["occ2018"] = wide_tbl["occ2018"].astype(str).str.zfill(4)

# The wide table should contain these columns; rename defensively if needed.
NATIVITY_COL = 'nativity_flag'

# Compute labor‑force count per record (employed + unemployed).
wide_tbl["lf"] = wide_tbl["EMPLOYED"] + wide_tbl["UNEMPLOYED"]

# Sum across states, split by nativity.
occ_nat = (
    wide_tbl.groupby(["occ2018", NATIVITY_COL], as_index=False)["lf"].sum()
)

# Pivot: native (0) vs foreign (1) into columns.
occ_tbl = (
    occ_nat.pivot(index="occ2018", columns=NATIVITY_COL, values="lf")
    .fillna(0.0)
    .rename(columns={0: "native", 1: "foreign"})
)
occ_tbl["total_lf"] = occ_tbl["native"] + occ_tbl["foreign"]
occ_tbl = (
    occ_tbl[["total_lf", "native", "foreign"]]
    .reset_index()
    .sort_values("total_lf", ascending=False)
)

# ---------------------------------------------------------------------------
# Write output
# ---------------------------------------------------------------------------
out_path.parent.mkdir(parents=True, exist_ok=True)
occ_tbl.to_csv(out_path, index=False)
print(f"✓ Wrote {out_path}")
