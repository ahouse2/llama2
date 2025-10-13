"""Document parsing and lightweight metadata extraction."""
"""Document parsing and metadata extraction utilities."""

from __future__ import annotations

import json
import logging
import re
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, List

MONTHS = {
    "january": 1,
    "february": 2,
    "march": 3,
    "april": 4,
    "may": 5,
    "june": 6,
    "july": 7,
    "august": 8,
    "september": 9,
    "october": 10,
    "november": 11,
    "december": 12,
}

ISO_DATE_PATTERN = re.compile(r"\b(\d{4})-(\d{2})-(\d{2})\b")
SLASH_DATE_PATTERN = re.compile(r"\b(\d{1,2})[/-](\d{1,2})[/-](\d{2,4})\b")
NATURAL_DATE_PATTERN = re.compile(
    r"\b(" + "|".join(MONTHS.keys()) + r")\s+(\d{1,2})(?:,)?\s+(\d{4})\b",
    re.IGNORECASE,
)
MONEY_PATTERN = re.compile(r"\$\s?([\d,]+(?:\.\d{2})?)")
EMAIL_PATTERN = re.compile(r"[\w.+-]+@[\w.-]+", re.IGNORECASE)
ENTITY_PATTERN = re.compile(r"\b([A-Z][a-z]+\s+[A-Z][a-z]+)\b")
TOKEN_PATTERN = re.compile(r"\b\w+\b")
from typing import Dict, Iterable, List, Optional

from dateparser.search import search_dates
from dateutil import parser as date_parser
from pypdf import PdfReader

logger = logging.getLogger(__name__)

DATE_PATTERN = re.compile(r"\b(\d{1,2}[/-]\d{1,2}[/-]\d{2,4}|\d{4}-\d{2}-\d{2})\b")
MONEY_PATTERN = re.compile(r"\$\s?([\d,]+(?:\.\d{2})?)")
EMAIL_PATTERN = re.compile(r"[\w.]+@[\w.-]+", re.IGNORECASE)
ENTITY_PATTERN = re.compile(r"\b([A-Z][a-z]+\s+[A-Z][a-z]+)\b")


@dataclass
class ParsedDocument:
    """Structured representation of a parsed document."""

    text: str
    metadata: Dict[str, List[str]]


class DocumentParser:
    """Parse local files and extract structured metadata."""

    def __init__(self) -> None:
        self.supported_extensions = {".txt", ".md", ".json"}

    def parse(self, path: Path) -> ParsedDocument:
        if path.suffix.lower() not in self.supported_extensions:
            raise ValueError(f"Unsupported extension: {path.suffix}")
        if path.suffix.lower() == ".json":
            text = self._render_json(path)
        else:
            text = path.read_text(encoding="utf-8", errors="ignore")
        metadata = {
            "dates": self._extract_dates(text),
            "monetary_amounts": self._extract_pattern(MONEY_PATTERN, text),
            "emails": sorted(set(match.lower() for match in EMAIL_PATTERN.findall(text))),
            "entities": sorted(set(match.strip() for match in ENTITY_PATTERN.findall(text))),
        }
        return ParsedDocument(text=text, metadata=metadata)

    def _render_json(self, path: Path) -> str:
        return json.dumps(json.loads(path.read_text(encoding="utf-8")), indent=2, sort_keys=True)

    def _extract_dates(self, text: str) -> List[str]:
        candidates: List[str] = []
        candidates.extend(self._parse_iso_dates(text))
        candidates.extend(self._parse_slash_dates(text))
        candidates.extend(self._parse_natural_dates(text))
        unique = sorted(set(candidates))
        return unique

    def _parse_iso_dates(self, text: str) -> List[str]:
        return ["-".join(match) for match in ISO_DATE_PATTERN.findall(text)]

    def _parse_slash_dates(self, text: str) -> List[str]:
        results: List[str] = []
        for month, day, year in SLASH_DATE_PATTERN.findall(text):
            try:
                year_int = int(year)
                if year_int < 100:
                    year_int += 2000 if year_int < 50 else 1900
                parsed = datetime(year_int, int(month), int(day))
                results.append(parsed.date().isoformat())
            except ValueError:
                continue
        return results

    def _parse_natural_dates(self, text: str) -> List[str]:
        results: List[str] = []
        for month_name, day, year in NATURAL_DATE_PATTERN.findall(text):
            month = MONTHS.get(month_name.lower())
            if not month:
                continue
            try:
                parsed = datetime(int(year), month, int(day))
            except ValueError:
                continue
            results.append(parsed.date().isoformat())
        return results

    def _extract_pattern(self, pattern: re.Pattern[str], text: str) -> List[str]:
        return [match.strip() for match in pattern.findall(text)]

    def tokenize(self, text: str) -> List[str]:
        return [token.lower() for token in TOKEN_PATTERN.findall(text)]
    """Parse documents and extract structured metadata."""

    def __init__(self) -> None:
        self.supported_extensions = {".txt", ".md", ".json", ".pdf"}

    def parse(self, path: Path) -> ParsedDocument:
        """Parse the file and return text with metadata."""

        suffix = path.suffix.lower()
        if suffix not in self.supported_extensions:
            raise ValueError(f"Unsupported extension: {suffix}")
        if suffix in {".txt", ".md"}:
            text = path.read_text(encoding="utf-8", errors="ignore")
        elif suffix == ".json":
            text = self._render_json(path)
        elif suffix == ".pdf":
            text = self._parse_pdf(path)
        else:  # pragma: no cover - unreachable due to guard above
            text = path.read_text(encoding="utf-8", errors="ignore")
        metadata = self._extract_metadata(text)
        return ParsedDocument(text=text, metadata=metadata)

    def _render_json(self, path: Path) -> str:
        """Render JSON file to canonical text."""

        data = json.loads(path.read_text(encoding="utf-8"))
        return json.dumps(data, indent=2, sort_keys=True)

    def _parse_pdf(self, path: Path) -> str:
        """Extract textual content from PDF using PyPDF."""

        reader = PdfReader(path)
        pages = []
        for page in reader.pages:
            try:
                pages.append(page.extract_text() or "")
            except Exception as exc:  # pragma: no cover - PyPDF internal behavior
                logger.warning("Failed to extract text from page due to %s", exc)
        return "\n".join(pages)

    def _extract_metadata(self, text: str) -> Dict[str, List[str]]:
        """Extract metadata fragments from text."""

        explicit_dates = self._normalize_dates(DATE_PATTERN.findall(text))
        parsed_dates = self._extract_natural_language_dates(text)
        dates = sorted(set(explicit_dates + parsed_dates))
        money = [amount for amount in MONEY_PATTERN.findall(text)]
        emails = sorted(set(EMAIL_PATTERN.findall(text)))
        entities = sorted({match.strip() for match in ENTITY_PATTERN.findall(text)})
        return {
            "dates": dates,
            "monetary_amounts": money,
            "emails": emails,
            "entities": entities,
        }

    def _normalize_dates(self, matches: Iterable[str]) -> List[str]:
        """Normalize extracted date strings to ISO format."""

        normalized: List[str] = []
        for raw in matches:
            try:
                parsed = date_parser.parse(raw, dayfirst=False, fuzzy=True)
                normalized.append(parsed.date().isoformat())
            except (ValueError, OverflowError):  # pragma: no cover - guard
                continue
        return sorted(set(normalized))

    def _extract_natural_language_dates(self, text: str) -> List[str]:
        """Use dateparser to identify month names and natural language dates."""

        results = search_dates(text, settings={"RETURN_AS_TIMEZONE_AWARE": False}) or []
        normalized = {result.date().isoformat() for _, result in results}
        return sorted(normalized)


parser_service = DocumentParser()
