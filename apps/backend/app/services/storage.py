"""Storage utilities for handling raw document persistence."""

from __future__ import annotations

import hashlib
import mimetypes
from pathlib import Path
from typing import Tuple

from ..config import settings


class StorageService:
    """Persist files to durable storage and expose helper utilities."""

    def __init__(self, base_directory: Path | None = None) -> None:
        self.base_directory = base_directory or settings.storage_directory
        self.base_directory.mkdir(parents=True, exist_ok=True)

    def save_upload(self, filename: str, data: bytes) -> Tuple[Path, str, str]:
        """Persist an uploaded file and return (path, checksum, mime type)."""

        sanitized = Path(filename).name
        destination = self.base_directory / sanitized
        destination.write_bytes(data)
        checksum = hashlib.sha256(data).hexdigest()
        mime_type, _ = mimetypes.guess_type(destination.name)
        return destination, checksum, mime_type or "application/octet-stream"

    def compute_checksum(self, path: Path) -> str:
        """Compute the SHA256 checksum for a file on disk."""

        hasher = hashlib.sha256()
        with path.open("rb") as file:
            for chunk in iter(lambda: file.read(8192), b""):
                hasher.update(chunk)
        return hasher.hexdigest()

    def detect_mime_type(self, path: Path) -> str:
        """Guess the MIME type for the provided path."""

        mime_type, _ = mimetypes.guess_type(path.name)
        return mime_type or "application/octet-stream"


storage_service = StorageService()
