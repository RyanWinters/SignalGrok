"""Webhook routes."""

import logging
from typing import Annotated

from fastapi import APIRouter, Depends, Header, HTTPException, status

from app.core.config import Settings, get_settings_dependency
from app.schemas.alerts import AlertAckResponse, AlertPayload
from app.services.alerts import normalize_alert, persist_incoming_alert

router = APIRouter(prefix="/webhooks", tags=["webhooks"])
logger = logging.getLogger(__name__)


@router.post("/trading-alert", response_model=AlertAckResponse)
def receive_trading_alert(
    payload: AlertPayload,
    settings: Annotated[Settings, Depends(get_settings_dependency)],
    x_signalgrok_key: str = Header(default="", alias="X-SignalGrok-Key"),
) -> AlertAckResponse:
    """Receive, authenticate, normalize, and persist inbound trading alerts."""

    if x_signalgrok_key != settings.SIGNALGROK_WEBHOOK_KEY.get_secret_value():
        logger.warning(
            "webhook_alert_rejected",
            extra={
                "route": "/webhooks/trading-alert",
                "method": "POST",
                "status": status.HTTP_401_UNAUTHORIZED,
                "outcome": "invalid_key",
            },
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized",
        )

    normalized = normalize_alert(payload)
    persist_result = persist_incoming_alert(
        database_url=settings.DATABASE_URL,
        webhook_endpoint_id=str(settings.WEBHOOK_ENDPOINT_ID),
        payload=payload,
        normalized=normalized,
    )

    logger.info(
        "webhook_alert_processed",
        extra={
            "route": "/webhooks/trading-alert",
            "method": "POST",
            "status": status.HTTP_200_OK,
            "outcome": "duplicate" if persist_result.duplicate else "accepted",
            "ticker": normalized.ticker,
            "signal_type": normalized.signal_type,
        },
    )

    return AlertAckResponse(
        status="accepted",
        ticker=normalized.ticker,
        signal_type=normalized.signal_type,
        duplicate=persist_result.duplicate,
    )
