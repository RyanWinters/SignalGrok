"""FastAPI app entrypoint for SignalGrok.

Run locally:
    uvicorn app.main:app --reload
"""

from fastapi import FastAPI

from app.api.routes.health import router as health_router
from app.api.routes.webhooks import router as webhooks_router
from app.core.logging import configure_logging

configure_logging()

app = FastAPI(title="SignalGrok Webhook Receiver", version="0.1.0")
app.include_router(health_router)
app.include_router(webhooks_router)
