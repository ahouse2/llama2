"""Runtime configuration for the Justice Platform backend."""

from __future__ import annotations

from functools import lru_cache
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class AppConfig(BaseSettings):
    """Application configuration parsed from the environment."""

    environment: Literal["dev", "staging", "prod"] = Field(
        default="dev", alias="JUSTICE_PLATFORM_ENV", description="Runtime environment label"
    )
    commit_sha: str = Field(
        default="unknown",
        alias="JUSTICE_PLATFORM_COMMIT_SHA",
        description="Git revision associated with the build.",
    )
    build_timestamp: str = Field(
        default="unknown",
        alias="JUSTICE_PLATFORM_BUILD_TS",
        description="ISO8601 build timestamp injected by CI/CD.",
    )

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", populate_by_name=True)


@lru_cache(maxsize=1)
def get_config() -> AppConfig:
    """Return a cached config instance to reuse across the application."""

    return AppConfig()
