"""GigaChat settings.

Environment variables use the ``GIGACHAT_`` prefix, except the token
(``GIGACHAT_TOKEN``) and the request timeout (``GIGACHAT_TIMEOUT``), which
carry explicit aliases. Legacy names from the reference project
(``GIGACHAT_COLLECT_FORM_*``) are still accepted for the prompt settings.
"""

from functools import lru_cache

from pydantic import AliasChoices, Field, SecretStr
from pydantic_settings import SettingsConfigDict

from .base_config import BaseConfig


class GigaChatConfig(BaseConfig):
    model_config = SettingsConfigDict(
        env_prefix="GIGACHAT_",
        extra="ignore",
        env_file=".env",
        env_file_encoding="utf-8",
    )

    # Required: without a token the service must not start (fail fast).
    # SecretStr keeps the value out of logs and repr().
    token: SecretStr = Field(
        validation_alias="GIGACHAT_TOKEN",
        description="GigaChat authorization key",
    )

    # Ultra models are served from a dedicated endpoint and require an explicit scope.
    ultra_base_url: str = Field(
        default="https://api.giga.chat/v1",
        description="Endpoint for ultra models",
    )
    ultra_scope: str = Field(
        default="GIGACHAT_API_PERS",
        description="Authorization scope for ultra models",
    )

    llm_model: str = Field(
        default="GigaChat-3-Ultra",
        validation_alias=AliasChoices("GIGACHAT_LLM_MODEL", "GIGACHAT_COLLECT_FORM_MODEL"),
        description="Model used for scoring",
    )
    llm_temperature: float = Field(
        default=0.1,
        validation_alias=AliasChoices(
            "GIGACHAT_LLM_TEMPERATURE", "GIGACHAT_COLLECT_FORM_TEMPERATURE"
        ),
        description="Sampling temperature for scoring",
    )
    llm_max_tokens: int = Field(
        default=5000,
        validation_alias=AliasChoices(
            "GIGACHAT_LLM_MAX_TOKENS", "GIGACHAT_COLLECT_FORM_MAX_TOKENS"
        ),
        description="Response token limit for scoring",
    )

    verify_ssl_certs: bool = Field(
        default=False,
        description="Verify provider TLS certificates (disabled for development)",
    )
    timeout: float = Field(
        default=60.0,
        validation_alias="GIGACHAT_TIMEOUT",
        description="Provider request timeout in seconds",
    )


@lru_cache
def get_gigachat_config() -> GigaChatConfig:
    """Return the process-wide GigaChat settings, failing fast without a token."""
    return GigaChatConfig()  # type: ignore[call-arg]
