# Labor Force Data Integration

This project implements a Qualtrics-based workflow to fetch labor force statistics from a custom API based on survey responses.

## Process Overview

1. **Collect survey data** – Respondents provide their two-digit Standard Occupational Classification (SOC) code and select their state of residence.
2. **Retrieve detailed occupations** – Using custom JavaScript in Qualtrics, the survey sends the two-digit SOC code to an API endpoint, which returns the list of six-digit SOC codes in that major SOC group. The respondent selects the appropriate occupation from this list.
   The new `/automation_family` endpoint can also be queried directly with a two-digit code to obtain the full list of matching occupations along with ONET synonyms.
3. **Fetch labor force data** – The survey makes additional API calls to retrieve the percentage of immigrants in the labor force for the selected occupation and for the respondent's state.
4. **Store in Embedded Data** – The retrieved data are saved to Qualtrics embedded data fields so they can be used later in the survey.

This pipeline allows the survey to display personalized labor force statistics to each respondent based on their occupation and location.

## Repository Contents

 - `API_database_laborforce/` – FastAPI application and JSON datasets powering the SOC lookup service.
- `ONET-Scrapped-Data/` – Raw occupation descriptions used to generate synonyms.
- `data_tables/` – Precomputed CSV tables consumed by the API, including national employment totals.
- `oesem_may24_data/` – Raw BLS employment spreadsheets downloaded May 2024.
- `frey_and_osborne18_data/` – Automation risk scores and crosswalks from Frey and Osborne (2018).
 - `API_database_laborforce/data_occup_consolidated.json` – Combined automation and foreign-share data for each SOC code.
- `documentation/` – Detailed guides for each data-preparation script.
- `run_pipeline.py` – Helper script that executes the pipelines in order.

See [`documentation/README.md`](documentation/README.md) for an index of all
available documentation.

## Running the Data Pipeline

To refresh all JSON datasets for the API, run:

```bash
python run_pipeline.py
```

Each step writes its outputs to `data_tables/` or `API_database_laborforce/`. See the Markdown files in `documentation/` for details on the logic of each stage.
