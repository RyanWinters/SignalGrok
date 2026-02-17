import json
import re

from fastapi.testclient import TestClient
from sqlalchemy import select

from app.main import create_app
from app.models import incoming_alerts
from app.core.config import get_settings
from app.core.db import get_engine


def test_health() -> None:
    with TestClient(create_app()) as client:
        response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_authenticated_intake_persists_and_returns_normalized_payload() -> None:
    with TestClient(create_app()) as client:
        response = client.post(
            "/webhooks/trading-alert",
            headers={"X-SignalGrok-Key": "test-webhook-key"},
            json={
                "alert_id": "tv-1001",
                "signal": "SPY MACD Crossover",
                "ticker": " spy ",
                "direction": "buy",
            },
        )

    assert response.status_code == 200
    assert response.json() == {
        "status": "accepted",
        "ticker": "SPY",
        "signal_type": "SPY_MACD_CROSSOVER",
        "duplicate": False,
    }

    settings = get_settings()
    engine = get_engine(settings.DATABASE_URL)
    with engine.connect() as connection:
        rows = connection.execute(select(incoming_alerts)).mappings().all()

    assert len(rows) == 1
    saved = rows[0]
    assert saved["external_alert_id"] == "tv-1001"
    assert saved["ticker"] == "SPY"
    assert saved["signal_type"] == "SPY_MACD_CROSSOVER"
    assert saved["direction"] == "BULLISH"
    assert saved["status"] == "RECEIVED"


def test_invalid_key_returns_401() -> None:
    with TestClient(create_app()) as client:
        response = client.post(
            "/webhooks/trading-alert",
            headers={"X-SignalGrok-Key": "wrong"},
            json={
                "signal": "SPY MACD Crossover",
                "ticker": "SPY",
            },
        )

    assert response.status_code == 401
    assert response.json() == {"detail": "Unauthorized"}


def test_duplicate_alert_is_idempotent() -> None:
    payload = {
        "alert_id": "tv-dup-1",
        "signal": "SPY MACD Crossover",
        "ticker": "SPY",
    }

    with TestClient(create_app()) as client:
        first = client.post(
            "/webhooks/trading-alert",
            headers={"X-SignalGrok-Key": "test-webhook-key"},
            json=payload,
        )
        second = client.post(
            "/webhooks/trading-alert",
            headers={"X-SignalGrok-Key": "test-webhook-key"},
            json=payload,
        )

    assert first.status_code == 200
    assert first.json()["duplicate"] is False
    assert second.status_code == 200
    assert second.json()["duplicate"] is True

    settings = get_settings()
    engine = get_engine(settings.DATABASE_URL)
    with engine.connect() as connection:
        rows = connection.execute(select(incoming_alerts)).mappings().all()

    assert len(rows) == 1


def test_malformed_payload_returns_422() -> None:
    with TestClient(create_app()) as client:
        response = client.post(
            "/webhooks/trading-alert",
            headers={"X-SignalGrok-Key": "test-webhook-key"},
            json={"signal": "SPY MACD Crossover"},
        )

    assert response.status_code == 422


def test_request_id_propagated_and_logged(capfd) -> None:
    with TestClient(create_app()) as client:
        response = client.post(
            "/webhooks/trading-alert",
            headers={
                "X-SignalGrok-Key": "test-webhook-key",
                "X-Request-ID": "req-smoke-123",
            },
            json={
                "signal": "SPY MACD Crossover",
                "ticker": "spy",
            },
        )

    assert response.status_code == 200
    assert response.headers["X-Request-ID"] == "req-smoke-123"

    logs = capfd.readouterr().err.strip().splitlines()
    parsed_logs = [json.loads(line) for line in logs if line.strip().startswith("{")]
    request_logs = [log for log in parsed_logs if log.get("message") == "request_completed"]

    assert request_logs
    assert any(log.get("request_id") == "req-smoke-123" for log in request_logs)


def test_request_id_generated_when_missing_and_secret_header_is_masked(capfd) -> None:
    with TestClient(create_app()) as client:
        response = client.post(
            "/webhooks/trading-alert",
            headers={"X-SignalGrok-Key": "test-webhook-key"},
            json={
                "signal": "SPY MACD Crossover",
                "ticker": "spy",
            },
        )

    assert response.status_code == 200
    generated_request_id = response.headers.get("X-Request-ID")
    assert generated_request_id is not None
    assert re.fullmatch(
        r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}",
        generated_request_id,
    )

    logs = capfd.readouterr().err.strip().splitlines()
    parsed_logs = [json.loads(line) for line in logs if line.strip().startswith("{")]
    request_logs = [log for log in parsed_logs if log.get("message") == "request_completed"]

    assert request_logs
    matching_log = next(
        log for log in request_logs if log.get("request_id") == generated_request_id
    )
    assert matching_log["headers"]["x-signalgrok-key"] == "***"


def test_database_health() -> None:
    with TestClient(create_app()) as client:
        response = client.get("/health/database")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
