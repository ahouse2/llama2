"""Retrieval and agent streaming endpoints."""

from __future__ import annotations

import json
from typing import AsyncGenerator, List

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import StreamingResponse

from ...schemas import SearchRequest, SearchResultRead
from ...services.retrieval import retriever_service
from ...services.timeline import timeline_service

router = APIRouter(prefix="/api/retrieval", tags=["retrieval"])


@router.get("/search", response_model=List[SearchResultRead])
async def search_get(query: str = Query(...), top_k: int = Query(5)) -> List[SearchResultRead]:
    results = retriever_service.search(query, top_k=top_k)
    return [SearchResultRead(**result.__dict__) for result in results]


@router.post("/search", response_model=List[SearchResultRead])
async def search_post(request: SearchRequest) -> List[SearchResultRead]:
    results = retriever_service.search(request.query, top_k=request.top_k, filters=request.filters)
    return [SearchResultRead(**result.__dict__) for result in results]


async def _stream_results(query: str, top_k: int) -> AsyncGenerator[bytes, None]:
    results = retriever_service.search(query, top_k=top_k)
    for result in results:
        payload = json.dumps(result.__dict__)
        yield payload.encode("utf-8") + b"\n"
    timeline = timeline_service.summarize()
    yield json.dumps({"timeline": timeline}).encode("utf-8") + b"\n"


@router.post("/stream")
async def stream_results(request: SearchRequest) -> StreamingResponse:
    if not request.query.strip():
        raise HTTPException(status_code=400, detail="Query must not be empty")
    return StreamingResponse(_stream_results(request.query, request.top_k), media_type="application/jsonl")
