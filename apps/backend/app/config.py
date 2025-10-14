"""Application configuration management backed by pydantic-settings."""

from __future__ import annotations

from pathlib import Path
from typing import List

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Strongly typed configuration for the backend services."""

    model_config = SettingsConfigDict(
        env_file=(".env", "apps/backend/.env"),
        env_prefix="DISCOVERY_",
        case_sensitive=False,
    )

    database_url: str = Field(
        default="sqlite+aiosqlite:///../storage/state.db",
        description="SQLAlchemy database URL for the primary persistence layer.",
    )
    storage_directory: Path = Field(
        default=Path("../storage/uploads"),
        description="Directory where raw uploaded documents are stored.",
    )
    graph_path: Path = Field(
        default=Path("../storage/graph.gpickle"),
        description="Persistence location for the knowledge graph.",
    )
    retriever_index_path: Path = Field(
        default=Path("../storage/retriever_index"),
        description="Directory containing persisted retrieval artefacts.",
    )
    prefect_log_level: str = Field(
        default="INFO",
        description="Log level hint for orchestration components that honour Prefect semantics.",
    )
    enable_ocr: bool = Field(
        default=True,
        description="Toggle OCR execution for image-heavy documents.",
    )
    agent_config_path: Path = Field(
        default=Path("../storage/agent_registry.yaml"),
        description="YAML manifest describing the agent network configuration.",
    )
    timeline_export_path: Path = Field(
        default=Path("../storage/timeline.csv"),
        description="CSV export destination for generated timelines.",
    )
    allowed_extensions: List[str] = Field(
        default_factory=lambda: [".txt", ".pdf", ".md", ".json"],
        description="Whitelisted document extensions accepted by the ingestion pipeline.",
    )
    ingestion_concurrency: int = Field(
        default=4,
        description="Maximum number of concurrent ingestion tasks processed by the pipeline.",
    )
    reranker_alpha: float = Field(
        default=0.65,
        description="Weight applied to semantic similarity during retrieval scoring.",
    )
    sentiment_threshold: float = Field(
        default=0.15,
        description="Compound sentiment threshold for assigning tonal labels to agent responses.",
    )
    timezone: str = Field(
        default="UTC",
        description="Canonical timezone used when normalising temporal analytics.",
    )

    def ensure_directories(self) -> None:
        """Guarantee that filesystem resources required at runtime exist."""

        self.storage_directory.mkdir(parents=True, exist_ok=True)
        self.retriever_index_path.mkdir(parents=True, exist_ok=True)
        self.graph_path.parent.mkdir(parents=True, exist_ok=True)
        self.timeline_export_path.parent.mkdir(parents=True, exist_ok=True)
        if not self.agent_config_path.exists():
            self.agent_config_path.write_text("agents: []\n", encoding="utf-8")


settings = Settings()
settings.ensure_directories()
