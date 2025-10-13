"""Simple knowledge graph persistence backed by JSON."""

from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Set

from ..config import settings


class GraphManager:
    def __init__(self, path: Path | None = None) -> None:
        self.path = path or settings.graph_path
        self.graph: Dict[str, Set[str]] = defaultdict(set)
        if self.path.exists():
            payload = json.loads(self.path.read_text(encoding="utf-8"))
            self.graph = {node: set(neighbors) for node, neighbors in payload.items()}

    def persist(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        serialisable = {node: sorted(neighbors) for node, neighbors in self.graph.items()}
        self.path.write_text(json.dumps(serialisable, indent=2), encoding="utf-8")

    def upsert_document(self, external_id: str, metadata: Dict[str, List[str]]) -> None:
        self.graph.setdefault(external_id, set())
        for key in ("dates", "entities", "emails", "monetary_amounts"):
            for value in metadata.get(key, []):
                target = f"{key}:{value}"
                self.graph[external_id].add(target)
                self.graph.setdefault(target, set()).add(external_id)
        self.persist()

    def neighbors(self, external_id: str) -> List[str]:
        neighbors = self.graph.get(external_id, set())
        return sorted(neighbors)


graph_manager = GraphManager()
