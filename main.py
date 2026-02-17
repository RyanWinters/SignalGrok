"""SignalGrok webhook receiver bootstrap.

Run locally:
    uvicorn main:app --reload
"""

from __future__ import annotations

import os
from typing import Any

from fastapi import FastAPI, Header, HTTPException, status
from pydantic import BaseModel, Field

app = FastAPI(title="SignalGrok Webhook Receiver", version="0.1.0")


class AlertPayload(BaseModel):
    """Normalized inbound trading alert payload."""

    alert_id: str | None = Field(default=None, description="Optional upstream alert id")
    signal: str = Field(..., description="Signal description, e.g. 'SPY MACD Crossover'")
    ticker: str = Field(..., min_length=1, max_length=10)
    direction: str | None = Field(default=None, description="bullish, bearish, etc")
    timeframe: str | None = Field(default=None, description="1m, 5m, 1h, etc")
    metadata: dict[str, Any] | None = Field(default=None)


@app.get("/health", tags=["system"])
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/webhooks/trading-alert", tags=["webhooks"])
def receive_trading_alert(
    payload: AlertPayload,
    x_signalgrok_key: str = Header(default="", alias="X-SignalGrok-Key"),
) -> dict[str, str]:
    """Receive and validate inbound webhook payload."""

    expected_key = os.getenv("SIGNALGROK_WEBHOOK_KEY", "")
    if not expected_key:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Webhook key not configured on server",
        )

    if x_signalgrok_key != expected_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid webhook key",
        )

    ticker = payload.ticker.upper().strip()
    print(f"[SignalGrok] Received ticker: {ticker}")

    return {"status": "accepted", "ticker": ticker}
