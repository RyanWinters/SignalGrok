from pathlib import Path
import os

import pytest

from app.core.config import get_settings
from app.core.db import get_engine


os.environ.setdefault("ENV", "dev")
os.environ.setdefault("LOG_LEVEL", "INFO")
os.environ.setdefault("SIGNALGROK_WEBHOOK_KEY", "test-webhook-key")
os.environ.setdefault("DATABASE_URL", "sqlite:///./bootstrap-test.db")
os.environ.setdefault("OPENAI_API_KEY", "test-openai-key")
os.environ.setdefault("FINNHUB_API_KEY", "test-finnhub-key")
os.environ.setdefault("DISCORD_WEBHOOK_URL", "https://discord.example/webhook")


@pytest.fixture(autouse=True)
def required_env(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.setenv("ENV", "dev")
    monkeypatch.setenv("LOG_LEVEL", "INFO")
    monkeypatch.setenv("SIGNALGROK_WEBHOOK_KEY", "test-webhook-key")
    monkeypatch.setenv("WEBHOOK_ENDPOINT_ID", "00000000-0000-0000-0000-000000000001")
    monkeypatch.setenv("OPENAI_API_KEY", "test-openai-key")
    monkeypatch.setenv("FINNHUB_API_KEY", "test-finnhub-key")
    monkeypatch.setenv("DISCORD_WEBHOOK_URL", "https://discord.example/webhook")

    db_path = tmp_path / "test.db"
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{db_path}")

    get_settings.cache_clear()
    get_engine.cache_clear()
