Automated Legal Discovery Platform (Enterprise-Grade Skeleton)

This repo contains a production-ready scaffold for an enterprise Automated Legal Discovery Platform per the TRD/PRP. It includes:

- Backend API (`FastAPI`) with modular services for ingestion, indexing, retrieval, and knowledge graph
- Frontend (`React + Vite + TypeScript`) neon-styled chat UI, uploads, search, and document viewer
- Infra (`docker-compose`) with Qdrant (vector DB), Neo4j (graph DB), MinIO (object storage), and Redis (jobs)

Quick Start

- Copy `.env.example` to `.env` and set keys
- Start infra: `docker compose -f infra/docker-compose.yml up -d`
- Backend (local): `cd apps/backend && python -m venv .venv && .venv/Scripts/Activate.ps1 && pip install -r requirements.txt && uvicorn app.main:app --reload`
- Frontend (local): `cd apps/frontend && corepack enable && pnpm i && pnpm dev`

Structure

- `apps/backend`: FastAPI app, service modules, and API routes
- `apps/frontend`: Vite React app with chat, upload, search, and viewer
- `infra/docker-compose.yml`: Dev stack (Qdrant, Neo4j, MinIO, Redis)
- `storage/`: Local document storage (mounted volume)

Backend Overview

- Endpoints: `/ingest`, `/search`, `/chat`, `/documents/{id}`, `/graph/entity/{id}`
- Services: `IngestionService`, `IndexService` (vector), `RetrievalService` (RAG), `GraphService` (KG)
- Pluggable providers via env (OpenAI, Qdrant, Neo4j, MinIO); graceful in-memory fallbacks

Frontend Overview

- Neon-themed chat with citations that open the document viewer
- Upload new evidence; auto-indexing feedback via toasts
- Search panel with semantic results and metadata chips

Environment Variables

- `OPENAI_API_KEY` (optional)
- `QDRANT_URL`, `QDRANT_API_KEY` (optional)
- `NEO4J_URI`, `NEO4J_USER`, `NEO4J_PASSWORD` (optional)
- `MINIO_ENDPOINT`, `MINIO_ACCESS_KEY`, `MINIO_SECRET_KEY`, `MINIO_BUCKET`
- `REDIS_URL` (optional)

Notes

- This is a robust scaffold with working stubs. Swap stub implementations with production providers incrementally.
- See inline `TODO:` markers for suggested next steps.

