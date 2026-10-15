"""Tests for the shared settings base class."""

from pydantic import Field
from pydantic_settings import SettingsConfigDict

from signals.config.base_config import BaseConfig


class ExampleConfig(BaseConfig):
    model_config = SettingsConfigDict(env_prefix="EXAMPLE_", extra="ignore")

    value: str = Field(default="fallback")


def test_reads_value_from_environment(monkeypatch) -> None:
    monkeypatch.setenv("EXAMPLE_VALUE", "from-env")

    assert ExampleConfig().value == "from-env"


def test_falls_back_to_default_when_unset(monkeypatch) -> None:
    monkeypatch.delenv("EXAMPLE_VALUE", raising=False)

    assert ExampleConfig().value == "fallback"


def test_ignores_unknown_environment_variables(monkeypatch) -> None:
    monkeypatch.setenv("EXAMPLE_UNRELATED", "ignored")

    assert ExampleConfig().value == "fallback"
