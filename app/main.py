"""FastAPI app entrypoint for SignalGrok.

Run locally:
    uvicorn app.main:app --reload
"""

from __future__ import annotations

import logging
import time
from contextlib import asynccontextmanager
from uuid import uuid4

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.routes.health import router as health_router
from app.api.routes.webhooks import router as webhooks_router
from app.core.config import get_settings
from app.core.db import init_db
from app.core.logging import (
    configure_logging,
    reset_request_id,
    sanitize_headers,
    set_request_id,
)

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Load and validate settings at startup."""

    settings = get_settings()
    app.state.settings = settings
    configure_logging(settings)
    init_db(settings.DATABASE_URL)
    yield


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(
        title="SignalGrok Webhook Receiver",
        version="0.1.0",
        debug=settings.debug,
        lifespan=lifespan,
    )

    if settings.is_dev:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
    else:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=settings.cors_origins,
            allow_credentials=False,
            allow_methods=["POST"],
            allow_headers=["X-SignalGrok-Key", "Content-Type"],
        )

    @app.middleware("http")
    async def request_context_middleware(request: Request, call_next):
        request_id = request.headers.get("X-Request-ID") or str(uuid4())
        set_request_id(request_id)
        request.state.request_id = request_id

        start = time.perf_counter()
        status_code = 500
        try:
            response = await call_next(request)
            status_code = response.status_code
            response.headers["X-Request-ID"] = request_id
            return response
        finally:
            duration_ms = (time.perf_counter() - start) * 1000
            logger.info(
                "request_completed",
                extra={
                    "request_id": request_id,
                    "route": request.url.path,
                    "method": request.method,
                    "status": status_code,
                    "duration_ms": duration_ms,
                    "headers": sanitize_headers(dict(request.headers.items())),
                },
            )
            reset_request_id()

    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        request_id = getattr(request.state, "request_id", "-")
        logger.exception(
            "unhandled_exception",
            extra={
                "request_id": request_id,
                "route": request.url.path,
                "method": request.method,
                "status": 500,
            },
            exc_info=exc,
        )
        return JSONResponse(
            status_code=500,
            content={
                "error": {
                    "code": "internal_error",
                    "message": "Internal server error",
                    "request_id": request_id,
                }
            },
            headers={"X-Request-ID": request_id},
        )

    app.include_router(health_router)
    app.include_router(webhooks_router)
    return app


app = create_app()
