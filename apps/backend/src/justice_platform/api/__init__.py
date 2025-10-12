"""API routers for the Justice Platform backend."""

from fastapi import FastAPI

from .routes import health


def register_routes(app: FastAPI) -> None:
    """Attach all API routers to the FastAPI app."""

    app.include_router(health.router)
