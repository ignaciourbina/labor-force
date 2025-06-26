from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data_tables"
FREY_DIR = ROOT / "frey_and_osborne18_data"
DOC_DIR = ROOT / "docum"
DOC_DIR.mkdir(exist_ok=True)

# Input files
FREY_FILE = FREY_DIR / "frey_osborne_automation_risk_index_clean.csv"
SOC2018_FILE = DATA_DIR / "automation_risk_soc2018.csv"
EMPLOY_FILE = DATA_DIR / "automation_risk_with_employment.csv"
NATIONAL_FILE = DATA_DIR / "national_employment_2024.csv"


def run_checks() -> None:
    frey = pd.read_csv(FREY_FILE, dtype={"SOC code": str})
    soc2018 = pd.read_csv(SOC2018_FILE, dtype={"SOC code": str, "2018 SOC Code": str})
    employ = pd.read_csv(EMPLOY_FILE, dtype={"2018 SOC Code": str})
    national = pd.read_csv(NATIONAL_FILE, dtype={"OCC_CODE": str})

    results = []
    # Check unique SOC2010 codes preserved
    orig_unique = frey["SOC code"].nunique()
    merged_unique = soc2018["SOC code"].nunique()
    results.append(f"Original unique SOC2010 codes: {orig_unique}")
    results.append(f"Unique SOC2010 codes after crosswalk: {merged_unique}")
    results.append(f"Count preserved: {orig_unique == merged_unique}")

    # Check for missing SOC2018 codes
    missing_2018 = soc2018["2018 SOC Code"].isna().sum()
    results.append(f"Rows without 2018 code: {missing_2018}")

    # Cross-check 2018 codes with national employment table
    unmatched = set(soc2018["2018 SOC Code"].dropna()) - set(national["OCC_CODE"])
    results.append(f"2018 codes missing from national employment table: {len(unmatched)}")

    # Missing employment values
    missing_emp = employ["TOT_EMP"].isna().sum()
    results.append(f"Rows with missing TOT_EMP: {missing_emp}")

    # Negative employment values (should not happen)
    neg_emp = pd.to_numeric(employ["TOT_EMP"], errors="coerce")
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
