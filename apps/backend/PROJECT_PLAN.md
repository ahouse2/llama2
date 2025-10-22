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

- Phase ι: Merge-Drift Remediation Blueprint
  - Step ι.1: Catalogue target modules (`schemas.py`, `services/agents.py`, `services/retrieval.py`) and identify orphaned stubs or duplicate constructs that diverge from the authoritative implementation.
    - Substep ι.1.a: Compare dataclass and service definitions against current runtime expectations to ensure a single canonical form remains.
    - Substep ι.1.b: Trace persistence interactions in each module, flagging any legacy JSON-session hooks for replacement with SQLAlchemy `Session` usage from `app.database`.
  - Step ι.2: Re-assess deterministic tooling requirements (sentiment analyser initialisation, Prefect hooks, TF-IDF retriever) to guarantee consistent imports at module scope and reproduceable behaviour.
    - Substep ι.2.a: Document any missing imports or lazy initialisations needing restoration.
    - Substep ι.2.b: Validate Prefect flow hook wiring and retriever loading semantics for determinism.

- Phase κ: Implementation Decomposition
  - Step κ.1: Update `app/schemas.py` to prune redundant dataclass stubs, retaining a single authoritative Pydantic model per payload while preserving validation semantics.
    - Substep κ.1.a: Ensure metadata defaults leverage `Field(default_factory=...)` for mutable values.
    - Substep κ.1.b: Align schema names with downstream service expectations to avoid breaking imports.
  - Step κ.2: Refactor `app/services/agents.py` to consolidate agent orchestration logic.
    - Substep κ.2.a: Reintroduce deterministic sentiment tooling and Prefect flow hooks at module scope.
    - Substep κ.2.b: Replace any stale persistence helpers with the canonical SQLAlchemy session context.
    - Substep κ.2.c: Guarantee that `AgentOrchestrator.delegate` operates against the restored service registry.
  - Step κ.3: Rebuild `app/services/retrieval.py` around the hybrid TF-IDF retriever implementation.
    - Substep κ.3.a: Remove placeholder dataclasses and ensure the `HybridRetriever` exposes deterministic artefact loading.
    - Substep κ.3.b: Confirm all ORM interactions utilise `get_session()`.
    - Substep κ.3.c: Reinstate graph-manager integration and metadata enrichment utilities.

- Phase λ: Regression Safeguards
  - Step λ.1: Design smoke-style tests under `apps/backend/tests` that import target modules and execute representative calls (`AgentOrchestrator.delegate`, `HybridRetriever.search`, schema instantiation) to detect future merge drift.
    - Substep λ.1.a: Mock external side effects (file I/O, Prefect hooks) where necessary while keeping behaviour realistic.
    - Substep λ.1.b: Ensure tests seed in-memory SQLite database fixtures that exercise SQLAlchemy paths deterministically.
  - Step λ.2: Confirm test coverage by running the backend test suite and verifying all modules import successfully post-refactor.

- Phase μ: Quality Gate & Delivery
  - Step μ.1: Perform multi-pass code review personally, verifying adherence to repository standards and absence of placeholder logic.
  - Step μ.2: Execute relevant tooling (`python -m compileall`, `pytest`) capturing output for reporting.
  - Step μ.3: Stage and commit changes with a descriptive message, prepare PR summary referencing restored deterministic tooling and regression tests.
