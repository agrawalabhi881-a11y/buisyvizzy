
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_protected_simulation_endpoint_rejects_anonymous_user():
    response = client.get("/api/simulation/state")

    assert response.status_code == 401


def test_public_demo_token_endpoint_is_removed():
    response = client.get(
        "/api/simulation/demo-token",
        params={"role": "ADMIN"},
    )

    assert response.status_code == 404


def test_demo_login_still_works():
    response = client.post(
        "/api/auth/login",
        json={
            "username": "admin",
            "password": "adminpassword",
        },
    )

    assert response.status_code == 200

    token = response.json()["access_token"]

    profile = client.get(
        "/api/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert profile.status_code == 200
    assert profile.json()["role"] == "ADMIN"
