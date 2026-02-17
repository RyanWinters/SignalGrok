"""Alert service helpers."""

from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import datetime, timezone
from uuid import uuid4

from sqlalchemy import insert
from sqlalchemy.exc import IntegrityError

from app.core.db import get_engine
from app.models import incoming_alerts
from app.schemas.alerts import AlertPayload, NormalizedAlert

_DIRECTION_MAP = {
    "bull": "BULLISH",
    "bullish": "BULLISH",
    "buy": "BULLISH",
    "long": "BULLISH",
    "bear": "BEARISH",
    "bearish": "BEARISH",
    "sell": "BEARISH",
    "short": "BEARISH",
}


@dataclass
class PersistResult:
    alert_id: str
    duplicate: bool


def normalize_ticker(raw_ticker: str) -> str:
    return raw_ticker.strip().upper()


def normalize_signal_type(raw_signal: str) -> str:
    compact = re.sub(r"[^A-Za-z0-9]+", "_", raw_signal.strip().upper())
    return re.sub(r"_+", "_", compact).strip("_")


def normalize_direction(raw_direction: str | None) -> str | None:
    if raw_direction is None:
        return None
    return _DIRECTION_MAP.get(raw_direction.strip().lower())


def normalize_alert(payload: AlertPayload) -> NormalizedAlert:
    return NormalizedAlert(
        external_alert_id=payload.alert_id,
        ticker=normalize_ticker(payload.ticker),
        signal_type=normalize_signal_type(payload.signal),
        direction=normalize_direction(payload.direction),
        timeframe=payload.timeframe.strip().lower() if payload.timeframe else None,
        received_at=payload.timestamp or datetime.now(timezone.utc),
    )


def persist_incoming_alert(
    *,
    database_url: str,
    webhook_endpoint_id: str,
    payload: AlertPayload,
    normalized: NormalizedAlert,
) -> PersistResult:
    engine = get_engine(database_url)
    alert_id = str(uuid4())
    stmt = insert(incoming_alerts).values(
        id=alert_id,
        webhook_endpoint_id=webhook_endpoint_id,
        external_alert_id=normalized.external_alert_id,
        raw_payload=payload.model_dump(mode="json"),
        ticker=normalized.ticker,
        signal_type=normalized.signal_type,
        direction=normalized.direction,
        status="RECEIVED",
        received_at=normalized.received_at,
    )

    try:
        with engine.begin() as connection:
            connection.execute(stmt)
    except IntegrityError:
        duplicate_id = f"duplicate:{webhook_endpoint_id}:{normalized.external_alert_id}"
        return PersistResult(alert_id=duplicate_id, duplicate=True)

    return PersistResult(alert_id=alert_id, duplicate=False)
