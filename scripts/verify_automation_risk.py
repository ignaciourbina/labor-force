from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data_tables"
FREY_DIR = ROOT / "frey_and_osborne18_data"
DOC_DIR = ROOT / "docum"
DOC_DIR.mkdir(exist_ok=True)

# Input files
FREY_FILE = FREY_DIR / "frey_osborne_automation_risk_index_clean.csv"
EMP_SOC2010_FILE = DATA_DIR / "employment_with_soc2010.csv"
MERGED_FILE = DATA_DIR / "automation_risk_with_employment.csv"


def run_checks() -> None:
    frey = pd.read_csv(FREY_FILE, dtype={"SOC code": str})
<<<<<<< HEAD
    emp_soc2010 = pd.read_csv(
        EMP_SOC2010_FILE,
        dtype={"OCC_CODE": str, "2010 SOC Code": str, "TOT_EMP": "Int64"},
    )
    national = pd.read_csv(
        DATA_DIR / "national_employment_2024.csv",
        dtype={"OCC_CODE": str, "TOT_EMP": "Int64"},
    )
    merged = pd.read_csv(MERGED_FILE, dtype={"2010 SOC Code": str})

    results = []
    # Check for missing SOC2010 codes and row/EMP totals
    missing_soc2010 = emp_soc2010["2010 SOC Code"].isna().sum()
    row_match = len(emp_soc2010) == len(national)
    emp_match = emp_soc2010["TOT_EMP"].sum() == national["TOT_EMP"].sum()
    results.append(f"Rows without 2010 code: {missing_soc2010}")
    results.append(f"Row count matches original: {row_match}")
    results.append(f"Employment totals match original: {emp_match}")
=======
    emp_soc2010 = pd.read_csv(EMP_SOC2010_FILE, dtype={"OCC_CODE": str, "2010 SOC Code": str})
    merged = pd.read_csv(MERGED_FILE, dtype={"2010 SOC Code": str})

    results = []
    # Check for missing SOC2010 codes
    missing_soc2010 = emp_soc2010["2010 SOC Code"].isna().sum()
    results.append(f"Rows without 2010 code: {missing_soc2010}")
>>>>>>> origin/main

    # Coverage of automation scores
    unmatched = set(emp_soc2010["2010 SOC Code"].dropna()) - set(frey["SOC code"])
    results.append(f"2010 codes missing from automation table: {len(unmatched)}")

<<<<<<< HEAD
    # Missing employment values and probabilities
    missing_emp = merged["TOT_EMP"].isna().sum()
    missing_prob = merged["Probability"].isna().sum()
=======
    # Missing employment values
    missing_emp = merged["TOT_EMP"].isna().sum()
>>>>>>> origin/main
    results.append(f"Rows with missing TOT_EMP: {missing_emp}")
    results.append(f"Rows without Probability: {missing_prob}")

    # Negative employment values (should not happen)
    neg_emp = pd.to_numeric(merged["TOT_EMP"], errors="coerce")
    results.append(f"Negative TOT_EMP values: {(neg_emp < 0).sum()}")

    # Write summary markdown
    summary_file = DOC_DIR / "automation_risk_verification_results.md"
    with summary_file.open("w") as f:
        f.write("# Automation Risk Verification Results\n\n")
        for line in results:
            f.write(f"- {line}\n")
    print(f"\u2713 Wrote {summary_file}")


if __name__ == "__main__":
    run_checks()
