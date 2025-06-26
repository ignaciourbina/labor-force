# Merging National Employment Counts with CPS Totals

This document outlines how national employment totals from the May 2024 OEWS release are combined with the CPS occupation totals.

## Inputs
1. `data_tables/national_employment_2024.csv` – employment counts by six‑digit SOC code. This file is generated from the OEWS Excel release if it does not already exist.
2. `data_tables/cps_occ_labor_force_totals_soc2018_xwalk.csv` – CPS labor‑force totals with a Census‑to‑SOC crosswalk.
3. `data_tables/csv_crosswalk_census18codes_to_soc18codes.csv` – Mapping from 2018 SOC codes (including wildcard values) to 2018 Census occupation codes.

The CPS file contains about 500 rows because several SOC codes are collapsed under a single Census occupation code. Wildcard values such as `51-20XX` or `51-4XXX` denote that all six‑digit SOC codes sharing that prefix belong to the same Census occupation.

## Method
1. Extract the national employment totals from `all_data_M_2024.xlsx` if the intermediate CSV does not exist.
2. Load both tables with occupation codes kept as strings.
3. For each `2018 SOC Code` in the CPS table:
   - When the code is a full six digits (e.g. `11-1011`), look up the exact match in the employment table.
   - When the code ends in `X` characters, remove the trailing `X`s and sum employment for all codes in the national table starting with that prefix.
4. Append the resulting `TOT_EMP` figure to the CPS row.
5. Save the merged table to `data_tables/cps_occ_labor_force_with_employment.csv`.

## Adding Census Codes to the Employment Table

For convenience the national employment table is also annotated with the
corresponding four‑digit Census occupation code for each six‑digit SOC code.
The crosswalk contains wildcard values like `15-124X` or group codes such as
`13-2070`. These are treated as prefixes when matching the SOC codes from the
employment file. The script does **not** aggregate rows—it simply appends a
`census_code` column.

Run the following command to generate
`data_tables/national_employment_2024_with_census.csv`:

```bash
python scripts/add_census_to_employment.py
```

## Reproducibility
Execute the pipeline with:

```bash
python scripts/merge_employment_with_cps.py
```

The script will write the merged table into the `data_tables` directory.
