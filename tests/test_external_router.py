"""Tests for the external-candidate endpoint."""

import asyncio
from typing import Any

import pytest
from fastapi.testclient import TestClient

from signals.__main__ import app
from signals.services.external_signals import (
    ExternalSignalsService,
    get_external_signals_service,
)

from .conftest import make_external_request


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


class SlowLLM:
    """Never answers within the test timeout."""

    async def ainvoke(self, messages: list[Any]) -> Any:
        await asyncio.sleep(5)
        return None


class BrokenService:
    """Fails before the LLM is reached."""

    async def score_candidate(self, payload: Any) -> Any:
        raise RuntimeError("service exploded")


@pytest.fixture(autouse=True)
def clear_overrides():
    yield
    app.dependency_overrides.clear()


def make_client(llm: Any, timeout: float = 1.0) -> TestClient:
    app.dependency_overrides[get_external_signals_service] = lambda: (
        ExternalSignalsService(llm=llm, timeout=timeout)
    )
    return TestClient(app)


def valid_payload() -> dict[str, Any]:
    return make_external_request().model_dump(mode="json")


def test_scores_a_valid_candidate() -> None:
    llm = FakeLLM(
        {"score": 4, "reason": "Strong public presence", "confidence": "high"}
    )

    response = make_client(llm).post(
        "/signals/weak-signals-external", json=valid_payload()
    )

    assert response.status_code == 200
    assert response.json() == {
        "username": "jane_doe",
        "score": 4,
        "reason": "Strong public presence",
        "confidence": "high",
    }


def test_rejects_an_invalid_payload_without_calling_the_provider() -> None:
    llm = FakeLLM({"score": 4, "reason": "Strong", "confidence": "high"})
    payload = valid_payload()
    payload.pop("username")

    response = make_client(llm).post("/signals/weak-signals-external", json=payload)

    assert response.status_code == 422
    assert llm.calls == []


def test_maps_an_unusable_answer_to_502() -> None:
    llm = FakeLLM({"score": 9, "reason": "out of range", "confidence": "high"})

    response = make_client(llm).post(
        "/signals/weak-signals-external", json=valid_payload()
    )

    assert response.status_code == 502


def test_maps_a_timeout_to_504() -> None:
    response = make_client(SlowLLM(), timeout=0.01).post(
        "/signals/weak-signals-external", json=valid_payload()
    )

    assert response.status_code == 504


def test_maps_an_unexpected_failure_to_500() -> None:
    app.dependency_overrides[get_external_signals_service] = lambda: BrokenService()

    response = TestClient(app).post(
        "/signals/weak-signals-external", json=valid_payload()
    )

    assert response.status_code == 500


def test_openapi_lists_both_signal_endpoints() -> None:
    paths = TestClient(app).get("/openapi.json").json()["paths"]

    assert "/signals/weak-signals-external" in paths
    assert "/signals/weak-signals" in paths


def test_response_carries_no_identifier() -> None:
    llm = FakeLLM({"score": 3, "reason": "Average", "confidence": "medium"})

    body = (
        make_client(llm)
        .post("/signals/weak-signals-external", json=valid_payload())
        .json()
    )

    assert "id" not in body
