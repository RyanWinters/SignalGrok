"""Structured logging setup and helpers."""

from __future__ import annotations

import contextvars
import json
import logging
from datetime import datetime, timezone
from typing import Any

from app.core.config import Settings

SERVICE_NAME = "signalgrok-api"
REQUEST_ID_CTX_KEY = "request_id"
_request_id_ctx_var: contextvars.ContextVar[str] = contextvars.ContextVar(
    REQUEST_ID_CTX_KEY,
    default="-",
)

SENSITIVE_HEADERS = {
    "authorization",
    "cookie",
    "set-cookie",
    "x-signalgrok-key",
    "x-api-key",
}


class RequestContextFilter(logging.Filter):
    """Attach request-scoped defaults to every log record."""

    def filter(self, record: logging.LogRecord) -> bool:
        record.request_id = get_request_id()
        record.service = SERVICE_NAME
        return True


class JsonFormatter(logging.Formatter):
    """Format log records in JSON for easier ingestion/search."""

    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, Any] = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "service": getattr(record, "service", SERVICE_NAME),
            "logger": record.name,
            "message": record.getMessage(),
            "request_id": getattr(record, "request_id", get_request_id()),
            "route": getattr(record, "route", None),
            "method": getattr(record, "method", None),
            "status": getattr(record, "status", None),
        }

        if hasattr(record, "duration_ms"):
            payload["duration_ms"] = round(float(record.duration_ms), 2)
        if hasattr(record, "headers"):
            payload["headers"] = record.headers

        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)

        return json.dumps(payload, default=str)


def configure_logging(settings: Settings) -> None:
    """Configure root logging handlers and formatters."""

    level = "DEBUG" if settings.is_dev else settings.LOG_LEVEL.upper()

    root_logger = logging.getLogger()
    root_logger.handlers.clear()
    handler = logging.StreamHandler()
    handler.setFormatter(JsonFormatter())
    handler.addFilter(RequestContextFilter())

    root_logger.addHandler(handler)
    root_logger.setLevel(level)


def set_request_id(request_id: str) -> None:
    _request_id_ctx_var.set(request_id)


def get_request_id() -> str:
    return _request_id_ctx_var.get()


def reset_request_id() -> None:
    _request_id_ctx_var.set("-")


def sanitize_headers(headers: dict[str, str]) -> dict[str, str]:
    """Mask sensitive header values prior to logging."""

    sanitized: dict[str, str] = {}
    for key, value in headers.items():
        if key.lower() in SENSITIVE_HEADERS:
            sanitized[key] = "***"
        else:
            sanitized[key] = value
    return sanitized
