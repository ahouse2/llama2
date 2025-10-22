# Integration Test Suites

This workspace centralizes integration scenarios that span multiple services. Tests run against the FastAPI backend using an in-memory database and HTTPX clients.

## Tooling
- **Poetry** defines dependencies in `pyproject.toml`.
- **Pytest** orchestrates asynchronous tests via `pytest-asyncio`.
- **Ruff** enforces linting across the integration suite.

## Running Tests
```bash
cd tests
poetry install
poetry run pytest
```

## Writing New Tests
1. Create a module under `integration/` describing the workflow under test.
2. Use fixtures from `conftest.py` to bootstrap HTTP clients and test data.
3. Assert on API responses as well as side effects observed through the backend persistence layer.
