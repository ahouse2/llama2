"""Hybrid retrieval service combining lexical, structural, and metadata cues."""

from __future__ import annotations

import json
import uuid
from pathlib import Path
from typing import Dict, Iterable, List, Optional

import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from ..config import settings
from ..database import Document, get_session
from ..schemas import SearchResult
from .graph import graph_manager


class HybridRetriever:
    """Combine TF-IDF similarity with graph proximity for ranked retrieval."""

    def __init__(self, artifact_dir: Path | None = None) -> None:
        self.artifact_dir = artifact_dir or settings.retriever_index_path
        self.vectorizer_path = self.artifact_dir / "vectorizer.joblib"
        self.matrix_path = self.artifact_dir / "matrix.joblib"
        self.doc_ids_path = self.artifact_dir / "doc_ids.json"
        self.vectorizer = TfidfVectorizer(stop_words="english", ngram_range=(1, 2))
        self.document_matrix = None
        self.document_ids: List[str] = []
        self.metadata_cache: Dict[str, Dict[str, List[str]]] = {}
        self.text_cache: Dict[str, str] = {}
        self._load_if_exists()

    def _load_if_exists(self) -> None:
        if self.vectorizer_path.exists():
            self.vectorizer = joblib.load(self.vectorizer_path)
        if self.matrix_path.exists():
            self.document_matrix = joblib.load(self.matrix_path)
        if self.doc_ids_path.exists():
            self.document_ids = json.loads(self.doc_ids_path.read_text(encoding="utf-8"))
        self._hydrate_metadata()

    def _hydrate_metadata(self) -> None:
        if not self.document_ids:
            self.metadata_cache.clear()
            self.text_cache.clear()
            return
        with get_session() as session:
            documents = (
                session.query(Document)
                .filter(Document.external_id.in_(self.document_ids))
                .all()
            )
            self.metadata_cache = {doc.external_id: doc.metadata_json or {} for doc in documents}
            self.text_cache = {doc.external_id: doc.text_content for doc in documents}

    def rebuild(self) -> None:
        with get_session() as session:
            documents = session.query(Document).order_by(Document.id).all()
            texts = [document.text_content for document in documents]
            if not texts:
                self.document_matrix = None
                self.document_ids = []
                self.metadata_cache = {}
                self.text_cache = {}
                self._persist()
                return
            self.document_matrix = self.vectorizer.fit_transform(texts)
            self.document_ids = [document.external_id for document in documents]
            self.metadata_cache = {document.external_id: document.metadata_json or {} for document in documents}
            self.text_cache = {document.external_id: document.text_content for document in documents}
            self._persist()

    def update_with_document(self, document: Document | None = None) -> None:
        """Refresh the retrieval index after a document change."""

        # For simplicity and determinism rebuild the full index. The dataset is expected to be small.
        self.rebuild()

    def _persist(self) -> None:
        self.artifact_dir.mkdir(parents=True, exist_ok=True)
        joblib.dump(self.vectorizer, self.vectorizer_path)
        joblib.dump(self.document_matrix, self.matrix_path)
        self.doc_ids_path.write_text(json.dumps(self.document_ids), encoding="utf-8")

    def search(self, query: str, *, filters: Optional[Dict[str, Iterable[str]]] = None, top_k: int = 5) -> List[SearchResult]:
        if not query.strip():
            return []
        if self.document_matrix is None:
            self.rebuild()
        if self.document_matrix is None:
            return []
        query_vector = self.vectorizer.transform([query])
        semantic_scores = cosine_similarity(query_vector, self.document_matrix)[0]
        results: List[SearchResult] = []
        for idx, doc_id in enumerate(self.document_ids):
            metadata = self.metadata_cache.get(doc_id, {})
            structural_bonus = self._graph_bonus(doc_id, query)
            filter_penalty = self._apply_filters(metadata, filters)
            score = float(semantic_scores[idx]) * settings.reranker_alpha + structural_bonus
            score *= filter_penalty
            snippet = self._build_snippet(doc_id, query)
            highlights = self._build_highlights(metadata, query)
            trace_id = f"search-{uuid.uuid4().hex[:12]}"
            results.append(
                SearchResult(
                    document_id=doc_id,
                    score=score,
                    snippet=snippet,
                    highlights=highlights,
                    trace_id=trace_id,
                )
            )
        results.sort(key=lambda item: item.score, reverse=True)
        return results[:top_k]

    def _graph_bonus(self, doc_id: str, query: str) -> float:
        neighbors = graph_manager.neighbors(doc_id)
        if not neighbors:
            return 0.0
        tokens = query.lower().split()
        hits = sum(1 for neighbor in neighbors for token in tokens if token in neighbor.lower())
        return min(hits * 0.05, 0.25)

    def _apply_filters(self, metadata: Dict[str, List[str]], filters: Optional[Dict[str, Iterable[str]]]) -> float:
        if not filters:
            return 1.0
        penalty = 1.0
        for key, values in filters.items():
            doc_values = {value.lower() for value in metadata.get(key, [])}
            if values and not doc_values.intersection({value.lower() for value in values}):
                penalty *= 0.1
        return penalty

    def _build_snippet(self, doc_id: str, query: str, length: int = 320) -> str:
        text = self.text_cache.get(doc_id)
        if text is None:
            with get_session() as session:
                document = session.query(Document).filter_by(external_id=doc_id).one_or_none()
                text = document.text_content if document else ""
                if document:
                    self.text_cache[doc_id] = text
        lowered = text.lower()
        tokens = query.lower().split()
        for token in tokens:
            index = lowered.find(token)
            if index != -1:
                start = max(0, index - length // 2)
                end = min(len(text), start + length)
                return text[start:end].strip()
        return text[:length].strip()

    def _build_highlights(self, metadata: Dict[str, List[str]], query: str) -> Dict[str, List[str]]:
        tokens = {token.lower() for token in query.split()}
        highlights: Dict[str, List[str]] = {}
        for key, values in metadata.items():
            matched = [value for value in values if any(token in value.lower() for token in tokens)]
            if matched:
                highlights[key] = matched
        return highlights


retriever_service = HybridRetriever()
