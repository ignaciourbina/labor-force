from __future__ import annotations

"""Build per-state foreign-born labor-force percentages.

Reads ``data_tables/cps_state_labor_force_totals.csv`` and writes
``API_database_laborforce/data_state_foreign.json`` with records of the form::
    {"state": "CA", "state_name": "California", "foreign_pct": 32.48}
"""

import json
from pathlib import Path

import pandas as pd

DATA_FILE = Path("data_tables/cps_state_labor_force_totals.csv")
OUT_FILE = Path("API_database_laborforce/data_state_foreign.json")


def main() -> None:
    df = pd.read_csv(DATA_FILE)
    df["foreign_pct"] = (df["foreign"] / df["total_lf"] * 100).round(2)
    rows = (
        df[["state_abbr", "state_name", "foreign_pct"]]
        .rename(columns={"state_abbr": "state"})
        .to_dict(orient="records")
    )
    OUT_FILE.write_text(json.dumps(rows, indent=2))
    print(f"\u2713 Wrote {OUT_FILE}")


if __name__ == "__main__":
    main()
