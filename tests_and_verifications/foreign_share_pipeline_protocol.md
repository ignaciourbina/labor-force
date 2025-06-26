# Foreign Share Verification Protocol

This document outlines the recommended checks to ensure that the table
`data_tables/cps_occ_labor_force_totals.csv` is faithfully
translated into the API file `API_database_laborforce/data_occup_foreign_extended.json`.
The goal is to confirm that no occupations are dropped and that the
foreign‑born labor‑force percentages remain accurate throughout the
pipeline.

## 1. Validate the Census→SOC Crosswalk

1. **Unique mapping** – Load `data_tables/csv_crosswalk_census18codes_to_soc18codes.csv`
   and verify that each `2018 Census Code` appears exactly once. The only
   duplicate `2018 SOC Code` should be the special row labelled `none`.
2. **Coverage** – Confirm that every `occ2018` value from
   `cps_occ_labor_force_totals.csv` is present in the crosswalk.

Example Python snippet:
```python
import pandas as pd
cross = pd.read_csv("data_tables/csv_crosswalk_census18codes_to_soc18codes.csv")
totals = pd.read_csv("data_tables/cps_occ_labor_force_totals.csv")
assert totals['occ2018'].isin(cross['2018 Census Code']).all()
```

## 2. Check the Merged CPS Table

Run `scripts/occtable_merge_soc2018codes.py` (or inspect the existing
file) and confirm:

- Row count remains 523 (matching the original CPS totals).
- Exactly 521 rows contain a valid `2018 SOC Code`; the remaining two
  correspond to "Occupation not reported" and "Armed Forces".
- Summing `foreign` and `total_lf` columns before and after the merge
  yields the same totals.

```python
merged = pd.read_csv("data_tables/cps_occ_labor_force_totals_soc2018_xwalk.csv")
assert len(merged) == 523
assert merged['foreign'].sum().round(2) == totals['foreign'].sum().round(2)
```

## 3. Verify `data_occup_foreign.json`

Execute `python scripts/occupation_foreign_share.py` and ensure that:

1. The script prints a confirmation message and writes exactly 521
   records.
2. Every `soc` value is unique and matches one of the codes from the
   merged CPS table.
3. Recomputing `foreign_pct` from the CSV totals reproduces the values in
   the JSON (within rounding).

## 4. Verify the Extended JSON

Run `python scripts/extend_foreign_data.py` and check that:

- The extended file has the same number of rows as the base JSON.
- All occupation fields are preserved and a `synonyms` field is added.

```python
import json
base = json.load(open("API_database_laborforce/data_occup_foreign.json"))
ext  = json.load(open("API_database_laborforce/data_occup_foreign_extended.json"))
assert len(base) == len(ext)
```

## 5. Spot‑Check Wildcard SOC Codes

Wildcard SOC codes in the crosswalk (codes ending in `X`) should map to
multiple full SOC codes. Use the three‑digit `soc3` field to verify that
aggregated percentages are consistent across matching occupations.

Example:
```python
rows = [r for r in base if r['soc'].startswith('51-20')]
values = {r['soc']: r['foreign_pct'] for r in rows}
print(values)
```
Confirm that all codes sharing the same `soc3` prefix have the same
`foreign_pct_soc3` value.

## 6. Document the Results

Record the outcome of these checks in a short Markdown summary under
`tests_and_verifications/` whenever the pipeline is run. This provides a
history of successful validations.

