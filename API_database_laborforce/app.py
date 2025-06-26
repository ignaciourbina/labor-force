# app.py  ────────────────
from fastapi import FastAPI, HTTPException, Query
import json, pathlib
from fastapi.middleware.cors import CORSMiddleware

# ── CONFIG ──────────────────────────────────────────────────────
ALLOWED_ORIGINS = ["https://stonybrookuniversity.co1.qualtrics.com/"]   
DATA_FILE       = pathlib.Path("data.json")             # dataset
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
