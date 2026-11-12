
from functools import lru_cache
from pathlib import Path

from pydantic import Field, SecretStr, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


BACKEND_ROOT = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    jwt_secret_key: SecretStr = Field(min_length=32)
    jwt_algorithm: str = "HS256"
    access_token_expire_hours: int = Field(default=24, gt=0, le=168)

    model_config = SettingsConfigDict(
        env_file=BACKEND_ROOT / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @field_validator("jwt_secret_key")
    @classmethod
    def validate_jwt_secret(cls, value: SecretStr) -> SecretStr:
        secret = value.get_secret_value()

        known_weak_values = {
            "scm-digital-twin-secure-secret-key-change-in-prod",
            "secret",
            "changeme",
            "your-secret-key",
        }

        if secret.strip() != secret or secret.lower() in known_weak_values:
            raise ValueError("JWT_SECRET_KEY must be a strong, non-default secret")

        return value

    @field_validator("jwt_algorithm")
    @classmethod
    def validate_algorithm(cls, value: str) -> str:
        if value != "HS256":
            raise ValueError("Only HS256 is supported")
        return value


@lru_cache
def get_settings() -> Settings:
    return Settings()
