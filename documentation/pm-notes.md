# Project Pipeline Notes

This document summarizes the data-management workflow for the labor-force project and lists open items for the next version (v2.0).

## 1. Current Pipeline Overview

The survey workflow relies on a custom API that returns labor‑force statistics based on the respondent's selected occupation and state. The key pieces are:

1. **Qualtrics front end** – JavaScript snippets under `API_database_laborforce/qualtricsEngine_js_snippets/` capture the respondent's two‑digit SOC code and fetch the list of matching six‑digit codes. The chosen code is stored in embedded data.
2. **API back end** – `API_database_laborforce/app.py` serves the `/query` and `/foreign_rate` endpoints. It loads `data.json` (occupation records) and `data_state_foreign.json` (state foreign‑born percentages).
3. **Precomputed tables** – CSV files in `data_tables/` provide occupation totals, state totals, national employment counts, and automation-risk percentiles. They are produced by the scripts in `scripts/` and notebooks in the repository.
4. **Automation risk & employment** – `scripts/automation_risk_pipeline.py` merges employment totals with the Frey‑Osborne automation-risk scores, resulting in `automation_risk_percentiles.csv`.
5. **State foreign share** – `scripts/state_foreign_share.py` reads `cps_state_labor_force_totals.csv` and writes `API_database_laborforce/data_state_foreign.json` so the API can return per-state percentages.

### Data Preparation Scripts

- `scripts/cps_data_wrangling.py` – Processes raw CPS microdata into long and wide tables of weighted counts.
- `scripts/occupation_labor_force_table.py` – Aggregates the wide CPS table to occupation-level totals (`cps_occ_labor_force_totals.csv`).
- `scripts/state_labor_force_table.py` – Aggregates to state-level totals (`cps_state_labor_force_totals.csv`).
- `scripts/occtable_merge_soc2018codes.py` – Merges the Census–SOC crosswalk onto the occupation totals.
- `scripts/add_census_to_employment.py` – Adds four‑digit Census codes to the national OEWS employment table.
- `scripts/merge_employment_with_cps.py` – Assigns national employment counts to each occupation in the CPS totals.
- `scripts/verify_automation_risk.py` – Sanity checks for the automation‑risk pipeline.

## 2. Repository Layout

- `API_database_laborforce/` – FastAPI application and JSON datasets used by Qualtrics.
- `data_tables/` – Final CSV tables consumed by the API.
- `frey_and_osborne18_data/` – Source automation‑risk scores and crosswalks.
- `oesem_may24_data/` – Raw OEWS employment spreadsheets.
- `ONET-Scrapped-Data/` – Scrapers and outputs for O*NET occupation descriptions.
- `cps_occup_data-DRIVE-Folder_06_25_8pm/` – Intermediate results from the CPS processing notebooks.

## 3. Open Items for Pipeline v2.0

The following tasks need attention before the next version of the workflow can be released:

1. **Finalize CPS data validation** – `scripts/cps_data_validation.py` is currently empty. Implement checks for missing values, weight totals, and outlier detection.
2. **Integrate O*NET descriptions** – The scraped data in `ONET-Scrapped-Data/` should be cleaned and merged with `data.json` so that the API can provide occupation descriptions.
3. **Automate end-to-end builds** – Create a Makefile or similar orchestration script to run all pipelines (`cps_data_wrangling.py`, `merge_employment_with_cps.py`, `automation_risk_pipeline.py`, `state_foreign_share.py`) with a single command.
4. **Expand API endpoints** – Include automation risk percentiles and foreign-born share in a single `/details` endpoint to reduce client queries.
5. **Improve documentation** – Convert existing notebooks (`CPS_data_table.ipynb`, `validations_checks_BLS_data.ipynb`) into Markdown guides and link them from the main `README.md`.
6. **Continuous verification** – Schedule regular runs of `verify_automation_risk.py` and future validation scripts to catch data issues when source files change.

---

*Updated June 2025*
