"""Logging setup."""

import logging

from app.core.config import Settings


def configure_logging(settings: Settings) -> None:
    level = "DEBUG" if settings.is_dev else settings.LOG_LEVEL.upper()
    logging.basicConfig(
        level=level,
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
    )
