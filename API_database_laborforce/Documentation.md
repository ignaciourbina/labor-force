# API Database Documentation

This directory contains the code and dataset for the SOC lookup API used by the project.

## Contents

- `app.py` – FastAPI application that exposes several endpoints including `/query` and `/automation_family`.
- `data.json` – JSON database containing the SOC records that are loaded by `app.py`.
- `requirements.txt` – Python dependencies for running the API.
- `Dockerfile` – Container instructions to build a minimal image for the API.
- `qualtricsEngine_js_snippets` – Example JavaScript snippets for calling the API from Qualtrics.
- `data_occup_automation_extended.json` – Automation percentile data augmented with two‑digit major codes and synonyms from ONET.
- `scripts/onet_synonyms_json.py` – Converts the scraped ONET CSV to JSON.
- `scripts/extend_automation_data.py` – Generates `data_occup_automation_extended.json`.

## Running the API locally

1. Create a virtual environment and install dependencies from `requirements.txt`.
2. Launch the application with `uvicorn app:app --reload`.
3. Access `http://localhost:8000/query?state=FL&major=15` to fetch entries from `data.json`.

The API indexes `data.json` on startup so queries are fast. Edit `data.json` to update or add new SOC entries.

To retrieve all six‑digit occupations within a two‑digit major SOC group use the `/automation_family` endpoint, for example:

```
http://localhost:8000/automation_family?major=15
```
