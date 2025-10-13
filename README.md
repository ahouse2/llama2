Automated Legal Discovery Platform (Enterprise-Grade Skeleton)

This repo contains a production-ready scaffold for an enterprise Automated Legal Discovery Platform per the TRD/PRP. Phase 2 delivers the intelligence and workflow engines described in the roadmap.

## Phase 2 Highlights

- **Asynchronous Prefect ingestion** with checksum validation, OCR fallback (Tesseract), metadata extraction, and retry-aware dead letter queues.
- **Semantic parsing + rule-driven classification** that computes document types, privilege risk, and importance scoring while persisting structured fragments to SQLite and a persisted NetworkX knowledge graph.
- **Hybrid retrieval service** blending TF-IDF similarity with graph proximity scoring, exposing JSON and streaming APIs for conversational agents.
- **Multi-agent orchestrator** driven by a YAML registry that records conversation memory, governs tool usage, and adds sentiment-aware tone modulation.
- **Timeline synthesizer** exporting chronological CSV summaries to support downstream analytics.

## Quick Start (Backend)

```bash
cd apps/backend
python -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows
pip install -e .[tests]
uvicorn app.main:app --reload
```

Set environment variables to relocate storage directories or database connection if desired. Defaults write to `../storage` relative to the backend package.

## API Surface

- `POST /api/ingest/upload` – upload a document and trigger an ingestion flow.
- `POST /api/ingest/folder` – recursively ingest a directory of evidence.
- `GET /api/ingest/runs` / `GET /api/ingest/dead_letters` – operator dashboards for orchestration visibility.
- `POST /api/retrieval/search` – hybrid semantic search with typed filters.
- `POST /api/retrieval/stream` – newline-delimited streaming results with timeline context.
- `POST /api/agents/delegate` – invoke the multi-agent network for grounded responses.

## Testing

```bash
cd apps/backend
pytest
```

The test suite provisions an isolated SQLite database and validates end-to-end ingestion, retrieval, and agent delegation flows.

