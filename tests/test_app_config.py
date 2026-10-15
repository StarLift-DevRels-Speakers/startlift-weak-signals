"""Tests for the HTTP server settings."""

from signals.config.app_config import AppConfig, get_app_config


def test_defaults(monkeypatch) -> None:
    monkeypatch.delenv("SIGNALS_HOST", raising=False)
    monkeypatch.delenv("SIGNALS_PORT", raising=False)

    settings = AppConfig()

    assert settings.host == "0.0.0.0"
    assert settings.port == 8000


def test_overrides(monkeypatch) -> None:
    monkeypatch.setenv("SIGNALS_HOST", "127.0.0.1")
    monkeypatch.setenv("SIGNALS_PORT", "9001")

    settings = AppConfig()

    assert settings.host == "127.0.0.1"
    assert settings.port == 9001


def test_get_app_config_is_cached() -> None:
    assert get_app_config() is get_app_config()
