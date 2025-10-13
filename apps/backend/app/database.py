"""Lightweight JSON-backed persistence layer used by the backend services."""

from __future__ import annotations

import json
from contextlib import contextmanager
from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Dict, Iterator, List, Optional

from .config import settings


@dataclass
class Document:
    id: int
    external_id: str
    source_path: str
    source: str
    checksum: str
    mime_type: str
    text_content: str
    summary: str
    document_type: str
    privilege_risk: float
    importance_score: float
    metadata: Dict[str, List[str]]
    ingestion_run_id: int
    created_at: str
    updated_at: str


@dataclass
class IngestionRun:
    id: int
    trace_id: str
    source: str
    status: str
    started_at: str
    completed_at: Optional[str] = None
    duration_seconds: Optional[float] = None
    error_message: Optional[str] = None


@dataclass
class MetadataFragment:
    id: int
    document_id: int
    fragment_type: str
    fragment_value: str
    confidence: float


@dataclass
class DeadLetter:
    id: int
    trace_id: str
    payload: Dict[str, Any]
    error_message: str
    stacktrace: Optional[str]
    created_at: str


@dataclass
class ConversationMemory:
    id: int
    trace_id: str
    agent_role: str
    turn_index: int
    message: str
    summary: Optional[str]
    created_at: str


@dataclass
class DatabaseState:
    documents: List[Document] = field(default_factory=list)
    ingestion_runs: List[IngestionRun] = field(default_factory=list)
    metadata_fragments: List[MetadataFragment] = field(default_factory=list)
    dead_letters: List[DeadLetter] = field(default_factory=list)
    conversation_memory: List[ConversationMemory] = field(default_factory=list)
    counters: Dict[str, int] = field(
        default_factory=lambda: {
            "documents": 0,
            "ingestion_runs": 0,
            "metadata_fragments": 0,
            "dead_letters": 0,
            "conversation_memory": 0,
        }
    )
"""Database utilities and ORM models."""

from __future__ import annotations

from contextlib import asynccontextmanager, contextmanager
from datetime import UTC, datetime
from typing import Any, AsyncIterator, Dict, Iterator, Optional

from sqlalchemy import JSON, Float, ForeignKey, Integer, String, Text, create_engine
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column, relationship, sessionmaker

from .config import settings


def utc_now() -> datetime:
    """Return a timezone-naive UTC timestamp."""

    return datetime.now(UTC).replace(tzinfo=None)


class DatabaseSession:
    """Mutable session wrapper that persists state on context exit."""

    def __init__(self, state: DatabaseState, storage_path: Path) -> None:
        self._state = state
        self._storage_path = storage_path
        self._dirty = False

    # ------------------------------------------------------------------
    # Document helpers
    # ------------------------------------------------------------------
    def add_document(
        self,
        *,
        external_id: str,
        source_path: str,
        source: str,
        checksum: str,
        mime_type: str,
        text_content: str,
        summary: str,
        document_type: str,
        privilege_risk: float,
        importance_score: float,
        metadata: Dict[str, List[str]],
        ingestion_run_id: int,
    ) -> Document:
        doc_id = self._next_id("documents")
        timestamp = utc_now().isoformat()
        document = Document(
            id=doc_id,
            external_id=external_id,
            source_path=source_path,
            source=source,
            checksum=checksum,
            mime_type=mime_type,
            text_content=text_content,
            summary=summary,
            document_type=document_type,
            privilege_risk=privilege_risk,
            importance_score=importance_score,
            metadata={key: list(values) for key, values in metadata.items()},
            ingestion_run_id=ingestion_run_id,
            created_at=timestamp,
            updated_at=timestamp,
        )
        self._state.documents.append(document)
        self._dirty = True
        return document

    def update_document(self, document: Document) -> None:
        for index, existing in enumerate(self._state.documents):
            if existing.id == document.id:
                document.updated_at = utc_now().isoformat()
                self._state.documents[index] = document
                self._dirty = True
                return
        raise ValueError(f"Document with id={document.id} not found")

    def list_documents(self) -> List[Document]:
        return [Document(**asdict(document)) for document in self._state.documents]

    def get_document_by_external_id(self, external_id: str) -> Optional[Document]:
        for document in self._state.documents:
            if document.external_id == external_id:
                return Document(**asdict(document))
        return None

    # ------------------------------------------------------------------
    # Ingestion runs
    # ------------------------------------------------------------------
    def add_ingestion_run(self, *, trace_id: str, source: str, status: str) -> IngestionRun:
        run_id = self._next_id("ingestion_runs")
        run = IngestionRun(
            id=run_id,
            trace_id=trace_id,
            source=source,
            status=status,
            started_at=utc_now().isoformat(),
        )
        self._state.ingestion_runs.append(run)
        self._dirty = True
        return run

    def get_ingestion_run(self, trace_id: str) -> Optional[IngestionRun]:
        for run in self._state.ingestion_runs:
            if run.trace_id == trace_id:
                return IngestionRun(**asdict(run))
        return None

    def update_ingestion_run(
        self,
        trace_id: str,
        *,
        status: Optional[str] = None,
        completed_at: Optional[datetime] = None,
        error_message: Optional[str] = None,
    ) -> None:
        for index, run in enumerate(self._state.ingestion_runs):
            if run.trace_id == trace_id:
                if status:
                    run.status = status
                if completed_at:
                    run.completed_at = completed_at.isoformat()
                    duration = datetime.fromisoformat(run.started_at)
                    run.duration_seconds = max(
                        0.0,
                        (completed_at - duration).total_seconds(),
                    )
                if error_message:
                    run.error_message = error_message
                self._state.ingestion_runs[index] = run
                self._dirty = True
                return
        raise ValueError(f"Ingestion run with trace_id={trace_id} not found")

    def list_ingestion_runs(self) -> List[IngestionRun]:
        return [IngestionRun(**asdict(run)) for run in self._state.ingestion_runs]

    # ------------------------------------------------------------------
    # Metadata fragments
    # ------------------------------------------------------------------
    def add_metadata_fragment(
        self,
        *,
        document_id: int,
        fragment_type: str,
        fragment_value: str,
        confidence: float,
    ) -> MetadataFragment:
        fragment_id = self._next_id("metadata_fragments")
        fragment = MetadataFragment(
            id=fragment_id,
            document_id=document_id,
            fragment_type=fragment_type,
            fragment_value=fragment_value,
            confidence=confidence,
        )
        self._state.metadata_fragments.append(fragment)
        self._dirty = True
        return fragment

    def list_metadata_fragments(self, *, fragment_type: Optional[str] = None) -> List[MetadataFragment]:
        fragments = self._state.metadata_fragments
        if fragment_type is not None:
            fragments = [fragment for fragment in fragments if fragment.fragment_type == fragment_type]
        return [MetadataFragment(**asdict(fragment)) for fragment in fragments]

    # ------------------------------------------------------------------
    # Dead letters
    # ------------------------------------------------------------------
    def add_dead_letter(
        self,
        *,
        trace_id: str,
        payload: Dict[str, Any],
        error_message: str,
        stacktrace: Optional[str],
    ) -> DeadLetter:
        letter_id = self._next_id("dead_letters")
        record = DeadLetter(
            id=letter_id,
            trace_id=trace_id,
            payload=payload,
            error_message=error_message,
            stacktrace=stacktrace,
            created_at=utc_now().isoformat(),
        )
        self._state.dead_letters.append(record)
        self._dirty = True
        return record

    def list_dead_letters(self) -> List[DeadLetter]:
        return [DeadLetter(**asdict(record)) for record in self._state.dead_letters]

    # ------------------------------------------------------------------
    # Conversation memory
    # ------------------------------------------------------------------
    def add_conversation_memory(
        self,
        *,
        trace_id: str,
        agent_role: str,
        turn_index: int,
        message: str,
        summary: Optional[str],
    ) -> ConversationMemory:
        memory_id = self._next_id("conversation_memory")
        record = ConversationMemory(
            id=memory_id,
            trace_id=trace_id,
            agent_role=agent_role,
            turn_index=turn_index,
            message=message,
            summary=summary,
            created_at=utc_now().isoformat(),
        )
        self._state.conversation_memory.append(record)
        self._dirty = True
        return record

    def list_conversation_memory(self, trace_id: str) -> List[ConversationMemory]:
        return [
            ConversationMemory(**asdict(record))
            for record in self._state.conversation_memory
            if record.trace_id == trace_id
        ]

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------
    def _next_id(self, name: str) -> int:
        current = self._state.counters.get(name, 0) + 1
        self._state.counters[name] = current
        return current

    def _persist(self) -> None:
        if not self._dirty:
            return
        serialisable = {
            "documents": [asdict(document) for document in self._state.documents],
            "ingestion_runs": [asdict(run) for run in self._state.ingestion_runs],
            "metadata_fragments": [asdict(fragment) for fragment in self._state.metadata_fragments],
            "dead_letters": [asdict(record) for record in self._state.dead_letters],
            "conversation_memory": [asdict(record) for record in self._state.conversation_memory],
            "counters": dict(self._state.counters),
        }
        self._storage_path.parent.mkdir(parents=True, exist_ok=True)
        self._storage_path.write_text(json.dumps(serialisable, indent=2), encoding="utf-8")
        self._dirty = False

    def close(self) -> None:
        self._persist()


class Database:
    """Facade around the JSON document state."""

    def __init__(self, path: Path) -> None:
        self._path = path
        self._state = self._load()

    def _load(self) -> DatabaseState:
        if not self._path.exists():
            return DatabaseState()
        payload = json.loads(self._path.read_text(encoding="utf-8"))
        state = DatabaseState()
        state.documents = [Document(**document) for document in payload.get("documents", [])]
        state.ingestion_runs = [IngestionRun(**run) for run in payload.get("ingestion_runs", [])]
        state.metadata_fragments = [
            MetadataFragment(**fragment) for fragment in payload.get("metadata_fragments", [])
        ]
        state.dead_letters = [DeadLetter(**record) for record in payload.get("dead_letters", [])]
        state.conversation_memory = [
            ConversationMemory(**record) for record in payload.get("conversation_memory", [])
        ]
        state.counters.update(payload.get("counters", {}))
        return state

    @contextmanager
    def session(self) -> Iterator[DatabaseSession]:
        session = DatabaseSession(self._state, self._path)
        try:
            yield session
        finally:
            session.close()


_database = Database(settings.database_path)


@contextmanager
def get_session() -> Iterator[DatabaseSession]:
    """Public context manager that mirrors ORM session semantics."""

    with _database.session() as session:
        yield session


def init_db() -> None:
    """Initialise the JSON file if required."""

    settings.database_path.parent.mkdir(parents=True, exist_ok=True)
    if not settings.database_path.exists():
        settings.database_path.write_text(json.dumps(asdict(DatabaseState()), indent=2), encoding="utf-8")
class Base(DeclarativeBase):
    """Declarative base class."""

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    created_at: Mapped[datetime] = mapped_column(default=utc_now)
    updated_at: Mapped[datetime] = mapped_column(default=utc_now, onupdate=utc_now)


class Document(Base):
    """Document metadata and content."""

    __tablename__ = "documents"

    external_id: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    source_path: Mapped[str] = mapped_column(String(1024))
    source: Mapped[str] = mapped_column(String(128))
    checksum: Mapped[str] = mapped_column(String(128))
    mime_type: Mapped[str] = mapped_column(String(128))
    text_content: Mapped[str] = mapped_column(Text)
    summary: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    document_type: Mapped[Optional[str]] = mapped_column(String(64))
    privilege_risk: Mapped[float] = mapped_column(Float, default=0.0)
    importance_score: Mapped[float] = mapped_column(Float, default=0.0)
    metadata_json: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict)

    ingestion_run_id: Mapped[int] = mapped_column(ForeignKey("ingestion_runs.id"))
    ingestion_run: Mapped["IngestionRun"] = relationship(back_populates="documents")
    fragments: Mapped[list["MetadataFragment"]] = relationship(back_populates="document", cascade="all, delete-orphan")


class IngestionRun(Base):
    """Tracks a Prefect flow execution."""

    __tablename__ = "ingestion_runs"

    trace_id: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    source: Mapped[str] = mapped_column(String(128))
    status: Mapped[str] = mapped_column(String(32))
    started_at: Mapped[datetime] = mapped_column(default=utc_now)
    completed_at: Mapped[Optional[datetime]] = mapped_column(nullable=True)
    duration_seconds: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    documents: Mapped[list[Document]] = relationship(back_populates="ingestion_run")


class MetadataFragment(Base):
    """Structured metadata extracted from a document."""

    __tablename__ = "metadata_fragments"

    document_id: Mapped[int] = mapped_column(ForeignKey("documents.id"))
    fragment_type: Mapped[str] = mapped_column(String(64))
    fragment_value: Mapped[str] = mapped_column(Text)
    confidence: Mapped[float] = mapped_column(Float, default=1.0)

    document: Mapped[Document] = relationship(back_populates="fragments")


class DeadLetter(Base):
    """Failed ingestion tasks."""

    __tablename__ = "dead_letters"

    trace_id: Mapped[str] = mapped_column(String(64), index=True)
    payload: Mapped[Dict[str, Any]] = mapped_column(JSON)
    error_message: Mapped[str] = mapped_column(Text)
    stacktrace: Mapped[Optional[str]] = mapped_column(Text, nullable=True)


class ConversationMemory(Base):
    """Stores agent conversation transcripts for traceability."""

    __tablename__ = "conversation_memory"

    trace_id: Mapped[str] = mapped_column(String(64), index=True)
    agent_role: Mapped[str] = mapped_column(String(64))
    turn_index: Mapped[int] = mapped_column(Integer)
    message: Mapped[str] = mapped_column(Text)
    summary: Mapped[Optional[str]] = mapped_column(Text, nullable=True)


async_engine = create_async_engine(settings.database_url, future=True, echo=False)
AsyncSessionMaker = async_sessionmaker(async_engine, expire_on_commit=False)

sync_engine = create_engine(settings.database_url.replace("+aiosqlite", ""), future=True, echo=False)
SessionMaker = sessionmaker(sync_engine, expire_on_commit=False)


@asynccontextmanager
async def get_async_session() -> AsyncIterator[AsyncSession]:
    """Provide an async session."""

    async with AsyncSessionMaker() as session:
        yield session


@contextmanager
def get_session() -> Iterator[Session]:
    """Provide a synchronous session."""

    session = SessionMaker()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def init_db() -> None:
    """Create all tables if they do not exist."""

    Base.metadata.create_all(sync_engine)


init_db()
