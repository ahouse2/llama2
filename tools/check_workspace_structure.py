"""Validate the canonical workspace layout for the discovery platform."""

from __future__ import annotations

import json
import sys
from collections import defaultdict
from pathlib import Path
from typing import Callable, Iterable

import tomllib

REPO_ROOT = Path(__file__).resolve().parents[1]

REQUIRED_PATHS = {
    "apps/backend": ["pyproject.toml", "README.md"],
    "apps/frontend": ["package.json", "README.md", "vite.config.ts", "tailwind.config.ts", "tsconfig.json"],
    "infra": ["README.md", "terraform/main.tf", "terraform/backend.tf", "helm/platform/Chart.yaml"],
    "docs": ["README.md", "mkdocs.yml", "docusaurus/package.json"],
    "tests": ["README.md", "pyproject.toml", "integration"]
}


ValidationFn = Callable[[Path], list[str]]


def _ensure_non_empty(path: Path) -> list[str]:
    if not path.read_text(encoding="utf-8").strip():
        return ["file is empty"]
    return []


def _ensure_package_json_dependencies(path: Path, required: Iterable[str]) -> list[str]:
    try:
        package = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:  # pragma: no cover - defensive
        return [f"invalid JSON: {exc}"]
    deps = {
        **package.get("dependencies", {}),
        **package.get("devDependencies", {})
    }
    missing = [dep for dep in required if dep not in deps]
    if missing:
        return [f"missing required dependencies: {', '.join(sorted(missing))}"]
    return []


def _ensure_pyproject_tooling(path: Path) -> list[str]:
    try:
        pyproject = tomllib.loads(path.read_text(encoding="utf-8"))
    except tomllib.TOMLDecodeError as exc:  # pragma: no cover - defensive
        return [f"invalid TOML: {exc}"]
    tool_section = pyproject.get("tool", {})
    poetry = tool_section.get("poetry", {})
    deps = poetry.get("dependencies", {})
    groups = poetry.get("group", {})
    dev_deps = groups.get("dev", {}).get("dependencies", {}) if groups.get("dev") else {}
    tests_deps = groups.get("tests", {}).get("dependencies", {}) if groups.get("tests") else {}

    missing: list[str] = []
    if "black" not in dev_deps:
        missing.append("black (tool.poetry.group.dev.dependencies)")
    if "ruff" not in dev_deps:
        missing.append("ruff (tool.poetry.group.dev.dependencies)")
    if "mypy" not in dev_deps:
        missing.append("mypy (tool.poetry.group.dev.dependencies)")
    if "pytest" not in tests_deps and "pytest" not in deps:
        missing.append("pytest (testing dependency)")
    return [f"missing {entry}" for entry in missing]


def _ensure_contains(path: Path, substrings: Iterable[str]) -> list[str]:
    text = path.read_text(encoding="utf-8")
    missing = [snippet for snippet in substrings if snippet not in text]
    if missing:
        return [f"missing required content: {', '.join(missing)}"]
    return []


FILE_CHECKS: list[tuple[str, ValidationFn]] = [
    ("apps/backend/README.md", _ensure_non_empty),
    ("apps/backend/pyproject.toml", _ensure_pyproject_tooling),
    ("apps/frontend/README.md", _ensure_non_empty),
    (
        "apps/frontend/package.json",
        lambda path: _ensure_package_json_dependencies(
            path,
            [
                "react",
                "react-dom",
                "@vitejs/plugin-react-swc",
                "tailwindcss",
                "@radix-ui/react-toast",
            ],
        ),
    ),
    ("infra/README.md", _ensure_non_empty),
    ("infra/terraform/main.tf", lambda path: _ensure_contains(path, ["resource \"aws_s3_bucket\"", "kubernetes_namespace"])),
    ("infra/helm/platform/Chart.yaml", lambda path: _ensure_contains(path, ["apiVersion: v2", "name: discovery-platform"])),
    ("docs/README.md", _ensure_non_empty),
    ("docs/mkdocs.yml", lambda path: _ensure_contains(path, ["site_name:", "theme:"])),
    (
        "docs/docusaurus/package.json",
        lambda path: _ensure_package_json_dependencies(path, ["@docusaurus/core", "react"]),
    ),
    ("tests/README.md", _ensure_non_empty),
    ("tests/pyproject.toml", lambda path: _ensure_contains(path, ["[tool.pytest.ini_options]", "[tool.ruff]"])),
]


def validate_paths() -> dict[str, list[str]]:
    missing: dict[str, list[str]] = {}
    for relative_dir, required_entries in REQUIRED_PATHS.items():
        directory = REPO_ROOT / relative_dir
        if not directory.exists():
            missing[relative_dir] = ["<directory missing>"]
            continue
        missing_entries = [entry for entry in required_entries if not (directory / entry).exists()]
        if missing_entries:
            missing[relative_dir] = missing_entries
    return missing


def run_file_checks() -> dict[str, list[str]]:
    errors: dict[str, list[str]] = defaultdict(list)
    for relative_path, check in FILE_CHECKS:
        file_path = REPO_ROOT / relative_path
        if not file_path.exists():
            errors[relative_path].append("missing file for content validation")
            continue
        issues = check(file_path)
        if issues:
            errors[relative_path].extend(issues)
    return errors


def main() -> int:
    missing = validate_paths()
    content_issues = run_file_checks()
    if missing or content_issues:
        sys.stderr.write("Workspace structure validation failed.\n")
        merged = defaultdict(list)
        for bucket in (missing, content_issues):
            for key, items in bucket.items():
                merged[key].extend(items)
        sys.stderr.write(json.dumps(merged, indent=2))
        sys.stderr.write("\n")
        return 1
    print("Workspace structure validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
