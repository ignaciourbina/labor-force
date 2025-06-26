from __future__ import annotations

"""Verification checks for the foreign-share pipeline."""

import json
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data_tables"
API_DIR = ROOT / "API_database_laborforce"
DOC_DIR = ROOT / "tests_and_verifications"
DOC_DIR.mkdir(exist_ok=True)

CROSSWALK_FILE = DATA_DIR / "csv_crosswalk_census18codes_to_soc18codes.csv"
TOTALS_FILE = DATA_DIR / "cps_occ_labor_force_totals.csv"
MERGED_FILE = DATA_DIR / "soc2018_codes_mergedWith_cps_occ_labor_force_totals.csv"
BASE_JSON = API_DIR / "data_occup_foreign.json"
EXT_JSON = API_DIR / "data_occup_foreign_extended.json"


def run_checks() -> None:
    results: list[str] = []

    cross = pd.read_csv(CROSSWALK_FILE, dtype=str)
    totals = pd.read_csv(TOTALS_FILE, dtype=str)

    # --------------------------------------------------
    # 1. Validate crosswalk uniqueness and coverage
    # --------------------------------------------------
    dup_census = cross["2018 Census Code"].duplicated().sum()
    results.append(f"Duplicate Census codes: {dup_census}")

    soc_counts = cross["2018 SOC Code"].value_counts()
    dup_soc = soc_counts[soc_counts > 1]
    if len(dup_soc) == 1 and dup_soc.index[0] == "none":
        results.append("Duplicate SOC codes only for 'none'")
    else:
        results.append(f"Duplicate SOC codes: {dup_soc.to_dict()}")

    missing_codes = sorted(set(totals["occ2018"]) - set(cross["2018 Census Code"]))
    if missing_codes:
        results.append(f"Codes missing from crosswalk: {', '.join(missing_codes)}")
    else:
        results.append("Crosswalk covers all occ2018 codes")

    # --------------------------------------------------
    # 2. Check merged CPS table
    # --------------------------------------------------
    merged = pd.read_csv(MERGED_FILE)
    rows_with_soc = merged["2018 SOC Code"].notna().sum()
    results.append(f"Merged table rows: {len(merged)}")
    results.append(f"Rows with SOC code: {rows_with_soc}")

    totals_sum_pre = totals[["foreign", "total_lf"]].astype(float).sum()
    totals_sum_post = merged[["foreign", "total_lf"]].astype(float).sum()
    foreign_match = round(totals_sum_pre.foreign, 2) == round(
        totals_sum_post.foreign, 2
    )
    total_lf_match = round(totals_sum_pre.total_lf, 2) == round(
        totals_sum_post.total_lf, 2
    )
    results.append(f"Foreign sum matches: {foreign_match}")
    results.append(f"Total_lf sum matches: {total_lf_match}")

    # --------------------------------------------------
    # 3. Verify base JSON
    # --------------------------------------------------
    base_rows = json.loads(BASE_JSON.read_text())
    unique_soc = {r["soc"] for r in base_rows}
    results.append(f"JSON rows: {len(base_rows)}")
    results.append(f"Unique soc values: {len(unique_soc)}")

    missing_soc = set(merged["2018 SOC Code"].dropna()) - unique_soc
    results.append(f"SOC codes missing from JSON: {len(missing_soc)}")

    csv_pct = merged[merged["2018 SOC Code"].notna()].copy()
    csv_pct["calc_pct"] = (csv_pct["foreign"] / csv_pct["total_lf"] * 100).round(2)
    json_map = {r["soc"]: r["foreign_pct"] for r in base_rows}
    mismatches = sum(
        abs(json_map[row["2018 SOC Code"]] - row["calc_pct"]) > 0.01
        for _, row in csv_pct.iterrows()
    )
    results.append(f"foreign_pct mismatches: {mismatches}")

    # --------------------------------------------------
    # 4. Verify extended JSON
    # --------------------------------------------------
    ext_rows = json.loads(EXT_JSON.read_text())
    results.append(f"Extended JSON rows: {len(ext_rows)}")
    synonyms_added = sum("synonyms" in r for r in ext_rows)
    results.append(f"Records with synonyms field: {synonyms_added}")
    results.append(f"Extended rows match base: {len(ext_rows) == len(base_rows)}")

    # --------------------------------------------------
    # 5. Wildcard SOC codes consistency
    # --------------------------------------------------
    df = pd.DataFrame(base_rows)
    mismatched_soc3 = df.groupby("soc3")["foreign_pct_soc3"].nunique()
    mismatched_soc3 = mismatched_soc3[mismatched_soc3 > 1]
    results.append(f"SOC3 mismatch groups: {len(mismatched_soc3)}")

    # --------------------------------------------------
    # 6. Write summary
    # --------------------------------------------------
    summary_file = DOC_DIR / "foreign_share_verification_results.md"
    with summary_file.open("w") as f:
        f.write("# Foreign Share Verification Results\n\n")
        for line in results:
            f.write(f"- {line}\n")
    print(f"\u2713 Wrote {summary_file}")


if __name__ == "__main__":
    run_checks()
