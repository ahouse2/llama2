"""Deterministic service container."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

from ..config import AppConfig
from ..core.runtime import runtime_fingerprint
from .clock import ClockService


@dataclass(slots=True)
class ServiceContainer:
    """Simple dependency injection container for backend services."""

    config: AppConfig
    started_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    _clock: ClockService = field(init=False, repr=False)

    def __post_init__(self) -> None:
        self._clock = ClockService()

    @property
    def clock(self) -> ClockService:
        """Return the singleton clock service."""

        return self._clock

    def describe_runtime(self) -> dict[str, Any]:
        """Expose runtime fingerprint for diagnostics."""

        return runtime_fingerprint(self.config, self.started_at)
