"""Database helpers."""

from functools import lru_cache

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine

from app.models import metadata


@lru_cache
def get_engine(database_url: str) -> Engine:
    """Create and cache SQLAlchemy engine by database URL."""

    return create_engine(database_url, pool_pre_ping=True)


def init_db(database_url: str) -> None:
    """Initialize required database tables."""

    engine = get_engine(database_url)
    metadata.create_all(bind=engine)
