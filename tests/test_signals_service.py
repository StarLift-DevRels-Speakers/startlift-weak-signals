"""Tests for the scoring service."""

import asyncio
import subprocess
import sys
from typing import Any

import pytest
from langchain_core.messages import HumanMessage, SystemMessage
from pydantic import ValidationError

from signals.schemas.signals import TalentLLMResponse, TalentResponse
from signals.services.llm_services.system_prompt import SYSTEM_PROMPT
from signals.services.signals import (
    ScoreUnavailableError,
    SignalsService,
    get_signals_service,
)


class FakeLLM:
    """Stands in for the structured-output runnable."""

    def __init__(self, answer: Any = None, error: Exception | None = None) -> None:
        self._answer = answer
        self._error = error
        self.calls: list[list[Any]] = []

    async def ainvoke(self, messages: list[Any]) -> Any:
        self.calls.append(messages)
        if self._error is not None:
            raise self._error
        return self._answer


def make_service(llm: Any, timeout: float = 1.0) -> SignalsService:
    return SignalsService(llm=llm, timeout=timeout)


async def test_returns_score_for_the_speaker(speaker) -> None:
    llm = FakeLLM(TalentLLMResponse(score=4, reason="Strong speaker", confidence="high"))

    response = await make_service(llm).score_talent(speaker)

    assert response == TalentResponse(
        id=speaker.id, score=4, reason="Strong speaker", confidence="high"
    )


async def test_sends_the_fixed_system_prompt_and_the_built_user_message(speaker) -> None:
    llm = FakeLLM(TalentLLMResponse(score=3, reason="Average", confidence="medium"))

    await make_service(llm).score_talent(speaker)

    messages = llm.calls[0]
    assert isinstance(messages[0], SystemMessage)
    assert messages[0].content == SYSTEM_PROMPT
    assert isinstance(messages[1], HumanMessage)
    assert "username: speaker" in messages[1].content


async def test_accepts_a_raw_mapping_from_the_provider(speaker) -> None:
    llm = FakeLLM({"score": 5, "reason": "Exceptional", "confidence": "high"})

    response = await make_service(llm).score_talent(speaker)

    assert response.score == 5
    assert response.confidence == "high"


async def test_provider_error_raises_score_unavailable(speaker) -> None:
    llm = FakeLLM(error=RuntimeError("provider exploded"))

    with pytest.raises(ScoreUnavailableError):
        await make_service(llm).score_talent(speaker)


async def test_unusable_answer_raises_score_unavailable(speaker) -> None:
    llm = FakeLLM({"score": 9, "reason": "out of range", "confidence": "high"})

    with pytest.raises(ScoreUnavailableError):
        await make_service(llm).score_talent(speaker)


async def test_unparseable_answer_raises_score_unavailable(speaker) -> None:
    llm = FakeLLM("not a scoring object")

    with pytest.raises(ScoreUnavailableError):
        await make_service(llm).score_talent(speaker)


async def test_slow_provider_raises_timeout(speaker) -> None:
    class SlowLLM:
        async def ainvoke(self, messages: list[Any]) -> Any:
            await asyncio.sleep(5)
            return None

    with pytest.raises(TimeoutError):
        await make_service(SlowLLM(), timeout=0.01).score_talent(speaker)


def test_scoring_schema_rejects_out_of_range_values() -> None:
    with pytest.raises(ValidationError):
        TalentLLMResponse(score=0, reason="no", confidence="high")


def test_dependency_wires_the_configured_runnable(monkeypatch) -> None:
    monkeypatch.setenv("GIGACHAT_TOKEN", "test-token")

    service = get_signals_service()

    assert isinstance(service, SignalsService)
    assert service._timeout > 0


def test_importing_the_service_needs_no_credentials_or_network() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "-c",
            "import signals.services.signals; print('imported')",
        ],
        capture_output=True,
        text=True,
        env={"PATH": "", "SYSTEMROOT": "C:\\Windows"},
        check=False,
    )

    assert result.returncode == 0, result.stderr
