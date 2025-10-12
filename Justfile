set shell := ["/bin/bash", "-c"]

@default:
just --list

backend-install:
cd apps/backend && python -m pip install -e .[dev]

backend-test:
cd apps/backend && pytest

backend-serve:
cd apps/backend && uvicorn justice_platform.app:get_app --reload

frontend-install:
cd apps/frontend && pnpm install

frontend-dev:
cd apps/frontend && pnpm dev

frontend-build:
cd apps/frontend && pnpm build
