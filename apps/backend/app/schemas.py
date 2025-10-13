"""Simple data structures used by optional API endpoints."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class IngestionRunRead:
    trace_id: str
    source: str
    status: str
    started_at: str
    completed_at: Optional[str] = None
"""Pydantic schemas for API responses."""

from __future__ import annotations

from datetime import datetime
from typing import Dict, List, Optional

from pydantic import BaseModel, Field


class IngestionRunRead(BaseModel):
    trace_id: str
    source: str
    status: str
    started_at: datetime
    completed_at: Optional[datetime] = None
    duration_seconds: Optional[float] = None
    error_message: Optional[str] = None


@dataclass
class DeadLetterRead:
class DeadLetterRead(BaseModel):
    trace_id: str
    payload: Dict[str, str]
    error_message: str
    stacktrace: Optional[str] = None
    created_at: str = ""


@dataclass
class DocumentRead:
    created_at: datetime


class DocumentRead(BaseModel):
    external_id: str
    document_type: Optional[str]
    privilege_risk: float
    importance_score: float
    metadata: Dict[str, List[str]] = field(default_factory=dict)


@dataclass
class SearchResultRead:
    metadata: Dict[str, List[str]] = Field(default_factory=dict)


class SearchResultRead(BaseModel):
    document_id: str
    score: float
    snippet: str
    highlights: Dict[str, List[str]]
    trace_id: str


@dataclass
class AgentMessage:
    trace_id: str
    role: str
class AgentMessage(BaseModel):
    trace_id: str
    role: str = "user"
    message: str
    summary: Optional[str] = None


@dataclass
class SearchRequest:
class SearchRequest(BaseModel):
    query: str
    top_k: int = 5
    filters: Optional[Dict[str, List[str]]] = None


@dataclass
class FolderIngestionRequest:
    folder_path: str


@dataclass
class TriggerIngestionRequest:
class FolderIngestionRequest(BaseModel):
    folder_path: str


class TriggerIngestionRequest(BaseModel):
    documents: List[str]
    source: str = "api"
