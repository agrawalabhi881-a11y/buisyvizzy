from datetime import timedelta

from fastapi.testclient import TestClient

from app.main import app
from app.services.auth_service import create_access_token, decode_token

client = TestClient(app)


def test_protected_simulation_endpoint_rejects_anonymous_user() -> None:
    response = client.get("/api/simulation/state")
    assert response.status_code == 401


def test_public_demo_token_endpoint_is_removed() -> None:
    response = client.get("/api/simulation/demo-token", params={"role": "ADMIN"})
    assert response.status_code == 404


def test_demo_login_still_works() -> None:
    response = client.post(
        "/api/auth/login",
        json={"username": "admin", "password": "adminpassword"},
    )
    assert response.status_code == 200

    token = response.json()["access_token"]
    profile = client.get(
        "/api/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert profile.status_code == 200
    assert profile.json()["role"] == "ADMIN"


def test_expired_token_is_rejected() -> None:
    token = create_access_token(
        {"sub": "admin", "role": "ADMIN"},
        expires_delta=timedelta(seconds=-1),
    )
    try:
        decode_token(token)
    except Exception as exc:
        assert getattr(exc, "status_code", None) == 401
    else:
        raise AssertionError("Expired token should be rejected")


def test_token_without_expiration_is_rejected() -> None:
    import base64
    import hashlib
    import hmac
    import json

    from app.services.auth_service import SECRET_KEY

    header = base64.urlsafe_b64encode(b'{"alg":"HS256","typ":"JWT"}').decode().rstrip("=")
    payload = base64.urlsafe_b64encode(b'{"sub":"admin","role":"ADMIN"}').decode().rstrip("=")
    signing_input = f"{header}.{payload}".encode()
    signature = hmac.new(SECRET_KEY.encode(), signing_input, hashlib.sha256).digest()
    signature_b64 = base64.urlsafe_b64encode(signature).decode().rstrip("=")
    token = f"{header}.{payload}.{signature_b64}"

    try:
        decode_token(token)
    except Exception as exc:
        assert getattr(exc, "status_code", None) == 401
    else:
        raise AssertionError("Token without exp should be rejected")
