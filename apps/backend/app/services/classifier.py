"""Document classification services."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Iterable, List

from rapidfuzz import fuzz
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from .parser import parser_service


@dataclass
class DocumentClassification:
    """Classification outputs for a document."""

    document_type: str
    privilege_risk: float
    importance_score: float


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
        document_type = self._infer_document_type(tokens, text)
        privilege_risk = self._score_privilege(tokens)
        importance_score = self._estimate_importance(text, metadata)
        self.corpus_lengths.append(len(tokens))
        self.corpus.add_document(text)
        return DocumentClassification(document_type, privilege_risk, importance_score)

    def _infer_document_type(self, tokens: List[str], raw_text: str) -> str:
        if not tokens:
            return "unknown"
        lowered = raw_text.lower()
        best_type = "unknown"
        best_score = -1.0
        for candidate, keywords in self.type_keywords.items():
            coverage = sum(1 for keyword in keywords if keyword in lowered)
            if coverage == 0:
                continue
            fuzzy = max(fuzz.partial_ratio(keyword, lowered) for keyword in keywords)
            score = coverage * 10 + fuzzy
            if score > best_score:
                best_score = score
                best_type = candidate
        return best_type

    def _score_privilege(self, tokens: List[str]) -> float:
        if not tokens:
            return 0.0
        tokenized = " ".join(tokens)
        hits = sum(tokenized.count(keyword.replace(" ", "")) for keyword in self.privilege_keywords)
        density = hits / max(len(tokens), 1)
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
