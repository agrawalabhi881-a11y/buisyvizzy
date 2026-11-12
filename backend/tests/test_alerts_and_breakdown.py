
"""
Comprehensive tests for:
- State inspection
- Truck breakdown triggering
- Autonomous recommendation approval & failover execution
- Alert acknowledge/resolve lifecycle
- Custom disruption injection
- Activity audit logging
"""

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_simulation_state_is_authoritative(admin_headers):
    response = client.get(
        "/api/simulation/state",
        headers=admin_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "tick" in data
    assert "metrics" in data
    assert "fleet" in data
    assert len(data["fleet"]) == 10
    assert data["provenance"]["authoritative"] is True


def test_truck_breakdown_generates_alert_and_recommendation(admin_headers):
    response = client.post(
        "/api/simulation/truck-breakdown",
        json={"truck_id": "TRUCK_03"},
        headers=admin_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "breakdown_registered"
    assert data["broken_truck_id"] == "TRUCK_03"

    alert = data["alert"]
    assert alert["severity"] == "CRITICAL"
    assert alert["source_type"] == "TRUCK_BREAKDOWN"
    assert alert["source_id"] == "TRUCK_03"

    rec = data["recommendation"]
    assert rec["type"] == "TRUCK_FAILOVER"
    assert rec["status"] == "PENDING"
    assert rec["projected_savings_usd"] > 0
    assert "TRUCK_04" in rec["title"]

    alerts_resp = client.get("/api/alerts", headers=admin_headers)
    assert alerts_resp.status_code == 200
    alerts = alerts_resp.json()
    assert any(a["id"] == alert["id"] for a in alerts)

    approve_resp = client.post(
        f"/api/recommendations/{rec['id']}/approve",
        headers=admin_headers,
    )
    assert approve_resp.status_code == 200
    approve_data = approve_resp.json()
    assert approve_data["status"] == "success"
    assert approve_data["recommendation_status"] == "EXECUTED"

    alerts_after = client.get("/api/alerts", headers=admin_headers)
    assert alerts_after.status_code == 200
    resolved_alert = next(
        a for a in alerts_after.json() if a["id"] == alert["id"]
    )
    assert resolved_alert["status"] == "RESOLVED"


def test_alert_acknowledgment_and_resolution(admin_headers):
    alerts_resp = client.get("/api/alerts", headers=admin_headers)
    assert alerts_resp.status_code == 200
    alerts = alerts_resp.json()
    assert len(alerts) > 0
    target_alert = alerts[0]

    ack_resp = client.post(
        f"/api/alerts/{target_alert['id']}/acknowledge",
        headers=admin_headers,
    )
    assert ack_resp.status_code == 200
    assert ack_resp.json()["status"] == "ACKNOWLEDGED"

    res_resp = client.post(
        f"/api/alerts/{target_alert['id']}/resolve",
        headers=admin_headers,
    )
    assert res_resp.status_code == 200
    assert res_resp.json()["status"] == "RESOLVED"


def test_disruption_injection_creates_alert_and_mitigation(admin_headers):
    inj_resp = client.post(
        "/api/simulation/disruptions/inject",
        json={
            "disruption_type": "SUPPLIER_FAILURE",
            "target_id": "MFR_01",
            "severity": 3.0,
            "duration_ticks": 5,
            "description": "Blackout at primary chemical processor",
        },
        headers=admin_headers,
    )
    assert inj_resp.status_code == 200
    inj_data = inj_resp.json()
    assert inj_data["status"] == "injected"
    assert inj_data["disruption"]["target_id"] == "MFR_01"
    assert inj_data["alert"]["severity"] == "CRITICAL"
    assert inj_data["recommendation"]["type"] == "LATERAL_REBALANCE"


def test_activity_log_records_events(admin_headers):
    act_resp = client.get("/api/activity", headers=admin_headers)
    assert act_resp.status_code == 200
    activities = act_resp.json()
    assert len(activities) > 0
    assert any(
        a["event_type"] in [
            "SYSTEM_INITIALIZE",
            "TRUCK_BREAKDOWN",
            "RECOMMENDATION_APPROVED",
            "DISRUPTION_INJECTED",
        ]
        for a in activities
    )
