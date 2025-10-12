"""Runtime metadata helpers."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict

from ..config import AppConfig


def runtime_fingerprint(config: AppConfig, started_at: datetime) -> Dict[str, Any]:
    """Build a fingerprint describing build identity and uptime."""

    now = datetime.now(timezone.utc)
    uptime_seconds = (now - started_at).total_seconds()
    return {
        "environment": config.environment,
        "commit_sha": config.commit_sha,
        "build_timestamp": config.build_timestamp,
        "started_at": started_at.isoformat(),
        "observed_at": now.isoformat(),
        "uptime_seconds": uptime_seconds,
    }
