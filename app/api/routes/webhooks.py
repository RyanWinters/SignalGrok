import logging

from fastapi import APIRouter, Depends, Header, HTTPException, status

from app.core.config import Settings, get_settings
from app.schemas.alerts import AlertPayload

router = APIRouter(prefix="/webhooks", tags=["webhooks"])
logger = logging.getLogger("signalgrok.webhook")


@router.post("/trading-alert")
def receive_trading_alert(
    payload: AlertPayload,
    x_signalgrok_key: str = Header(default="", alias="X-SignalGrok-Key"),
    settings: Settings = Depends(get_settings),
) -> dict[str, str]:
    if x_signalgrok_key != settings.signalgrok_webhook_key:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid webhook key")

    ticker = payload.ticker.upper().strip()
    logger.info("received_alert", extra={"ticker": ticker})
    return {"status": "accepted", "ticker": ticker}
