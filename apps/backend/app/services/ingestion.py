"""Prefect-based ingestion orchestrator."""

from __future__ import annotations

from pathlib import Path
from typing import Dict, List, Optional
from uuid import uuid4

from prefect import flow, get_run_logger, task

from ..config import settings
from ..database import DeadLetter, Document, IngestionRun, MetadataFragment, get_session, utc_now
from .classifier import DocumentClassification, classifier_service
from .graph import graph_manager
from .ocr import OCRResult, ocr_engine
from .parser import ParsedDocument, parser_service
from .retrieval import retriever_service
from .storage import storage_service


@task(retries=2, retry_delay_seconds=5)
def compute_checksum(path: str) -> str:
    return storage_service.compute_checksum(Path(path))


@task(retries=2, retry_delay_seconds=3)
def detect_mime_type(path: str) -> str:
    return storage_service.detect_mime_type(Path(path))


@task(retries=1)
def parse_document(path: str) -> ParsedDocument:
    return parser_service.parse(Path(path))


@task(retries=1)
def run_ocr(path: str) -> OCRResult:
    return ocr_engine.extract_text(Path(path))


@task(retries=1)
def classify_document(text: str, metadata: Dict[str, List[str]]) -> DocumentClassification:
    return classifier_service.classify(text, metadata)


@task
def persist_document(
    *,
    trace_id: str,
    source: str,
    path: str,
    checksum: str,
    mime_type: str,
    text: str,
    metadata: Dict[str, List[str]],
    classification: DocumentClassification,
    ocr_warnings: Optional[List[str]] = None,
) -> str:
    external_id = f"doc-{uuid4().hex[:12]}"
    with get_session() as session:
        run = session.query(IngestionRun).filter_by(trace_id=trace_id).one()
        document = Document(
            external_id=external_id,
            source_path=path,
            source=source,
            checksum=checksum,
            mime_type=mime_type,
            text_content=text,
            summary=text[:500],
            document_type=classification.document_type,
            privilege_risk=classification.privilege_risk,
            importance_score=classification.importance_score,
            metadata_json={**metadata, "ocr_warnings": ocr_warnings or []},
            ingestion_run=run,
        )
        session.add(document)
        session.flush()
        for fragment_type, values in metadata.items():
            for value in values:
                fragment = MetadataFragment(
                    document=document,
                    fragment_type=fragment_type,
                    fragment_value=value,
                    confidence=1.0,
                )
                session.add(fragment)
    graph_manager.upsert_document(external_id, metadata)
    retriever_service.update_with_document(document)  # type: ignore[arg-type]
    return external_id


@task
def start_ingestion_run(trace_id: str, source: str) -> None:
    with get_session() as session:
        run = IngestionRun(trace_id=trace_id, source=source, status="running", started_at=utc_now())
        session.add(run)


@task
def finalize_ingestion_run(trace_id: str, status: str, *, error_message: Optional[str] = None) -> None:
    with get_session() as session:
        run = session.query(IngestionRun).filter_by(trace_id=trace_id).one()
        run.status = status
        run.completed_at = utc_now()
        started = run.started_at if run.started_at.tzinfo is None else run.started_at.replace(tzinfo=None)
        run.duration_seconds = (run.completed_at - started).total_seconds()
        run.error_message = error_message


@task
def record_dead_letter(trace_id: str, payload: Dict[str, str], error_message: str, stacktrace: str) -> None:
    with get_session() as session:
        session.add(DeadLetter(trace_id=trace_id, payload=payload, error_message=error_message, stacktrace=stacktrace))


@flow(name="document_ingestion_flow", retries=0)
async def ingest_document_flow(path: str, source: str = "upload") -> str:
    logger = get_run_logger()
    absolute_path = str(Path(path).resolve())
    trace_id = uuid4().hex
    start_future = start_ingestion_run.submit(trace_id, source)
    start_future.result()
    try:
        checksum_future = compute_checksum.submit(absolute_path)
        mime_future = detect_mime_type.submit(absolute_path)
        parsed_future = parse_document.submit(absolute_path)
        checksum = checksum_future.result()
        mime_type = mime_future.result()
        parsed = parsed_future.result()
        text = parsed.text
        metadata = parsed.metadata
        ocr_warnings: List[str] = []
        if not text.strip() and settings.enable_ocr:
            ocr_future = run_ocr.submit(absolute_path)
            ocr_result = ocr_future.result()
            text = ocr_result.text
            metadata.setdefault("ocr_warnings", ocr_result.warnings)
            ocr_warnings = ocr_result.warnings
        classification_future = classify_document.submit(text, metadata)
        classification = classification_future.result()
        persist_future = persist_document.submit(
            trace_id=trace_id,
            source=source,
            path=absolute_path,
            checksum=checksum,
            mime_type=mime_type,
            text=text,
            metadata=metadata,
            classification=classification,
            ocr_warnings=ocr_warnings,
        )
        external_id = persist_future.result()
        finalize_ingestion_run.submit(trace_id, "completed").result()
        logger.info("Ingestion completed for %s", absolute_path)
        return external_id
    except Exception as exc:
        logger.exception("Ingestion failed for %s", absolute_path)
        finalize_ingestion_run.submit(trace_id, "failed", error_message=str(exc)).result()
        import traceback

        record_dead_letter.submit(
            trace_id,
            {"path": absolute_path, "source": source},
            str(exc),
            traceback.format_exc(),
        ).result()
        raise


async def ingest_paths(paths: List[Path], source: str = "upload") -> List[str]:
    """Convenience helper to run ingestion sequentially for tests and batch jobs."""

    results: List[str] = []
    for path in paths:
        external_id = await ingest_document_flow(path=str(path), source=source)
        results.append(external_id)
    return results
