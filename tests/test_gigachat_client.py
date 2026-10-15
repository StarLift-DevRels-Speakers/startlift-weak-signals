"""Tests for the GigaChat client factory."""

import pytest
from langchain_gigachat import GigaChat
from pydantic import ValidationError

from signals.config.gigachat_config import GigaChatConfig, get_gigachat_config
from signals.schemas.signals import TalentLLMResponse
from signals.services.llm_services.gigachat_client import (
    SCORING_TOOL_DESCRIPTION,
    build_gigachat_client,
    build_scoring_tool_schema,
    get_gigachat_client,
    get_provider_timeout,
    get_structured_scoring_runnable,
    parse_scoring_answer,
)


@pytest.fixture(autouse=True)
def configured_environment(monkeypatch):
    """Provide a token and clear the settings and factory caches per test."""
    monkeypatch.setenv("GIGACHAT_TOKEN", "test-token")
    get_gigachat_config.cache_clear()
    get_gigachat_client.cache_clear()
    get_structured_scoring_runnable.cache_clear()
    yield
    get_gigachat_config.cache_clear()
    get_gigachat_client.cache_clear()
    get_structured_scoring_runnable.cache_clear()


def test_builds_client_from_settings(monkeypatch) -> None:
    monkeypatch.setenv("GIGACHAT_LLM_MODEL", "GigaChat-Test")
    monkeypatch.setenv("GIGACHAT_LLM_TEMPERATURE", "0.4")
    monkeypatch.setenv("GIGACHAT_LLM_MAX_TOKENS", "321")
    monkeypatch.setenv("GIGACHAT_ULTRA_BASE_URL", "https://example.invalid/v1")
    monkeypatch.setenv("GIGACHAT_ULTRA_SCOPE", "GIGACHAT_API_CORP")
    monkeypatch.setenv("GIGACHAT_VERIFY_SSL_CERTS", "true")
    monkeypatch.setenv("GIGACHAT_TIMEOUT", "3.5")
    config = GigaChatConfig()

    client = build_gigachat_client(config)

    assert isinstance(client, GigaChat)
    assert client.model == "GigaChat-Test"
    assert client.temperature == 0.4
    assert client.max_tokens == 321
    assert client.base_url == "https://example.invalid/v1"
    assert client.scope == "GIGACHAT_API_CORP"
    assert client.verify_ssl_certs is True
    assert client.timeout == 3.5


def test_token_is_passed_as_credentials(monkeypatch) -> None:
    monkeypatch.setenv("GIGACHAT_TOKEN", "another-token")

    client = build_gigachat_client(GigaChatConfig())

    assert client.credentials == "another-token"
    assert client.access_token is None


def test_client_is_cached() -> None:
    assert get_gigachat_client() is get_gigachat_client()


def test_structured_runnable_is_cached() -> None:
    assert get_structured_scoring_runnable() is get_structured_scoring_runnable()


def test_scoring_tool_schema_forces_the_fixed_response_shape() -> None:
    tool = build_scoring_tool_schema()

    assert tool["type"] == "function"
    function = tool["function"]
    assert function["name"] == TalentLLMResponse.__name__
    assert function["description"] == SCORING_TOOL_DESCRIPTION
    assert function["parameters"] == TalentLLMResponse.model_json_schema()


def test_structured_runnable_calls_the_scoring_function() -> None:
    runnable = get_structured_scoring_runnable()
    binding = runnable.steps[0]

    assert binding.kwargs["function_call"] == {"name": TalentLLMResponse.__name__}
    assert binding.kwargs["tools"] == [build_scoring_tool_schema()]
    assert runnable.steps[1].key_name == TalentLLMResponse.__name__


def test_parse_scoring_answer_validates_the_schema() -> None:
    parsed = parse_scoring_answer({"score": 4, "reason": "solid", "confidence": "high"})

    assert parsed == TalentLLMResponse(score=4, reason="solid", confidence="high")


def test_parse_scoring_answer_rejects_out_of_range_values() -> None:
    with pytest.raises(ValidationError):
        parse_scoring_answer({"score": 9, "reason": "no", "confidence": "high"})


def test_parse_scoring_answer_rejects_non_objects() -> None:
    with pytest.raises(TypeError):
        parse_scoring_answer("not an object")


def test_provider_timeout_comes_from_settings(monkeypatch) -> None:
    monkeypatch.setenv("GIGACHAT_TIMEOUT", "12.5")
    get_gigachat_config.cache_clear()

    assert get_provider_timeout() == 12.5
