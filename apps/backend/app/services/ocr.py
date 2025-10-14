"""OCR microservice integration using Tesseract via pytesseract."""

from __future__ import annotations

import logging
import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List

import numpy as np
from PIL import Image
from pypdfium2 import PdfDocument

try:
    import pytesseract
except ImportError as exc:  # pragma: no cover - import guard
    raise RuntimeError(
        "pytesseract must be installed to use the OCR engine. Ensure dependencies from pyproject are installed."
    ) from exc

logger = logging.getLogger(__name__)


@dataclass
class OCRResult:
    """Structured OCR output including quality metrics."""

    text: str
    mean_confidence: float
    warnings: List[str]


class OCREngine:
    """OCR engine backed by the Tesseract command line tool."""

    def __init__(self) -> None:
        if shutil.which("tesseract") is None:  # pragma: no cover - environment check
            logger.warning("Tesseract executable not found in PATH; OCR requests will fail until installed.")
        self.ocr_lang = "eng"

    def _run_ocr(self, image: Image.Image) -> OCRResult:
        """Execute OCR on a PIL image and compute quality metrics."""

        data = pytesseract.image_to_data(image, lang=self.ocr_lang, output_type=pytesseract.Output.DICT)
        text = " ".join([word for word in data["text"] if word.strip()])
        confidences = np.array([float(conf) for conf in data["conf"] if conf not in {"-1", "-1.0"}], dtype=float)
        mean_confidence = float(confidences.mean()) if confidences.size else 0.0
        warnings: List[str] = []
        if mean_confidence < 65:
            warnings.append(f"Low OCR confidence detected ({mean_confidence:.2f}). Consider manual review.")
        if len(text) < 20:
            warnings.append("OCR output is sparse; input might require better scanning resolution.")
        return OCRResult(text=text.strip(), mean_confidence=mean_confidence, warnings=warnings)

    def _pdf_pages(self, path: Path) -> Iterable[Image.Image]:
        """Render PDF pages to PIL images for OCR."""

        document = PdfDocument(path)
        try:
            for page in document:
                pil_image = page.render(scale=2).to_pil()
                yield pil_image
        finally:
            document.close()

    def extract_text(self, path: Path) -> OCRResult:
        """Extract text from the provided document via OCR."""

        suffix = path.suffix.lower()
        if suffix in {".png", ".jpg", ".jpeg", ".tiff", ".bmp"}:
            image = Image.open(path)
            return self._run_ocr(image)
        if suffix == ".pdf":
            results: List[OCRResult] = []
            for page_image in self._pdf_pages(path):
                results.append(self._run_ocr(page_image))
            if not results:
                return OCRResult(text="", mean_confidence=0.0, warnings=["PDF rendered zero pages for OCR."])
            text = "\n".join(result.text for result in results)
            mean_conf = float(np.mean([result.mean_confidence for result in results]))
            warnings = [msg for result in results for msg in result.warnings]
            return OCRResult(text=text, mean_confidence=mean_conf, warnings=warnings)
        raise ValueError(f"Unsupported file type for OCR: {suffix}")


ocr_engine = OCREngine()
