# 2025-10-16 CI Workflow Remediation Plan

## Objective
- Restore the GitHub Actions quality pipeline by aligning uv wheel prefetch commands with supported flags while preserving dependency export guarantees.

## Phase Breakdown
- Phase 1 — Discovery
  - Review CI logs to confirm `uv pip install` failure signature and identify offending arguments.
  - Inventory existing remediation efforts documented on 2025-10-15 to maintain continuity.
- Phase 2 — Design
  - Define the minimal workflow amendment required to satisfy uv’s CLI contract without compromising caching strategy.
  - Determine stewardship updates (ledger, deliverables) mandated by `AGENTS.md` directives.
- Phase 3 — Implementation
  - Edit `.github/workflows/ci.yml` to remove the unsupported `--download-only` argument from both uv invocations.
  - Update `AGENTS.md` Completed Deliverables and Stewardship Ledger to reflect the 2025-10-15 and 2025-10-16 interventions collectively.
- Phase 4 — Verification
  - Manually sanity-check the YAML snippet for indentation and argument parity across backend/tests installs.
  - Re-run git status diff review to confirm only intentional files changed.
- Phase 5 — Documentation & Handoff
  - Capture this plan and outcomes in dated project notes for future maintainers.
  - Reinforce the directive in `AGENTS.md` requiring each maintainer to append their ledger entry and cumulative deliverable summary.

## Task Decomposition
- Task 1.1 — Analyze failure context
  - Inspect `.github/workflows/ci.yml` uv invocation block for deprecated arguments.
- Task 1.2 — Cross-reference documentation
  - Confirm supported uv flags for parity (implicit from failure log; no additional flags required).
- Task 2.1 — Define workflow edits
  - Remove only `--download-only`, retaining Python path and requirement files.
- Task 2.2 — Stewardship requirements
  - Ensure Completed Deliverables enumerates 2024-05-06, 2025-10-15, and new 2025-10-16 work.
- Task 3.1 — Modify workflow
  - Update both uv lines accordingly.
- Task 3.2 — Revise AGENTS ledger
  - Append dated entry summarizing actions, validations, and outstanding follow-ups.
- Task 4.1 — Self-review
  - Use `git diff` to verify only intended removal occurs.
- Task 4.2 — Validate documentation changes
  - Check AGENTS Markdown structure renders cleanly (headings, bullets).
- Task 5.1 — Finalize notes
  - Save this roadmap and reference in ledger entry.
- Task 5.2 — Prepare PR summary and testing notes post-commit.

## Risks & Mitigations
- Risk: Removing `--download-only` could alter caching semantics.
  - Mitigation: uv defaults to installing into cache when provided; step already prefetched without virtualization, so removal simply resolves CLI error while maintaining downloads.
- Risk: Stewardship ledger divergence.
  - Mitigation: Explicitly repeat directive and enumerate prior rounds to keep continuity.

## Validation Checklist
- [x] `.github/workflows/ci.yml` contains uv commands without `--download-only`.
- [x] `AGENTS.md` Completed Deliverables includes new 2025-10-16 bullet and retains prior entries.
- [x] New stewardship ledger entry added with directive repeated verbatim.
- [x] `git status` shows only expected files.
- [x] Commit message and PR drafted summarizing workflow fix and documentation updates.
