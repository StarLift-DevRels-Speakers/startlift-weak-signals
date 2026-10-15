### Кейс 1: «Выдающийся талант» (ожидаемый score = 5)
```json
{
  "id": 42,
  "username": "ivan_petrov",
  "region": "Москва",
  "company": "Ozon",
  "company_role": "Senior Backend Engineer",
  "about": "Backend-разработчик с 8-летним опытом в высоконагруженных системах. Выступаю с 2022 года, специализируюсь на Kafka, DDD и оптимизации производительности. Регулярно участвую в крупных конференциях.",
  "influence": "international",
  "talks_total": 47,
  "talks_last_3_months": 6,
  "last_talk_date": "2026-09-28T10:00:00Z",
  "avg_rating": 9.3,
  "feedback_count": 41,
  "nps": 9.6,
  "profile_completion": 98,
  "achievements_progress_pct": 87.5,
  "cfp_high_match_count": 12,
  "recent_talks": [
    {
      "topic": "Оптимизация Kafka в проде: от 100k до 1M msg/s",
      "conference_type": "international",
      "format": "offline",
      "talk_date": "2026-09-28T10:00:00Z"
    },
    {
      "topic": "DDD для стартапов: как не утонуть в абстракциях",
      "conference_type": "conference",
      "format": "offline",
      "talk_date": "2026-08-15T14:30:00Z"
    },
    {
      "topic": "Highload на Go: практические паттерны",
      "conference_type": "meetup",
      "format": "online",
      "talk_date": "2026-07-10T18:00:00Z"
    }
  ],
  "recent_feedback": [
    {
      "rating": 10,
      "positive": "Потрясающие живые примеры из продакшена, спикер держит зал 40 минут без слайдов",
      "negative": "Мало времени на вопросы в конце",
      "improvement_suggestions": "Выделить отдельный блок Q&A на 15 минут"
    },
    {
      "rating": 9,
      "positive": "Глубокая экспертиза, отвечает на сложные вопросы на лету",
      "negative": "Немного быстрый темп в середине",
      "improvement_suggestions": "Добавить паузы для осмысления"
    },
    {
      "rating": 9,
      "positive": "Отличная структура, понятные выводы, применимо на практике",
      "negative": "Хотелось бы больше кейсов с цифрами",
      "improvement_suggestions": "Больше метрик до/после"
    }
  ],
  "achievements": [
    {
      "title": "Выступить на 10 конференциях за год",
      "description": "Цель на 2026 год",
      "current_value": 9,
      "target_value": 10
    },
    {
      "title": "Собрать 5000 подписчиков в блоге",
      "description": "Технический блог о backend",
      "current_value": 4200,
      "target_value": 5000
    },
    {
      "title": "Снять 20 лекций",
      "description": "Образовательный курс",
      "current_value": 15,
      "target_value": 20
    }
  ],
  "parsing_events": [
    {
      "conference": "HighLoad++ 2026",
      "company": "Ozon",
      "event_date": "2026-09-28",
      "note": "Заявлен как ключевой спикер секции Backend"
    },
    {
      "conference": "Devoxx Russia",
      "company": "Ozon",
      "event_date": "2026-08-15",
      "note": "Упоминание в программе"
    }
  ],
  "profile_tags": ["kafka", "ddd", "backend", "highload", "golang", "performance"]
}
```
Ожидаемо: score = 5, confidence = "high", reason про системную активность, качество и международный уровень.

### Кейс 2: «Стабильный середняк» (ожидаемый score = 3)
```json
{
  "id": 108,
  "username": "maria_smirnova",
  "region": "Санкт-Петербург",
  "company": "Yandex Cloud",
  "company_role": "Middle Frontend Developer",
  "about": "Фронтенд-разработчик, 4 года опыта. Люблю React и TypeScript, иногда выступаю на внутренних митапах.",
  "influence": "regional",
  "talks_total": 9,
  "talks_last_3_months": 1,
  "last_talk_date": "2026-08-20T18:00:00Z",
  "avg_rating": 7.2,
  "feedback_count": 7,
  "nps": 7.5,
  "profile_completion": 65,
  "achievements_progress_pct": 42.0,
  "cfp_high_match_count": 1,
  "recent_talks": [
    {
      "topic": "React Server Components: что это и зачем",
      "conference_type": "meetup",
      "format": "offline",
      "talk_date": "2026-08-20T18:00:00Z"
    },
    {
      "topic": "TypeScript: типизация API-слоя",
      "conference_type": "internal",
      "format": "online",
      "talk_date": "2026-03-14T15:00:00Z"
    }
  ],
  "recent_feedback": [
    {
      "rating": 8,
      "positive": "Хорошая структура, понятные примеры",
      "negative": "Читала со слайдов почти весь доклад",
      "improvement_suggestions": "Меньше текста на слайдах, больше живого объяснения"
    },
    {
      "rating": 7,
      "positive": "Актуальная тема, хорошо подготовлена",
      "negative": "Не хватило глубины, поверхностно",
      "improvement_suggestions": "Добавить реальные кейсы из практики"
    },
    {
      "rating": 6,
      "positive": "Дружелюбная подача",
      "negative": "Слабый звук, часть зала не слышала",
      "improvement_suggestions": "Проверять оборудование заранее"
    }
  ],
  "achievements": [
    {
      "title": "Выступить на 5 митапах",
      "description": "Цель на год",
      "current_value": 2,
      "target_value": 5
    },
    {
      "title": "Написать 10 статей",
      "description": "Технический блог",
      "current_value": 4,
      "target_value": 10
    }
  ],
  "parsing_events": [
    {
      "conference": "Frontend Meetup SPb",
      "company": "Yandex Cloud",
      "event_date": "2026-08-20",
      "note": null
    }
  ],
  "profile_tags": ["react", "typescript", "frontend"]
}
```
Ожидаемо: score = 3, confidence = "medium", reason про регулярность, но без ярких сигналов.

### Кейс 3: «Новичок» (ожидаемый score = 2)
```json
{
  "id": 501,
  "username": "alex_novikov",
  "region": "Казань",
  "company": "Unknown",
  "company_role": "Junior Developer",
  "about": "Начинающий разработчик, хочу попробовать себя в публичных выступлениях.",
  "influence": "local",
  "talks_total": 1,
  "talks_last_3_months": 0,
  "last_talk_date": "2026-02-10T18:00:00Z",
  "avg_rating": 5.0,
  "feedback_count": 1,
  "nps": null,
  "profile_completion": 30,
  "achievements_progress_pct": 10.0,
  "cfp_high_match_count": 0,
  "recent_talks": [
    {
      "topic": "Введение в Docker для джунов",
      "conference_type": "internal",
      "format": "online",
      "talk_date": "2026-02-10T18:00:00Z"
    }
  ],
  "recent_feedback": [
    {
      "rating": 5,
      "positive": "Понятно для новичков",
      "negative": "Много воды, мало конкретики, читал с листа",
      "improvement_suggestions": "Готовиться тщательнее, репетировать"
    }
  ],
  "achievements": [
    {
      "title": "Выступить на первом митапе",
      "description": "Первый шаг",
      "current_value": 1,
      "target_value": 10
    }
  ],
  "parsing_events": [],
  "profile_tags": ["docker", "junior"]
}
```
Ожидаемо: score = 2, confidence = "high" (данных достаточно, чтобы понять — рано), reason про единичный опыт и слабую обратную связь.

### Кейс 4: «Пустой профиль» (edge case, ожидаемый score = 1)
```json
{
  "id": 999,
  "username": "ghost_user",
  "region": null,
  "company": null,
  "company_role": null,
  "about": null,
  "influence": "local",
  "talks_total": 0,
  "talks_last_3_months": 0,
  "last_talk_date": null,
  "avg_rating": 0,
  "feedback_count": 0,
  "nps": null,
  "profile_completion": 5,
  "achievements_progress_pct": 0,
  "cfp_high_match_count": 0,
  "recent_talks": [],
  "recent_feedback": [],
  "achievements": [],
  "parsing_events": [],
  "profile_tags": []
}
```
Ожидаемо: score = 1, confidence = "high", reason про отсутствие данных и активности.


### Кейс 5: «Противоречивый» (для проверки рассуждений LLM)
```json
{
  "id": 777,
  "username": "dmitry_orlov",
  "region": "Новосибирск",
  "company": "Sber",
  "company_role": "Lead Data Scientist",
  "about": "10 лет в ML, выступаю на конференциях с 2015 года. Автор курса по ML в проде.",
  "influence": "federal",
  "talks_total": 35,
  "talks_last_3_months": 0,
  "last_talk_date": "2025-11-15T10:00:00Z",
  "avg_rating": 8.9,
  "feedback_count": 30,
  "nps": 8.5,
  "profile_completion": 95,
  "achievements_progress_pct": 55.0,
  "cfp_high_match_count": 8,
  "recent_talks": [
    {
      "topic": "ML в проде: как перестать бояться",
      "conference_type": "conference",
      "format": "offline",
      "talk_date": "2025-11-15T10:00:00Z"
    }
  ],
  "recent_feedback": [
    {
      "rating": 9,
      "positive": "Глубокий опыт, отличные кейсы",
      "negative": "Тема уже была в прошлом году, мало нового",
      "improvement_suggestions": "Обновлять материал"
    }
  ],
  "achievements": [
    {
      "title": "Запустить курс",
      "description": "Онлайн-курс по ML",
      "current_value": 1,
      "target_value": 1
    }
  ],
  "parsing_events": [
    {
      "conference": "AI Journey 2025",
      "company": "Sber",
      "event_date": "2025-11-15",
      "note": "Ключевой спикер"
    }
  ],
  "profile_tags": ["ml", "datascience", "python", "mlops"]
}
```

Ожидаемо: score = 3-4, confidence = "high", reason про активность.
