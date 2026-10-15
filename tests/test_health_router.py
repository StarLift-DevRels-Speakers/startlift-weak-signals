"""Tests for the liveness endpoint."""

from fastapi.testclient import TestClient

from signals.__main__ import app
from signals.config.gigachat_config import get_gigachat_config


def test_reports_status_and_configured_model(monkeypatch) -> None:
    monkeypatch.setenv("GIGACHAT_TOKEN", "test-token")
    monkeypatch.setenv("GIGACHAT_LLM_MODEL", "GigaChat-Health-Test")
    get_gigachat_config.cache_clear()
    client = TestClient(app)

    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok", "model": "GigaChat-Health-Test"}
    get_gigachat_config.cache_clear()


def test_does_not_touch_the_provider(monkeypatch) -> None:
    monkeypatch.setenv("GIGACHAT_TOKEN", "test-token")
    get_gigachat_config.cache_clear()

    def fail_on_client_access():
        raise AssertionError("health must not touch the provider client")

    monkeypatch.setattr(
        "signals.services.llm_services.gigachat_client.get_gigachat_client",
        fail_on_client_access,
    )

    assert TestClient(app).get("/health").status_code == 200
    get_gigachat_config.cache_clear()
