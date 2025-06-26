# Automation Percentile JSON Pipeline

This script converts the percentile ranks in `data_tables/automation_risk_percentiles.csv`
into a compact JSON file for the API.

## Inputs
1. `data_tables/automation_risk_percentiles.csv` – automation risk percentiles by SOC code.

## Method
1. Read the CSV with pandas.
2. Keep the columns `2018 SOC Code`, `Occupation`, and `percentile_rank`.
3. Drop rows missing any of those fields and remove duplicate SOC codes.
4. Write `API_database_laborforce/data_occup_automation.json` with records of the form:
   `{ "soc": "15-1256", "occupation": "Software Developers", "automation_pctile": 12.34 }`.

## Usage
Run the pipeline with:
```bash
python scripts/automation_percentile_json.py
```

