from datetime import datetime, timezone

from app.schemas.alerts import AlertPayload
from app.services.alerts import (
    normalize_alert,
    normalize_direction,
    normalize_signal_type,
    normalize_ticker,
)


def test_normalize_ticker() -> None:
    assert normalize_ticker(" spy ") == "SPY"


def test_normalize_signal_type() -> None:
    assert normalize_signal_type("SPY MACD Crossover") == "SPY_MACD_CROSSOVER"


def test_normalize_direction_mapping() -> None:
    assert normalize_direction("buy") == "BULLISH"
    assert normalize_direction("bearish") == "BEARISH"
    assert normalize_direction("unknown") is None


def test_normalize_alert_is_deterministic() -> None:
    ts = datetime(2025, 1, 2, 3, 4, 5, tzinfo=timezone.utc)
    payload = AlertPayload(
        alert_id="external-1",
        signal=" SPY MACD Crossover ",
        ticker=" spy ",
        direction="long",
        timeframe=" 5M ",
        timestamp=ts,
    )

    normalized = normalize_alert(payload)
    assert normalized.external_alert_id == "external-1"
    assert normalized.ticker == "SPY"
    assert normalized.signal_type == "SPY_MACD_CROSSOVER"
    assert normalized.direction == "BULLISH"
    assert normalized.timeframe == "5m"
    assert normalized.received_at == ts
