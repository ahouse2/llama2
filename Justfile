set shell := ["bash", "-lc"]

@default:
@just --list

# ----- Backend -----
backend-install:
cd apps/backend && poetry install

backend-lint:
cd apps/backend && poetry run ruff check app tests

backend-format:
cd apps/backend && poetry run black app tests

backend-typecheck:
cd apps/backend && poetry run mypy app

backend-test:
cd apps/backend && poetry run pytest

# ----- Frontend -----
frontend-install:
cd apps/frontend && npm install

frontend-lint:
cd apps/frontend && npm run lint

frontend-format:
cd apps/frontend && npm run format:write

frontend-typecheck:
cd apps/frontend && npm run typecheck

frontend-test:
cd apps/frontend && npm test

# ----- Integration Tests -----
integration-install:
cd tests && poetry install

integration-lint:
cd tests && poetry run ruff check integration

integration-test:
cd tests && poetry run pytest

# ----- Documentation -----
docs-mkdocs-serve:
cd docs && mkdocs serve

docs-docusaurus-start:
cd docs/docusaurus && npm install && npm run start

# ----- Quality Gates -----
structure-check:
python tools/check_workspace_structure.py

ci:
just structure-check
just backend-install
just backend-lint
just backend-typecheck
just backend-test
just frontend-install
just frontend-lint
just frontend-typecheck
just frontend-test
just integration-install
just integration-lint
just integration-test
