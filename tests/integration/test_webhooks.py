import json

from fastapi.testclient import TestClient

from app.main import create_app


def test_health() -> None:
    with TestClient(create_app()) as client:
        response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


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


def test_database_health() -> None:
    with TestClient(create_app()) as client:
        response = client.get("/health/database")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
