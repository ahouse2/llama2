# Infrastructure & Observability Enhancements Roadmap

## Vision
- Deliver production-grade containerization, supply-chain security, and operational visibility for the discovery platform.

## Phase 1: Container Hardening
- ### Backend service image
  - #### Requirements
    - ##### Adopt multi-stage builds with dependency isolation.
    - ##### Enforce non-root execution and drop shell utilities.
    - ##### Preserve OCR dependencies (Tesseract, PDFium) across stages.
  - #### Tasks
    - ##### Build base stage with Poetry, system libraries, and cached wheels.
    - ##### Bake runtime venv and application sources into distroless final stage.
    - ##### Provide uvicorn entrypoint exposing health probes on port 8080.
- ### Worker image
  - #### Requirements
    - ##### Share dependency graph with backend to avoid drift.
    - ##### Ship Prefect CLI and flow assets with non-root default user.
  - #### Tasks
    - ##### Assemble identical builder workflow as backend.
    - ##### Configure Prefect work queue, concurrency tuning, and telemetry env defaults.
- ### Frontend image
  - #### Requirements
    - ##### Compile SPA via pnpm with reproducible lockfiles.
    - ##### Serve production assets through hardened Node HTTP server on distroless base.
  - #### Tasks
    - ##### Stage pnpm install/build with corepack in Node builder image.
    - ##### Embed lightweight server.mjs with security headers and compression.
    - ##### Expose port 4173 with health endpoint for readiness.

## Phase 2: Supply-Chain CI Pipeline
- ### Container matrix workflow
  - #### Objectives
    - ##### Build backend, worker, frontend images in parallel using Buildx cache.
    - ##### Run Trivy vulnerability scans with critical/severity gating.
    - ##### Execute Snyk container scans when token is available.
    - ##### Generate SPDX SBOMs and publish as workflow artifacts.

## Phase 3: Platform Orchestration Templates
- ### Helm chart evolution
  - #### Deliverables
    - ##### Namespace manifest for `discovery` workloads.
    - ##### Backend Deployment + Service with HPA + ServiceMonitor.
    - ##### Worker Deployment with autoscaling tuned to queue depth metrics.
    - ##### Frontend Deployment + Service + optional ingress.
    - ##### ArgoCD Application definitions for GitOps promotion.
- ### Terraform modules
  - #### Deliverables
    - ##### Parameterized module for namespaces, service accounts, and network policies.
    - ##### Module for ArgoCD Application + Project to bootstrap GitOps flows.
    - ##### Outputs for Grafana datasource and Prometheus service endpoints.

## Phase 4: Observability Defaults
- ### OpenTelemetry collector
  - #### Goals
    - ##### Define OTLP gRPC/HTTP exporters pointing at central observability stack.
    - ##### Configure batch/span processors with resource attributes.
- ### Prometheus integration
  - #### Goals
    - ##### Provide scrape configs for backend/worker pods and Prefect metrics.
    - ##### Publish recording rules for request latency and queue depth.
- ### Grafana assets
  - #### Goals
    - ##### Dashboard for API throughput, error ratios, and OCR latency.
    - ##### Dashboard for worker queue depth, flow success rates, and resource saturation.

## Phase 5: Documentation
- ### Ops README updates
  - #### Items
    - ##### Document image build targets and runtime env vars.
    - ##### Explain CI security workflow outputs.
    - ##### Link observability configs and dashboards for quick import.
