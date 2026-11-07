"""Request and response models for the external-candidate endpoint.

Kept separate from ``schemas/signals.py``: a public profile has no product features
and carries no identifier.
"""

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


class ExternalFeedbackItem(BaseModel):
    """One public review of a talk."""

    feedback: str
    platform_name: str
    rating: int | None = Field(default=None, ge=1, le=5)
    conference: str | None = None


class ExternalTalkItem(BaseModel):
    """One public talk announcement."""

    topic: str
    talk_date: datetime


class ExternalTalentRequest(BaseModel):
    """Input of the external endpoint: a speaker profile collected from the internet."""

    # identification
    username: str

    # required public signals
    talks_total: int = Field(ge=0)
    profile_tags: list[str]
    recent_talks: list[ExternalTalkItem]
    recent_feedback: list[ExternalFeedbackItem]

    # optional profile
    about: str | None = None
    company: str | None = None
    company_role: str | None = None
    region: str | None = None
    social_links_count: int = Field(default=0, ge=0)


class ExternalTalentResponse(BaseModel):
    """Scoring result for one external candidate; username replaces any identifier."""

    username: str
    score: int = Field(ge=1, le=5)
    reason: str = Field(min_length=1, max_length=500)
    confidence: Literal["low", "medium", "high"]
