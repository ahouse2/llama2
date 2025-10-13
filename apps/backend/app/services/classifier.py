"""Rule-based document classification utilities."""
"""Document classification services."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List

from .parser import parser_service
from typing import Dict, Iterable, List

from rapidfuzz import fuzz
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


@dataclass
class DocumentClassification:
    """Classification outputs for a document."""

    document_type: str
    privilege_risk: float
    importance_score: float


class DocumentClassifier:
    """Rule-driven classifier relying on keyword statistics."""

    def __init__(self) -> None:
        self.type_keywords: Dict[str, List[str]] = {
            "contract": ["agreement", "contract", "obligation", "services", "party"],
            "email": ["from:", "sent:", "subject:", "mailto", "inbox"],
            "pleading": ["court", "plaintiff", "defendant", "motion", "hearing"],
            "financial": ["invoice", "payment", "account", "balance", "statement"],
        }
        self.privilege_markers = [
class CorpusStatistics:
    """Maintain TF-IDF centroid for importance scoring."""

    def __init__(self) -> None:
        self.vectorizer = TfidfVectorizer(stop_words="english", ngram_range=(1, 2))
        self.document_vectors = None
        self.documents: List[str] = []

    def add_document(self, text: str) -> None:
        self.documents.append(text)
        self.document_vectors = self.vectorizer.fit_transform(self.documents)

    def novelty(self, text: str) -> float:
        if not self.documents:
            return 1.0
        vector = self.vectorizer.transform([text])
        similarities = cosine_similarity(vector, self.document_vectors)[0]
        novelty_score = 1.0 - float(similarities.max(initial=0.0))
        return max(novelty_score, 0.0)


class DocumentClassifier:
    """Rule-driven classifier with TF-IDF backed novelty scoring."""

    def __init__(self, corpus: CorpusStatistics | None = None) -> None:
        self.corpus = corpus or CorpusStatistics()
        self.type_keywords: Dict[str, Iterable[str]] = {
            "contract": ["agreement", "party", "term", "obligation", "contract"],
            "email": ["from:", "sent:", "subject", "mailto"],
            "pleading": ["court", "plaintiff", "defendant", "motion", "hearing"],
            "financial": ["invoice", "balance", "payment", "account", "statement"],
        }
        self.privilege_keywords = [
            "privileged",
            "confidential",
            "attorney",
            "counsel",
            "work product",
            "do not disclose",
        ]
        self.corpus_lengths: List[int] = []

    def classify(self, text: str, metadata: Dict[str, List[str]]) -> DocumentClassification:
        tokens = parser_service.tokenize(text)
        document_type = self._infer_document_type(tokens)
        privilege_risk = self._score_privilege(tokens)
        importance_score = self._estimate_importance(text, metadata)
        self.corpus_lengths.append(len(tokens))
        return DocumentClassification(document_type, privilege_risk, importance_score)

    def _infer_document_type(self, tokens: List[str]) -> str:
        best_type = "unknown"
        best_score = -1
        token_set = set(tokens)
        for candidate, keywords in self.type_keywords.items():
            coverage = sum(1 for keyword in keywords if keyword.lower() in token_set)
            if coverage == 0:
                continue
            proximity = sum(tokens.count(keyword.lower()) for keyword in keywords)
            score = coverage * 5 + proximity
            if score > best_score:
                best_score = score
                best_type = candidate
        return best_type

    def _score_privilege(self, tokens: List[str]) -> float:
        if not tokens:
            return 0.0
        hits = sum(tokens.count(marker.lower()) for marker in self.privilege_markers)
        density = hits / max(len(tokens), 1)
        return round(min(1.0, hits * 0.1 + density * 5), 3)

    def _estimate_importance(self, text: str, metadata: Dict[str, List[str]]) -> float:
        word_count = len(parser_service.tokenize(text))
        avg_length = sum(self.corpus_lengths) / len(self.corpus_lengths) if self.corpus_lengths else word_count
        length_factor = min(word_count / max(avg_length, 1), 2.0) / 2.0
        entity_bonus = min(len(metadata.get("entities", [])) / 10, 0.3)
        date_bonus = min(len(metadata.get("dates", [])) / 5, 0.3)
        monetary_bonus = 0.2 if metadata.get("monetary_amounts") else 0.0
        score = length_factor * 0.4 + entity_bonus + date_bonus + monetary_bonus
        return round(min(score, 1.0), 3)

    def classify(self, text: str, metadata: Dict[str, List[str]]) -> DocumentClassification:
        document_type = self._determine_type(text)
        privilege_risk = self._compute_privilege_risk(text)
        importance_score = self._estimate_importance(text, metadata)
        self.corpus.add_document(text)
        return DocumentClassification(document_type=document_type, privilege_risk=privilege_risk, importance_score=importance_score)

    def _determine_type(self, text: str) -> str:
        lowered = text.lower()
        best_match = "unknown"
        highest_score = 0.0
        for candidate, keywords in self.type_keywords.items():
            coverage = sum(1 for keyword in keywords if keyword in lowered)
            fuzzy = max(fuzz.partial_ratio(keyword, lowered) for keyword in keywords)
            score = coverage * 10 + fuzzy
            if score > highest_score:
                highest_score = score
                best_match = candidate
        return best_match

    def _compute_privilege_risk(self, text: str) -> float:
        lowered = text.lower()
        hits = sum(1 for keyword in self.privilege_keywords if keyword in lowered)
        density = hits / max(len(lowered.split()), 1)
        signal = min(1.0, hits * 0.2 + density * 10)
        return round(signal, 3)

    def _estimate_importance(self, text: str, metadata: Dict[str, List[str]]) -> float:
        length_factor = min(len(text) / 5000, 1.0)
        entity_bonus = min(len(metadata.get("entities", [])) / 10, 1.0)
        date_bonus = min(len(metadata.get("dates", [])) / 5, 1.0)
        novelty = self.corpus.novelty(text)
        importance = 0.3 * length_factor + 0.25 * entity_bonus + 0.25 * date_bonus + 0.2 * novelty
        return round(min(max(importance, 0.0), 1.0), 3)


classifier_service = DocumentClassifier()
