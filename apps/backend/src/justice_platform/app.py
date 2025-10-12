"""FastAPI application factory."""

from __future__ import annotations

from fastapi import FastAPI

from . import api
from .config import AppConfig, get_config
from .services import ServiceContainer


def create_app(config: AppConfig | None = None) -> FastAPI:
    """Create and configure the FastAPI application."""

    cfg = config or get_config()
    container = ServiceContainer(cfg)
    app = FastAPI(
        title="Justice Platform Backend",
        version="0.1.0",
        description="API surface for the automated legal discovery platform.",
    )

    app.state.container = container
    api.register_routes(app)
    return app


def get_app() -> FastAPI:
    """Return an application instance for ASGI servers."""

    return create_app()
