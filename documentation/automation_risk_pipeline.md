# Automation Risk Pipeline

This document explains how the Frey and Osborne automation-risk scores are combined with the national employment totals to produce an automation-risk percentile for each SOC 2018 occupation.

## Inputs
1. `data_tables/national_employment_2024.csv` – national employment counts by 2018 SOC code.
2. `frey_and_osborne18_data/crosswalk_soc2010_to_soc2018.csv` – mapping between 2010 and 2018 SOC codes.
3. `frey_and_osborne18_data/frey_osborne_automation_risk_index_clean.csv` – automation‑risk probabilities indexed by 2010 SOC codes.

## Method
1. Start with the national employment table and append the corresponding 2010 SOC code using the crosswalk. If a 2018 code lacks a mapping, it is kept and flagged in a `missing_soc2010` column. The result is saved as `data_tables/employment_with_soc2010.csv`.
2. Merge that table with the Frey–Osborne automation scores on the 2010 SOC code. The merged table is written to `data_tables/automation_risk_with_employment.csv`.
3. Percentile ranks are computed only for occupations with a probability. Unmatched occupations remain with `NaN` in the percentile column. The final data (retaining the original employment totals) are saved as `data_tables/automation_risk_percentiles.csv`.

## Usage
Run the pipeline with:

```bash
python scripts/automation_risk_pipeline.py
```

The script writes all intermediate and final CSV files to the `data_tables` directory.
