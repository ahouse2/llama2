"""Application configuration management."""

from __future__ import annotations

from pathlib import Path
from typing import List

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Strongly typed application settings."""

    model_config = SettingsConfigDict(env_file=(".env", "apps/backend/.env"), env_prefix="DISCOVERY_", case_sensitive=False)

    database_url: str = Field(default="sqlite+aiosqlite:///../storage/state.db", description="SQLAlchemy database URL")
    storage_directory: Path = Field(default=Path("../storage/uploads"), description="Directory where raw documents are stored")
    graph_path: Path = Field(default=Path("../storage/graph.gpickle"), description="Knowledge graph persistence path")
    retriever_index_path: Path = Field(default=Path("../storage/retriever_index"), description="Directory for hybrid retriever artifacts")
    prefect_log_level: str = Field(default="INFO", description="Log level for Prefect orchestration")
    enable_ocr: bool = Field(default=True, description="Toggle OCR execution for image-based documents")
    agent_config_path: Path = Field(default=Path("../storage/agent_registry.yaml"), description="YAML DSL describing agent registry")
    timeline_export_path: Path = Field(default=Path("../storage/timeline.csv"), description="Timeline analytics export destination")
    allowed_extensions: List[str] = Field(default_factory=lambda: [".txt", ".pdf", ".md", ".json"], description="Whitelisted document extensions")
    ingestion_concurrency: int = Field(default=4, description="Maximum number of concurrent ingestion flows")
    reranker_alpha: float = Field(default=0.65, description="Blending coefficient between semantic and structural scores")
    sentiment_threshold: float = Field(default=0.15, description="Threshold for emotion controller to mark response as empathetic")
    timezone: str = Field(default="UTC", description="Canonical timezone for timeline synthesis")

    def ensure_directories(self) -> None:
        """Materialize required directories on disk."""

        self.storage_directory.mkdir(parents=True, exist_ok=True)
        self.retriever_index_path.mkdir(parents=True, exist_ok=True)
        self.graph_path.parent.mkdir(parents=True, exist_ok=True)
        self.timeline_export_path.parent.mkdir(parents=True, exist_ok=True)
        if not self.agent_config_path.exists():
            self.agent_config_path.write_text("agents: []\n", encoding="utf-8")


settings = Settings()
settings.ensure_directories()
