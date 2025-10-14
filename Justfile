set shell := ["bash", "-lc"]

@default:
@just --list

# ----- Backend -----
backend-install:
    cd apps/backend && poetry install

backend-lint:
    cd apps/backend && poetry run ruff check app tests

backend-format-write:
    cd apps/backend && poetry run black app tests

backend-format-check:
    cd apps/backend && poetry run black --check app tests

backend-typecheck:
    cd apps/backend && poetry run mypy app

backend-test:
    cd apps/backend && poetry run pytest

# ----- Frontend -----
frontend-install:
    cd apps/frontend && npm install

frontend-lint:
    cd apps/frontend && npm run lint

frontend-format-write:
    cd apps/frontend && npm run format:write

frontend-format-check:
    cd apps/frontend && npm run format

frontend-typecheck:
    cd apps/frontend && npm run typecheck

frontend-test:
    cd apps/frontend && npm run test

# ----- Integration Tests -----
integration-install:
    cd tests && poetry install

integration-lint:
    cd tests && poetry run ruff check integration

integration-format-write:
    cd tests && poetry run ruff format integration

integration-format-check:
    cd tests && poetry run ruff format --check integration

integration-test:
    cd tests && poetry run pytest

# ----- Documentation -----
docs-mkdocs-serve:
    cd docs && mkdocs serve

docs-docusaurus-start:
    cd docs/docusaurus && npm install && npm run start

# ----- Aggregate Workflows -----
install-all:
    just backend-install
    just frontend-install
    just integration-install

lint-all:
    just backend-lint
    just frontend-lint
    just integration-lint

typecheck-all:
    just backend-typecheck
    just frontend-typecheck

format-write-all:
    just backend-format-write
    just frontend-format-write
    just integration-format-write

format-check-all:
    just backend-format-check
    just frontend-format-check
    just integration-format-check

test-all:
    just backend-test
    just frontend-test
    just integration-test

# ----- Quality Gates -----
structure-check:
    python tools/check_workspace_structure.py

check-all:
    just structure-check
    just lint-all
    just typecheck-all
    just format-check-all
    just test-all

ci:
    just install-all
    just check-all
