"""
Role-based authentication and token verification for the five supply chain personas:
ADMIN, DISTRIBUTOR, WAREHOUSE_MANAGER, STORE_OWNER, TRUCK_DRIVER.
"""

import base64
import binascii
import hashlib
import hmac
import json
from datetime import datetime, timedelta, timezone
from typing import Any, Optional

from fastapi import HTTPException, Security, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel

from app.core.config import get_settings

settings = get_settings()
SECRET_KEY = settings.jwt_secret_key.get_secret_value()
ALGORITHM = settings.jwt_algorithm
security_bearer = HTTPBearer(auto_error=False)


class UserProfile(BaseModel):
    username: str
    role: str
    entity_id: Optional[int] = None


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: str
    username: str


# Demo-only credentials for the local demonstration. Replace with managed identity
# storage before exposing this service to untrusted users.
DEMO_USERS = {
    "admin": {"password": "adminpassword", "role": "ADMIN", "entity_id": None},
    "distributor": {"password": "distpassword", "role": "DISTRIBUTOR", "entity_id": 1},
    "warehouse_mgr": {"password": "whpassword", "role": "WAREHOUSE_MANAGER", "entity_id": 1},
    "store_owner": {"password": "storepassword", "role": "STORE_OWNER", "entity_id": 1},
    "driver": {"password": "driverpassword", "role": "TRUCK_DRIVER", "entity_id": 1},
}


def _unauthorized(detail: str) -> HTTPException:
    return HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=detail)


def _decode_segment(segment: str) -> dict[str, Any]:
    padded = segment + "=" * (-len(segment) % 4)
    decoded = base64.urlsafe_b64decode(padded.encode("ascii"))
    value = json.loads(decoded.decode("utf-8"))
    if not isinstance(value, dict):
        raise ValueError("JWT segment must contain a JSON object")
    return value


def create_access_token(
    data: dict[str, Any], expires_delta: Optional[timedelta] = None
) -> str:
    """Create a signed HMAC-SHA256 token with a mandatory expiry claim."""
    to_encode = data.copy()
    lifetime = expires_delta or timedelta(hours=settings.access_token_expire_hours)
    expire = datetime.now(timezone.utc) + lifetime
    to_encode["exp"] = int(expire.timestamp())

    header = {"alg": ALGORITHM, "typ": "JWT"}
    header_b64 = (
        base64.urlsafe_b64encode(json.dumps(header).encode()).decode().rstrip("=")
    )
    payload_b64 = (
        base64.urlsafe_b64encode(json.dumps(to_encode).encode()).decode().rstrip("=")
    )
    signing_input = f"{header_b64}.{payload_b64}".encode()
    signature = hmac.new(SECRET_KEY.encode(), signing_input, hashlib.sha256).digest()
    signature_b64 = base64.urlsafe_b64encode(signature).decode().rstrip("=")
    return f"{header_b64}.{payload_b64}.{signature_b64}"


def decode_token(token: str) -> dict[str, Any]:
    """Verify JWT structure, algorithm, signature, and mandatory expiration."""
    parts = token.split(".")
    if len(parts) != 3:
        raise _unauthorized("Invalid token format")
    header_b64, payload_b64, signature_b64 = parts

    expected_signature = hmac.new(
        SECRET_KEY.encode(),
        f"{header_b64}.{payload_b64}".encode(),
        hashlib.sha256,
    ).digest()
    expected_signature_b64 = (
        base64.urlsafe_b64encode(expected_signature).decode().rstrip("=")
    )
    if not hmac.compare_digest(signature_b64, expected_signature_b64):
        raise _unauthorized("Invalid token signature")

    try:
        header = _decode_segment(header_b64)
        payload = _decode_segment(payload_b64)
    except (ValueError, UnicodeDecodeError, binascii.Error):
        raise _unauthorized("Invalid token payload") from None

    if header.get("alg") != ALGORITHM or header.get("typ") != "JWT":
        raise _unauthorized("Unsupported token algorithm")

    expires_at = payload.get("exp")
    if isinstance(expires_at, bool) or not isinstance(expires_at, (int, float)):
        raise _unauthorized("Token expiration is missing or invalid")
    if datetime.now(timezone.utc).timestamp() >= expires_at:
        raise _unauthorized("Token has expired")

    return payload


def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Security(security_bearer),
) -> UserProfile:
    """FastAPI dependency to extract the current authenticated user."""
    if not credentials:
        raise _unauthorized("Authorization header missing")
    payload = decode_token(credentials.credentials)
    username = payload.get("sub")
    role = payload.get("role")
    entity_id = payload.get("entity_id")
    if not isinstance(username, str) or not username or not isinstance(role, str) or not role:
        raise _unauthorized("Invalid token payload")
    return UserProfile(username=username, role=role, entity_id=entity_id)


def require_roles(allowed_roles: list[str]):
    """FastAPI dependency factory enforcing role-based permissions."""

    def role_checker(user: UserProfile = Security(get_current_user)) -> UserProfile:
        if user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Forbidden: role '{user.role}' lacks permission. Allowed: {allowed_roles}",
            )
        return user

    return role_checker


def require_roles_or_demo(allowed_roles: list[str]):
    """
    Backward-compatible role dependency.

    Authentication is mandatory. Demo users must explicitly log in and provide
    a valid Bearer token.
    """
    return require_roles(allowed_roles)
