# Automated Legal Discovery Platform Reinvention

This repository houses the next-generation build-out of the Automated Legal Discovery Platform. Phase 1 focuses on establishing a disciplined monorepo architecture, production-grade service scaffolds, and ergonomic tooling that enable rapid yet reliable iteration for the intelligence layers to follow.

## Monorepo Layout

```
apps/
  backend/    # FastAPI service powering core APIs and health diagnostics
  frontend/   # Vite + React experience layer with neon courtroom storytelling
infra/        # Infrastructure-as-code, container, and cloud blueprints (in progress)
docs/         # Architecture notes, roadmaps, and schema plans
reports/      # Due diligence artifacts from Phase 0
tests/        # Centralized automated test suites
```

## Phase 1 Highlights

### Backend (`apps/backend`)

- FastAPI application factory with deterministic dependency injection via a handcrafted `ServiceContainer`.
- Runtime fingerprinting utilities that expose environment, commit, build timestamp, and uptime through `/health/ready`.
- Liveness endpoint `/health/live` returning precise UTC timestamps for observability pipelines.
- Pytest suite validating the health contract to guard against regressions.

### Frontend (`apps/frontend`)

- Vite + React workspace rendering the Phase 1 strategic narrative with Tailwind CSS + Radix-powered neon theming.
- Modular composition (`HeroPanel`, `MilestoneRoadmap`) ready to expand into chat, timeline, and simulation views.
- TypeScript-first configuration with strict mode, shared design primitives, and documented PNPM workflows.

### Tooling

- Root `Justfile` orchestrating installation, testing, development servers, and production builds across workspaces.
- Hierarchical execution blueprint at `docs/phase1/architecture.md` tracking completion state and upcoming objectives.

## Getting Started

### Backend

```bash
cd apps/backend
python -m venv .venv
source .venv/bin/activate
pip install -e .[dev]
uvicorn justice_platform.app:get_app --reload
```

Run backend tests from the repo root:

```bash
PYTHONPATH=apps/backend/src pytest tests/backend
```

### Frontend

```bash
cd apps/frontend
pnpm install
pnpm dev
```

Visit http://localhost:5173 to explore the Phase 1 roadmap experience. Build production assets with `pnpm build`.

## Roadmap & Status

- Phase 0 due diligence artifacts remain available under `reports/` for auditability; execution has shifted to Phase 1 per stakeholder directive.
- Phase 1 deliverables and verification checklist live in `docs/phase1/architecture.md` and `ROADMAP.md`.
- Upcoming work: devcontainer + Poetry/PNPM locks, Docker/Kubernetes baselines, and shared schema contracts.

## Contributing

1. Install dependencies via the Justfile targets (`just backend-install`, `just frontend-install`).
2. Keep commits focused and reference roadmap identifiers in messages.
3. Ensure backend tests pass (`just backend-test`) and capture frontend visual diffs for UX-impacting changes.
