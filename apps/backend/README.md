# Justice Platform Backend

The Justice Platform backend is a modular FastAPI service that powers ingestion, retrieval, and simulation workflows for the reinvented legal discovery experience. This scaffold establishes a production-minded foundation with explicit dependency wiring, typed configuration, and health introspection.

## Features

- FastAPI application factory with structured settings management via `pydantic-settings`.
- Deterministic dependency container to provide services (e.g., clock, build metadata) to route handlers.
- Observability-friendly health endpoints exposing build, uptime, and configuration fingerprints.
- Pytest-enabled test suite exercising the HTTP contract for readiness checks.

## Getting Started

### Install

```bash
cd apps/backend
python -m venv .venv
source .venv/bin/activate
pip install -e .
```

For development extras:

```bash
pip install -e .[dev]
```

### Run

```bash
uvicorn justice_platform.app:get_app --reload
```

### Test

```bash
pytest
```

## Project Layout

```
src/justice_platform/
  app.py              # FastAPI factory, router registration, dependency overrides
  main.py             # CLI entrypoint with uvicorn bootstrap
  config.py           # Settings definitions and environment parsing
  core/runtime.py     # Runtime metadata helpers
  services/
    __init__.py
    container.py      # Deterministic service registry for dependency injection
    clock.py          # Time service powering health checks
  api/
    __init__.py
    dependencies/
      __init__.py
      container.py    # FastAPI dependency to access the service container
    routes/
      __init__.py
      health.py       # Readiness and liveness endpoints
```

## Environment Variables

| Variable | Description | Default |
| --- | --- | --- |
| `JUSTICE_PLATFORM_ENV` | Runtime environment name (`dev`, `staging`, `prod`) | `dev` |
| `JUSTICE_PLATFORM_COMMIT_SHA` | Git revision injected at build time | `unknown` |
| `JUSTICE_PLATFORM_BUILD_TS` | ISO8601 build timestamp | `unknown` |

## Next Steps

- Expand the service container with persistence, messaging, and analytics clients.
- Layer structured logging (structlog) and OpenTelemetry instrumentation.
- Integrate authentication/authorization modules before exposing stateful APIs.
