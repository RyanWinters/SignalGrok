from typing import Any

from pydantic import BaseModel, Field


class AlertPayload(BaseModel):
    alert_id: str | None = Field(default=None, description="Optional upstream alert id")
    signal: str = Field(..., description="Signal description, e.g. 'SPY MACD Crossover'")
    ticker: str = Field(..., min_length=1, max_length=10)
    direction: str | None = Field(default=None, description="bullish, bearish, etc")
    timeframe: str | None = Field(default=None, description="1m, 5m, 1h, etc")
    metadata: dict[str, Any] | None = Field(default=None)
