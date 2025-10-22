"""Asynchronous ingestion orchestration for documents."""

from __future__ import annotations

import asyncio
import traceback
from pathlib import Path
from typing import List
from uuid import uuid4

from ..config import settings
from ..database import DeadLetter, Document, IngestionRun, MetadataFragment, get_session, utc_now
from .classifier import classifier_service
from .graph import graph_manager
from .ocr import OCRResult, ocr_engine
from .parser import ParsedDocument, parser_service
from .retrieval import retriever_service
from .storage import storage_service


async def _compute_checksum(path: Path) -> str:
    return await asyncio.to_thread(storage_service.compute_checksum, path)


async def _detect_mime_type(path: Path) -> str:
    return await asyncio.to_thread(storage_service.detect_mime_type, path)


async def _parse_document(path: Path) -> ParsedDocument:
    return await asyncio.to_thread(parser_service.parse, path)


async def _run_ocr(path: Path) -> OCRResult:
    return await asyncio.to_thread(ocr_engine.extract_text, path)


async def ingest_document_flow(path: str, source: str = "upload") -> str:
    """Ingest a single document and return its external identifier."""

    absolute_path = Path(path).resolve()
    if not absolute_path.exists():
        raise FileNotFoundError(f"Document not found: {absolute_path}")
    if absolute_path.suffix.lower() not in settings.allowed_extensions:
        raise ValueError(f"Unsupported extension for ingestion: {absolute_path.suffix}")

    trace_id = uuid4().hex
    with get_session() as session:
        run = IngestionRun(trace_id=trace_id, source=source, status="running")
        session.add(run)

    try:
        checksum, mime_type, parsed = await asyncio.gather(
            _compute_checksum(absolute_path),
            _detect_mime_type(absolute_path),
            _parse_document(absolute_path),
        )
        text = parsed.text
        metadata = dict(parsed.metadata)
        ocr_warnings: List[str] = []
        if settings.enable_ocr and not text.strip():
            ocr_result = await _run_ocr(absolute_path)
            text = ocr_result.text
            ocr_warnings = ocr_result.warnings
            if ocr_warnings:
                metadata.setdefault("ocr_warnings", ocr_warnings)
        classification = classifier_service.classify(text, metadata)
        external_id = f"doc-{uuid4().hex[:12]}"
        with get_session() as session:
            run = session.query(IngestionRun).filter_by(trace_id=trace_id).one()
            document = Document(
                external_id=external_id,
                source_path=str(absolute_path),
                source=source,
                checksum=checksum,
                mime_type=mime_type,
                text_content=text,
                summary=text[:500],
                document_type=classification.document_type,
                privilege_risk=classification.privilege_risk,
                importance_score=classification.importance_score,
                metadata_json=metadata,
                ingestion_run=run,
            )
            session.add(document)
            session.flush()
            for fragment_type, values in metadata.items():
                if not isinstance(values, list):
                    continue
                for value in values:
                    session.add(
                        MetadataFragment(
                            document=document,
                            fragment_type=fragment_type,
                            fragment_value=value,
                            confidence=1.0,
                        )
                    )
        graph_manager.upsert_document(external_id, metadata)
        retriever_service.update_with_document()
        with get_session() as session:
            run = session.query(IngestionRun).filter_by(trace_id=trace_id).one()
            run.status = "completed"
            run.completed_at = utc_now()
            run.duration_seconds = (run.completed_at - run.started_at).total_seconds()
            run.error_message = None
        return external_id
    except Exception as exc:  # pragma: no cover - guarded by tests
        tb = traceback.format_exc()
        with get_session() as session:
            run = session.query(IngestionRun).filter_by(trace_id=trace_id).one()
            run.status = "failed"
            run.completed_at = utc_now()
            run.error_message = str(exc)
            session.add(
                DeadLetter(
                    trace_id=trace_id,
                    payload={"path": str(absolute_path), "source": source},
                    error_message=str(exc),
                    stacktrace=tb,
                )
            )
        raise


async def ingest_paths(paths: List[Path], source: str = "upload") -> List[str]:
    """Convenience helper to run ingestion sequentially for tests and batch jobs."""

    results: List[str] = []
    for path in paths:
        external_id = await ingest_document_flow(path=str(path), source=source)
        results.append(external_id)
    return results


__all__ = ["ingest_document_flow", "ingest_paths"]
