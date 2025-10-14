"""Pydantic schemas for API payloads and internal DTOs."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class IngestionRunRead(BaseModel):
    trace_id: str
    source: str
    status: str
    started_at: datetime
    completed_at: Optional[datetime] = None
    duration_seconds: Optional[float] = None
    error_message: Optional[str] = None


class DeadLetterRead(BaseModel):
    trace_id: str
    payload: Dict[str, Any]
    error_message: str
    stacktrace: Optional[str] = None
    created_at: datetime


class DocumentRead(BaseModel):
    external_id: str
    document_type: Optional[str]
    privilege_risk: float
    importance_score: float
    metadata: Dict[str, List[str]] = Field(default_factory=dict)
    summary: Optional[str] = None


class SearchResultRead(BaseModel):
    document_id: str
    score: float
    snippet: str
    highlights: Dict[str, List[str]] = Field(default_factory=dict)
    trace_id: str


class AgentMessage(BaseModel):
    trace_id: str
    role: str = Field(default="user")
    message: str
    summary: Optional[str] = None


class SearchRequest(BaseModel):
    query: str
    top_k: int = Field(default=5, ge=1, le=50)
    filters: Optional[Dict[str, List[str]]] = None


class FolderIngestionRequest(BaseModel):
    folder_path: str


class TriggerIngestionRequest(BaseModel):
    documents: List[str]
    source: str = "api"
