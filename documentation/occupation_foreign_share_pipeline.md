# Occupation Foreign Share Pipeline

This document explains how the percentage of foreign‑born workers is
computed for each occupation code and its three‑digit SOC aggregate.

## Inputs
1. `data_tables/cps_occ_labor_force_totals_soc2018_xwalk.csv` – CPS
   labor‑force totals with a Census‑to‑SOC crosswalk.

## Method
1. Read the CSV file keeping occupation codes as strings.
2. Drop rows without a valid `2018 SOC Code`.
3. Compute `foreign_pct` as `(foreign / total_lf) * 100`, rounded to two
   decimals.
4. Derive the three‑digit SOC prefix (e.g. `15-1`) from each
   six‑digit code.
5. Aggregate totals by this prefix to obtain `foreign_pct_soc3` for the
   three‑digit group.
6. Save the records to `API_database_laborforce/data_occup_foreign.json`
   with fields:
   `{ "soc": "11-1011", "occ_label": "Chief executives",
     "foreign_pct": 17.1, "soc3": "11-1", "foreign_pct_soc3": 15.95 }`.

## Usage
Run the pipeline with:
```bash
python scripts/occupation_foreign_share.py
```
