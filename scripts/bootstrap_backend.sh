#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
POETRY_VERSION="${POETRY_VERSION:-1.8.3}"
PYTHON_BIN="${PYTHON_BIN:-python3}"
INSTALL_TESTS="${BOOTSTRAP_INSTALL_INTEGRATION:-1}"
RUN_TESTS="${BOOTSTRAP_RUN_TESTS:-0}"

log() {
  printf "[backend-bootstrap] %s\n" "$*"
}

ensure_poetry() {
  if ! command -v poetry >/dev/null 2>&1; then
    log "Poetry not detected; installing version ${POETRY_VERSION}."
    "${PYTHON_BIN}" -m pip install --user "poetry==${POETRY_VERSION}" >/dev/null
    export PATH="$HOME/.local/bin:$PATH"
  fi
  local installed_version
  installed_version=$(poetry --version | awk '{print $3}')
  if [[ "${installed_version}" != "${POETRY_VERSION}" ]]; then
    log "Poetry ${installed_version} detected; upgrading to ${POETRY_VERSION}."
    poetry self update "${POETRY_VERSION}" >/dev/null
  fi
}

bootstrap_project() {
  local project_dir=$1
  log "Syncing dependencies for ${project_dir}."
  (cd "${REPO_ROOT}/${project_dir}" && POETRY_VIRTUALENVS_CREATE=${POETRY_VIRTUALENVS_CREATE:-false} poetry install --sync)
  if [[ "${RUN_TESTS}" == "1" ]]; then
    log "Running unit tests for ${project_dir}."
    (cd "${REPO_ROOT}/${project_dir}" && poetry run pytest --maxfail=1 --disable-warnings -q)
  fi
}

main() {
  log "Bootstrapping Python toolchain."
  ensure_poetry
  bootstrap_project "apps/backend"
  if [[ "${INSTALL_TESTS}" == "1" ]]; then
    bootstrap_project "tests"
  fi
  log "Backend bootstrap complete."
}

main "$@"
