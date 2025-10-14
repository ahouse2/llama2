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


class Base(DeclarativeBase):
    """Declarative base class used for all ORM models."""


class Document(Base):
    """Represents an ingested document with extracted metadata."""

    __tablename__ = "documents"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
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
    created_at: Mapped[datetime] = mapped_column(default=utc_now)
    updated_at: Mapped[datetime] = mapped_column(default=utc_now, onupdate=utc_now)

    ingestion_run_id: Mapped[int] = mapped_column(ForeignKey("ingestion_runs.id"))
    ingestion_run: Mapped["IngestionRun"] = relationship(back_populates="documents")
    fragments: Mapped[list["MetadataFragment"]] = relationship(
        back_populates="document",
        cascade="all, delete-orphan",
    )


class IngestionRun(Base):
    """Tracks the lifecycle of a document ingestion request."""

    __tablename__ = "ingestion_runs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    trace_id: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    source: Mapped[str] = mapped_column(String(128))
    status: Mapped[str] = mapped_column(String(32))
    started_at: Mapped[datetime] = mapped_column(default=utc_now)
    completed_at: Mapped[Optional[datetime]] = mapped_column(nullable=True)
    duration_seconds: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(default=utc_now)

    documents: Mapped[list[Document]] = relationship(back_populates="ingestion_run")


class MetadataFragment(Base):
    """Metadata extracted from a document such as entities or dates."""

    __tablename__ = "metadata_fragments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    document_id: Mapped[int] = mapped_column(ForeignKey("documents.id"))
    fragment_type: Mapped[str] = mapped_column(String(64))
    fragment_value: Mapped[str] = mapped_column(Text)
    confidence: Mapped[float] = mapped_column(Float, default=1.0)

    document: Mapped[Document] = relationship(back_populates="fragments")


class DeadLetter(Base):
    """Failed ingestion task payload for later analysis."""

    __tablename__ = "dead_letters"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    trace_id: Mapped[str] = mapped_column(String(64), index=True)
    payload: Mapped[Dict[str, Any]] = mapped_column(JSON)
    error_message: Mapped[str] = mapped_column(Text)
    stacktrace: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(default=utc_now)


class ConversationMemory(Base):
    """Stores conversational exchanges for each trace."""

    __tablename__ = "conversation_memory"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    trace_id: Mapped[str] = mapped_column(String(64), index=True)
    agent_role: Mapped[str] = mapped_column(String(64))
    turn_index: Mapped[int] = mapped_column(Integer)
    message: Mapped[str] = mapped_column(Text)
    summary: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(default=utc_now)


async_engine = create_async_engine(settings.database_url, future=True, echo=False)
AsyncSessionMaker = async_sessionmaker(async_engine, expire_on_commit=False)

sync_url = settings.database_url.replace("+aiosqlite", "")
sync_engine = create_engine(sync_url, future=True, echo=False)
SessionMaker = sessionmaker(sync_engine, expire_on_commit=False)


@asynccontextmanager
async def get_async_session() -> AsyncIterator[AsyncSession]:
    """Provide an async SQLAlchemy session."""

    async with AsyncSessionMaker() as session:
        yield session


@contextmanager
def get_session() -> Iterator[Session]:
    """Provide a synchronous SQLAlchemy session."""

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
    """Create all tables if they do not already exist."""

    Base.metadata.create_all(sync_engine)


init_db()


__all__ = [
    "ConversationMemory",
    "DeadLetter",
    "Document",
    "IngestionRun",
    "MetadataFragment",
    "get_async_session",
    "get_session",
    "init_db",
    "utc_now",
]
