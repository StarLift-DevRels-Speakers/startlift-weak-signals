"""Shared fixtures for the signals test suite."""

from datetime import UTC, date, datetime

import pytest

from signals.schemas.signals import (
    AchievementItem,
    FeedbackItem,
    Influence,
    ParsingEventItem,
    TalentRequest,
    TalkItem,
)


def make_talent_request(**overrides: object) -> TalentRequest:
    """Build a fully populated speaker request, with per-test overrides."""
    payload: dict[str, object] = {
        "id": 42,
        "username": "speaker",
        "region": "Moscow",
        "company": "Acme",
        "company_role": "Staff Engineer",
        "about": "Talks about distributed systems.",
        "influence": Influence.FEDERAL,
        "talks_total": 12,
        "talks_last_3_months": 3,
        "last_talk_date": datetime(2026, 3, 1, 12, 30, tzinfo=UTC),
        "avg_rating": 8.5,
        "feedback_count": 7,
        "nps": 9.0,
        "profile_completion": 95,
        "achievements_progress_pct": 60.0,
        "cfp_high_match_count": 2,
        "recent_talks": [
            TalkItem(
                topic="Scaling queues",
                conference_type="meetup",
                format="online",
                talk_date=datetime(2026, 3, 1, 12, 30, tzinfo=UTC),
            )
        ],
        "recent_feedback": [
            FeedbackItem(
                rating=9,
                positive="Clear structure",
                negative="Too fast",
                improvement_suggestions="Add examples",
            )
        ],
        "achievements": [
            AchievementItem(
                title="Speaker of the year",
                description="Internal award",
                current_value=1,
                target_value=2,
            )
        ],
        "parsing_events": [
            ParsingEventItem(
                conference="DevConf",
                company="Acme",
                event_date=date(2026, 2, 10),
                note="Keynote",
            )
        ],
        "profile_tags": ["backend", "platform"],
    }
    payload.update(overrides)

    return TalentRequest.model_validate(payload)


@pytest.fixture
def speaker() -> TalentRequest:
    """A fully populated speaker request."""
    return make_talent_request()
