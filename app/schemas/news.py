"""Schemas for Finnhub news responses."""

from pydantic import BaseModel, Field


class RawNewsItem(BaseModel):
    """Typed representation of a Finnhub company-news item."""

    category: str
    datetime: int = Field(..., description="Unix timestamp in seconds")
    headline: str
    id: int
    image: str
    related: str
    source: str
    summary: str
    url: str
