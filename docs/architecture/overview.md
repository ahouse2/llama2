# Architecture Overview

The platform is organized as a constellation of micro-applications orchestrated through shared data contracts.

## Applications
- **Backend (`apps/backend`)** — FastAPI services orchestrating retrieval, ingestion, and graph analytics.
- **Frontend (`apps/frontend`)** — React interface offering analysts a unified operations console.
- **Docs (`docs`)** — MkDocs + Docusaurus hybrid documentation stack.

## Cross-Cutting Concerns
- **Observability:** Prefect instrumentation, OpenTelemetry traces (planned), and automated pipeline status surfacing in the frontend.
- **Security:** Role-based access, encrypted storage, and audit trails enforced at the service layer.
- **Automation:** Justfile-driven workflows guarantee consistent lint, test, and build steps across the repo.
