#!/usr/bin/env python3
"""Generate a TRD traceability matrix by mapping requirements to repository assets."""

from __future__ import annotations

import argparse
import datetime as dt
import json
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple

STATUS_ORDER = [
    "missing",
    "candidate",
    "partial",
    "full",
    "not-applicable",
]
STATUS_PRIORITY = {name: index for index, name in enumerate(STATUS_ORDER)}


class RequirementNode:
    """Represents a single requirement in the hierarchy."""

    def __init__(
        self,
        node_id: str,
        title: str,
        description: str,
        level: int,
        path_titles: List[str],
        keywords: Optional[Iterable[str]] = None,
        parent_id: Optional[str] = None,
    ) -> None:
        self.id = node_id
        self.title = title
        self.description = description
        self.level = level
        self.path_titles = path_titles
        self.parent_id = parent_id
        self.keywords = [kw.lower() for kw in keywords or []]
        self.children: List[str] = []
        self.status: str = "missing"
        self.implemented_assets: List[str] = []
        self.auto_matched_assets: List[str] = []
        self.notes: List[str] = []

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "level": self.level,
            "path_titles": self.path_titles,
            "keywords": self.keywords,
            "parent_id": self.parent_id,
            "children": self.children,
            "status": self.status,
            "implemented_assets": self.implemented_assets,
            "auto_matched_assets": self.auto_matched_assets,
            "notes": self.notes,
        }

    @property
    def is_leaf(self) -> bool:
        return not self.children


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate TRD traceability matrix")
    parser.add_argument(
        "--requirements",
        type=Path,
        default=Path("reports/due_diligence/trd_requirements.json"),
        help="Path to hierarchical TRD requirements JSON file.",
    )
    parser.add_argument(
        "--inventory",
        type=Path,
        default=Path("reports/due_diligence/repo_inventory.json"),
        help="Path to repository inventory JSON artifact produced by repo_inventory.py.",
    )
    parser.add_argument(
        "--overrides",
        type=Path,
        default=Path("reports/due_diligence/traceability_overrides.json"),
        help="Optional overrides JSON specifying manual coverage adjustments.",
    )
    parser.add_argument(
        "--json",
        type=Path,
        required=True,
        help="Destination path for JSON traceability matrix output.",
    )
    parser.add_argument(
        "--markdown",
        type=Path,
        help="Destination path for Markdown summary output.",
    )
    return parser.parse_args()


def load_requirements(path: Path) -> Tuple[Dict[str, RequirementNode], List[str]]:
    data = json.loads(path.read_text(encoding="utf-8"))
    nodes: Dict[str, RequirementNode] = {}
    order: List[str] = []

    def visit(node: Dict[str, Any], parent: Optional[RequirementNode], depth: int) -> None:
        path_titles = parent.path_titles + [node["title"]] if parent else [node["title"]]
        requirement = RequirementNode(
            node_id=node["id"],
            title=node["title"],
            description=node.get("description", ""),
            level=depth,
            path_titles=path_titles,
            keywords=node.get("keywords"),
            parent_id=parent.id if parent else None,
        )
        nodes[requirement.id] = requirement
        order.append(requirement.id)
        if parent:
            parent.children.append(requirement.id)
        for child in node.get("children", []):
            visit(child, requirement, depth + 1)

    visit(data, None, 0)
    return nodes, order


def load_inventory(path: Path) -> List[Dict[str, Any]]:
    data = json.loads(path.read_text(encoding="utf-8"))
    entries: List[Dict[str, Any]] = []
    for file_entry in data.get("files", []):
        entries.append(
            {
                "path": file_entry["path"],
                "category": file_entry.get("category", ""),
                "type": "file",
            }
        )
    for directory, meta in data.get("directories", {}).items():
        entries.append(
            {
                "path": directory,
                "category": "directory",
                "type": "directory",
                "meta": meta,
            }
        )
    return entries


def load_overrides(path: Path) -> Dict[str, Dict[str, Any]]:
    if not path.exists():
        return {}
    raw = path.read_text(encoding="utf-8").strip()
    if not raw:
        return {}
    return json.loads(raw)


def auto_match(requirement: RequirementNode, inventory: Iterable[Dict[str, Any]]) -> List[str]:
    if not requirement.keywords:
        return []
    keyword_set = [kw for kw in requirement.keywords if kw]
    if not keyword_set:
        return []
    matches: List[str] = []
    for entry in inventory:
        path_lower = entry["path"].lower()
        if all(keyword in path_lower for keyword in keyword_set):
            matches.append(entry["path"])
    return sorted(set(matches))


def aggregate_status(child_statuses: Iterable[str]) -> str:
    statuses = list(child_statuses)
    if not statuses:
        return "missing"
    if all(status == "not-applicable" for status in statuses):
        return "not-applicable"
    if any(status == "missing" for status in statuses):
        return "missing"
    if any(status == "candidate" for status in statuses):
        return "candidate"
    if any(status == "partial" for status in statuses):
        return "partial"
    if all(status == "full" for status in statuses):
        return "full"
    return statuses[0]


def summarise(nodes: Dict[str, RequirementNode]) -> Dict[str, Any]:
    leaf_nodes = [node for node in nodes.values() if node.is_leaf and node.level > 0]
    counts: Dict[str, int] = {status: 0 for status in STATUS_ORDER}
    for node in leaf_nodes:
        counts[node.status] = counts.get(node.status, 0) + 1
    total = sum(counts.values())
    coverage = 0.0
    if total:
        covered = counts.get("full", 0)
        partial = counts.get("partial", 0)
        coverage = (covered + 0.5 * partial) / total
    return {
        "total_requirements": total,
        "status_counts": counts,
        "coverage_ratio": coverage,
    }


def render_markdown(
    nodes: Dict[str, RequirementNode],
    order: List[str],
    summary: Dict[str, Any],
) -> str:
    lines: List[str] = []
    lines.append("# TRD Traceability Matrix")
    lines.append("")
    lines.append("## Summary")
    lines.append("")
    counts = summary["status_counts"]
    lines.append("| Status | Count |")
    lines.append("| --- | --- |")
    for status in STATUS_ORDER:
        if status not in counts:
            continue
        lines.append(f"| {status.title()} | {counts[status]} |")
    lines.append("")
    lines.append(
        f"Coverage Score: {summary['coverage_ratio']:.2%} (Full + 0.5×Partial over total requirements)"
    )
    lines.append("")

    root_children = [node_id for node_id in order if nodes[node_id].level == 1]
    for category_id in root_children:
        category = nodes[category_id]
        lines.append(f"## {category.title} ({category.status.title()})")
        if category.description:
            lines.append("")
            lines.append(category.description)
        lines.append("")
        lines.append(
            "| ID | Requirement | Description | Status | Coverage Evidence | Notes |"
        )
        lines.append("| --- | --- | --- | --- | --- | --- |")
        for leaf in iterate_leaves(nodes, category_id):
            evidence = "<br>".join(leaf.implemented_assets) if leaf.implemented_assets else "—"
            note_text = "<br>".join(leaf.notes) if leaf.notes else ""
            lines.append(
                "| {id} | {title} | {description} | {status} | {evidence} | {notes} |".format(
                    id=leaf.id,
                    title=leaf.title.replace("|", "\\|"),
                    description=leaf.description.replace("|", "\\|"),
                    status=leaf.status.title(),
                    evidence=evidence.replace("|", "\\|"),
                    notes=note_text.replace("|", "\\|"),
                )
            )
        lines.append("")
    return "\n".join(lines).strip() + "\n"


def iterate_leaves(nodes: Dict[str, RequirementNode], root_id: str) -> List[RequirementNode]:
    root = nodes[root_id]
    if root.is_leaf:
        return [root]
    leaves: List[RequirementNode] = []
    for child_id in root.children:
        leaves.extend(iterate_leaves(nodes, child_id))
    return [leaf for leaf in leaves if leaf.level > 0]


def main() -> None:
    args = parse_args()
    nodes, order = load_requirements(args.requirements)
    inventory = load_inventory(args.inventory)
    overrides = load_overrides(args.overrides)

    # Evaluate nodes bottom-up so children finalize before parents.
    for node_id in reversed(order):
        node = nodes[node_id]
        override = overrides.get(node.id)
        if node.is_leaf:
            matches = auto_match(node, inventory)
            if matches:
                node.auto_matched_assets = matches
                node.notes.append("Auto-matched assets by keyword heuristics; requires validation.")
            if override:
                status = override.get("status", node.status)
                if status not in STATUS_PRIORITY:
                    raise ValueError(f"Invalid status '{status}' for requirement {node.id}")
                node.status = status
                assets = override.get("implemented_assets")
                if assets:
                    node.implemented_assets = sorted(set(assets))
                elif matches:
                    node.implemented_assets = matches
                notes = override.get("notes")
                if notes:
                    if isinstance(notes, list):
                        node.notes.extend(notes)
                    else:
                        node.notes.append(str(notes))
            else:
                if matches:
                    node.status = "candidate"
                    node.implemented_assets = matches
                else:
                    node.status = "missing"
        else:
            child_statuses = [nodes[child_id].status for child_id in node.children]
            node.status = aggregate_status(child_statuses)
            assets: List[str] = []
            notes: List[str] = []
            for child_id in node.children:
                child = nodes[child_id]
                assets.extend(child.implemented_assets)
                notes.extend(child.notes)
            if assets:
                node.implemented_assets = sorted(set(assets))
            if notes:
                node.notes = sorted(set(notes))
            if override:
                status = override.get("status")
                if status:
                    if status not in STATUS_PRIORITY:
                        raise ValueError(f"Invalid status '{status}' for requirement {node.id}")
                    node.status = status
                assets_override = override.get("implemented_assets")
                if assets_override:
                    node.implemented_assets = sorted(set(assets_override))
                notes_override = override.get("notes")
                if notes_override:
                    if isinstance(notes_override, list):
                        node.notes.extend(notes_override)
                    else:
                        node.notes.append(str(notes_override))

    summary = summarise(nodes)
    generated_at = dt.datetime.now(dt.timezone.utc).isoformat().replace("+00:00", "Z")
    payload = {
        "generated_at": generated_at,
        "requirements": [nodes[node_id].to_dict() for node_id in order if nodes[node_id].level > 0],
        "summary": summary,
        "source_files": {
            "requirements": str(args.requirements),
            "inventory": str(args.inventory),
            "overrides": str(args.overrides) if args.overrides else None,
        },
    }
    args.json.parent.mkdir(parents=True, exist_ok=True)
    args.json.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    if args.markdown:
        args.markdown.parent.mkdir(parents=True, exist_ok=True)
        markdown = render_markdown(nodes, order, summary)
        args.markdown.write_text(markdown, encoding="utf-8")


if __name__ == "__main__":
    main()
