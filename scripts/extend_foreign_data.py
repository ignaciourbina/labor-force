"""Add ONET synonyms to the occupation foreign share JSON.

Reads ``API_database_laborforce/data_occup_foreign.json`` and
``ONET-Scrapped-Data/onet_synonyms.json`` and writes a new
``API_database_laborforce/data_occup_foreign_extended.json`` file with
an additional ``synonyms`` field for each occupation record.
"""
from __future__ import annotations

import json
from pathlib import Path

OCC_FILE = Path("API_database_laborforce/data_occup_foreign.json")
SYN_FILE = Path("ONET-Scrapped-Data/onet_synonyms.json")
OUT_FILE = Path("API_database_laborforce/data_occup_foreign_extended.json")


def main() -> None:
    occ_rows = json.loads(OCC_FILE.read_text())
    syn_rows = json.loads(SYN_FILE.read_text()) if SYN_FILE.exists() else []
    syn_map = {r["soc"]: r.get("synonyms", "") for r in syn_rows}

    new_rows = []
    for r in occ_rows:
        soc = r.get("soc", "")
        new_rows.append({
            **r,
            "synonyms": syn_map.get(soc, ""),
        })

    OUT_FILE.write_text(json.dumps(new_rows, indent=2))
    print(f"\u2713 Wrote {OUT_FILE}")


if __name__ == "__main__":
    main()
