"""Checks that the documented environment variables exist in the settings."""

import re
from pathlib import Path

import pytest

from signals.config.app_config import AppConfig
from signals.config.gigachat_config import GigaChatConfig

README = Path(__file__).resolve().parents[1] / "README.md"

# Values, not variable names: they appear in backticks as setting values.
SCOPE_VALUES = {"GIGACHAT_API_PERS", "GIGACHAT_API_B2B", "GIGACHAT_API_CORP"}


def documented_variables() -> set[str]:
    text = README.read_text(encoding="utf-8")
    found = set(re.findall(r"`((?:GIGACHAT|SIGNALS)_[A-Z_]+)`", text))
    return found - SCOPE_VALUES


def known_variables() -> set[str]:
    names = set()
    for model, prefix in ((GigaChatConfig, "GIGACHAT_"), (AppConfig, "SIGNALS_")):
        for name, field in model.model_fields.items():
            alias = field.validation_alias
            choices = getattr(alias, "choices", None)
            if choices:
                names.update(str(choice) for choice in choices)
                continue
            if isinstance(alias, str):
                names.add(alias)
                continue
            names.add(f"{prefix}{name.upper()}")
    return names


@pytest.fixture(autouse=True)
def configured_environment(monkeypatch):
    monkeypatch.setenv("GIGACHAT_TOKEN", "test-token")


def test_readme_documents_only_real_settings() -> None:
    assert documented_variables() <= known_variables()


def test_readme_documents_every_required_setting() -> None:
    documented = documented_variables()

    assert "GIGACHAT_TOKEN" in documented
    assert "SIGNALS_HOST" in documented
    assert "SIGNALS_PORT" in documented
