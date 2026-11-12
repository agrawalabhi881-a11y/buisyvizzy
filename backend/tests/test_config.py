import pytest
from pydantic import ValidationError

from app.core.config import Settings


def test_settings_accept_generated_jwt_secret() -> None:
    settings = Settings(
        _env_file=None,
        jwt_secret_key="generated-test-secret-" + "x" * 40,
    )
    assert len(settings.jwt_secret_key.get_secret_value()) >= 32
    assert settings.jwt_algorithm == "HS256"


@pytest.mark.parametrize(
    "secret",
    [
        "short",
        "replace-with-generated-random-secret-at-least-32-characters",
        "scm-digital-twin-secure-secret-key-change-in-prod",
    ],
)
def test_settings_reject_weak_jwt_secret(secret: str) -> None:
    with pytest.raises(ValidationError):
        Settings(_env_file=None, jwt_secret_key=secret)
