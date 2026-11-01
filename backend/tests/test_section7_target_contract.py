"""
backend/tests/test_section7_target_contract.py
Tests verifying exact compliance with Section 7 Target Backend API Contract.
"""

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_get_network_contract():
    resp = client.get("/api/network")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "ok"
    assert "suppliers" in data
    assert "warehouses" in data
    assert "stores" in data
    assert len(data["warehouses"]) == 3
    assert len(data["stores"]) == 20


def test_get_shipments_contract():
    resp = client.get("/api/shipments")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "ok"
    assert "active_shipments" in data


def test_get_trucks_and_breakdown_rescue_contract():
    # 1. GET /api/trucks
    resp = client.get("/api/trucks")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "ok"
    assert data["trucks_count"] == 10
    assert len(data["trucks"]) == 10

    # 2. POST /api/trucks/{truck_id}/breakdown
    brk_resp = client.post("/api/trucks/TRUCK_03/breakdown")
    assert brk_resp.status_code == 200
    brk_data = brk_resp.json()
    assert brk_data["status"] == "breakdown_registered"
    assert brk_data["broken_truck_id"] == "TRUCK_03"
    assert brk_data["alert"]["severity"] == "CRITICAL"

    # 3. POST /api/trucks/{truck_id}/rescue
    res_resp = client.post("/api/trucks/TRUCK_03/rescue", json={"rescue_truck_id": "TRUCK_04"})
    assert res_resp.status_code == 200
    res_data = res_resp.json()
    assert res_data["status"] == "rescue_dispatched"
    assert res_data["rescue_truck_id"] == "TRUCK_04"


def test_scenarios_and_disruptions_contract():
    # GET /api/scenarios
    sc_resp = client.get("/api/scenarios")
    assert sc_resp.status_code == 200
    sc_data = sc_resp.json()
    assert len(sc_data["scenarios"]) >= 5

    # POST /api/disruptions
    disr_resp = client.post(
        "/api/disruptions",
        json={
            "disruption_type": "DEMAND_SPIKE",
            "target_id": "STORE_01",
            "severity": 2.5,
            "duration_ticks": 4,
            "description": "Flash promotional demand shock",
        },
    )
    assert disr_resp.status_code == 200
    disr_data = disr_resp.json()
    assert disr_data["status"] == "scheduled"
    assert "alert" in disr_data
    assert "recommendation" in disr_data

    # GET /api/disruptions
    get_disr = client.get("/api/disruptions")
    assert get_disr.status_code == 200
    assert "active" in get_disr.json()


def test_simulation_play_pause_step_contract():
    play_resp = client.post("/api/simulation/play")
    assert play_resp.status_code == 200
    assert play_resp.json()["status"] == "playing"

    pause_resp = client.post("/api/simulation/pause")
    assert pause_resp.status_code == 200
    assert pause_resp.json()["status"] == "paused"

    step_resp = client.post("/api/simulation/step")
    assert step_resp.status_code == 200
    assert step_resp.json()["status"] == "ok"
    assert "snapshot" in step_resp.json()


def test_forecasts_contract():
    # GET /api/forecasts
    fc_resp = client.get("/api/forecasts?store_id=STORE_01&product_id=PROD_001&horizon_days=5")
    assert fc_resp.status_code == 200
    fc_data = fc_resp.json()
    assert len(fc_data) == 5
    assert all("p10" in p and "p50" in p and "p90" in p for p in fc_data)
