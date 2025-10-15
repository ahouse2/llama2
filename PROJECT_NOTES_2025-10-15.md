# CI Remediation Blueprint — Poetry Export Failures

## Volume I — Strategic Overview
- ### Chapter 1 — Problem Statement
  - Identify CI failures stemming from `poetry export` errors on GitHub Actions runners.
  - Catalog prior remediation work (metadata fixes, submodule removal) to ensure historical continuity.
- ### Chapter 2 — Success Criteria
  - Regenerate lock files compatible with Poetry 1.8.3 so `uv` prefetch succeeds across OS matrix.
  - Maintain reproducible dependency graphs without introducing placeholder constraints.
  - Update stewardship artifacts (`AGENTS.md`, project notes) to reflect cumulative knowledge.

## Volume II — Decision Forest
- ### Chapter 3 — Toolchain Compatibility Branch
  - #### Leaf A — Downgrade workflow Poetry version
    - Rejected: Workflow explicitly pins 1.8.3 and altering CI pipeline is out-of-scope for repo-only changes.
  - #### Leaf B — Regenerate lock files with Poetry 1.8.3
    - Selected: Produces exporter-friendly lockfiles without mutating dependency intent.
- ### Chapter 4 — Dependency Integrity Branch
  - #### Leaf A — Pin transitive `click` version via direct dependency
    - Risk: Hides upstream constraints and duplicates management across projects.
  - #### Leaf B — Allow resolver to select compliant version during lock regeneration
    - Selected: Leverages Poetry's solver to reconcile `click` range expectations across packages.
- ### Chapter 5 — Knowledge Stewardship Branch
  - #### Leaf A — Leave prior AGENTS entry untouched
    - Risk: Future agents lack consolidated history of consecutive remediations.
  - #### Leaf B — Expand AGENTS ledger + directive with latest and prior change log
    - Selected: Preserves institutional memory and enforces update discipline.

## Volume III — Implementation Chapters
- ### Chapter 6 — Backend Lock Refresh
  - Activate isolated Poetry 1.8.3 virtual environment mirroring CI.
  - Execute `poetry -C apps/backend lock --no-update` to regenerate deterministic lockfile.
  - Validate `poetry -C apps/backend export --without-hashes --format requirements.txt` completes successfully.
- ### Chapter 7 — Tests Lock Refresh
  - Run `poetry -C tests lock --no-update` under same toolchain context.
  - Validate `poetry -C tests export --without-hashes --format requirements.txt` success.
- ### Chapter 8 — Verification & Regression Checks
  - Run `poetry -C apps/backend check` and `poetry -C tests check` to confirm manifest integrity.
  - Capture command outputs for inclusion in final QA evidence.

## Volume IV — Documentation & Stewardship
- ### Chapter 9 — Update AGENTS Ledger
  - Summarize previous round (metadata + submodule) and current round (lock regeneration) under Completed Deliverables.
  - Append new dated maintainer entry detailing actions, rationale, and pending follow-ups.
  - Reinforce directive that each maintainer must perform similar updates going forward.
- ### Chapter 10 — Prepare Final Report
  - Stage updated lockfiles, stewardship notes, and documentation.
  - Record executed test commands for the testing section of the final summary.
  - Commit with message referencing CI lock regeneration and documentation refresh.
