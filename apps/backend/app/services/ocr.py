"""Optional OCR engine with graceful degradation when dependencies are missing."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import List


@dataclass
class OCRResult:
    text: str
    warnings: List[str]


class OCREngine:
    def __init__(self) -> None:
        try:
            from PIL import Image  # type: ignore
            import pytesseract  # type: ignore
        except Exception:  # pragma: no cover - optional dependency
            self._available = False
            self._image = None
            self._pytesseract = None
        else:  # pragma: no cover - optional dependency
            self._available = True
            self._image = Image
            self._pytesseract = pytesseract

    def extract_text(self, path: Path) -> OCRResult:
        warnings: List[str] = []
        if not self._available:
            warnings.append("OCR dependencies are not installed; returning empty text.")
            return OCRResult(text="", warnings=warnings)
        suffix = path.suffix.lower()
        if suffix not in {".png", ".jpg", ".jpeg", ".tif", ".tiff"}:
            warnings.append(f"OCR unsupported for extension {suffix} in lightweight runtime.")
            return OCRResult(text="", warnings=warnings)
        try:  # pragma: no cover - depends on optional libraries
            image = self._image.open(path)
            text = self._pytesseract.image_to_string(image)
            return OCRResult(text=text.strip(), warnings=warnings)
        except Exception as exc:  # pragma: no cover - depends on optional libraries
            warnings.append(f"OCR failed: {exc}")
            return OCRResult(text="", warnings=warnings)


ocr_engine = OCREngine()
