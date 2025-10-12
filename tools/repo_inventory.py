"""Repository inventory utility for Automated Legal Discovery platform due diligence.

This script scans the repository tree, classifies files into semantic buckets
(code, infrastructure, documentation, data, assets, other), and emits both a
structured JSON artifact and an optional Markdown summary. It is engineered to
serve as the authoritative source for requirement traceability workstreams.
"""

from __future__ import annotations

import argparse
import json
import os
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Iterable, List, Mapping, MutableMapping, Optional

CATEGORY_EXTENSION_MAP: Mapping[str, Iterable[str]] = {
    "code": {
        ".py",
        ".ts",
        ".tsx",
        ".js",
        ".jsx",
        ".java",
        ".cs",
        ".cpp",
        ".c",
        ".rs",
        ".go",
        ".rb",
        ".swift",
        ".kt",
        ".m",
        ".scala",
        ".php",
        ".sh",
        ".ps1",
        ".sql",
    },
    "infrastructure": {
        "Dockerfile",
        "docker-compose.yml",
        ".tf",
        ".hcl",
        ".yaml",
        ".yml",
        ".jsonnet",
        ".nix",
        ".toml",
        ".ini",
    },
    "documentation": {
        ".md",
        ".rst",
        ".adoc",
        ".pdf",
        ".docx",
        ".pptx",
        ".xlsx",
        ".csv",
    },
    "data": {
        ".parquet",
        ".feather",
        ".arrow",
        ".json",
        ".ndjson",
        ".xml",
        ".yamldata",
        ".csvdata",
    },
    "assets": {
        ".png",
        ".jpg",
        ".jpeg",
        ".svg",
        ".gif",
        ".ico",
        ".mp3",
        ".wav",
        ".mp4",
        ".mov",
        ".webm",
        ".woff",
        ".woff2",
        ".ttf",
        ".otf",
    },
}

DEFAULT_IGNORED_DIRECTORIES = {
    ".git",
    "__pycache__",
    ".mypy_cache",
    ".pytest_cache",
    "node_modules",
    ".idea",
    ".vscode",
    "dist",
    "build",
    ".ruff_cache",
    ".cache",
    ".venv",
    "env",
    "venv",
    "conda",
}

CATEGORY_ORDER = [
    "code",
    "infrastructure",
    "documentation",
    "data",
    "assets",
    "other",
]


def normalize_extension(path: Path) -> str:
    """Return a normalized extension identifier for classification."""
    if path.name in CATEGORY_EXTENSION_MAP.get("infrastructure", set()):
        return path.name  # handle Dockerfile-style names with no dot
    return path.suffix.lower()


def classify(path: Path) -> str:
    """Classify a path into one of the predefined categories."""
    ext = normalize_extension(path)
    for category, extensions in CATEGORY_EXTENSION_MAP.items():
        if ext in extensions:
            return category
    return "other"


@dataclass
class DirectoryStats:
    """Aggregate statistics for a directory."""

    total_files: int = 0
    total_size_bytes: int = 0
    category_file_counts: MutableMapping[str, int] = field(
        default_factory=lambda: Counter({category: 0 for category in CATEGORY_ORDER})
    )
    category_size_bytes: MutableMapping[str, int] = field(
        default_factory=lambda: defaultdict(int)
    )

    def add_file(self, category: str, size_bytes: int) -> None:
        self.total_files += 1
        self.total_size_bytes += size_bytes
        self.category_file_counts[category] += 1
        self.category_size_bytes[category] += size_bytes

    def to_dict(self) -> Dict[str, object]:
        return {
            "total_files": self.total_files,
            "total_size_bytes": self.total_size_bytes,
            "category_file_counts": dict(self.category_file_counts),
            "category_size_bytes": dict(self.category_size_bytes),
        }


@dataclass
class InventoryReport:
    """Structured inventory data container."""

    root: str
    generated_at: str
    total_files: int
    total_size_bytes: int
    directories: Dict[str, DirectoryStats]
    files: List[Dict[str, object]]

    def to_dict(self) -> Dict[str, object]:
        return {
            "root": self.root,
            "generated_at": self.generated_at,
            "total_files": self.total_files,
            "total_size_bytes": self.total_size_bytes,
            "directories": {path: stats.to_dict() for path, stats in self.directories.items()},
            "files": self.files,
        }


def scan_repository(root: Path, ignored_dirs: Optional[Iterable[str]] = None) -> InventoryReport:
    ignored = set(DEFAULT_IGNORED_DIRECTORIES)
    if ignored_dirs:
        ignored.update(ignored_dirs)

    root = root.resolve()
    directories: Dict[str, DirectoryStats] = defaultdict(DirectoryStats)
    files: List[Dict[str, object]] = []
    total_files = 0
    total_size = 0

    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in ignored]
        current_dir = Path(dirpath)
        relative_dir = current_dir.relative_to(root)
        relative_dir_str = "." if str(relative_dir) == "." else str(relative_dir)

        # Ensure the directory entry exists even if empty
        _ = directories[relative_dir_str]

        for filename in filenames:
            file_path = current_dir / filename
            try:
                stat_result = file_path.stat()
            except (FileNotFoundError, PermissionError):
                continue

            size_bytes = stat_result.st_size
            category = classify(file_path)
            relative_file_path = file_path.relative_to(root)

            files.append(
                {
                    "path": str(relative_file_path),
                    "size_bytes": size_bytes,
                    "category": category,
                    "extension": normalize_extension(file_path),
                }
            )

            total_files += 1
            total_size += size_bytes

            # Update stats for current directory and its ancestors up to root
            for ancestor in [relative_dir] + list(relative_dir.parents):
                ancestor_str = "." if str(ancestor) == "." else str(ancestor)
                directories[ancestor_str].add_file(category, size_bytes)

    return InventoryReport(
        root=str(root),
        generated_at=datetime.now(timezone.utc).isoformat(),
        total_files=total_files,
        total_size_bytes=total_size,
        directories=directories,
        files=sorted(files, key=lambda entry: entry["path"]),
    )


def human_readable_size(num_bytes: int) -> str:
    if num_bytes == 0:
        return "0 B"
    units = ["B", "KB", "MB", "GB", "TB"]
    size = float(num_bytes)
    idx = 0
    while size >= 1024 and idx < len(units) - 1:
        size /= 1024
        idx += 1
    return f"{size:.2f} {units[idx]}"


def render_markdown(report: InventoryReport) -> str:
    lines = [
        "# Repository Inventory Report",
        "",
        f"- Root: `{report.root}`",
        f"- Generated: {report.generated_at}",
        f"- Total files: {report.total_files}",
        f"- Total size: {human_readable_size(report.total_size_bytes)}",
        "",
        "## Directory Summary",
        "",
        "| Directory | Files | Size | Code | Infra | Docs | Data | Assets | Other |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]

    for directory, stats in sorted(report.directories.items()):
        lines.append(
            "| {directory} | {files} | {size} | {code} | {infra} | {docs} | {data} | {assets} | {other} |".format(
                directory=directory,
                files=stats.total_files,
                size=human_readable_size(stats.total_size_bytes),
                code=stats.category_file_counts["code"],
                infra=stats.category_file_counts["infrastructure"],
                docs=stats.category_file_counts["documentation"],
                data=stats.category_file_counts["data"],
                assets=stats.category_file_counts["assets"],
                other=stats.category_file_counts["other"],
            )
        )

    lines.extend(
        [
            "",
            "## Category Breakdown",
            "",
        ]
    )

    category_totals = Counter()
    category_sizes = defaultdict(int)
    for file_entry in report.files:
        category = file_entry["category"]
        category_totals[category] += 1
        category_sizes[category] += file_entry["size_bytes"]

    for category in CATEGORY_ORDER:
        category_totals.setdefault(category, 0)
        category_sizes.setdefault(category, 0)

    lines.append("| Category | Files | Size |")
    lines.append("| --- | ---: | ---: |")

    for category in CATEGORY_ORDER:
        lines.append(
            "| {category} | {files} | {size} |".format(
                category=category.capitalize(),
                files=category_totals[category],
                size=human_readable_size(category_sizes[category]),
            )
        )

    lines.extend(
        [
            "",
            "## Notable Files",
            "",
            "Top 20 largest files by size for immediate inspection:",
            "",
            "| Path | Size | Category |",
            "| --- | ---: | --- |",
        ]
    )

    for file_entry in sorted(report.files, key=lambda entry: entry["size_bytes"], reverse=True)[:20]:
        lines.append(
            "| {path} | {size} | {category} |".format(
                path=file_entry["path"],
                size=human_readable_size(file_entry["size_bytes"]),
                category=file_entry["category"],
            )
        )

    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate a repository inventory report.")
    parser.add_argument(
        "--root",
        type=Path,
        default=Path.cwd(),
        help="Repository root to scan (defaults to current working directory).",
    )
    parser.add_argument(
        "--json",
        type=Path,
        help="Optional path to write JSON report.",
    )
    parser.add_argument(
        "--markdown",
        type=Path,
        help="Optional path to write Markdown report.",
    )
    parser.add_argument(
        "--ignore",
        nargs="*",
        default=(),
        help="Additional directory names to ignore during scan.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    report = scan_repository(args.root, args.ignore)

    if args.json:
        args.json.parent.mkdir(parents=True, exist_ok=True)
        args.json.write_text(json.dumps(report.to_dict(), indent=2))

    if args.markdown:
        args.markdown.parent.mkdir(parents=True, exist_ok=True)
        args.markdown.write_text(render_markdown(report))

    if not args.json and not args.markdown:
        print(json.dumps(report.to_dict(), indent=2))


if __name__ == "__main__":
    main()
