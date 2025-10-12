"""Time-related services."""

from __future__ import annotations

from datetime import datetime, timezone


class ClockService:
    """Provides monotonic, timezone-aware timestamps for observability."""

    def now(self) -> datetime:
        """Return the current UTC timestamp."""

        return datetime.now(timezone.utc)

    def iso_now(self) -> str:
        """Return the current UTC timestamp in ISO8601 format."""

        return self.now().isoformat()
