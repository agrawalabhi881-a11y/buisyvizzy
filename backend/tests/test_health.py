from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_root_returns_service_status() -> None:
    response = client.get("/")

    assert response.status_code == 200
    assert response.json() == {"service": "supply-chain-digital-twin", "status": "ok"}


def test_health_returns_application_status_only() -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok", "service": "supply-chain-digital-twin"}
