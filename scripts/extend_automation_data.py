"""Add major SOC codes and synonyms to the automation percentile JSON.

This script reads ``API_database_laborforce/data_occup_automation.json`` and
``ONET-Scrapped-Data/onet_synonyms.json`` and writes a new
``API_database_laborforce/data_occup_automation_extended.json`` file with the
additional fields ``major`` and ``synonyms`` for each occupation record.
"""
from __future__ import annotations

import json
from pathlib import Path

AUTO_FILE = Path("API_database_laborforce/data_occup_automation.json")
SYN_FILE = Path("ONET-Scrapped-Data/onet_synonyms.json")
OUT_FILE = Path("API_database_laborforce/data_occup_automation_extended.json")


def main() -> None:
    auto_rows = json.loads(AUTO_FILE.read_text())
    syn_rows = json.loads(SYN_FILE.read_text()) if SYN_FILE.exists() else []
    syn_map = {r["soc"]: r.get("synonyms", "") for r in syn_rows}

    new_rows = []
    for r in auto_rows:
        soc = r.get("soc", "")
        major = soc.split("-")[0] if "-" in soc else soc[:2]
        new_rows.append({
            **r,
            "major": major,
            "synonyms": syn_map.get(soc, ""),
        })

    OUT_FILE.write_text(json.dumps(new_rows, indent=2))
    print(f"\u2713 Wrote {OUT_FILE}")


if __name__ == "__main__":
    main()
