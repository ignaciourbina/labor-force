# app.py  ────────────────
from fastapi import FastAPI, HTTPException, Query
import json
from pathlib import Path
from fastapi.middleware.cors import CORSMiddleware

# ── CONFIG ──────────────────────────────────────────────────────
ALLOWED_ORIGINS = ["https://stonybrookuniversity.co1.qualtrics.com/"]

# Base directory containing the JSON datasets
BASE_DIR = Path(__file__).resolve().parent

DATA_FILE  = BASE_DIR / "data.json"             # occupation dataset
STATE_FILE = BASE_DIR / "data_state_foreign.json"
AUTO_FILE  = BASE_DIR / "data_occup_automation.json"
# ────────────────────────────────────────────────────────────────

app = FastAPI(
    title="SOC lookup API",
    description="Returns minor SOC codes for a given (major, state) pair."
)

# CORS so the browser accepts fetch() from Qualtrics
app.add_middleware(
    CORSMiddleware,
    #allow_origins=ALLOWED_ORIGINS,   # ["*"] while testing
    allow_origins=["*"],   # ["*"] while testing
    allow_methods=["GET"],
    allow_headers=["*"],
)

# ── Root for quick health-check ─────────────────────────────────
@app.get("/")
def greet_json():
    """Simple liveness probe – useful for curl tests."""
    return {"Hello": "World!"}

# ── Load & index dataset on startup ─────────────────────────────
with DATA_FILE.open(encoding="utf-8") as f:
    rows = json.load(f)

INDEX: dict[str, dict[str, list[dict]]] = {}
for r in rows:
    INDEX.setdefault(r["state"], {}) \
         .setdefault(r["major"], []).append(r)

with STATE_FILE.open(encoding="utf-8") as f:
    state_rows = json.load(f)

STATE_INDEX: dict[str, float] = {r["state"]: r["foreign_pct"] for r in state_rows}

with AUTO_FILE.open(encoding="utf-8") as f:
    auto_rows = json.load(f)

AUTO_INDEX: dict[str, dict] = {r["soc"]: r for r in auto_rows}

with OCC_FOREIGN_FILE.open(encoding="utf-8") as f:
    occ_rows = json.load(f)

OCC_FOREIGN_INDEX: dict[str, dict] = {r["soc"]: r for r in occ_rows}


# ── Lookup endpoint used by Qualtrics ───────────────────────────
@app.get("/query")
def query(
    state: str = Query(..., min_length=2, max_length=2, description="Two-letter state, e.g. FL"),
    major: str = Query(..., min_length=1, max_length=2, description="Major SOC digits, e.g. 15")
):
    state = state.upper()
    major = major.zfill(2)

    try:
        return INDEX[state][major]
    except KeyError:
        raise HTTPException(status_code=404, detail="Combination not found")


@app.get("/foreign_rate")
def foreign_rate(
    state: str = Query(..., min_length=2, max_length=2, description="Two-letter state code, e.g. FL")
):
    state = state.upper()
    try:
        return {"state": state, "foreign_pct": STATE_INDEX[state]}
    except KeyError:
        raise HTTPException(status_code=404, detail="State not found")

@app.get("/automation_percentile")
def automation_percentile(
    soc: str = Query(..., min_length=7, max_length=7, description="Six-digit SOC code, e.g. 15-1256")
):
    soc = soc.strip()
    try:
        return AUTO_INDEX[soc]
    except KeyError:
        raise HTTPException(status_code=404, detail="Occupation code not found")

@app.get("/occ_foreign_rate")
def occ_foreign_rate(
    soc: str = Query(..., min_length=5, max_length=7, description="Six-digit SOC code, e.g. 11-1011")
):
    try:
        return OCC_FOREIGN_INDEX[soc]
    except KeyError:
        raise HTTPException(status_code=404, detail="SOC code not found")

