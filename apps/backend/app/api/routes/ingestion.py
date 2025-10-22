"""FastAPI routes for document ingestion."""

from __future__ import annotations

from pathlib import Path
from typing import List

from fastapi import APIRouter, HTTPException, UploadFile
from fastapi.responses import JSONResponse

from ...database import DeadLetter, IngestionRun, get_session
from ...schemas import DeadLetterRead, FolderIngestionRequest, IngestionRunRead, TriggerIngestionRequest
from ...services.ingestion import ingest_document_flow, ingest_paths
from ...services.storage import storage_service

router = APIRouter(prefix="/api/ingest", tags=["ingestion"])


@router.post("/upload")
async def upload_document(file: UploadFile) -> JSONResponse:
    data = await file.read()
    saved_path, checksum, mime_type = storage_service.save_upload(file.filename, data)
    external_id = await ingest_document_flow(path=str(saved_path), source="upload")
    return JSONResponse(
        {
            "external_id": external_id,
            "checksum": checksum,
            "mime_type": mime_type,
            "path": str(saved_path),
        }
    )


@router.post("/folder")
async def ingest_folder(request: FolderIngestionRequest) -> JSONResponse:
    folder = Path(request.folder_path)
    if not folder.exists():
        raise HTTPException(status_code=404, detail=f"Folder not found: {folder}")
    paths: List[Path] = [path for path in folder.rglob("*") if path.is_file()]
    external_ids = await ingest_paths(paths, source="folder")
    return JSONResponse({"ingested": external_ids})


@router.post("/trigger")
async def trigger_ingestion(request: TriggerIngestionRequest) -> JSONResponse:
    paths = [Path(path) for path in request.documents]
    missing = [str(path) for path in paths if not path.exists()]
    if missing:
        raise HTTPException(status_code=404, detail={"missing": missing})
    external_ids = await ingest_paths(paths, source=request.source)
    return JSONResponse({"ingested": external_ids})


@router.get("/runs", response_model=List[IngestionRunRead])
async def list_runs() -> List[IngestionRunRead]:
    with get_session() as session:
        runs = session.query(IngestionRun).order_by(IngestionRun.created_at.desc()).all()
        return [
            IngestionRunRead(
                trace_id=run.trace_id,
                source=run.source,
                status=run.status,
                started_at=run.started_at,
                completed_at=run.completed_at,
                duration_seconds=run.duration_seconds,
                error_message=run.error_message,
            )
            for run in runs
        ]


@router.get("/dead_letters", response_model=List[DeadLetterRead])
async def list_dead_letters() -> List[DeadLetterRead]:
    with get_session() as session:
        records = session.query(DeadLetter).order_by(DeadLetter.created_at.desc()).all()
        return [
            DeadLetterRead(
                trace_id=record.trace_id,
                payload=record.payload,
                error_message=record.error_message,
                stacktrace=record.stacktrace,
                created_at=record.created_at,
            )
            for record in records
        ]
