"""FastAPI app entrypoint for SignalGrok.

Run locally:
    uvicorn app.main:app --reload
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes.health import router as health_router
from app.api.routes.webhooks import router as webhooks_router
from app.core.config import get_settings
from app.core.logging import configure_logging


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Load and validate settings at startup."""

    settings = get_settings()
    app.state.settings = settings
    configure_logging(settings)
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

    app.include_router(health_router)
    app.include_router(webhooks_router)
    return app


app = create_app()
