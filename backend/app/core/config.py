from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic import Field, SecretStr, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


BACKEND_ROOT = Path(__file__).resolve().parents[2]
REPOSITORY_ROOT = BACKEND_ROOT.parent


class Settings(BaseSettings):
    """Validated application settings shared by local and container deployments."""

    jwt_secret_key: SecretStr = Field(min_length=32)
    jwt_algorithm: Literal["HS256"] = "HS256"
    access_token_expire_hours: int = Field(default=24, gt=0, le=168)
    database_url: str = "sqlite:///./dev_scm.db"
    app_env: Literal["development", "test", "production"] = "development"

    model_config = SettingsConfigDict(
        env_file=(REPOSITORY_ROOT / ".env", BACKEND_ROOT / ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @field_validator("jwt_secret_key")
    @classmethod
    def validate_jwt_secret(cls, value: SecretStr) -> SecretStr:
        secret = value.get_secret_value()
        normalized = secret.strip().lower()
        weak_markers = (
            "scm-digital-twin-secure-secret-key-change-in-prod",
            "secret",
            "changeme",
            "change_me",
            "replace-with",
            "your-secret-key",
        )
        if secret != secret.strip() or any(marker in normalized for marker in weak_markers):
            raise ValueError(
                "JWT_SECRET_KEY must be a generated, non-default secret of at least 32 characters"
            )
        return value


@lru_cache
def get_settings() -> Settings:
    """Return the validated, cached settings instance."""
    return Settings()
