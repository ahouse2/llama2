# Discovery Intelligence Platform Workspace

This monorepo houses the automation, orchestration, and experience layers for the automated legal discovery platform. Each application is developed in isolation but wired together through a shared task runner, canonical documentation, and infrastructure as code.

## Workspace Layout

```
.
├── apps
│   ├── backend      # FastAPI microservices managed with Poetry
│   └── frontend     # React + Vite console styled with Tailwind CSS + Radix UI
├── docs             # MkDocs (ops) + Docusaurus (product) documentation systems
├── infra            # Terraform modules and Helm charts for platform provisioning
├── tests            # Cross-application integration suites (Pytest + HTTPX)
└── tools            # Repository automation, including structure validation
```

Each workspace includes an in-depth README with stack notes, bootstrap commands, and contribution standards.

## Bootstrapping by Workspace

### Backend (`apps/backend`)
```bash
just backend-install
just backend-test
```
Expose the API locally via `poetry run uvicorn app.main:app --reload` once dependencies are installed.

### Frontend (`apps/frontend`)
```bash
just frontend-install
just frontend-test
just frontend-typecheck
```
Start the Vite dev server with `npm run dev`.

### Integration Tests (`tests`)
```bash
just integration-install
just integration-test
```

### Documentation (`docs`)
- MkDocs runbooks: `just docs-mkdocs-serve`
- Docusaurus knowledge base: `just docs-docusaurus-start`

### Infrastructure (`infra`)
```bash
cd infra/terraform
terraform init
terraform plan -var-file=envs/dev/terraform.tfvars
```
Helm releases ship from `infra/helm/platform`:
```bash
helm upgrade --install discovery infra/helm/platform \
  --namespace discovery --create-namespace \
  --values infra/helm/platform/values-dev.yaml
```

## Automation via `just`

The root [`Justfile`](Justfile) orchestrates formatting, linting, type-checking, and tests across every workspace:

```bash
just install-all        # Install backend, frontend, and integration dependencies
just lint-all           # Ruff + ESLint coverage
just typecheck-all      # mypy + TypeScript checks
just format-check-all   # Black/Prettier/Ruff format verification
just test-all           # Backend, frontend, and integration test suites
just check-all          # Runs structure validation + all quality gates
just ci                 # Installs dependencies then executes the full quality stack
```

Run `just --list` to discover every available recipe, including workspace-specific format writers.

## Continuous Integration Guardrails

- [`tools/check_workspace_structure.py`](tools/check_workspace_structure.py) enforces the canonical directory layout and validates critical configuration (dependencies, README content, Terraform/Helm markers).
- `just ci` mirrors the CI pipeline by running structure validation, linting, formatting checks, type-checking, and tests after installing dependencies.
- Documentation and infrastructure directories are versioned to prevent drift between deployment assets and runtime services.
