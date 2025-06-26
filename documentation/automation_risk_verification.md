# Automation Risk Verification

This document describes the checks performed on the outputs of
`automation_risk_pipeline.py`.

## Checks
1. **Crosswalk coverage** – Every row in `employment_with_soc2010.csv`
   should have a matching 2010 SOC code. Missing values indicate that the
   crosswalk does not cover the employment table entry.
2. **Automation score coverage** – All 2010 SOC codes in the employment table
   must appear in `frey_osborne_automation_risk_index_clean.csv`.
3. **National employment data** – The merged table
   `automation_risk_with_employment.csv` should contain no missing or
   negative values in the `TOT_EMP` column.

Run the verification with:

```bash
python scripts/verify_automation_risk.py
```

The script writes a summary of the results to `docum/automation_risk_verification_results.md`.
