import os

import pytest

from app.core.config import get_settings


os.environ.setdefault("ENV", "dev")
os.environ.setdefault("LOG_LEVEL", "INFO")
os.environ.setdefault("SIGNALGROK_WEBHOOK_KEY", "test-webhook-key")
os.environ.setdefault("DATABASE_URL", "sqlite:///./test.db")
os.environ.setdefault("OPENAI_API_KEY", "test-openai-key")
os.environ.setdefault("FINNHUB_API_KEY", "test-finnhub-key")
os.environ.setdefault("DISCORD_WEBHOOK_URL", "https://discord.example/webhook")


@pytest.fixture(autouse=True)
def required_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("ENV", "dev")
    monkeypatch.setenv("LOG_LEVEL", "INFO")
    monkeypatch.setenv("SIGNALGROK_WEBHOOK_KEY", "test-webhook-key")
    monkeypatch.setenv("DATABASE_URL", "sqlite:///./test.db")
    monkeypatch.setenv("OPENAI_API_KEY", "test-openai-key")
    monkeypatch.setenv("FINNHUB_API_KEY", "test-finnhub-key")
    monkeypatch.setenv("DISCORD_WEBHOOK_URL", "https://discord.example/webhook")
    get_settings.cache_clear()
