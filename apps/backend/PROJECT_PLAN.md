# Backend Packaging Refactor Roadmap

- Phase α: Reconnaissance & Constraints Enumeration
  - Step α.1: Inspect existing `pyproject.toml` for structural issues and metadata gaps.
  - Step α.2: Identify repository-wide tooling expectations (Phase 1 decision on Poetry + UV lock discipline).
  - Step α.3: Confirm absence of directory-specific agent instructions impacting backend packaging work.

- Phase β: Target Architecture Blueprint
  - Step β.1: Define canonical `[project]` metadata schema (name, version, description, readme, authors, classifiers).
  - Step β.2: Curate authoritative runtime dependency list for the backend core service.
  - Step β.3: Design extras taxonomy consolidating API and test capabilities under `[project.optional-dependencies]`.
  - Step β.4: Select build backend interface consistent with repo mandate (Poetry + `poetry-core`).
  - Step β.5: Outline lockfile generation strategy (`poetry lock` rooted in `apps/backend`).

- Phase γ: Implementation Orchestration
  - Step γ.1: Rewrite `pyproject.toml` adhering to PEP 621 with a single `[project]` table.
  - Step γ.2: Add `[project.optional-dependencies]` with validated lists and properly closed arrays.
  - Step γ.3: Introduce `[tool.poetry]` stanza mirroring canonical metadata and package inclusion semantics.
  - Step γ.4: Preserve/refresh `[build-system]` block targeting `poetry-core`.
  - Step γ.5: Generate `poetry.lock`, ensuring deterministic resolution and compatibility with extras.

- Phase δ: Verification & Quality Gates
  - Step δ.1: Create isolated virtual environment dedicated to packaging validation.
  - Step δ.2: Execute `pip install .[tests,api]` from repository root with environment activated.
  - Step δ.3: Run `python -m compileall app` post-install to verify import graph integrity.
  - Step δ.4: Destroy or deactivate validation environment to avoid repository contamination.

- Phase ε: Review & Polish
  - Step ε.1: Manually re-read modified files twice to confirm formatting, metadata accuracy, and dependency completeness.
  - Step ε.2: Run `poetry check` (if available) to lint configuration semantics; fall back to syntactic inspection otherwise.
  - Step ε.3: Stage artifacts (`pyproject.toml`, `poetry.lock`, `PROJECT_PLAN.md`) and produce concise commit message.
  - Step ε.4: Prepare PR summary aligning with repo narrative and instructions.

- Phase ζ: Runtime Integrity Remediation
  - Step ζ.1: Execute `python -m compileall apps/backend/app` to enumerate syntax, indentation, and merge-conflict remnants.
  - Step ζ.2: Catalogue every failing module (config, database, schemas, services) and map them to responsible subsystems.
  - Step ζ.3: Decide authoritative implementation per subsystem (SQLAlchemy persistence, Pydantic schemas, asyncio ingestion) to avoid duplicated paradigms.

- Phase η: Module Reconstruction Blueprint
  - Step η.1: Redesign `config.py` around a single `pydantic-settings`-powered configuration object with directory bootstrapping guarantees.
  - Step η.2: Rebuild `database.py` to expose a coherent SQLAlchemy ORM, UTC helpers, and safe session/context utilities.
  - Step η.3: Consolidate `schemas.py` and all service modules (parser, OCR, classifier, retrieval, timeline, agents, ingestion) by removing conflicting definitions and implementing the chosen architecture end-to-end.
  - Step η.4: Review FastAPI routes and tests to ensure they target the reconstructed APIs.

- Phase θ: Implementation & Validation
  - Step θ.1: Refactor modules iteratively, running `python -m compileall apps/backend/app` after each cluster of changes to catch regressions immediately.
  - Step θ.2: Re-run backend tests (`pytest apps/backend/tests`) once compilation succeeds to validate behavioural coherence.
  - Step θ.3: Perform a final lint/read-through cycle ensuring type hints, docstrings, and logging are consistent.
