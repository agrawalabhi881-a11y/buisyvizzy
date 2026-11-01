"""
backend/app/services/auth_service.py
Role-based authentication and token verification for the five supply chain personas:
ADMIN, DISTRIBUTOR, WAREHOUSE_MANAGER, STORE_OWNER, TRUCK_DRIVER.
"""

from datetime import datetime, timezone, timedelta
from typing import List, Optional
import base64
import hashlib
import hmac
import json
from fastapi import HTTPException, Security, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel

SECRET_KEY = "scm-digital-twin-secure-secret-key-change-in-prod"
ALGORITHM = "HS256"
security_bearer = HTTPBearer(auto_error=False)


class UserProfile(BaseModel):
    username: str
    role: str
    entity_id: Optional[int] = None  # warehouse_id, store_id, etc.


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: str
    username: str


# Pre-configured demo accounts for each role
DEMO_USERS = {
    "admin": {"password": "adminpassword", "role": "ADMIN", "entity_id": None},
    "distributor": {"password": "distpassword", "role": "DISTRIBUTOR", "entity_id": 1},
    "warehouse_mgr": {"password": "whpassword", "role": "WAREHOUSE_MANAGER", "entity_id": 1},
    "store_owner": {"password": "storepassword", "role": "STORE_OWNER", "entity_id": 1},
    "driver": {"password": "driverpassword", "role": "TRUCK_DRIVER", "entity_id": 1},
}


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Creates a signed HMAC-SHA256 token."""
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(hours=24))
    to_encode.update({"exp": int(expire.timestamp())})

    header = {"alg": ALGORITHM, "typ": "JWT"}
    header_b64 = base64.urlsafe_b64encode(json.dumps(header).encode()).decode().rstrip("=")
    payload_b64 = base64.urlsafe_b64encode(json.dumps(to_encode).encode()).decode().rstrip("=")

    signature_raw = f"{header_b64}.{payload_b64}".encode()
    signature = hmac.new(SECRET_KEY.encode(), signature_raw, hashlib.sha256).digest()
    sig_b64 = base64.urlsafe_b64encode(signature).decode().rstrip("=")

    return f"{header_b64}.{payload_b64}.{sig_b64}"


def decode_token(token: str) -> dict:
    """Verifies signature and expiration of access token."""
    parts = token.split(".")
    if len(parts) != 3:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token format",
        )
    header_b64, payload_b64, sig_b64 = parts

    expected_sig = hmac.new(
        SECRET_KEY.encode(),
        f"{header_b64}.{payload_b64}".encode(),
        hashlib.sha256,
    ).digest()
    expected_sig_b64 = base64.urlsafe_b64encode(expected_sig).decode().rstrip("=")

    if not hmac.compare_digest(sig_b64, expected_sig_b64):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token signature",
        )

    # Pad payload if needed
    rem = len(payload_b64) % 4
    if rem:
        payload_b64 += "=" * (4 - rem)
    payload = json.loads(base64.urlsafe_b64decode(payload_b64).decode())

    exp = payload.get("exp")
    if exp and datetime.now(timezone.utc).timestamp() > exp:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
        )

    return payload


def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Security(security_bearer),
) -> UserProfile:
    """FastAPI dependency to extract current authenticated user."""
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization header missing",
        )
    payload = decode_token(credentials.credentials)
    username = payload.get("sub")
    role = payload.get("role")
    entity_id = payload.get("entity_id")
    if not username or not role:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
        )
    return UserProfile(username=username, role=role, entity_id=entity_id)


def require_roles(allowed_roles: List[str]):
    """FastAPI dependency factory enforcing role-based permissions."""
    def role_checker(user: UserProfile = Security(get_current_user)) -> UserProfile:
        if user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Forbidden: role '{user.role}' lacks permission. Allowed: {allowed_roles}",
            )
        return user
    return role_checker


def require_roles_or_demo(allowed_roles: List[str]):
    """
    FastAPI dependency factory:
    Enforces role check if a Bearer token is provided.
    If no authorization header is provided (e.g. Swagger UI exploration),
    defaults to demo Admin user for frictionless execution.
    """
    def role_checker(
        credentials: Optional[HTTPAuthorizationCredentials] = Security(security_bearer),
    ) -> UserProfile:
        if not credentials:
            return UserProfile(username="demo_admin", role="ADMIN")
        user = get_current_user(credentials)
        if user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Forbidden: role '{user.role}' lacks permission. Allowed: {allowed_roles}",
            )
        return user
    return role_checker
