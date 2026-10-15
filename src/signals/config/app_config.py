"""Application settings for the HTTP server."""

from functools import lru_cache

from pydantic import Field
from pydantic_settings import SettingsConfigDict

from .base_config import BaseConfig


class AppConfig(BaseConfig):
    model_config = SettingsConfigDict(
        env_prefix="SIGNALS_",
        extra="ignore",
        env_file=".env",
        env_file_encoding="utf-8",
    )

    host: str = Field(default="0.0.0.0", description="Interface the server binds to")
    port: int = Field(default=8000, description="Port the server listens on")


@lru_cache
def get_app_config() -> AppConfig:
    """Return the process-wide application settings."""
    return AppConfig()
