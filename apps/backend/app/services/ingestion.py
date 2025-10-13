"""Async ingestion pipeline implemented with standard library building blocks."""

from __future__ import annotations

import asyncio
from pathlib import Path
from typing import List
from uuid import uuid4

from ..config import settings
from ..database import get_session, utc_now
from .classifier import classifier_service
from .graph import graph_manager
from .ocr import ocr_engine
from .parser import ParsedDocument, parser_service
from .retrieval import retriever_service
from .storage import storage_service


async def _compute_checksum(path: Path) -> str:
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(None, storage_service.compute_checksum, path)


async def _detect_mime_type(path: Path) -> str:
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(None, storage_service.detect_mime_type, path)


async def _parse_document(path: Path) -> ParsedDocument:
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(None, parser_service.parse, path)


async def _run_ocr(path: Path):
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(None, ocr_engine.extract_text, path)


async def ingest_document_flow(path: str, source: str = "upload") -> str:
    """Ingest a single document and return its external identifier."""

    absolute_path = Path(path).resolve()
    if not absolute_path.exists():
        raise FileNotFoundError(f"Document not found: {absolute_path}")

    trace_id = uuid4().hex
    with get_session() as session:
        run = session.add_ingestion_run(trace_id=trace_id, source=source, status="running")
    try:
        checksum, mime_type, parsed = await asyncio.gather(
            _compute_checksum(absolute_path),
            _detect_mime_type(absolute_path),
            _parse_document(absolute_path),
        )
        text = parsed.text
        metadata = dict(parsed.metadata)
        if settings.enable_ocr and not text.strip():
            ocr_result = await _run_ocr(absolute_path)
            text = ocr_result.text
            if ocr_result.warnings:
                metadata.setdefault("ocr_warnings", ocr_result.warnings)
        classification = classifier_service.classify(text, metadata)
        with get_session() as session:
            run = session.get_ingestion_run(trace_id)
            if run is None:  # pragma: no cover - defensive guard
                raise RuntimeError(f"Ingestion run missing for trace {trace_id}")
            document = session.add_document(
                external_id=f"doc-{uuid4().hex[:12]}",
                source_path=str(absolute_path),
                source=source,
                checksum=checksum,
                mime_type=mime_type,
                text_content=text,
                summary=text[:500],
                document_type=classification.document_type,
                privilege_risk=classification.privilege_risk,
                importance_score=classification.importance_score,
                metadata=metadata,
                ingestion_run_id=run.id,
            )
            for fragment_type, values in metadata.items():
                if not isinstance(values, list):
                    continue
                for value in values:
                    session.add_metadata_fragment(
                        document_id=document.id,
                        fragment_type=fragment_type,
                        fragment_value=value,
                        confidence=1.0,
                    )
        graph_manager.upsert_document(document.external_id, metadata)
        retriever_service.update_with_document(document)
        with get_session() as session:
            session.update_ingestion_run(trace_id, status="completed", completed_at=utc_now())
        return document.external_id
    except Exception as exc:  # pragma: no cover - guarded via tests
        with get_session() as session:
            session.update_ingestion_run(trace_id, status="failed", completed_at=utc_now(), error_message=str(exc))
            session.add_dead_letter(
                trace_id=trace_id,
                payload={"path": str(absolute_path), "source": source},
                error_message=str(exc),
                stacktrace=None,
            )
        raise


async def ingest_paths(paths: List[Path], source: str = "upload") -> List[str]:
    """Convenience helper used by tests and batch jobs."""

    results: List[str] = []
    for path in paths:
        results.append(await ingest_document_flow(str(path), source=source))
    return results
