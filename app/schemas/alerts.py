"""Alert request and response schemas."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class AlertPayload(BaseModel):
    """Inbound trading alert payload."""

    alert_id: str | None = Field(default=None, description="Optional upstream alert id")
    signal: str = Field(..., min_length=1, description="Signal description")
    ticker: str = Field(..., min_length=1, max_length=10)
    direction: str | None = Field(default=None, description="bullish, bearish, buy, sell")
    timeframe: str | None = Field(default=None, description="1m, 5m, 1h, etc")
    timestamp: datetime | None = Field(default=None, description="Alert trigger timestamp")
    metadata: dict[str, Any] | None = Field(default=None)


class NormalizedAlert(BaseModel):
    """Normalized and DB-ready alert contract."""

    external_alert_id: str | None
    ticker: str
    signal_type: str
    direction: str | None
    timeframe: str | None
    received_at: datetime


class AlertAckResponse(BaseModel):
    """Webhook acknowledgement payload."""

    status: str
    ticker: str
    signal_type: str
    duplicate: bool = False
