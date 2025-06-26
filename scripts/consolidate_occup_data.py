from __future__ import annotations
"""Merge automation and foreign share JSON files into one dataset."""

import json
from pathlib import Path

AUTO_FILE = Path("API_database_laborforce/data_occup_automation_extended.json")
FOREIGN_FILE = Path("API_database_laborforce/data_occup_foreign_extended.json")
OUT_FILE = Path("API_database_laborforce/data_occup_consolidated.json")


def main() -> None:
    auto_rows = json.loads(AUTO_FILE.read_text())
    foreign_rows = json.loads(FOREIGN_FILE.read_text())

    auto_map = {r["soc"]: r for r in auto_rows}
    foreign_map = {r["soc"]: r for r in foreign_rows}

    all_socs = sorted(set(auto_map) | set(foreign_map))
    merged: list[dict] = []
    for soc in all_socs:
        a = auto_map.get(soc, {})
        f = foreign_map.get(soc, {})
        merged.append(
            {
                "soc": soc,
                "occupation": a.get("occupation", ""),
                "automation_pctile": a.get("automation_pctile"),
                "major": a.get("major") or f.get("major"),
                "minor": a.get("minor"),
                "occ_label": f.get("occ_label", ""),
                "foreign_pct": f.get("foreign_pct"),
                "soc3": f.get("soc3", ""),
                "foreign_pct_soc3": f.get("foreign_pct_soc3"),
                "synonyms": a.get("synonyms") or f.get("synonyms", ""),
            }
        )

    OUT_FILE.write_text(json.dumps(merged, indent=2))
    print(f"\u2713 Wrote {OUT_FILE}")


if __name__ == "__main__":
    main()

