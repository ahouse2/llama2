"""Validate the canonical workspace layout for the discovery platform."""

from __future__ import annotations

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]

REQUIRED_PATHS = {
    "apps/backend": ["pyproject.toml", "README.md"],
    "apps/frontend": ["package.json", "README.md", "vite.config.ts", "tailwind.config.ts"],
    "infra": ["README.md", "terraform/main.tf", "helm/platform/Chart.yaml"],
    "docs": ["README.md", "mkdocs.yml", "docusaurus/package.json"],
    "tests": ["README.md", "pyproject.toml", "integration"]
}


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


def main() -> int:
    missing = validate_paths()
    if missing:
        sys.stderr.write("Workspace structure validation failed.\n")
        sys.stderr.write(json.dumps(missing, indent=2))
        sys.stderr.write("\n")
        return 1
    print("Workspace structure validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
