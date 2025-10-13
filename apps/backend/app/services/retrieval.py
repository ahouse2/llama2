"""Hybrid retrieval combining token similarity with graph signals."""

from __future__ import annotations

import math
import re
import uuid
from dataclasses import dataclass
from typing import Dict, Iterable, List, Optional

from ..config import settings
from ..database import Document, get_session
from .graph import graph_manager

TOKEN_PATTERN = re.compile(r"\b\w+\b")


@dataclass
class SearchResult:
    document_id: str
    score: float
    snippet: str
    highlights: Dict[str, List[str]]
    trace_id: str


class HybridRetriever:
    def __init__(self) -> None:
        self.document_vectors: Dict[str, Dict[str, float]] = {}
        self.document_norms: Dict[str, float] = {}
        self.document_metadata: Dict[str, Dict[str, List[str]]] = {}
        self._rebuild_index()

    def _tokenize(self, text: str) -> List[str]:
        return [token.lower() for token in TOKEN_PATTERN.findall(text)]

    def _rebuild_index(self) -> None:
        with get_session() as session:
            documents = session.list_documents()
        if not documents:
            self.document_vectors.clear()
            self.document_norms.clear()
            self.document_metadata.clear()
            return
        doc_tokens: Dict[str, List[str]] = {}
        for document in documents:
            tokens = self._tokenize(document.text_content)
            doc_tokens[document.external_id] = tokens
            self.document_metadata[document.external_id] = document.metadata
        doc_freq: Dict[str, int] = {}
        for tokens in doc_tokens.values():
            for token in set(tokens):
                doc_freq[token] = doc_freq.get(token, 0) + 1
        total_docs = len(doc_tokens)
        self.document_vectors.clear()
        self.document_norms.clear()
        for doc_id, tokens in doc_tokens.items():
            tf: Dict[str, float] = {}
            for token in tokens:
                tf[token] = tf.get(token, 0.0) + 1.0
            vector: Dict[str, float] = {}
            norm = 0.0
            for token, term_freq in tf.items():
                idf = math.log((1 + total_docs) / (1 + doc_freq.get(token, 0))) + 1
                weight = (term_freq / len(tokens)) * idf
                vector[token] = weight
                norm += weight * weight
            self.document_vectors[doc_id] = vector
            self.document_norms[doc_id] = math.sqrt(norm) if norm else 1.0

    def rebuild(self) -> None:
        self._rebuild_index()

    def update_with_document(self, document: Document) -> None:
        self._rebuild_index()

    def search(
        self,
        query: str,
        *,
        filters: Optional[Dict[str, Iterable[str]]] = None,
        top_k: int = 5,
    ) -> List[SearchResult]:
        if not query.strip():
            return []
        if not self.document_vectors:
            self._rebuild_index()
        if not self.document_vectors:
            return []
        query_tokens = self._tokenize(query)
        if not query_tokens:
            return []
        tf: Dict[str, float] = {}
        for token in query_tokens:
            tf[token] = tf.get(token, 0.0) + 1.0
        total_docs = max(len(self.document_vectors), 1)
        query_vector: Dict[str, float] = {}
        query_norm = 0.0
        for token, term_freq in tf.items():
            doc_freq = sum(1 for vector in self.document_vectors.values() if token in vector)
            idf = math.log((1 + total_docs) / (1 + doc_freq)) + 1
            weight = (term_freq / len(query_tokens)) * idf
            query_vector[token] = weight
            query_norm += weight * weight
        query_norm = math.sqrt(query_norm) if query_norm else 1.0

        results: List[SearchResult] = []
        for doc_id, vector in self.document_vectors.items():
            dot = sum(weight * query_vector.get(token, 0.0) for token, weight in vector.items())
            semantic_score = dot / (self.document_norms.get(doc_id, 1.0) * query_norm)
            metadata = self.document_metadata.get(doc_id, {})
            structural_bonus = self._graph_bonus(doc_id, query_tokens)
            filter_multiplier = self._apply_filters(metadata, filters)
            final_score = semantic_score * settings.reranker_alpha + structural_bonus
            final_score *= filter_multiplier
            snippet = self._build_snippet(doc_id, query_tokens)
            highlights = self._build_highlights(metadata, query_tokens)
            trace_id = f"search-{uuid.uuid4().hex[:12]}"
            results.append(SearchResult(doc_id, final_score, snippet, highlights, trace_id))
        results.sort(key=lambda item: item.score, reverse=True)
        return results[:top_k]

    def _graph_bonus(self, doc_id: str, tokens: List[str]) -> float:
        neighbors = graph_manager.neighbors(doc_id)
        if not neighbors:
            return 0.0
        matches = 0
        for token in tokens:
            matches += sum(1 for neighbor in neighbors if token in neighbor.lower())
        return min(matches * 0.05, 0.25)

    def _apply_filters(self, metadata: Dict[str, List[str]], filters: Optional[Dict[str, Iterable[str]]]) -> float:
        if not filters:
            return 1.0
        multiplier = 1.0
        for key, values in filters.items():
            expected = {value.lower() for value in values}
            actual = {value.lower() for value in metadata.get(key, [])}
            if expected and not actual.intersection(expected):
                multiplier *= 0.1
        return multiplier

    def _build_snippet(self, doc_id: str, tokens: List[str]) -> str:
        with get_session() as session:
            document = session.get_document_by_external_id(doc_id)
        if not document:
            return ""
        text = document.text_content
        lowered = text.lower()
        for token in tokens:
            index = lowered.find(token)
            if index != -1:
                start = max(0, index - 80)
                end = min(len(text), index + 120)
                return text[start:end].strip()
        return text[:160].strip()

    def _build_highlights(self, metadata: Dict[str, List[str]], tokens: List[str]) -> Dict[str, List[str]]:
        highlights: Dict[str, List[str]] = {}
        lowered_tokens = [token.lower() for token in tokens]
        for key, values in metadata.items():
            matches = [value for value in values if any(token in value.lower() for token in lowered_tokens)]
            if matches:
                highlights[key] = matches
        return highlights


retriever_service = HybridRetriever()
