"""Document parsing utilities with metadata extraction."""

from __future__ import annotations

import json
import logging
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List

from dateparser.search import search_dates
from dateutil import parser as date_parser
from pypdf import PdfReader

logger = logging.getLogger(__name__)

DATE_PATTERN = re.compile(r"\b(\d{1,2}[/-]\d{1,2}[/-]\d{2,4}|\d{4}-\d{2}-\d{2})\b")
MONEY_PATTERN = re.compile(r"\$\s?([\d,]+(?:\.\d{2})?)")
EMAIL_PATTERN = re.compile(r"[\w.+-]+@[\w.-]+", re.IGNORECASE)
ENTITY_PATTERN = re.compile(r"\b([A-Z][a-z]+\s+[A-Z][a-z]+)\b")
TOKEN_PATTERN = re.compile(r"\b\w+\b")


@dataclass
class ParsedDocument:
    """Structured representation of parsed text and extracted metadata."""

    text: str
    metadata: Dict[str, List[str]]


class DocumentParser:
    """Parse supported files and derive structured metadata."""

    def __init__(self) -> None:
        self.supported_extensions = {".txt", ".md", ".json", ".pdf"}

    def parse(self, path: Path) -> ParsedDocument:
        """Parse the provided file and return text content with metadata."""

        suffix = path.suffix.lower()
        if suffix not in self.supported_extensions:
            raise ValueError(f"Unsupported extension: {suffix}")
        if suffix in {".txt", ".md"}:
            text = path.read_text(encoding="utf-8", errors="ignore")
        elif suffix == ".json":
            text = self._render_json(path)
        elif suffix == ".pdf":
            text = self._parse_pdf(path)
        else:  # pragma: no cover - guard for future extensions
            text = path.read_text(encoding="utf-8", errors="ignore")
        metadata = self._extract_metadata(text)
        return ParsedDocument(text=text, metadata=metadata)

    def tokenize(self, text: str) -> List[str]:
        """Tokenise text for downstream NLP utilities."""

        return [token.lower() for token in TOKEN_PATTERN.findall(text)]

    def _render_json(self, path: Path) -> str:
        data = json.loads(path.read_text(encoding="utf-8"))
        return json.dumps(data, indent=2, sort_keys=True)

    def _parse_pdf(self, path: Path) -> str:
        pages: List[str] = []
        reader = PdfReader(path)
        for page in reader.pages:
            try:
                pages.append(page.extract_text() or "")
            except Exception as exc:  # pragma: no cover - PyPDF variability
                logger.warning("Failed to extract text from page due to %s", exc)
        return "\n".join(pages)

    def _extract_metadata(self, text: str) -> Dict[str, List[str]]:
        explicit_dates = self._normalize_dates(DATE_PATTERN.findall(text))
        natural_dates = self._extract_natural_language_dates(text)
        dates = sorted(set(explicit_dates + natural_dates))
        money = [amount for amount in MONEY_PATTERN.findall(text)]
        emails = sorted(set(match.lower() for match in EMAIL_PATTERN.findall(text)))
        entities = sorted({match.strip() for match in ENTITY_PATTERN.findall(text)})
        return {
            "dates": dates,
            "monetary_amounts": money,
            "emails": emails,
            "entities": entities,
        }

    def _normalize_dates(self, matches: Iterable[str]) -> List[str]:
        normalized: List[str] = []
        for raw in matches:
            try:
                parsed = date_parser.parse(raw, dayfirst=False, fuzzy=True)
                normalized.append(parsed.date().isoformat())
            except (ValueError, OverflowError):  # pragma: no cover - defensive guard
                continue
        return sorted(set(normalized))

    def _extract_natural_language_dates(self, text: str) -> List[str]:
        results = search_dates(text, settings={"RETURN_AS_TIMEZONE_AWARE": False}) or []
        normalized = {result.date().isoformat() for _, result in results}
        return sorted(normalized)


parser_service = DocumentParser()
