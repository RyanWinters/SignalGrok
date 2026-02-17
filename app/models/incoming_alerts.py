"""Incoming alert persistence model."""

from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4

from sqlalchemy import JSON, Column, DateTime, MetaData, String, Table, UniqueConstraint

metadata = MetaData()

incoming_alerts = Table(
    "incoming_alerts",
    metadata,
    Column("id", String(36), primary_key=True, default=lambda: str(uuid4())),
    Column("webhook_endpoint_id", String(36), nullable=False, index=True),
    Column("external_alert_id", String(255), nullable=True),
    Column("raw_payload", JSON, nullable=False),
    Column("ticker", String(16), nullable=False, index=True),
    Column("signal_type", String(64), nullable=False),
    Column("direction", String(16), nullable=True),
    Column("status", String(32), nullable=False, default="RECEIVED"),
    Column(
        "received_at",
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    ),
    UniqueConstraint(
        "webhook_endpoint_id",
        "external_alert_id",
        name="uq_incoming_alerts_endpoint_external",
    ),
)
