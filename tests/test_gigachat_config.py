"""Tests for the GigaChat settings."""

import pytest
from pydantic import ValidationError

from signals.config.gigachat_config import GigaChatConfig, get_gigachat_config

PREFIXED_VARIABLES = (
    "GIGACHAT_ULTRA_BASE_URL",
    "GIGACHAT_ULTRA_SCOPE",
    "GIGACHAT_LLM_MODEL",
    "GIGACHAT_LLM_TEMPERATURE",
    "GIGACHAT_LLM_MAX_TOKENS",
    "GIGACHAT_VERIFY_SSL_CERTS",
    "GIGACHAT_TIMEOUT",
    "GIGACHAT_COLLECT_FORM_MODEL",
    "GIGACHAT_COLLECT_FORM_TEMPERATURE",
    "GIGACHAT_COLLECT_FORM_MAX_TOKENS",
)


@pytest.fixture(autouse=True)
def clean_environment(monkeypatch):
    """Keep provider variables out of the tests unless a test sets them."""
    for name in PREFIXED_VARIABLES:
        monkeypatch.delenv(name, raising=False)
    monkeypatch.setenv("GIGACHAT_TOKEN", "test-token")
    get_gigachat_config.cache_clear()
    yield
    get_gigachat_config.cache_clear()


def test_defaults_need_only_the_token() -> None:
    settings = GigaChatConfig()

    assert settings.llm_model == "GigaChat-3-Ultra"
    assert settings.ultra_base_url == "https://api.giga.chat/v1"
    assert settings.ultra_scope == "GIGACHAT_API_PERS"
    assert settings.llm_temperature == 0.1
    assert settings.llm_max_tokens == 5000
    assert settings.verify_ssl_certs is False
    assert settings.timeout == 60.0


def test_token_is_read_from_gigachat_token() -> None:
    assert GigaChatConfig().token.get_secret_value() == "test-token"


def test_token_is_not_exposed_by_repr() -> None:
    assert "test-token" not in repr(GigaChatConfig())


def test_token_is_required(monkeypatch) -> None:
    monkeypatch.delenv("GIGACHAT_TOKEN", raising=False)
    # Keep the developer's local .env out of this test.
    monkeypatch.setitem(
        GigaChatConfig.model_config, "env_file", None
    )

    with pytest.raises(ValidationError) as excinfo:
        GigaChatConfig()

    assert "GIGACHAT_TOKEN" in str(excinfo.value)


def test_prefixed_override_is_used(monkeypatch) -> None:
    monkeypatch.setenv("GIGACHAT_ULTRA_BASE_URL", "https://example.invalid/v1")
    monkeypatch.setenv("GIGACHAT_ULTRA_SCOPE", "GIGACHAT_API_CORP")
    monkeypatch.setenv("GIGACHAT_LLM_MODEL", "GigaChat-Override")
    monkeypatch.setenv("GIGACHAT_LLM_TEMPERATURE", "0.7")
    monkeypatch.setenv("GIGACHAT_LLM_MAX_TOKENS", "1234")
    monkeypatch.setenv("GIGACHAT_VERIFY_SSL_CERTS", "true")
    monkeypatch.setenv("GIGACHAT_TIMEOUT", "5.5")

    settings = GigaChatConfig()

    assert settings.ultra_base_url == "https://example.invalid/v1"
    assert settings.ultra_scope == "GIGACHAT_API_CORP"
    assert settings.llm_model == "GigaChat-Override"
    assert settings.llm_temperature == 0.7
    assert settings.llm_max_tokens == 1234
    assert settings.verify_ssl_certs is True
    assert settings.timeout == 5.5


def test_legacy_collect_form_names_are_accepted(monkeypatch) -> None:
    monkeypatch.setenv("GIGACHAT_COLLECT_FORM_MODEL", "GigaChat-Legacy")
    monkeypatch.setenv("GIGACHAT_COLLECT_FORM_TEMPERATURE", "0.3")
    monkeypatch.setenv("GIGACHAT_COLLECT_FORM_MAX_TOKENS", "777")

    settings = GigaChatConfig()

    assert settings.llm_model == "GigaChat-Legacy"
    assert settings.llm_temperature == 0.3
    assert settings.llm_max_tokens == 777


def test_get_gigachat_config_is_cached() -> None:
    assert get_gigachat_config() is get_gigachat_config()
