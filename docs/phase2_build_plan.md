# Phase 2 Build Plan: Intelligence & Workflow Engines

## Objectives
- Deliver a dependable ingestion workflow that processes local evidence files, enriches metadata, and persists results without external orchestration dependencies.
- Provide deterministic retrieval, timeline, and agent orchestration services that operate entirely on locally persisted artefacts.
- Maintain complete traceability for every automated action through lightweight storage primitives.

## Milestones

### 2.1 Document Ingestion Pipeline
- Implement coroutine-based ingestion that performs checksum computation, MIME detection, parsing, optional OCR, classification, and persistence in a single transaction.
- Store documents, metadata fragments, and ingestion run ledgers inside a JSON-backed datastore to avoid heavyweight database requirements.
- Emit knowledge-graph edges for entities, dates, emails, and monetary amounts so downstream retrieval can exploit structural signals.

### 2.2 Retrieval-Augmented Intelligence Layer
- Build a TF-IDF style retriever that recalculates document vectors on demand and augments relevance scores with graph-based bonuses and metadata filters.
- Generate contextual snippets and highlight metadata hits for every search result to support citeable responses.
- Produce CSV timeline exports summarising date fragments for quick historical reviews.

### 2.3 Agent Orchestration
- Load agent definitions from disk (JSON) and execute retrieval/timeline tools per agent role.
- Apply rule-based sentiment detection to modulate tone and record conversation memory for each trace.
- Ensure every delegation call returns citations pointing back to ingested document identifiers.

## Quality Gates
- Comprehensive pytest coverage for ingestion, retrieval, and agent delegation flows operating in an isolated temporary workspace.
- Deterministic heuristics and reproducible metadata extraction with no reliance on external network calls.

## Delivery Checklist
- Update README with minimal setup instructions and optional extras for the HTTP API.
- Refresh roadmap checkboxes to reflect the subset of Phase 2 functionality that is now complete.
- Commit and tag artifacts once tests pass locally.

- Phase 2 Overview
  - Mission: Implement robust ingestion, retrieval, and agent orchestration capabilities that transform uploaded discovery materials into actionable intelligence with auditable provenance.
  - Guiding Constraints
    - Maintain deterministic, testable modules (no placeholders, every component production-capable out of the gate).
    - Ensure atomic persistence across storage layers (relational + graph + search index).
    - Provide operator observability (runs, retries, dead-letter queue visibility).

- 2.1 Document Ingestion Pipeline MVP
  - 2.1.1 Asynchronous Ingestion Orchestrator (Prefect-based)
    - 2.1.1.1 Input Surfaces
      - Upload API (`/api/ingest/upload`) — streaming multipart uploads → durable storage.
      - Folder sync trigger (`/api/ingest/folder`) — recursively enumerate directories and enqueue flows.
      - Programmatic trigger (`/api/ingest/trigger`) — accept JSON payload referencing remote URIs / metadata.
    - 2.1.1.2 Flow Architecture
      - Prefect flow `ingest_document_flow` orchestrates checksum → parsing → OCR → enrichment → persistence.
      - Prefect tasks instrumented with retries/backoff (`prefect.task(retries=N, retry_delay_seconds=...)`).
      - Concurrent execution via asyncio + Prefect task runner (async-native flow implementation).
    - 2.1.1.3 Operational Resilience
      - Dead-letter queue persisted in SQLite with failure metadata & stack traces.
      - Ingestion run ledger capturing timestamps, duration, throughput metrics.
      - FastAPI operator dashboard endpoints: `/api/ingest/runs`, `/api/ingest/dead_letters`.
  - 2.1.2 Semantic Parsing & Classification Services
    - 2.1.2.1 Metadata Extraction
      - Parser pipeline supporting TXT + PDF (PyPDF) with fallback OCR for image-based PDFs.
      - Regex + statistical heuristics for entity extraction (dates, parties, monetary amounts).
      - Normalization utilities (timezone-aware date parsing, currency normalization).
    - 2.1.2.2 Classification Engines
      - Document type classifier (rule-based + TF-IDF logistic fallback) for contracts, emails, pleadings, financials.
      - Privilege risk scorer using keyword scoring & structural signals.
      - Importance ranking using summarized features (entity counts, deadlines, novelty vs corpus centroid).
    - 2.1.2.3 Atomic Persistence
      - SQLAlchemy ORM for relational storage (`Document`, `IngestionRun`, `MetadataFragment`).
      - NetworkX-backed knowledge graph persisted to disk (`storage/graph.gpickle`).
      - Transaction boundary ensures document + metadata + graph edges commit together.

- 2.2 Retrieval-Augmented Intelligence Layer
  - 2.2.1 Hybrid Retrieval Service
    - 2.2.1.1 Query Planner
      - Combine TF-IDF cosine similarity with graph proximity scoring (entity overlap) and metadata filters.
      - Support boolean filters (date range, doc type) derived from request payload.
    - 2.2.1.2 Contextual Reranking & Citation Verification
      - Cross-scorer using scikit-learn Ridge regression on features (semantic score, entity match, recency).
      - Citation verifier ensures returned snippets reference stored spans; fall back to high-fidelity segments.
    - 2.2.1.3 API Surface
      - `/api/retrieval/search` returns typed JSON (Pydantic schemas) with trace IDs.
      - `/api/retrieval/stream` streams newline-delimited JSON chunks for conversational agents.
  - 2.2.2 Multi-Agent Orchestration (Autogen-inspired)
    - 2.2.2.1 Configuration DSL
      - YAML-driven agent registry describing roles, tools, and escalation policies.
      - Loader converts DSL into runtime `Agent` objects with capabilities (retrieval, summarization, ingestion commands).
    - 2.2.2.2 Memory & Tool Governance
      - Conversation memory persisted per trace ID (SQLite table) with summary + full transcript.
      - Tool access control enforced via capability matrix; unauthorized requests raise audited events.
    - 2.2.2.3 Automated Evaluations
      - Unit tests simulating delegation scenarios (retrieval query, ingestion follow-up) verifying grounding & citations.
  - 2.2.3 Co-Counsel Agent Network Integrations
    - 2.2.3.1 Shared Memory Fabric
      - Connect agents to hybrid store (retriever + graph) through typed service interfaces.
    - 2.2.3.2 GraphRAG Query Engine
      - Graph traversal utilities to collect related documents/entities for agent prompts.
    - 2.2.3.3 Temporal Awareness
      - Timeline summarizer aligning events chronologically for conversation context injection.
    - 2.2.3.4 Emotion Controller Hook
      - Sentiment analysis stub integrated with responses (real classification using VADER lexicon).

- 2.3 Knowledge Graph & Analytics Foundations
  - 2.3.1 Graph Extraction Pipeline
    - Triple extraction deriving `(entity, relation, target)` from parser metadata.
    - Confidence scoring & optional human review queue persisted in DB.
    - Neo4j-compatible export (CSV) for future integration.
  - 2.3.2 Analytics Modules
    - Timeline synthesizer computing event sequences & contradiction alerts.
    - Privilege risk trend dashboard (aggregate metrics from classification outputs).

- Quality Gates & Testing Strategy
  - Pytest suite covering ingestion (text + OCR fallback) and hybrid retrieval scoring.
  - Deterministic fixtures for classification heuristics and agent delegation flows.
  - Integration smoke test exercising FastAPI endpoints via TestClient.

- Delivery Checklist
  - Implement code per modules above with inline documentation and type hints.
  - Generate migration script to initialize SQLite schema on startup.
  - Update README with backend usage instructions (Phase 2 scope).
  - Commit code and produce PR summary once test suite passes.
