"""User prompt builder for the external-candidate endpoint."""

from datetime import datetime

from signals.schemas.external import (
    ExternalFeedbackItem,
    ExternalTalentRequest,
    ExternalTalkItem,
)

ABSENT = "— нет данных —"
EMPTY = "—"


def _fmt_dt(value: datetime) -> str:
    return value.strftime("%Y-%m-%d %H:%M")


def _fmt_talks(talks: list[ExternalTalkItem]) -> str:
    if not talks:
        return ABSENT
    return "\n".join(f'- {_fmt_dt(t.talk_date)} | "{t.topic}"' for t in talks)


def _fmt_feedback(items: list[ExternalFeedbackItem]) -> str:
    if not items:
        return ABSENT
    lines = []
    for item in items:
        details = [f"platform: {item.platform_name}"]
        if item.rating is not None:
            details.append(f"rating {item.rating}/5")
        if item.conference:
            details.append(f"conference: {item.conference}")
        lines.append(f'- {"; ".join(details)} | "{item.feedback}"')
    return "\n".join(lines)


def build_external_prompt(candidate: ExternalTalentRequest) -> str:
    """Build the user prompt from an external candidate payload."""
    return f"""Оцени уровень спикера по публичным данным о нём.

=== ПРОФИЛЬ ===
username: {candidate.username}
about: {candidate.about or EMPTY}
company: {candidate.company or EMPTY}
company_role: {candidate.company_role or EMPTY}
region: {candidate.region or EMPTY}

=== ПУБЛИЧНАЯ АКТИВНОСТЬ ===
talks_total: {candidate.talks_total} (по публичным анонсам, приблизительно)
social_links_count: {candidate.social_links_count}

=== ТЕМЫ ===
{", ".join(candidate.profile_tags) if candidate.profile_tags else EMPTY}

=== ПОСЛЕДНИЕ ДОКЛАДЫ ===
{_fmt_talks(candidate.recent_talks)}

=== ОТЗЫВЫ ===
{_fmt_feedback(candidate.recent_feedback)}

Верни JSON: {{"score": 1-5, "reason": "<до 200 символов>", "confidence": "low|medium|high"}}.
"""
