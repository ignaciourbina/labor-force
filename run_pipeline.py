from __future__ import annotations
import subprocess
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent / "scripts"

# Ordered list of scripts required to refresh the API datasets.
PIPELINE = [
    SCRIPT_DIR / "onet_synonyms_json.py",
    SCRIPT_DIR / "automation_risk_pipeline.py",
    SCRIPT_DIR / "automation_percentile_json.py",
    SCRIPT_DIR / "extend_automation_data.py",
    SCRIPT_DIR / "occupation_foreign_share.py",
    SCRIPT_DIR / "extend_foreign_data.py",
    SCRIPT_DIR / "state_foreign_share.py",
    SCRIPT_DIR / "verify_foreign_share.py",
]


def run_step(script: Path) -> None:
    """Execute a single pipeline script."""
    print(f"\n>>> Running {script}...")
    subprocess.run(["python", str(script)], check=True)


def main() -> None:
    for script in PIPELINE:
        run_step(script)
    print("\nPipeline finished successfully.")


if __name__ == "__main__":
    main()
