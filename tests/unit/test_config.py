import pytest
from pydantic import ValidationError

from app.core.config import Settings, get_settings
from app.main import create_app


REQUIRED_KEYS = [
    "ENV",
    "LOG_LEVEL",
    "SIGNALGROK_WEBHOOK_KEY",
    "DATABASE_URL",
    "OPENAI_API_KEY",
    "FINNHUB_API_KEY",
    "DISCORD_WEBHOOK_URL",
]


def test_settings_load_with_required_env() -> None:
    settings = get_settings()
    assert settings.ENV == "dev"
    assert settings.debug is True
    assert settings.cors_origins == ["*"]


def test_settings_fail_when_required_variable_missing(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    get_settings.cache_clear()

    with pytest.raises(ValidationError):
        get_settings()


def test_create_app_fails_fast_when_settings_invalid(monkeypatch: pytest.MonkeyPatch) -> None:
    for key in REQUIRED_KEYS:
        monkeypatch.delenv(key, raising=False)
    get_settings.cache_clear()

    with pytest.raises(ValidationError):
        create_app()


def test_prod_environment_is_strict(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("ENV", "prod")
    monkeypatch.setenv("CORS_ALLOWED_ORIGINS", '["https://signalgrok.example"]')
    get_settings.cache_clear()

    settings = Settings()
    assert settings.debug is False
    assert settings.cors_origins == ["https://signalgrok.example"]
