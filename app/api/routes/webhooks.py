"""Webhook routes."""

from fastapi import APIRouter, Header, HTTPException, status

from app.core.config import get_settings
from app.schemas.alerts import AlertAckResponse, AlertPayload
from app.services.alerts import normalize_ticker

router = APIRouter(prefix="/webhooks", tags=["webhooks"])


@router.post("/trading-alert", response_model=AlertAckResponse)
def receive_trading_alert(
    payload: AlertPayload,
    x_signalgrok_key: str = Header(default="", alias="X-SignalGrok-Key"),
) -> AlertAckResponse:
    """Receive and validate inbound webhook payload."""

    settings = get_settings()
    if not settings.signalgrok_webhook_key:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Webhook key not configured on server",
        )

    if x_signalgrok_key != settings.signalgrok_webhook_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid webhook key",
        )

    ticker = normalize_ticker(payload.ticker)
    print(f"[SignalGrok] Received ticker: {ticker}")

    return AlertAckResponse(status="accepted", ticker=ticker)
