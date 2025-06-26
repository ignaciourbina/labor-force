import os, sys; sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from fastapi.testclient import TestClient
from API_database_laborforce.app import app

client = TestClient(app)


def test_query_endpoint():
    resp = client.get("/query", params={"state": "CA", "major": "15"})
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)
    assert len(data) > 0
    assert "minor" in data[0]


def test_foreign_rate_endpoint():
    resp = client.get("/foreign_rate", params={"state": "CA"})
    assert resp.status_code == 200
    body = resp.json()
    assert body["state"] == "CA"
    assert "foreign_pct" in body


def test_automation_percentile_endpoint():
    resp = client.get("/automation_percentile", params={"soc": "11-1011"})
    assert resp.status_code == 200
    body = resp.json()
    assert body["soc"] == "11-1011"
    assert "automation_pctile" in body


def test_consolidated_fields():
    soc = "11-1011"
    auto_resp = client.get("/automation_percentile", params={"soc": soc})
    foreign_resp = client.get("/occ_foreign_rate", params={"soc": soc})

    assert auto_resp.status_code == 200
    assert foreign_resp.status_code == 200

    auto_data = auto_resp.json()
    foreign_data = foreign_resp.json()

    assert "automation_pctile" in auto_data
    assert "foreign_pct" in foreign_data

