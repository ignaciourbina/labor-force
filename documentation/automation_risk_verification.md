# Automation Risk Verification

This document describes the checks performed on the outputs of
`automation_risk_pipeline.py`.

## Checks
1. **SOC2010 codes preserved** – The number of unique SOC 2010
   codes in the original Frey & Osborne file must match the number
   of unique SOC codes after applying the SOC2010→SOC2018 crosswalk.
2. **SOC2018 mapping** – Every row in the crosswalked table should
   contain a valid SOC 2018 code. Missing values indicate that the
   crosswalk does not cover the original occupation.
3. **National employment coverage** – All SOC 2018 codes should
   appear in `national_employment_2024.csv`. Any codes not present
   imply missing employment data. Additionally we check for rows with
   missing or negative employment totals.

Run the verification with:

```bash
python scripts/verify_automation_risk.py
```

The script writes a summary of the results to `docum/automation_risk_verification_results.md`.
