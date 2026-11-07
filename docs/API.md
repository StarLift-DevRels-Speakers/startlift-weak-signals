# API

Сервис — HTTP-скорер без состояния: принимает профиль одного спикера и возвращает одну оценку от
LLM. Ничего не сохраняется.

Базовый URL: `SIGNALS_HOST:SIGNALS_PORT`, по умолчанию `http://0.0.0.0:8000`.
Тела запросов и ответов — JSON; любая ошибка возвращается как `{"detail": "<message>"}` без текста
провайдера, токенов и стека.

| Метод | Путь | Назначение |
|---|---|---|
| `GET` | `/health` | Проверка живости и настроенная модель оценки |
| `POST` | `/signals/weak-signals` | Оценка пользователя платформы по внутренним сигналам |
| `POST` | `/signals/weak-signals-external` | Оценка внешнего кандидата по публичным сигналам |

## Модель ошибок

| Статус | Когда |
|---|---|
| `422` | Тело не прошло валидацию; LLM не вызывается |
| `502` | Провайдер отказал или вернул данные вне схемы оценки |
| `504` | Провайдер не ответил за `GIGACHAT_TIMEOUT` |
| `500` | Прочая внутренняя ошибка |

## GET /health

Отвечает из состояния процесса, провайдер не вызывается. Доступность токена проверяется один раз
на старте, поэтому успешный ответ означает, что процесс запущен с рабочими учётными данными.

```json
{"status": "ok", "model": "GigaChat-3-Ultra"}
```

## POST /signals/weak-signals

Оценивает одного спикера платформы. В запросе — числовые продуктовые признаки и текстовый контекст.

### Запрос

| Поле | Тип | Обязательное | Комментарий |
|---|---|---|---|
| `id` | `int` | да | Возвращается в ответе |
| `username` | `str` | да | |
| `region` | `str \| null` | нет | |
| `company` | `str \| null` | нет | |
| `company_role` | `str \| null` | нет | |
| `about` | `str \| null` | нет | Короткое био |
| `influence` | `"local" \| "regional" \| "federal" \| "international"` | да | Уровень влияния |
| `talks_total` | `int`, `>= 0` | да | Число докладов |
| `talks_last_3_months` | `int`, `>= 0` | да | Докладов за последние три месяца |
| `last_talk_date` | `datetime \| null` | нет | |
| `avg_rating` | `float`, 0..10 | да | Средняя оценка выступлений |
| `feedback_count` | `int`, `>= 0` | да | Число отзывов |
| `nps` | `float \| null`, 0..10 | нет | |
| `profile_completion` | `int`, 0..100 | да | Заполненность профиля, % |
| `achievements_progress_pct` | `float`, 0..100 | да | Прогресс по достижениям, % |
| `cfp_high_match_count` | `int`, `>= 0` | да | Число сильных совпадений по CFP |
| `profile_tags` | `list[str]` | нет | По умолчанию `[]` |
| `recent_talks` | `list[TalkItem]` | нет | По умолчанию `[]` |
| `recent_feedback` | `list[FeedbackItem]` | нет | По умолчанию `[]` |
| `achievements` | `list[AchievementItem]` | нет | По умолчанию `[]` |
| `parsing_events` | `list[ParsingEventItem]` | нет | По умолчанию `[]` |

`TalkItem`:

| Поле | Тип | Обязательное |
|---|---|---|
| `topic` | `str` | да |
| `conference_type` | `str` | да |
| `format` | `str` | да |
| `talk_date` | `datetime` | да |

`FeedbackItem`:

| Поле | Тип | Обязательное | Комментарий |
|---|---|---|---|
| `rating` | `int`, 0..10 | да | |
| `positive` | `str` | да | За что хвалят |
| `negative` | `str` | да | На что жалуются |
| `improvement_suggestions` | `str` | да | Что улучшить |

`AchievementItem`: `title: str`, `description: str`, `current_value: int`, `target_value: int` —
все обязательны.

`ParsingEventItem`: `conference: str`, `company: str | null`, `event_date: date`,
`note: str | null`.

### Ответ `200`

```json
{
  "id": 42,
  "score": 4,
  "reason": "Regular speaker with strong recent feedback and visible growth.",
  "confidence": "high"
}
```

| Поле | Тип | Комментарий |
|---|---|---|
| `id` | `int` | Копируется из запроса |
| `score` | `int`, 1..5 | Оценка таланта |
| `reason` | `str`, 1..500 символов | Обоснование одним предложением |
| `confidence` | `"low" \| "medium" \| "high"` | Уверенность в оценке |

## POST /signals/weak-signals-external

Оценивает внешнего кандидата, найденного в интернете, чтобы решить, стоит ли приглашать его на
платформу. Профиль собирает внешний коллектор; эндпоинт не ходит в интернет, не переходит по
ссылкам и не присваивает идентификатор.

Смысл оценки: шкала 1-5 показывает уровень человека как спикера по публичным сигналам — объём и
регулярность докладов, широта тем, внешняя активность, текст отзывов. Отсутствие отзывов у
внешнего человека нормально: оно снижает `confidence`, а не оценку. Меньше одного доклада
(`talks_total = 0` и пустой `recent_talks`) — оценка не выше 2.

### Запрос

| Поле | Тип | Обязательное | Комментарий |
|---|---|---|---|
| `username` | `str` | да | Единственный идентификатор, возвращается в ответе |
| `talks_total` | `int`, `>= 0` | да | Приблизительно, по публичным анонсам |
| `profile_tags` | `list[str]` | да | Темы докладов |
| `recent_talks` | `list[ExternalTalkItem]` | да | Может быть пустым |
| `recent_feedback` | `list[ExternalFeedbackItem]` | да | Может быть пустым |
| `about` | `str \| null` | нет | Короткое био |
| `company` | `str \| null` | нет | |
| `company_role` | `str \| null` | нет | |
| `region` | `str \| null` | нет | |
| `social_links_count` | `int`, `>= 0` | нет | По умолчанию `0`; `0` — соцсети и личный сайт не найдены |

`ExternalTalkItem`:

| Поле | Тип | Обязательное |
|---|---|---|
| `topic` | `str` | да |
| `talk_date` | `datetime` | да |

Если коллектору известен только год выступления, он подставляет условную дату: точность дат в
оценке не переоценивается.

`ExternalFeedbackItem`:

| Поле | Тип | Обязательное | Комментарий |
|---|---|---|---|
| `feedback` | `str` | да | Текст отзыва или комментария |
| `platform_name` | `str` | да | Где найден отзыв |
| `rating` | `int \| null`, 1..5 | нет | Если оценку удалось найти |
| `conference` | `str \| null` | нет | Название конференции |

### Пример запроса

```json
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
    {"topic": "Postgres internals", "talk_date": "2025-11-14T18:00:00Z"}
  ],
  "recent_feedback": [
    {"feedback": "Clear structure, useful examples.", "platform_name": "Habr", "rating": 5},
    {"feedback": "Too fast in the demo part.", "platform_name": "YouTube", "conference": "DevConf"}
  ]
}
```

### Ответ `200`

```json
{
  "username": "jane_doe",
  "score": 4,
  "reason": "Regular speaker with a consistent topic focus and positive public feedback.",
  "confidence": "medium"
}
```

| Поле | Тип | Комментарий |
|---|---|---|
| `username` | `str` | Копируется из запроса |
| `score` | `int`, 1..5 | Оценка таланта |
| `reason` | `str`, 1..500 символов | Обоснование одним предложением |
| `confidence` | `"low" \| "medium" \| "high"` | Уверенность в оценке |

Поля `id` нет: сервис не хранит состояние. Когда появится внутренняя база, идентификатор будет
выдавать она, а необязательное поле `id` в ответе станет совместимым расширением контракта.
