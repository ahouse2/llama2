# Workspace Canonicalization Implementation Plan

## Phase 0 — Context Assimilation
- Survey existing repository topology
  - Map current `apps`, `docs`, `infra`, `tests` contents
  - Identify existing automation (e.g., `Justfile`, CI scripts)
- Extract requirements from user directive & AGENTS charter
  - Guarantee no placeholder code; deliver production-ready scaffolding
  - Maintain documentation-first mindset for future maintainers

## Phase 1 — Directory Audit & Gap Analysis
- Validate presence and health of target workspaces
  - `apps/frontend`: confirm Vite + Tailwind + Radix stack completeness
  - `infra`: ensure Terraform & Helm baselines exist
  - `docs`: check MkDocs + Docusaurus integration points
  - `tests`: inspect integration suite layout and tooling manifests
- Decide whether to augment or refactor READMEs for alignment with mandate
  - Record missing conceptual overviews or setup steps per workspace

## Phase 2 — Canonical Documentation & Structure Enhancements
- Strengthen workspace READMEs where knowledge gaps are detected
  - Add stack deep dives, bootstrap instructions, and guardrails
  - Embed cross-linking to shared tooling and conventions
- Introduce additional scaffolding assets if required (e.g., baseline configs)
  - Ensure Tailwind/Radix references align with actual dependencies

## Phase 3 — Task Runner Orchestration Uplift
- Evaluate current `Justfile`
  - Confirm coverage of lint/typecheck/format/test commands across backends/frontend/tests
  - Identify missing aggregation targets (format-all, lint-all, etc.)
- Implement enhancements
  - Add phony recipes for combined workflows (e.g., `lint-all`, `test-all`, `check-all`)
  - Ensure commands respect dependency management (install steps preceding execution)
  - Preserve idempotency and developer ergonomics (colorful logging, help text)

## Phase 4 — Root README Revamp
- Document workspace topology with annotated diagrammatic structure
  - Provide quick-start instructions for backend, frontend, infra, docs, tests
- Detail bootstrap commands leveraging the task runner
  - Highlight CI guardrails and structure validation mechanism

## Phase 5 — CI Structure Enforcement Hardening
- Extend `tools/check_workspace_structure.py`
  - Enforce canonical files & directories derived from requirements
  - Validate README presence and non-empty status (fail on stubs)
  - Provide actionable error messaging for missing artifacts
- Wire script into task runner (`just ci`) and document usage

## Phase 6 — Verification & Polish
- Run `just structure-check` (and other relevant commands) to confirm compliance
- Re-run lint/typecheck/test commands where feasible or note constraints
- Perform iterative review passes over modified files to guarantee clarity & correctness

## Phase 7 — Documentation of Outcomes
- Summarize changes in commit message & PR body
- Reference verification commands in final report with citations
