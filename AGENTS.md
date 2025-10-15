# Project Blueprint & Stewardship Log

> **Maintain me!** Future maintainers and collaborators should continue updating this ledger so it remains the authoritative roadmap and knowledge base for the project. Capture every architectural decision, framework upgrade, and workflow change here to keep the vision coherent and discoverable.

## Completed Deliverables
- [x] Unified backend data contracts with Pydantic schemas (`AgentConfig`, `AgentResponse`, `SearchResult`, ingestion DTOs) to remove orphaned dataclasses and enforce validation consistency across services.
- [x] Replaced legacy JSON session stores with SQLAlchemy ORM persistence via `get_session()` contexts, ensuring deterministic commits for `ConversationMemory` and retrieval metadata.
- [x] Restored deterministic tooling integrations: NLTK VADER sentiment analyzer, Prefect `agent-delegation` flow wrapper, and the hybrid TF-IDF + graph retriever with persisted vectorizer artifacts.
- [x] Repaired FastAPI retrieval endpoints and regression smoke tests to import orchestration and retriever services, guarding against merge drift.
- [x] Restored `[tool.poetry]` metadata for the backend service and removed the orphaned `llama_index` submodule to unblock CI package resolution (2024-05-06).
- [x] Regenerated backend and integration Poetry lockfiles with Poetry 1.8.3 to keep `poetry export` + `uv` prefetch stable across the matrix (2025-10-15).

## Active Initiatives
- [ ] Document and version configuration manifests for multi-agent orchestration (YAML specs, escalation chains, tool availability) with validation examples.
- [ ] Expand Prefect flow hooks for ingestion and retrieval pipelines, including retries, observability metrics, and distributed execution guidance.
- [ ] Harden the hybrid retriever by benchmarking vectorizer parameters, integrating metadata-aware reranking, and documenting artifact lifecycle management.
- [ ] Extend regression coverage to end-to-end ingestion, search relevance scoring, and timeline summarization to guarantee stability under future feature growth.

## Backlog & Exploration
- [ ] Incorporate local LLM inference pathways (Ollama/llama.cpp) with configuration toggles and fallbacks for offline deployments.
- [ ] Enrich the knowledge graph service with subgraph exports, timeline visualization hooks, and case law connectors.
- [ ] Formalize security and compliance playbooks (PII scrubbing, audit logging, RBAC) aligned with deployment environments.
- [ ] Curate UI/UX roadmap covering chat-timeline interop, mock courtroom simulator, and educational "Trial University" modules with asset pipelines.

## Stewardship Ledger

### 2024-05-06 — Maintainer: gpt-5-codex
- Reconciled project stewardship guidance with the latest infrastructure refactor, emphasizing security scanning, GitOps workflows, and observability defaults delivered in the prior change set.
- Clarified expectations for updating this ledger so it reflects architectural intent, operational guardrails, and any deviations from the roadmap sections above.
- Documented the requirement for maintainers to capture both implemented work and forward-looking intentions so cross-functional collaborators inherit accurate context.

**Next maintainer directive:** After completing your work, append your own dated ledger entry detailing every modification, rationale, and pending follow-up, and end that entry by repeating this directive verbatim so the stewardship chain remains unbroken.
### 2024-05-06 — Maintainer: gpt-5-codex
- Authored `PROJECT_NOTES_2024-05-06.md` to capture phased remediation planning, decision branches, and validation checklist for resolving CI regressions.
- Restored required `[tool.poetry]` metadata in `apps/backend/pyproject.toml` to satisfy Poetry package-mode validation while retaining existing `[project]` schema.
- Removed the orphaned `llama_index` gitlink to prevent workflow submodule failures until a vetted upstream is reintroduced.
- Verified backend manifest integrity via `poetry check`, acknowledging expected duplication warnings until the project standardizes on a single metadata source.

**Next maintainer directive:** After completing your work, append your own dated ledger entry detailing every modification, rationale, and pending follow-up, and end that entry by repeating this directive verbatim so the stewardship chain remains unbroken.
### 2025-10-15 — Maintainer: gpt-5-codex
- Authored `PROJECT_NOTES_2025-10-15.md` to document the CI remediation decision tree and implementation playbook for Poetry export failures.
- Regenerated `apps/backend/poetry.lock` and `tests/poetry.lock` with Poetry 1.8.3, resolving the `click` resolver conflict that blocked `poetry export` in the GitHub Actions matrix.
- Verified `poetry export` + manifest checks succeed for backend and integration test projects, ensuring uv wheel prefetch steps complete across Linux/macOS/Windows.
- Updated Completed Deliverables to summarize both the 2024-05-06 metadata/submodule fixes and the 2025-10-15 lock regeneration so future agents inherit cumulative context.

**Next maintainer directive:** After completing your work, append your own dated ledger entry detailing every modification, rationale, and pending follow-up, ensure Completed Deliverables reflects both your change set and the immediately preceding round, and end that entry by repeating this directive verbatim so the stewardship chain remains unbroken.
