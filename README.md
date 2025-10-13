# Automated Legal Discovery Platform (Phase 2 Foundations)


This repository provides a focused, fully functional slice of the intelligence layer for the automated legal discovery platform. The backend exposes ingestion, retrieval, and agent orchestration services designed to run in a minimal Python environment without external ML dependencies.

## Phase 2 Highlights

- **Asynchronous ingestion coroutine** that computes checksums, parses structured metadata, optionally runs OCR if available, and stores results in a JSON-backed persistence layer.
- **Deterministic parsing and classification** using regular expressions and keyword heuristics with metadata fan-out into a lightweight knowledge graph.
- **Hybrid retrieval service** combining TF-IDF style term weighting with graph-derived boosts and metadata filters.
- **Timeline synthesizer** that aggregates date fragments into chronologically ordered exports for downstream review.
- **Multi-agent orchestrator** that consults retrieval and timeline services, applies sentiment-aware tone selection, and records every response for traceability.

This repo contains a production-ready scaffold for an enterprise Automated Legal Discovery Platform per the TRD/PRP. Phase 2 delivers the intelligence and workflow engines described in the roadmap.

## Quick Start (Backend)

```bash
cd apps/backend
python -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows
pip install -e .[tests]    # add .[api] if you want to expose FastAPI endpoints
```

The service modules can be exercised directly from the REPL or through the test suite. API endpoints are optional; installing the `.[api]` extra enables FastAPI routing in `app/api`.

## Running Tests


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

The tests execute an end-to-end ingestion, retrieval, and agent delegation flow against an isolated temporary workspace.
