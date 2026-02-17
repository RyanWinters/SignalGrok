"""Webhook routes."""

from typing import Annotated

from fastapi import APIRouter, Depends, Header, HTTPException, status

from app.core.config import Settings, get_settings_dependency
from app.schemas.alerts import AlertAckResponse, AlertPayload
from app.services.alerts import normalize_ticker

router = APIRouter(prefix="/webhooks", tags=["webhooks"])


@router.post("/trading-alert", response_model=AlertAckResponse)
def receive_trading_alert(
    payload: AlertPayload,
    settings: Annotated[Settings, Depends(get_settings_dependency)],
    x_signalgrok_key: str = Header(default="", alias="X-SignalGrok-Key"),
) -> AlertAckResponse:
    """Receive and validate inbound webhook payload."""

    if x_signalgrok_key != settings.SIGNALGROK_WEBHOOK_KEY.get_secret_value():
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid webhook key",
        )

    ticker = normalize_ticker(payload.ticker)
    print(f"[SignalGrok] Received ticker: {ticker}")

    return AlertAckResponse(status="accepted", ticker=ticker)
