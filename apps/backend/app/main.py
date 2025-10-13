"""FastAPI application entrypoint."""

from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .api.routes import agents, ingestion, retrieval
from .config import settings
from .database import init_db


def create_app() -> FastAPI:
    app = FastAPI(title="Automated Legal Discovery Backend", version="0.1.0")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    init_db()

    app.include_router(ingestion.router)
    app.include_router(retrieval.router)
    app.include_router(agents.router)

    @app.get("/health")
    async def health() -> dict[str, str]:
        return {"status": "ok"}

    return app


app = create_app()
