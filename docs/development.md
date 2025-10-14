# Development Environment Guide

This guide codifies the reproducible developer experience for the project across Linux, macOS, and Windows.

## 1. Toolchains at a Glance
- **Python**: 3.11 with Poetry `1.8.3` as the project manager.
- **Node.js**: 20.12.x managed by `pnpm 8.15.6` inside a multi-package workspace (`apps/frontend`, `docs/docusaurus`).
- **Task runners**: `just` for Python orchestration, `turbo` for cached pnpm pipelines.
- **Accelerators**: `uv` pre-fetches Python wheels; the pnpm store and Turbo outputs are cached in CI and local shells.

## 2. Bootstrap Workflow
### 2.1 Scripts
The repository ships two idempotent bootstrappers:

| Script | Purpose |
| --- | --- |
| `scripts/bootstrap_backend.sh` | Installs/updates Poetry, syncs `apps/backend` and `tests`, optional test execution via `BOOTSTRAP_RUN_TESTS=1`. |
| `scripts/bootstrap_frontend.sh` | Enables pnpm via corepack, installs workspace dependencies, runs lint/test smoke checks when `BOOTSTRAP_RUN_TESTS=1`. |

Each script respects environment overrides (`POETRY_VERSION`, `PNPM_VERSION`, `BOOTSTRAP_INSTALL_INTEGRATION`).

Run both scripts from the repository root:

```bash
./scripts/bootstrap_backend.sh
./scripts/bootstrap_frontend.sh
```

### 2.2 Manual Install (if you opt out of scripts)
1. Install Poetry `1.8.3`: `python -m pip install poetry==1.8.3` and export `POETRY_VIRTUALENVS_CREATE=false`.
2. Install pnpm: `corepack enable pnpm && corepack prepare pnpm@8.15.6 --activate`.
3. Sync dependencies:
   ```bash
   poetry -C apps/backend install --sync
   poetry -C tests install --sync
   pnpm install --frozen-lockfile
   ```
4. Run quality gates:
   ```bash
   poetry -C apps/backend run ruff check app tests
   poetry -C apps/backend run mypy app
   poetry -C apps/backend run black --check app tests
   poetry -C apps/backend run pytest
   pnpm exec turbo run lint --filter=legal-discovery-frontend
   pnpm exec turbo run typecheck --filter=legal-discovery-frontend
   pnpm exec turbo run test --filter=legal-discovery-frontend
   pnpm exec turbo run lint --filter=discovery-docs
   ```

## 3. Dev Container
A full-featured container definition lives at `.devcontainer/devcontainer.json`.

### Highlights
- **GPU toggle**: set `DEVCONTAINER_GPU_MODE=all` locally to enable `--gpus` flag; default is `none`.
- **Secret mounts**: drop secrets into `.devcontainer/secrets/` on your host; they bind-mount to `/workspaces/llama2/.secrets`.
- **Post-create bootstrap**: automatically runs the backend and frontend bootstrappers.
- **VS Code extras**: Python, Ruff, ESLint, and Prettier extensions are pre-installed with formatting on save.

### Usage
1. Install the [Dev Containers](https://aka.ms/vscode-remote/download/devcontainer-cli) extension or CLI.
2. From the repo root, run:
   ```bash
   devcontainer up --workspace-folder .
   ```
3. To skip GPU runtime: do nothing (default `--gpus=none`). To enable: `DEVCONTAINER_GPU_MODE=all devcontainer up ...`.
4. Populate `.devcontainer/secrets/` with files such as `openai.key` or `.env`; only `.gitkeep` is committed.

## 4. Deterministic Environments
### 4.1 Docker Image
- **Location**: `infra/docker/Dockerfile.dev`
- **Contents**: Ubuntu 22.04 base with Python 3.11, Poetry 1.8.3, Node 20.12.2, pnpm 8.15.6, uv 0.4.18, and just.
- **Bootstrap**: Installs backend/tests dependencies via Poetry and the entire pnpm workspace with `--frozen-lockfile`.
- **Usage**:
  ```bash
  docker build -f infra/docker/Dockerfile.dev -t llama2-dev .
  docker run --rm -it -v "$(pwd)":/workspace -w /workspace llama2-dev bash
  ```
  Pass `--gpus all` at `docker run` time if your host has NVIDIA drivers.

### 4.2 Nix Flake
- **Files**: `flake.nix`, `flake.lock` pinning `nixpkgs` via FlakeHub to rev `b1b3291469652d5a2edb0becc4ef0246fff97a7c`.
- **Dev shells**: `nix develop` exposes Poetry, Node 20 + pnpm, uv (auto-downloaded per platform), Docker CLI, and just for all major Darwin/Linux architectures.
- **Usage**:
  ```bash
  nix develop         # defaults to your host system
  nix develop .#x86_64-linux   # cross-shell if needed
  ```

## 5. Continuous Integration
The GitHub Actions workflow (`.github/workflows/ci.yml`) runs across **ubuntu-latest**, **macos-latest**, and **windows-latest** with these stages:

1. Install Python 3.11 and configure uv with cache hydration.
2. Install Poetry 1.8.3, prefetch wheels using uv, and sync backend/tests environments.
3. Install Node 20.12.2 + pnpm 8.15.6; restore pnpm and Turbo caches.
4. Execute backend lint/typecheck/format/test gates, integration pytest, and pnpm Turbo pipelines for frontend/docs.

### Cache Strategy
- **uv**: Managed by `astral-sh/setup-uv`, keyed off Poetry manifests to reuse downloaded wheels.
- **pnpm/Turbo**: Uses `actions/cache` for `~/.pnpm-store` and the `.turbo` directory keyed by the workspace lockfile.

## 6. Local Testing Matrix
To mirror CI locally:

| Command | Description |
| --- | --- |
| `just backend-test` | Backend pytest suite. |
| `just frontend-test` | pnpm workspace test target (Vitest). |
| `just integration-test` | Integration pytest suite. |
| `pnpm exec turbo run lint` | Lint every workspace package with caching. |
| `nix develop` | Drop into the pinned toolchain shell if you use Nix. |

## 7. Troubleshooting
- **Poetry virtualenv confusion**: ensure `POETRY_VIRTUALENVS_CREATE=false` is exported (devcontainer and Nix shells set it automatically).
- **pnpm complaining about node linkage**: rerun `corepack prepare pnpm@8.15.6 --activate`.
- **uv download rate limits**: the bootstrap scripts and Nix shell both install uv on demand; set `UV_CACHE_DIR` to a persistent location to reuse archives.
- **GPU runtime errors**: confirm Docker/Dev Container CLI is >= 0.55 and NVIDIA drivers are exposed; fallback to CPU by omitting `DEVCONTAINER_GPU_MODE`.

## 8. Decision Ledger
- Adopted pnpm workspaces + Turbo for deterministic Node pipelines.
- Standardized Poetry 1.8.3 with uv caching to accelerate CI and local reinstalls.
- Authored Dev Container, Dockerfile, and Nix flake so Linux/macOS/Windows developers converge on a single dependency stack.
