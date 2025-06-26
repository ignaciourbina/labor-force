# Automation Risk Verification

This document describes the checks performed on the outputs of
`automation_risk_pipeline.py`.

## Checks
1. **Crosswalk coverage** – The number of rows and the total employment in
   `employment_with_soc2010.csv` must match `national_employment_2024.csv`.
   The file also flags any occupations missing a SOC 2010 code.
2. **Automation score coverage** – All SOC 2010 codes used in that file should
   appear in `frey_osborne_automation_risk_index_clean.csv`.
3. **Data quality** – The merged table `automation_risk_with_employment.csv`
   retains the original employment totals and reports how many occupations lack
   an automation probability.

Run the verification with:

```bash
python scripts/verify_automation_risk.py
```

The script writes a summary of the results to `docum/automation_risk_verification_results.md`.
