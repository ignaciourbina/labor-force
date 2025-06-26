# Documentation Overview

This folder contains step-by-step notes for each data-processing stage.
Use these guides when updating the datasets or debugging the pipeline.

- **automation_risk_pipeline.md** – Combines automation probabilities with
  national employment totals and computes percentile ranks.
- **automation_percentile_json_pipeline.md** – Converts the percentile table
  into a compact JSON file for the API.
- **occupation_foreign_share_pipeline.md** – Calculates the foreign-born share
  of each occupation.
- **state_foreign_share_pipeline.md** – Builds per-state foreign-share totals.
- **employment_merge_pipeline.md** – Adds national employment counts to the
  CPS occupation totals.
- **automation_risk_verification.md** – Checks the outputs of the automation
  risk pipeline.
- **pm-notes.md** – High-level discussion of the overall workflow and
  outstanding tasks.

Run `python run_pipeline.py` from the repository root to execute the most
important steps in sequence.
