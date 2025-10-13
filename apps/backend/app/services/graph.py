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
"""Knowledge graph management."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Dict, Iterable, List

import networkx as nx
import pickle

from ..config import settings

logger = logging.getLogger(__name__)


class GraphManager:
    """Persist a NetworkX-backed knowledge graph to disk."""

    def __init__(self, path: Path | None = None) -> None:
        self.path = path or settings.graph_path
        if self.path.exists():
            with self.path.open("rb") as handle:
                self.graph = pickle.load(handle)
        else:
            self.graph = nx.MultiDiGraph()

    def persist(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open("wb") as handle:
            pickle.dump(self.graph, handle)

    def upsert_document(self, external_id: str, metadata: Dict[str, List[str]]) -> None:
        """Insert or update document node with metadata edges."""

        self.graph.add_node(external_id, type="document")
        for date in metadata.get("dates", []):
            self._link(external_id, f"date::{date}", relation="occurs_on")
        for entity in metadata.get("entities", []):
            self._link(external_id, f"entity::{entity}", relation="mentions")
        for email in metadata.get("emails", []):
            self._link(external_id, f"email::{email}", relation="involves")
        for amount in metadata.get("monetary_amounts", []):
            self._link(external_id, f"amount::{amount}", relation="values")
        self.persist()

    def neighbors(self, external_id: str) -> List[str]:
        if external_id not in self.graph:
            return []
        neighbor_nodes = set(self.graph.neighbors(external_id))
        neighbor_nodes.update(self.graph.predecessors(external_id))
        return list(neighbor_nodes)

    def _link(self, source: str, target: str, relation: str) -> None:
        self.graph.add_node(target, type=relation)
        self.graph.add_edge(source, target, relation=relation)


graph_manager = GraphManager()
