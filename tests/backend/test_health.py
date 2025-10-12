from __future__ import annotations

from fastapi.testclient import TestClient

from justice_platform.app import create_app


def test_live_endpoint_returns_timestamp() -> None:
    client = TestClient(create_app())

    response = client.get("/health/live")

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "alive"
    assert payload["timestamp"].endswith("Z") or payload["timestamp"].endswith("+00:00")


def test_ready_endpoint_reports_runtime() -> None:
    client = TestClient(create_app())

    response = client.get("/health/ready")

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "ready"
    runtime = payload["runtime"]
    assert runtime["environment"] == "dev"
    assert "uptime_seconds" in runtime
    assert runtime["commit_sha"] == "unknown"
