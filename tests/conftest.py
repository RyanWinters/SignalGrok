import os
import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
os.environ.setdefault("SIGNALGROK_WEBHOOK_KEY", "test-secret")

from app.core.config import get_settings
from app.main import app


@pytest.fixture(autouse=True)
def configure_env():
    os.environ["SIGNALGROK_WEBHOOK_KEY"] = "test-secret"
    get_settings.cache_clear()
    yield
    get_settings.cache_clear()


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)
