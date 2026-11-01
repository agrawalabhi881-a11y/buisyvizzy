"""
backend/app/api/routes/auth.py
Authentication endpoints: login and user profile inspection.
"""

from fastapi import APIRouter, HTTPException, Security, status
from pydantic import BaseModel

from app.services.auth_service import (
    DEMO_USERS,
    TokenResponse,
    UserProfile,
    create_access_token,
    get_current_user,
)

router = APIRouter(prefix="/auth", tags=["Authentication"])


class LoginRequest(BaseModel):
    username: str
    password: str


@router.post("/login", response_model=TokenResponse)
def login(request: LoginRequest):
    """Logs in as one of the 5 roles using demo credentials."""
    user = DEMO_USERS.get(request.username)
    if not user or user["password"] != request.password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )

    token = create_access_token({
        "sub": request.username,
        "role": user["role"],
        "entity_id": user["entity_id"],
    })

    return TokenResponse(
        access_token=token,
        token_type="bearer",
        role=user["role"],
        username=request.username,
    )


@router.get("/me", response_model=UserProfile)
def get_profile(current_user: UserProfile = Security(get_current_user)):
    """Returns the authenticated user's profile and active role."""
    return current_user
