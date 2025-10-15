# Infrastructure Stack

This workspace codifies infrastructure using **Terraform** for cloud primitives and **Helm** for Kubernetes workload orchestration. The goal is reproducible, auditable environments across development, staging, and production.

## Terraform
- Root module: `infra/terraform`
- Environment overlays: `infra/terraform/envs/<environment>`
- State backend: remote (Terraform Cloud or S3) configured in `backend.tf`

### Usage
```bash
cd infra/terraform
terraform init
terraform plan -var-file=envs/dev/terraform.tfvars
terraform apply -var-file=envs/dev/terraform.tfvars
```

The root module wires the new `modules/platform` package, which provisions the Kubernetes namespace and ArgoCD GitOps assets. Override the namespace, labels, and ArgoCD topology through `platform_namespace*` and `argocd_config` variables inside each environment tfvars file.

## Helm
- Chart: `infra/helm/platform`
- Values per environment stored in `infra/helm/platform/values-<environment>.yaml`

### Usage
```bash
helm dependency update infra/helm/platform
helm upgrade --install discovery infra/helm/platform \
  --namespace discovery --create-namespace \
  --values infra/helm/platform/values-dev.yaml
```

The chart now deploys three workloads:

1. **Backend API** (`*-backend` Deployment/Service/HPA) with OpenTelemetry defaults and Prometheus scrape annotations.
2. **Worker agent** (`*-worker` Deployment/HPA) tuned for Prefect queue processing.
3. **Frontend SPA** (`*-frontend` Deployment/Service/HPA) served by the hardened distroless Node runtime.

Each workload exposes environment-specific knobs in `values.yaml`, including autoscaling policies, ingress routing, and telemetry wiring. When ArgoCD is enabled, the Helm release can be managed via the generated `AppProject` and `Application` manifests.

## Container Images
- Dockerfiles live in `infra/docker`:
  - `backend.Dockerfile`: multi-stage build that compiles Python/Poetry dependencies, vendors OCR libraries, and publishes a distroless runtime.
  - `worker.Dockerfile`: shares the hardened Python toolchain with a Prefect-focused command surface.
  - `frontend.Dockerfile`: builds the Vite SPA with pnpm and packages a non-root distroless Node server.

Build locally with BuildKit:

```bash
docker build -f infra/docker/backend.Dockerfile -t discovery-backend:dev .
docker build -f infra/docker/worker.Dockerfile -t discovery-worker:dev .
docker build -f infra/docker/frontend.Dockerfile -t discovery-frontend:dev .
```

## Observability Assets
- OpenTelemetry Collector configuration: `infra/observability/opentelemetry/collector-config.yaml`
- Prometheus scrape configuration & recording rules: `infra/observability/prometheus/`
- Grafana dashboards: `infra/observability/grafana/dashboards/`

Mount these assets into your cluster observability stack to ingest OTLP signals, scrape metrics from the backend/worker services, and visualize key service-level indicators out-of-the-box.

## Conventions
1. Terraform modules must specify provider versions and remote state locking.
2. Helm charts enforce resource requests/limits and provide liveness/readiness probes.
3. CI pipelines execute validation (`terraform fmt -check`, `terraform validate`, `helm lint`) before deployment.
