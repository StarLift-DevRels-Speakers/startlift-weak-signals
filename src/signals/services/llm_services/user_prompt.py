from datetime import date, datetime

from signals.schemas.signals import (
    AchievementItem,
    FeedbackItem,
    ParsingEventItem,
    TalentRequest,
    TalkItem,
)


def _fmt_dt(value: datetime | date | None) -> str:
    if value is None:
        return "—"
    if isinstance(value, datetime):
        return value.strftime("%Y-%m-%d %H:%M")
    return value.strftime("%Y-%m-%d")


def _fmt_talks(talks: list[TalkItem]) -> str:
    if not talks:
        return "— нет данных —"
    return "\n".join(
        f'- {_fmt_dt(t.talk_date)} | "{t.topic}" | {t.conference_type} | {t.format}'
        for t in talks
    )


def _fmt_feedback(items: list[FeedbackItem]) -> str:
    if not items:
        return "— нет данных —"
    return "\n".join(
        f'- rating {f.rating} | + "{f.positive}" | - "{f.negative}" '
        f'| improvement: "{f.improvement_suggestions}"'
        for f in items
    )


def _fmt_achievements(items: list[AchievementItem]) -> str:
    if not items:
        return "— нет данных —"
    return "\n".join(
        f'- "{a.title}" ({a.current_value}/{a.target_value}) — {a.description}'
        for a in items
    )


def _fmt_parsing(items: list[ParsingEventItem]) -> str:
    if not items:
        return "— нет данных —"
    return "\n".join(
        f'- {_fmt_dt(p.event_date)} | {p.conference} | {p.company or "—"} '
        f'| {p.note or "—"}'
        for p in items
    )


def build_prompt(speaker: TalentRequest) -> str:
    """Собирает пользовательский промпт из TalentRequest."""
    return f"""Оцени потенциал спикера на основе данных.

=== ПРОФИЛЬ ===
id: {speaker.id}
username: {speaker.username}
region: {speaker.region or "—"}
company: {speaker.company or "—"}
company_role: {speaker.company_role or "—"}
influence: {speaker.influence.value}
profile_completion: {speaker.profile_completion}%
about: {speaker.about or "—"}

=== АКТИВНОСТЬ ===
talks_total: {speaker.talks_total}
talks_last_3_months: {speaker.talks_last_3_months}
last_talk_date: {_fmt_dt(speaker.last_talk_date)}

=== КАЧЕСТВО ===
avg_rating: {speaker.avg_rating} / 10
feedback_count: {speaker.feedback_count}
nps: {speaker.nps if speaker.nps is not None else "—"}

=== ДОСТИЖЕНИЯ ===
achievements_progress_pct: {speaker.achievements_progress_pct}%
{_fmt_achievements(speaker.achievements)}

=== ВОСТРЕБОВАННОСТЬ ===
cfp_high_match_count: {speaker.cfp_high_match_count}
profile_tags: {", ".join(speaker.profile_tags) if speaker.profile_tags else "—"}

=== ПОСЛЕДНИЕ ДОКЛАДЫ ===
{_fmt_talks(speaker.recent_talks)}

=== ОТЗЫВЫ СЛУШАТЕЛЕЙ ===
{_fmt_feedback(speaker.recent_feedback)}

=== ВНЕШНИЕ УПОМИНАНИЯ ===
{_fmt_parsing(speaker.parsing_events)}

Верни JSON: {{"score": 1-5, "reason": "<до 200 символов>", "confidence": "low|medium|high"}}.
"""