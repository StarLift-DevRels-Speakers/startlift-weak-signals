"""Tests for the user prompt builder."""

from signals.services.llm_services.user_prompt import build_prompt

from .conftest import make_talent_request


def test_renders_every_section(speaker) -> None:
    prompt = build_prompt(speaker)

    for section in (
        "=== ПРОФИЛЬ ===",
        "=== АКТИВНОСТЬ ===",
        "=== КАЧЕСТВО ===",
        "=== ДОСТИЖЕНИЯ ===",
        "=== ВОСТРЕБОВАННОСТЬ ===",
        "=== ПОСЛЕДНИЕ ДОКЛАДЫ ===",
        "=== ОТЗЫВЫ СЛУШАТЕЛЕЙ ===",
        "=== ВНЕШНИЕ УПОМИНАНИЯ ===",
    ):
        assert section in prompt


def test_renders_populated_values(speaker) -> None:
    prompt = build_prompt(speaker)

    assert "username: speaker" in prompt
    assert "region: Moscow" in prompt
    assert "influence: federal" in prompt
    assert "talks_total: 12" in prompt
    assert "avg_rating: 8.5 / 10" in prompt
    assert "nps: 9.0" in prompt
    assert "backend, platform" in prompt
    assert '"Scaling queues"' in prompt
    assert "2026-03-01 12:30" in prompt
    assert '"Clear structure"' in prompt
    assert '"Speaker of the year" (1/2)' in prompt
    assert "2026-02-10 | DevConf | Acme" in prompt
    assert "— нет данных —" not in prompt


def test_renders_absent_optional_data() -> None:
    speaker = make_talent_request(
        region=None,
        company=None,
        company_role=None,
        about=None,
        last_talk_date=None,
        nps=None,
        recent_talks=[],
        recent_feedback=[],
        achievements=[],
        parsing_events=[],
        profile_tags=[],
    )

    prompt = build_prompt(speaker)

    for section in (
        "=== ПРОФИЛЬ ===",
        "=== ПОСЛЕДНИЕ ДОКЛАДЫ ===",
        "=== ОТЗЫВЫ СЛУШАТЕЛЕЙ ===",
        "=== ВНЕШНИЕ УПОМИНАНИЯ ===",
    ):
        assert section in prompt
    assert prompt.count("— нет данных —") == 4
    assert "region: —" in prompt
    assert "last_talk_date: —" in prompt
    assert "nps: —" in prompt
    assert "profile_tags: —" in prompt
