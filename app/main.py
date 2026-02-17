from fastapi import FastAPI

from app.api.routes.health import router as health_router
from app.api.routes.webhooks import router as webhook_router
from app.core.logging import configure_logging
from app.core.middleware import RequestContextMiddleware


def create_app() -> FastAPI:
    configure_logging()
    app = FastAPI(title="SignalGrok Webhook Receiver", version="0.2.0")
    app.add_middleware(RequestContextMiddleware)
    app.include_router(health_router)
    app.include_router(webhook_router)
    return app


app = create_app()
