"""Rule-based document classification utilities."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List

from .parser import parser_service


@dataclass
class DocumentClassification:
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


classifier_service = DocumentClassifier()
