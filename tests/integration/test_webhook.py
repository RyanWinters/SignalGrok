def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
    assert "X-Request-ID" in response.headers


def test_webhook_auth_failure(client):
    response = client.post(
        "/webhooks/trading-alert",
        headers={"X-SignalGrok-Key": "bad"},
        json={"signal": "SPY MACD Crossover", "ticker": "SPY"},
    )
    assert response.status_code == 401


def test_webhook_success(client):
    response = client.post(
        "/webhooks/trading-alert",
        headers={"X-SignalGrok-Key": "test-secret"},
        json={"signal": "SPY MACD Crossover", "ticker": "spy"},
    )
    assert response.status_code == 200
    assert response.json() == {"status": "accepted", "ticker": "SPY"}
