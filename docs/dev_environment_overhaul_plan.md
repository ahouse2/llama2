# Development Environment Modernization Plan

## 1. Vision
- Deliver a hermetic, cross-platform developer experience mirroring production stacks.
- Encode environment definitions via Dev Containers, Nix, and Docker to remove drift.
- Standardize package management with Poetry (Python) and pnpm (Node) plus reproducible lockfiles.
- Automate bootstrap flows and CI caching layers (uv & Turbo) for speed and determinism.

## 2. Workstreams
### 2.1 Tooling Orchestration
- **Devcontainer authoring**
  - Define base image & GPU toggle via features / build args.
  - Mount secrets using `mounts` with env var hydration.
  - Invoke backend/frontend bootstrap scripts from `postCreateCommand`.
- **Bootstrap scripts**
  - Author `scripts/bootstrap_backend.sh` and `scripts/bootstrap_frontend.sh`.
  - Ensure idempotent installs (Poetry + pnpm) and lint/test smoke hooks.

### 2.2 Package Managers & Lockfiles
- Backend: confirm Poetry configuration, enable uv cache integration.
- Integration tests: align Poetry config, share cache path.
- Frontend: migrate from npm to pnpm, regenerate lockfile, embed packageManager metadata.
- Docs site: adopt pnpm workspace membership, update scripts.
- Update Just recipes, docs, and CI invocation commands.

### 2.3 Deterministic Environments
- **Nix**
  - Provide `flake.nix` & `flake.lock` exposing devShell with Python, Poetry, uv, Node (pnpm), Docker CLI, just.
- **Docker**
  - Craft `infra/docker/Dockerfile.dev` modelling production dependencies.
  - Include docker-compose or README guidance if necessary.

### 2.4 Continuous Integration
- Expand GitHub Actions matrix for `ubuntu-latest`, `macos-latest`, `windows-latest`.
- Cache Poetry via uv & pnpm via Turbo cache (pnpm store) keyed on lockfiles.
- Run segmented jobs for backend, frontend, integration.
- Ensure matrix respects OS-specific shell semantics.

### 2.5 Documentation
- Author `/docs/development.md` describing Dev Container, pnpm/Poetry workflows, Nix & Docker usage, CI expectations.
- Embed troubleshooting matrix and GPU toggle guidance.
- Cross-link plan and highlight caching strategy.

## 3. Deliverables
- `.devcontainer/devcontainer.json` with GPU/secrets toggles & bootstrap.
- `scripts/bootstrap_backend.sh`, `scripts/bootstrap_frontend.sh` (plus helpers if needed).
- pnpm workspace config & lockfiles for frontend & docs.
- Updated Justfile, CI workflow, documentation.
- `flake.nix`, `flake.lock`, `infra/docker/Dockerfile.dev`.
- Verified CI matrix definitions & local bootstrap instructions.

## 4. Validation Strategy
- Run `just backend-test`, `just frontend-test`, `just integration-test` post-migration.
- Execute `pnpm install` and `pnpm lint` locally to confirm workspace wiring.
- Use `nix develop` to ensure shells build on Linux container.
- Lint `devcontainer.json` via `devcontainer validate` (if available) or schema check.
- Ensure documentation builds with `mkdocs build` or `pnpm --filter docs build` as smoke tests.

## 5. Risk Mitigation
- Maintain backups of original lockfiles during migration for fallback.
- Use pinned tool versions (Poetry, pnpm, uv) within Dev Container/Nix to avoid drift.
- Document OS-specific quirks (path separators, `core.autocrlf`).
- Validate GPU optional path to avoid breakage when GPU unavailable.

## 6. Timeline & Iteration Loops
- Iteration 1: Introduce scripts & pnpm workspace; regenerate lockfiles; adjust Justfile.
- Iteration 2: Update CI pipeline and caching; ensure tests pass cross-platform.
- Iteration 3: Add Dev Container + environment artifacts (Nix/Docker).
- Iteration 4: Finalize documentation, run verification suite, polish.

## 7. Personal Notes
- Favor `uv pip install --system` semantics only where Poetry interop is proven; otherwise rely on Poetry env mgmt.
- Evaluate `pnpm dlx turbo` adoption; if overkill, configure pnpm cache + optional `turbo` entry for future adoption.
- Provide extra flourish in docs with decision tree diagrams referencing this plan.
