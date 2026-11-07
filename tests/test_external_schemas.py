"""Tests for the external-candidate schemas."""

import pytest
from pydantic import ValidationError

from signals.schemas.external import (
    ExternalTalentRequest,
    ExternalTalentResponse,
)


def minimal_payload(**overrides: object) -> dict[str, object]:
    """Build the smallest valid external payload, with per-test overrides."""
    payload: dict[str, object] = {
        "username": "jane_doe",
        "talks_total": 0,
        "profile_tags": [],
        "recent_talks": [],
        "recent_feedback": [],
    }
    payload.update(overrides)
    return payload


def test_accepts_a_minimal_payload_with_empty_lists() -> None:
    request = ExternalTalentRequest.model_validate(minimal_payload())

    assert request.recent_talks == []
    assert request.recent_feedback == []
    assert request.social_links_count == 0


def test_treats_omitted_optional_fields_as_absent() -> None:
    request = ExternalTalentRequest.model_validate(minimal_payload())

    assert request.about is None
    assert request.company is None
    assert request.company_role is None
    assert request.region is None


def test_accepts_the_documented_example_payload() -> None:
    request = ExternalTalentRequest.model_validate(
        {
            "username": "jane_doe",
            "about": "Backend engineer, talks about distributed systems.",
            "company": "Acme",
            "company_role": "Staff Engineer",
            "region": "Moscow",
            "social_links_count": 3,
            "talks_total": 8,
            "profile_tags": ["backend", "distributed systems", "databases"],
            "recent_talks": [
                {"topic": "Taming queues", "talk_date": "2026-03-01T12:30:00Z"},
                {"topic": "Postgres internals", "talk_date": "2025-11-14T18:00:00Z"},
            ],
            "recent_feedback": [
                {
                    "feedback": "Clear structure, useful examples.",
                    "platform_name": "Habr",
                    "rating": 5,
                },
                {
                    "feedback": "Too fast in the demo part.",
                    "platform_name": "YouTube",
                    "conference": "DevConf",
                },
            ],
        }
    )

    assert request.talks_total == 8
    assert request.recent_talks[0].topic == "Taming queues"
    assert request.recent_feedback[0].rating == 5
    assert request.recent_feedback[1].conference == "DevConf"


@pytest.mark.parametrize("rating", [0, 6])
def test_rejects_a_rating_outside_the_one_to_five_range(rating: int) -> None:
    with pytest.raises(ValidationError):
        ExternalTalentRequest.model_validate(
            minimal_payload(
                recent_feedback=[
                    {"feedback": "Solid", "platform_name": "Habr", "rating": rating}
                ]
            )
        )


@pytest.mark.parametrize(
    "field", ["username", "talks_total", "recent_talks", "recent_feedback"]
)
def test_rejects_a_missing_required_field(field: str) -> None:
    payload = minimal_payload()
    payload.pop(field)

    with pytest.raises(ValidationError):
        ExternalTalentRequest.model_validate(payload)


def test_response_carries_no_identifier() -> None:
    response = ExternalTalentResponse(
        username="jane_doe", score=4, reason="Regular speaker", confidence="medium"
    )

    assert "id" not in ExternalTalentResponse.model_fields
    assert response.model_dump() == {
        "username": "jane_doe",
        "score": 4,
        "reason": "Regular speaker",
        "confidence": "medium",
    }
