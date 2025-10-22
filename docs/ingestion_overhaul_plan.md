# Ingestion Overhaul Master Blueprint

## Phase Ω — Situational Awareness
- ### Chapter Ω.1 — Repository Forensics
  - #### Paragraph Ω.1.a — Dependency Cartography
    - ##### Sentence Ω.1.a.i — Enumerate existing ingestion packages and Prefect flow registries before modification.
      - ###### Character Ω.1.a.i.α — Use `poetry show --tree` inside `apps/backend` to map loader, OCR, and storage dependencies.
      - ###### Character Ω.1.a.i.β — Capture baseline versions for LlamaIndex, Prefect, PDFium bindings, pytesseract, boto3, and CourtListener clients.
    - ##### Sentence Ω.1.a.ii — Snapshot current ingestion DAG definitions, checksum utilities, and storage abstractions.
      - ###### Character Ω.1.a.ii.α — Audit `apps/backend/src/ingestion` for loader orchestration, dedupe, and persistence touchpoints.
      - ###### Character Ω.1.a.ii.β — Identify existing mock or placeholder parsers earmarked for replacement to avoid regression surprises.
  - #### Paragraph Ω.1.b — Observability Baseline
    - ##### Sentence Ω.1.b.i — Instrument temporary logging to benchmark current ingestion latency and success ratios for regression comparison.
      - ###### Character Ω.1.b.i.α — Capture Prefect task runtimes and failure counts via `prefect deployment ls` and ad-hoc flow runs.
      - ###### Character Ω.1.b.i.β — Store baseline metrics in `reports/ingestion_baseline.md` for future deltas.

## Phase I — Loader and Storage Renaissance
- ### Chapter I.1 — LlamaIndex Loader Convergence
  - #### Paragraph I.1.a — Directory Loader Integration
    - ##### Sentence I.1.a.i — Replace bespoke directory walkers with `SimpleDirectoryReader` configured for recursive traversal and metadata hydration.
      - ###### Character I.1.a.i.α — Inject checksum pre-filter hook leveraging SHA-256 digests persisted in managed ledger table `ingestion_checksums`.
      - ###### Character I.1.a.i.β — Preserve file permission masks and original paths within document metadata for downstream auditability.
    - ##### Sentence I.1.a.ii — Validate loader resilience across mixed filetypes (PDF, image, JSON) using golden-path fixtures.
      - ###### Character I.1.a.ii.α — Extend integration tests to assert metadata propagation (size, modified_at, checksum) after ingestion.
  - #### Paragraph I.1.b — S3 Loader Federation
    - ##### Sentence I.1.b.i — Configure `S3Reader` with session-scoped boto3 clients honoring IAM role chaining and retry policies.
      - ###### Character I.1.b.i.α — Parameterize bucket/prefix selection via Prefect block parameters, enabling multi-tenant deployments.
      - ###### Character I.1.b.i.β — Stream objects through checksum ledger before persistence to avoid duplicate uploads.
    - ##### Sentence I.1.b.ii — Implement pagination-aware tests using Moto or Localstack-backed S3 fixtures for deterministic coverage.
  - #### Paragraph I.1.c — CourtListener Feed Harness
    - ##### Sentence I.1.c.i — Introduce `CourtListenerRecentOpinionsReader` with pagination cursors persisted for resumable ingestion.
      - ###### Character I.1.c.i.α — Map docket metadata (court, citation, docket_id) onto unified document schema and timeline events.
      - ###### Character I.1.c.i.β — Implement rate limit respect via Prefect concurrency slots and exponential backoff.

- ### Chapter I.2 — Prefect Flow Orchestration
  - #### Paragraph I.2.a — Flow Composition
    - ##### Sentence I.2.a.i — Assemble modular Prefect flow `ingest_documents` orchestrating directory, S3, and CourtListener tasks with fan-in dedupe.
      - ###### Character I.2.a.i.α — Register tasks for checksum validation, document parsing, and persistence, each emitting structured events.
      - ###### Character I.2.a.i.β — Store run metadata in Prefect results backend plus project timeline ledger for UI synchronization.
  - #### Paragraph I.2.b — Deduplication Ledger
    - ##### Sentence I.2.b.i — Materialize `ingestion_checksums` table in managed datastore with composite keys (source, identifier, checksum).
      - ###### Character I.2.b.i.α — Provide transactional upsert semantics to prevent race conditions during concurrent ingests.
      - ###### Character I.2.b.i.β — Expose query utilities for APIs to surface dedupe decisions to clients.

## Phase II — Parser & OCR Transfiguration
- ### Chapter II.1 — GPU-Accelerated OCR Pipeline
  - #### Paragraph II.1.a — Tesseract GPU Enablement
    - ##### Sentence II.1.a.i — Compile Tesseract with CUDA-enabled `leptonica` support or integrate `tesserocr` builds leveraging GPU kernels.
      - ###### Character II.1.a.i.α — Dockerize GPU runtime with explicit NVIDIA base images and runtime validation scripts.
      - ###### Character II.1.a.i.β — Configure language packs and tessdata caching strategies to minimize cold-start latency.
    - ##### Sentence II.1.a.ii — Wrap OCR invocation in Prefect tasks capturing per-page confidence metrics.
      - ###### Character II.1.a.ii.α — Emit metrics to Prometheus-compatible sink and persist in `ocr_results` table keyed by document checksum.
      - ###### Character II.1.a.ii.β — Flag low-confidence spans for QA heuristics triggering dead-letter routing.
  - #### Paragraph II.1.b — PDFium Text Extraction
    - ##### Sentence II.1.b.i — Integrate PDFium via `pypdfium2` for high-fidelity text + layout extraction prior to OCR fallback.
      - ###### Character II.1.b.i.α — Parse structural elements (headings, tables) and map into metadata for retrieval weighting.
      - ###### Character II.1.b.i.β — Fall back to OCR when PDFium text confidence below threshold or when encountering scanned pages.
    - ##### Sentence II.1.b.ii — Persist extraction artifacts (text, bounding boxes, confidence) in managed blob storage with checksums.
      - ###### Character II.1.b.ii.α — Associate each artifact with ledger entries for timeline/backfill visibility.

- ### Chapter II.2 — Dead Letter & QA Orchestration
  - #### Paragraph II.2.a — Dead Letter Queue
    - ##### Sentence II.2.a.i — Route failed parsing/OCR tasks to `ingestion_dead_letter` with context payloads for operator triage.
      - ###### Character II.2.a.i.α — Provide Prefect notification hooks (Slack/webhook) for immediate visibility.
      - ###### Character II.2.a.i.β — Expose remediation API to requeue corrected artifacts after manual intervention.
  - #### Paragraph II.2.b — QA Heuristics
    - ##### Sentence II.2.b.i — Implement heuristics validating OCR average confidence, language detection, and structural completeness.
      - ###### Character II.2.b.i.α — Fail fast when heuristics breach thresholds, capturing artifacts and reason codes.
      - ###### Character II.2.b.i.β — Store QA outcomes in analytics warehouse for trend reporting.

## Phase III — API & Trigger Constellation
- ### Chapter III.1 — RESTful Interfaces
  - #### Paragraph III.1.a — `/api/ingest/upload`
    - ##### Sentence III.1.a.i — Accept multipart uploads, stream directly into ingestion flow, and emit ledger/timeline events.
      - ###### Character III.1.a.i.α — Validate checksum before storage; reject duplicates with informative response payload.
      - ###### Character III.1.a.i.β — Authenticate via JWT middleware, logging actor metadata into ledger entries.
  - #### Paragraph III.1.b — `/api/ingest/folder`
    - ##### Sentence III.1.b.i — Trigger directory loader with configurable recursion depth and file filters.
      - ###### Character III.1.b.i.α — Enqueue Prefect flow run asynchronously, returning tracking handle to clients.
      - ###### Character III.1.b.i.β — Emit timeline milestone "Folder ingestion scheduled" with source path metadata.
  - #### Paragraph III.1.c — `/api/ingest/sync`
    - ##### Sentence III.1.c.i — Kick off S3 and CourtListener sync runs respecting concurrency budgets.
      - ###### Character III.1.c.i.α — Accept optional cutoff timestamps for incremental backfills.
      - ###### Character III.1.c.i.β — Broadcast ledger/timeline events for ingestion start, dedupe decisions, and completion.

- ### Chapter III.2 — Webhook & Folder Observers
  - #### Paragraph III.2.a — Filesystem Watcher
    - ##### Sentence III.2.a.i — Deploy watchdog-based folder observer that invokes `/api/ingest/folder` when new files appear.
      - ###### Character III.2.a.i.α — Integrate debounce logic to coalesce bursty file writes.
  - #### Paragraph III.2.b — External Webhooks
    - ##### Sentence III.2.b.i — Provide authenticated webhook endpoint enabling external systems to push ingestion events.
      - ###### Character III.2.b.i.α — Validate payload schema, map to appropriate loader, and trigger Prefect runs with metadata context.

## Phase IV — Golden-Path Verification & Persistence Hardening
- ### Chapter IV.1 — Mixed Media Test Suite
  - #### Paragraph IV.1.a — Fixture Crafting
    - ##### Sentence IV.1.a.i — Construct canonical dataset containing vectorized PDF, scanned image, and structured JSON artifacts.
      - ###### Character IV.1.a.i.α — Embed deterministic metadata (case_id, docket, parties) for assertion convenience.
    - ##### Sentence IV.1.a.ii — Version fixtures under `tests/data/golden_path` with checksum annotations.
  - #### Paragraph IV.1.b — Test Coverage
    - ##### Sentence IV.1.b.i — Write integration tests executing Prefect flows end-to-end via `prefect.testing.utilities.run_test_flow`.
      - ###### Character IV.1.b.i.α — Assert metadata persistence, OCR confidence thresholds, QA heuristic responses, and ledger event emission.
      - ###### Character IV.1.b.i.β — Validate timeline updates reflect ingestion milestones with correct ordering.

- ### Chapter IV.2 — Persistence Validation
  - #### Paragraph IV.2.a — Managed Store Assertions
    - ##### Sentence IV.2.a.i — Confirm documents, OCR artifacts, dead letters, and events are persisted across cold restarts.
      - ###### Character IV.2.a.i.α — Simulate restart by tearing down caches and rehydrating from managed stores during tests.
    - ##### Sentence IV.2.a.ii — Document schema migrations and backup strategies in `docs/persistence.md`.

## Phase V — Release & Stewardship
- ### Chapter V.1 — Observability & Documentation
  - #### Paragraph V.1.a — Dashboards
    - ##### Sentence V.1.a.i — Publish Grafana dashboards summarizing ingestion throughput, OCR confidence, and dedupe efficacy.
  - #### Paragraph V.1.b — Runbooks
    - ##### Sentence V.1.b.i — Extend operational runbooks covering ingestion triggers, dead letter remediation, and scaling guidance.
- ### Chapter V.2 — Change Management
  - #### Paragraph V.2.a — Migration Plan
    - ##### Sentence V.2.a.i — Define rollout steps with canary ingestions, feature flags, and rollback protocols.
      - ###### Character V.2.a.i.α — Schedule post-deployment verification windows with QA sign-off checklist.

## Appendix — Personal Signature Flourish
- ### Chapter S.1 — Craftsmanship Touch
  - #### Paragraph S.1.a — Integrate celebratory timeline badge "Aurora Ingestion MkII" upon successful end-to-end run, reinforcing narrative cohesion.
