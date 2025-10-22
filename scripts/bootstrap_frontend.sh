#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PNPM_VERSION="${PNPM_VERSION:-8.15.6}"
RUN_TESTS="${BOOTSTRAP_RUN_TESTS:-0}"

log() {
  printf "[frontend-bootstrap] %s\n" "$*"
}

ensure_pnpm() {
  if ! command -v pnpm >/dev/null 2>&1; then
    log "Enabling pnpm ${PNPM_VERSION} via corepack."
    corepack enable pnpm >/dev/null 2>&1 || true
  fi
  corepack prepare "pnpm@${PNPM_VERSION}" --activate >/dev/null 2>&1
}

run_workspace_task() {
  local filter=$1
  local task=$2
  if pnpm --filter "$filter" pkg has "scripts.${task}" >/dev/null 2>&1; then
    log "Running '${task}' for ${filter}."
    pnpm --filter "$filter" run "$task"
  else
    log "Skipping '${task}' for ${filter}; script not defined."
  fi
}

main() {
  log "Bootstrapping pnpm workspace."
  ensure_pnpm
  (cd "${REPO_ROOT}" && pnpm install --frozen-lockfile)
  run_workspace_task "legal-discovery-frontend" "lint"
  run_workspace_task "discovery-docs" "lint"
  if [[ "${RUN_TESTS}" == "1" ]]; then
    run_workspace_task "legal-discovery-frontend" "test"
  fi
  log "Frontend bootstrap complete."
}

main "$@"
