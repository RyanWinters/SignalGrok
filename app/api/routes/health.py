"""System health routes."""

from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from app.core.config import Settings, get_settings_dependency
from app.core.db import get_engine

router = APIRouter(tags=["system"])


@router.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@router.get("/health/database")
def database_health(settings: Settings = Depends(get_settings_dependency)) -> JSONResponse:
    engine = get_engine(settings.DATABASE_URL)
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
    except SQLAlchemyError as exc:
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={"status": "error", "detail": str(exc)},
        )

    return JSONResponse(status_code=status.HTTP_200_OK, content={"status": "ok"})
