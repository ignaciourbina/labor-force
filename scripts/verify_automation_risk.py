from __future__ import annotations

"""Basic sanity checks for the automation risk pipeline."""

from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data_tables"
FREY_DIR = ROOT / "frey_and_osborne18_data"
DOC_DIR = ROOT / "documentation"
DOC_DIR.mkdir(exist_ok=True)

# Input files
FREY_FILE = FREY_DIR / "frey_osborne_automation_risk_index_clean.csv"
EMP_SOC2010_FILE = DATA_DIR / "employment_with_soc2010.csv"
MERGED_FILE = DATA_DIR / "automation_risk_with_employment.csv"


def run_checks() -> None:
    frey = pd.read_csv(FREY_FILE, dtype={"SOC code": str})
    emp_soc2010 = pd.read_csv(
        EMP_SOC2010_FILE,
        dtype={"OCC_CODE": str, "2010 SOC Code": str, "TOT_EMP": "Int64"},
    )
    merged = pd.read_csv(MERGED_FILE, dtype={"2010 SOC Code": str})

    results: list[str] = []
    # Check for missing SOC2010 codes
    missing_soc2010 = emp_soc2010["2010 SOC Code"].isna().sum()
    results.append(f"Rows without 2010 code: {missing_soc2010}")

    # Coverage of automation scores
    unmatched = set(emp_soc2010["2010 SOC Code"].dropna()) - set(frey["SOC code"])
    results.append(f"2010 codes missing from automation table: {len(unmatched)}")

    # Missing employment values and probabilities
    missing_emp = merged["TOT_EMP"].isna().sum()
    missing_prob = merged["Probability"].isna().sum()
    results.append(f"Rows with missing TOT_EMP: {missing_emp}")
    results.append(f"Rows without Probability: {missing_prob}")

    # Negative employment values (should not happen)
    neg_emp = pd.to_numeric(merged["TOT_EMP"], errors="coerce")
    results.append(f"Negative TOT_EMP values: {(neg_emp < 0).sum()}")

    summary_file = DOC_DIR / "automation_risk_verification_results.md"
    with summary_file.open("w") as f:
        f.write("# Automation Risk Verification Results\n\n")
        for line in results:
            f.write(f"- {line}\n")
    print(f"\u2713 Wrote {summary_file}")


if __name__ == "__main__":
    run_checks()
