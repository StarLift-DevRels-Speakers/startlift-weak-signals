from datetime import date, datetime
from enum import Enum
from typing import Literal

from pydantic import BaseModel, Field


class Influence(str, Enum):
    LOCAL = "local"
    REGIONAL = "regional"
    FEDERAL = "federal"
    INTERNATIONAL = "international"


class FeedbackItem(BaseModel):
    rating: int = Field(ge=0, le=10)
    positive: str
    negative: str
    improvement_suggestions: str


class TalkItem(BaseModel):
    topic: str
    conference_type: str
    format: str
    talk_date: datetime


class AchievementItem(BaseModel):
    title: str
    description: str
    current_value: int
    target_value: int


class ParsingEventItem(BaseModel):
    conference: str
    company: str | None = None
    event_date: date
    note: str | None = None


class TalentRequest(BaseModel):
    """Вход эндпоинта: спикер + фичи + текстовый контекст для LLM."""

    # идентификация
    id: int
    username: str
    region: str | None = None
    company: str | None = None
    company_role: str | None = None
    about: str | None = None
    influence: Influence

    # числовые фичи
    talks_total: int = Field(ge=0)
    talks_last_3_months: int = Field(ge=0)
    last_talk_date: datetime | None = None
    avg_rating: float = Field(ge=0, le=10)
    feedback_count: int = Field(ge=0)
    nps: float | None = Field(default=None, ge=0, le=10)
    profile_completion: int = Field(ge=0, le=100)
    achievements_progress_pct: float = Field(ge=0, le=100)
    cfp_high_match_count: int = Field(ge=0)

    # текстовый контекст для LLM
    recent_talks: list[TalkItem] = Field(default_factory=list)
    recent_feedback: list[FeedbackItem] = Field(default_factory=list)
    achievements: list[AchievementItem] = Field(default_factory=list)
    parsing_events: list[ParsingEventItem] = Field(default_factory=list)
    profile_tags: list[str] = Field(default_factory=list)


class TalentLLMResponse(BaseModel):
    score: int = Field(ge=1, le=5)
    reason: str = Field(min_length=1, max_length=500)
    confidence: Literal["low", "medium", "high"]


class TalentResponse(BaseModel):
    id: int
    score: int = Field(ge=1, le=5)
    reason: str = Field(min_length=1, max_length=500)
    confidence: Literal["low", "medium", "high"]