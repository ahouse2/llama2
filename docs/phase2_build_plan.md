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
