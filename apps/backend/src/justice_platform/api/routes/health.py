"""Health and diagnostics endpoints."""

from __future__ import annotations

from fastapi import APIRouter, Depends

from ...services import ServiceContainer
from ..dependencies.container import get_container

router = APIRouter(prefix="/health", tags=["health"])


@router.get("/live", summary="Liveness probe", response_model=dict[str, str])
def live(container: ServiceContainer = Depends(get_container)) -> dict[str, str]:
    """Return instantaneous heartbeat information."""

    return {"status": "alive", "timestamp": container.clock.iso_now()}


@router.get("/ready", summary="Readiness probe", response_model=dict[str, object])
def ready(container: ServiceContainer = Depends(get_container)) -> dict[str, object]:
    """Expose runtime metadata to indicate operational readiness."""

    return {"status": "ready", "runtime": container.describe_runtime()}
