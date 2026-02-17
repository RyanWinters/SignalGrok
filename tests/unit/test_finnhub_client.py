from datetime import date

import httpx
import pytest

from app.clients.finnhub import FinnhubClient, FinnhubPermanentError, FinnhubTransientError


def _sample_news() -> list[dict[str, object]]:
    return [
        {
            "category": "company",
            "datetime": 1718064000,
            "headline": "Test headline",
            "id": 101,
            "image": "https://example.com/image.jpg",
            "related": "AAPL",
            "source": "ExampleWire",
            "summary": "Summary text",
            "url": "https://example.com/news/101",
        }
    ]


def _patch_client(monkeypatch: pytest.MonkeyPatch, transport: httpx.MockTransport) -> None:
    original_client = httpx.Client

    def _factory(*args: object, **kwargs: object) -> httpx.Client:
        kwargs["transport"] = transport
        return original_client(*args, **kwargs)

    monkeypatch.setattr(httpx, "Client", _factory)


def test_fetch_company_news_success(monkeypatch: pytest.MonkeyPatch) -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.params["token"] == "secret-key"
        assert request.url.params["symbol"] == "AAPL"
        return httpx.Response(200, json=_sample_news())

    _patch_client(monkeypatch, httpx.MockTransport(handler))

    client = FinnhubClient(api_key="secret-key")
    items = client.fetch_company_news("AAPL", date(2024, 1, 1), date(2024, 1, 10))

    assert len(items) == 1
    assert items[0].id == 101


def test_retries_then_success(monkeypatch: pytest.MonkeyPatch) -> None:
    call_count = 0

    def handler(_request: httpx.Request) -> httpx.Response:
        nonlocal call_count
        call_count += 1
        if call_count < 3:
            return httpx.Response(500, json={"error": "temporary"})
        return httpx.Response(200, json=_sample_news())

    _patch_client(monkeypatch, httpx.MockTransport(handler))
    monkeypatch.setattr("app.clients.finnhub.time.sleep", lambda _: None)
    monkeypatch.setattr("app.clients.finnhub.random.uniform", lambda _a, _b: 0.0)

    client = FinnhubClient(api_key="secret-key", max_attempts=3, backoff_base_seconds=0.01)
    items = client.fetch_company_news("AAPL", date(2024, 1, 1), date(2024, 1, 10))

    assert call_count == 3
    assert len(items) == 1


def test_timeout_retries_and_raises_transient(monkeypatch: pytest.MonkeyPatch) -> None:
    def handler(_request: httpx.Request) -> httpx.Response:
        raise httpx.ReadTimeout("timed out")

    _patch_client(monkeypatch, httpx.MockTransport(handler))
    monkeypatch.setattr("app.clients.finnhub.time.sleep", lambda _: None)

    client = FinnhubClient(api_key="secret-key", max_attempts=2)

    with pytest.raises(FinnhubTransientError):
        client.fetch_company_news("AAPL", date(2024, 1, 1), date(2024, 1, 10))


def test_429_retries_then_raises_transient(monkeypatch: pytest.MonkeyPatch) -> None:
    def handler(_request: httpx.Request) -> httpx.Response:
        return httpx.Response(429, json={"error": "rate limited"})

    _patch_client(monkeypatch, httpx.MockTransport(handler))
    monkeypatch.setattr("app.clients.finnhub.time.sleep", lambda _: None)

    client = FinnhubClient(api_key="secret-key", max_attempts=2)

    with pytest.raises(FinnhubTransientError):
        client.fetch_company_news("AAPL", date(2024, 1, 1), date(2024, 1, 10))


def test_400_raises_permanent_without_retry(monkeypatch: pytest.MonkeyPatch) -> None:
    call_count = 0

    def handler(_request: httpx.Request) -> httpx.Response:
        nonlocal call_count
        call_count += 1
        return httpx.Response(401, json={"error": "unauthorized"})

    _patch_client(monkeypatch, httpx.MockTransport(handler))

    client = FinnhubClient(api_key="secret-key", max_attempts=3)

    with pytest.raises(FinnhubPermanentError):
        client.fetch_company_news("AAPL", date(2024, 1, 1), date(2024, 1, 10))

    assert call_count == 1
