"""Tests for application startup and serving."""

import logging

import pytest
from fastapi.testclient import TestClient

from signals import __main__ as main_module
from signals.config.app_config import get_app_config
from signals.config.gigachat_config import get_gigachat_config


class FakeModel:
    """Minimal stand-in for a provider model entry."""

    def __init__(self, model_id: str) -> None:
        self.id_ = model_id


class FakeModels:
    """Minimal stand-in for the provider model catalogue."""

    def __init__(self, model_ids: list[str]) -> None:
        self.data = [FakeModel(model_id) for model_id in model_ids]


class FakeClient:
    """Stands in for the GigaChat client at startup."""

    def __init__(self, model_ids: list[str] | None = None, error: Exception | None = None):
        self._model_ids = model_ids or []
        self._error = error
        self.calls = 0

    async def aget_models(self) -> FakeModels:
        self.calls += 1
        if self._error is not None:
            raise self._error
        return FakeModels(self._model_ids)


@pytest.fixture
def token(monkeypatch):
    monkeypatch.setenv("GIGACHAT_TOKEN", "test-token")
    get_gigachat_config.cache_clear()
    yield
    get_gigachat_config.cache_clear()


def patch_client(monkeypatch, client: FakeClient) -> None:
    monkeypatch.setattr(main_module, "get_gigachat_client", lambda: client)


def test_startup_logs_the_available_models(monkeypatch, token, caplog) -> None:
    client = FakeClient(["GigaChat-3-Ultra", "GigaChat-2"])
    patch_client(monkeypatch, client)

    with caplog.at_level(logging.INFO), TestClient(main_module.app):
        pass

    assert client.calls == 1
    assert "GigaChat-3-Ultra" in caplog.text
    assert "GigaChat-2" in caplog.text


def test_startup_succeeds_when_the_configured_model_is_absent(
    monkeypatch, token, caplog
) -> None:
    client = FakeClient(["Some-Other-Model"])
    patch_client(monkeypatch, client)

    with caplog.at_level(logging.INFO), TestClient(main_module.app):
        pass

    assert client.calls == 1
    assert "Some-Other-Model" in caplog.text


def test_startup_fails_when_the_model_list_cannot_be_fetched(monkeypatch, token) -> None:
    client = FakeClient(error=RuntimeError("401 Unauthorized"))
    patch_client(monkeypatch, client)

    with pytest.raises(RuntimeError), TestClient(main_module.app):
        pass


def test_serving_uses_the_configured_bind_address(monkeypatch) -> None:
    monkeypatch.setenv("SIGNALS_HOST", "127.0.0.1")
    monkeypatch.setenv("SIGNALS_PORT", "9123")
    get_app_config.cache_clear()
    captured: dict[str, object] = {}

    def fake_run(app, **kwargs):
        captured["app"] = app
        captured.update(kwargs)

    monkeypatch.setattr(main_module.uvicorn, "run", fake_run)

    main_module.main()

    assert captured["host"] == "127.0.0.1"
    assert captured["port"] == 9123
    assert captured["app"] is main_module.app
    get_app_config.cache_clear()


def test_serving_configures_application_logging(monkeypatch, capsys) -> None:
    """Regression: without handlers the startup log lines were silently dropped."""
    monkeypatch.setattr(main_module.uvicorn, "run", lambda app, **kwargs: None)
    root = logging.getLogger()
    original_handlers = root.handlers[:]
    original_level = root.level
    root.handlers = []
    try:
        main_module.main()
        main_module.logger.info("model catalogue probe")

        assert "model catalogue probe" in capsys.readouterr().err
    finally:
        root.handlers = original_handlers
        root.setLevel(original_level)
