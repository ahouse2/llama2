# Discovery Intelligence Platform Workspace

This monorepo houses the automation, orchestration, and experience layers for the automated legal discovery platform. Each application is developed in isolation but wired together through a shared task runner, canonical documentation, and infrastructure as code.

## Workspace Layout
- `apps/backend` — FastAPI microservices exposing ingestion, retrieval, and agent orchestration APIs. Managed with Poetry.
- `apps/frontend` — React + Vite console with Tailwind CSS and Radix UI components for analyst workflows.
- `docs` — Hybrid documentation stack: MkDocs for operational runbooks and Docusaurus for product knowledge.
- `infra` — Terraform modules and Helm charts that provision persistent infrastructure and deploy workloads.
- `tests` — Cross-application integration suites targeting the deployed services.
- `tools` — Repository automation utilities including structure validation.

## Bootstrap Instructions
### Backend
```bash
cd apps/backend
poetry install
poetry run uvicorn app.main:app --reload
```

### Frontend
```bash
cd apps/frontend
npm install
npm run dev
```

### Documentation
- MkDocs: `cd docs && mkdocs serve`
- Docusaurus: `cd docs/docusaurus && npm install && npm run start`

### Infrastructure
```bash
cd infra/terraform
terraform init
terraform plan -var-file=envs/dev/terraform.tfvars
```

Helm deployments live in `infra/helm/platform` and can be applied via:
```bash
helm upgrade --install discovery infra/helm/platform \
  --namespace discovery --create-namespace \
  --values infra/helm/platform/values-dev.yaml
```

### Integration Tests
```bash
cd tests
poetry install
poetry run pytest
```

## Task Runner
The root [`Justfile`](Justfile) coordinates linting, formatting, type-checking, testing, and documentation workflows:

```bash
just backend-lint
just frontend-test
just integration-test
just ci
```

Use `just` to list available recipes. The `just ci` aggregate mirrors the checks enforced in continuous integration.

## Continuous Integration Guarantees
- `tools/check_workspace_structure.py` fails fast if any canonical directory or configuration is missing.
- Linting, formatting, type-checking, and test suites run across backend, frontend, and integration workspaces.
- Infrastructure and documentation directories are versioned to prevent drift between code and deployment assets.
