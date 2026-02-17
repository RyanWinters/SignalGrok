import os

import pytest
from pydantic import ValidationError

from app.core.config import Settings


def test_settings_requires_webhook_key(monkeypatch):
    monkeypatch.delenv("SIGNALGROK_WEBHOOK_KEY", raising=False)
    with pytest.raises(ValidationError):
        Settings()


def test_settings_loads_webhook_key(monkeypatch):
    monkeypatch.setenv("SIGNALGROK_WEBHOOK_KEY", "abc")
    settings = Settings()
    assert settings.signalgrok_webhook_key == "abc"
