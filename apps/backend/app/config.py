"""Application configuration management without third-party dependencies."""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import List


DEFAULT_ALLOWED_EXTENSIONS = [".txt", ".md", ".json"]


@dataclass
class Settings:
    """Container for runtime settings sourced from environment variables."""

    database_path: Path = field(default_factory=lambda: Path("../storage/state.json"))
    storage_directory: Path = field(default_factory=lambda: Path("../storage/uploads"))
    graph_path: Path = field(default_factory=lambda: Path("../storage/graph.json"))
    retriever_index_path: Path = field(default_factory=lambda: Path("../storage/retriever_index"))
    timeline_export_path: Path = field(default_factory=lambda: Path("../storage/timeline.csv"))
    agent_config_path: Path = field(default_factory=lambda: Path("../storage/agent_registry.yaml"))
    allowed_extensions: List[str] = field(default_factory=lambda: list(DEFAULT_ALLOWED_EXTENSIONS))
    reranker_alpha: float = 0.7
    sentiment_threshold: float = 0.15
    timezone: str = "UTC"
    enable_ocr: bool = True

    @classmethod
    def from_environment(cls) -> "Settings":
        """Instantiate settings while respecting overrides in the environment."""

        def _path(key: str, default: Path) -> Path:
            value = os.getenv(f"DISCOVERY_{key}")
            return Path(value) if value else default

        def _float(key: str, default: float) -> float:
            value = os.getenv(f"DISCOVERY_{key}")
            if not value:
                return default
            try:
                return float(value)
            except ValueError:
                return default

        def _bool(key: str, default: bool) -> bool:
            value = os.getenv(f"DISCOVERY_{key}")
            if value is None:
                return default
            return value.lower() in {"1", "true", "yes", "on"}

        allowed = os.getenv("DISCOVERY_ALLOWED_EXTENSIONS")
        extensions = [ext.strip() for ext in allowed.split(",") if ext.strip()] if allowed else list(DEFAULT_ALLOWED_EXTENSIONS)

        return cls(
            database_path=_path("DATABASE_PATH", Path("../storage/state.json")),
            storage_directory=_path("STORAGE_DIRECTORY", Path("../storage/uploads")),
            graph_path=_path("GRAPH_PATH", Path("../storage/graph.json")),
            retriever_index_path=_path("RETRIEVER_INDEX_PATH", Path("../storage/retriever_index")),
            timeline_export_path=_path("TIMELINE_EXPORT_PATH", Path("../storage/timeline.csv")),
            agent_config_path=_path("AGENT_CONFIG_PATH", Path("../storage/agent_registry.yaml")),
            allowed_extensions=extensions,
            reranker_alpha=_float("RERANKER_ALPHA", 0.7),
            sentiment_threshold=_float("SENTIMENT_THRESHOLD", 0.15),
            timezone=os.getenv("DISCOVERY_TIMEZONE", "UTC"),
            enable_ocr=_bool("ENABLE_OCR", True),
        )

    def ensure_directories(self) -> None:
        """Guarantee that required directories exist before runtime usage."""
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
