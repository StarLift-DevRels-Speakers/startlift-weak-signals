"""Tests for the external user prompt builder."""

from signals.services.llm_services.external_user_prompt import build_external_prompt

from .conftest import make_external_request


def test_renders_every_section(external_candidate) -> None:
    prompt = build_external_prompt(external_candidate)

    for section in (
        "=== ПРОФИЛЬ ===",
        "=== ПУБЛИЧНАЯ АКТИВНОСТЬ ===",
        "=== ТЕМЫ ===",
        "=== ПОСЛЕДНИЕ ДОКЛАДЫ ===",
        "=== ОТЗЫВЫ ===",
    ):
        assert section in prompt


def test_renders_populated_values(external_candidate) -> None:
    prompt = build_external_prompt(external_candidate)

    assert "username: jane_doe" in prompt
    assert "region: Moscow" in prompt
    assert "talks_total: 8" in prompt
    assert "social_links_count: 3" in prompt
    assert "backend, distributed systems" in prompt
    assert '"Taming queues"' in prompt
    assert "2026-03-01 12:30" in prompt
    assert "platform: Habr" in prompt
    assert "rating 5/5" in prompt
    assert "conference: DevConf" in prompt
    assert '"Clear structure"' in prompt
    assert "— нет данных —" not in prompt


def test_renders_absent_optional_data() -> None:
    candidate = make_external_request(
        about=None,
        company=None,
        company_role=None,
        region=None,
        social_links_count=0,
        talks_total=0,
        profile_tags=[],
        recent_talks=[],
        recent_feedback=[],
    )

    prompt = build_external_prompt(candidate)

    assert "about: —" in prompt
    assert "region: —" in prompt
    assert prompt.count("— нет данных —") == 2
    assert "talks_total: 0" in prompt
    assert "social_links_count: 0" in prompt
