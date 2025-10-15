# Remediation Roadmap — CI Poetry/Submodule Failures

## Phase 1 — Context Reconnaissance
- ### Objective
  - Document failing CI steps and scope impacted components (Poetry config, Git submodule state).
- ### Actions
  - Parse workflow logs to isolate Poetry validation errors and submodule fetch failure triggers.
  - Inventory repository directories for local agent instructions (AGENTS.md) and existing dependency manifests.

## Phase 2 — Decision Tree Authoring
- ### Poetry Configuration Branch
  - #### Option A — Convert project to `pyproject` PEP 621 only (risk: Poetry tooling expecting `[tool.poetry]`).
  - #### Option B — Restore canonical `[tool.poetry]` metadata mirroring `[project]` definitions (chosen: maintains Poetry compatibility without losing PEP 621 metadata).
- ### Submodule Integrity Branch
  - #### Option A — Introduce `.gitmodules` entry pointing at upstream commit (blocked: unknown canonical remote for commit `2b6bcbef`).
  - #### Option B — Remove orphaned gitlink and treat dependency via package manager (chosen: eliminates CI fatal error while aligning with pip-installable `llama_index`).

## Phase 3 — Implementation Breakdown
- ### Task 3.1 — Augment `apps/backend/pyproject.toml`
  - Insert `name`, `version`, `description`, `authors` under `[tool.poetry]` to satisfy Poetry package mode validation.
- ### Task 3.2 — Excise orphaned `llama_index` submodule pointer
  - Use `git rm` to purge gitlink; ensure directory removal reflected in tree.
- ### Task 3.3 — Validation
  - Run `poetry check` in backend module to confirm manifest validity.
  - Execute `poetry -C tests check`? (poetry check requires?). Actually just verifying? (Hold) Instead run `poetry -C apps/backend check` due to [project] entries.
- ### Task 3.4 — Stewardship Update
  - Append dated entry to root `AGENTS.md` ledger capturing remediation narrative.

## Phase 4 — Retrospective & Documentation
- Ensure plan-to-execution traceability documented in final summary and stewardship ledger.
- Confirm Git history clean (one commit) and prepare PR metadata per contribution guidelines.
