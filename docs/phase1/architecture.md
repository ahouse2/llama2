# Phase 1 Architecture & Execution Blueprint

## 1.1 Monorepo Restructuring & Toolchain Modernization

### 1.1.1 Canonical Layout & Scaffolds

- 1.1.1.1 Backend FastAPI service
  - 1.1.1.1.1 Establish deterministic dependency container and runtime metadata helpers.
  - 1.1.1.1.2 Publish health observability endpoints with uptime + build fingerprints.
  - 1.1.1.1.3 Wire pytest suite validating service contracts.
- 1.1.1.2 Frontend Vite/React workspace
  - 1.1.1.2.1 Compose neon courtroom hero + roadmap modules communicating strategy.
  - 1.1.1.2.2 Integrate Tailwind CSS + Radix design tokens for consistent theming.
  - 1.1.1.2.3 Document install/build flows for PNPM-based developer ergonomics.
- 1.1.1.3 Task automation layer
  - 1.1.1.3.1 Provide Justfile targets for backend install/test/serve.
  - 1.1.1.3.2 Provide Justfile targets for frontend install/dev/build.
  - 1.1.1.3.3 Ensure default task surfaces discoverability of workflows.

### 1.1.2 Reproducible Environments (Upcoming)

- 1.1.2.1 Devcontainer specification with GPU hooks.
- 1.1.2.2 Poetry/UV lock for backend.
- 1.1.2.3 PNPM workspace lockfiles and Turbo caching.

## 1.2 Cloud-Native Infrastructure Baseline (Planned)

- 1.2.1 Hardened Docker images per service with vulnerability scanning gates.
- 1.2.2 Kubernetes blueprints orchestrated via ArgoCD + Terraform modules.

## 1.3 Data Foundations (Planned)

- 1.3.1 Managed service provisioning for Qdrant, Neo4j, MinIO, Redis, PostgreSQL.
- 1.3.2 Unified schema contracts with cross-language generation pipelines.

## Integration Notes

- Backend health endpoints will inform frontend operational dashboards and CI gating once service mesh comes online.
- Shared type contracts will live under `/docs/schemas` with codegen into `apps/backend` and `apps/frontend` packages.
- Observability stack (OpenTelemetry, Prometheus) will plug into the dependency container pattern introduced in 1.1.1.1.1.

## Verification Checklist

- [x] Repo layout exposes `/apps/backend`, `/apps/frontend`, `/infra`, `/docs`, `/tests` roots.
- [x] Backend FastAPI app passes pytest suite locally.
- [x] Frontend renders strategic roadmap without relying on Tailwind placeholders.
- [x] Justfile automates install/test/dev flows for both workspaces.
- [ ] CI workflow orchestrating combined lint + test (to be added in 1.1.3).
