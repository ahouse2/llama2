"""Dependency injection helpers for FastAPI routes."""

from __future__ import annotations

from fastapi import Depends, Request

from ...config import AppConfig, get_config
from ...services import ServiceContainer


def _build_container(config: AppConfig) -> ServiceContainer:
    return ServiceContainer(config=config)


def get_container(
    request: Request, config: AppConfig = Depends(get_config)
) -> ServiceContainer:
    """Provide the shared service container instance."""

    if not hasattr(request.app.state, "container"):
        request.app.state.container = _build_container(config)
    return request.app.state.container  # type: ignore[return-value]
