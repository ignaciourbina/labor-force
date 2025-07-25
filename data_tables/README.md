# Data Tables

This directory contains the final CSV tables used by the SOC lookup API and survey workflow described in the project [README](../README.md).
These files are derived from the Current Population Survey (CPS) and other BLS resources. They summarize labor force statistics and provide crosswalks between the 2018 Census occupation codes and the 2018 SOC codes.

## Files

- **cps_occ_labor_force_totals.csv** – Labor‑force totals for each 2018 Census occupation code. Columns:
  - `occ2018` – 2018 Census occupation code.
  - `total_lf` – Total civilian labor force (employed + unemployed) in that occupation.
  - `native` – Native‑born share of the labor force.
  - `foreign` – Foreign‑born (non‑citizen) share of the labor force.

- **soc2018_codes_mergedWith_cps_occ_labor_force_totals.csv** – The full list of detailed 2018 SOC codes with CPS labor‑force totals attached via the Census crosswalk. Rows without CPS data have missing totals.

- **cps_state_labor_force_totals.csv** – State‑level labor‑force totals. Columns:
  - `state_abbr` – Two‑letter USPS abbreviation.
  - `state_name` – Full state name.
  - `total_lf`, `native`, `foreign` – Same definitions as above.

- **csv_crosswalk_census18codes_to_soc18codes.csv** – Crosswalk mapping 2018 Census occupation codes to 2018 SOC codes as published by the Census Bureau. Used by the scripts in `../scripts/` to merge SOC titles into the occupation totals.
- **national_employment_2024.csv** – National employment totals by SOC code from the May 2024 OEWS release.
- **national_employment_2024_with_census.csv** – Same as above with an added `census_code` column indicating the matching four‑digit Census occupation code.
- **employment_summary.md** – Quick summary statistics for the `TOT_EMP` column in the national employment table.

## How These Tables Fit In

The notebooks and scripts in this repository process raw CPS microdata to produce these tables. They are then consumed by the API in `API_database_laborforce/` which returns labor‑force statistics in response to Qualtrics survey requests. Keeping the cleaned tables here allows the API to start quickly without recalculating totals.

