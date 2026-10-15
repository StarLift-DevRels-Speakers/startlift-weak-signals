"""Shared base for environment-driven settings."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class BaseConfig(BaseSettings):
    """Base class for settings read from the process environment.

    Subclasses set their own ``env_prefix`` and field aliases. Unknown
    environment variables are ignored, so unrelated variables in the
    environment or in a local ``.env`` file never break startup.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )
