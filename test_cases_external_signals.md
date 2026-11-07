### Кейс 1: «Выдающийся талант» (ожидаемый score = 5)
```json
{
  "username": "ivan_petrov",
  "about": "Backend-разработчик с 8-летним опытом в высоконагруженных системах. Выступаю с 2022 года, специализируюсь на Kafka, DDD и оптимизации производительности.",
  "company": "Ozon",
  "company_role": "Senior Backend Engineer",
  "region": "Москва",
  "social_links_count": 8,
  "talks_total": 47,
  "profile_tags": ["kafka", "ddd", "backend", "highload", "golang", "performance"],
  "recent_talks": [
    {
      "topic": "Оптимизация Kafka в проде: от 100k до 1M msg/s",
      "talk_date": "2026-09-28T10:00:00Z"
    },
    {
      "topic": "DDD для стартапов: как не утонуть в абстракциях",
      "talk_date": "2026-08-15T14:30:00Z"
    },
    {
      "topic": "Highload на Go: практические паттерны",
      "talk_date": "2026-07-10T18:00:00Z"
    }
  ],
  "recent_feedback": [
    {
      "feedback": "Потрясающие живые примеры из продакшена, спикер держит зал 40 минут без слайдов",
      "platform_name": "Habr",
      "rating": 5,
      "conference": "HighLoad++ 2026"
    },
    {
      "feedback": "Глубокая экспертиза, отвечает на сложные вопросы на лету, но темп в середине слишком быстрый",
      "platform_name": "YouTube",
      "rating": 5,
      "conference": "HighLoad++ 2026"
    },
    {
      "feedback": "Отличная структура и применимые на практике выводы, хотелось бы больше метрик до/после",
      "platform_name": "Telegram",
      "rating": 4
    }
  ]
}
```
Ожидаемо: score = 5, confidence = "high", reason про системную публичную активность, свежие доклады на заметных площадках и сильные отзывы.

### Кейс 2: «Стабильный середняк» (ожидаемый score = 3)
```json
{
  "username": "maria_smirnova",
  "about": "Фронтенд-разработчик, 4 года опыта. Люблю React и TypeScript, иногда выступаю на митапах.",
  "company": "Yandex Cloud",
  "company_role": "Middle Frontend Developer",
  "region": "Санкт-Петербург",
  "social_links_count": 2,
  "talks_total": 9,
  "profile_tags": ["react", "typescript", "frontend"],
  "recent_talks": [
    {
      "topic": "React Server Components: что это и зачем",
      "talk_date": "2026-08-20T18:00:00Z"
    },
    {
      "topic": "TypeScript: типизация API-слоя",
      "talk_date": "2026-03-14T15:00:00Z"
    }
  ],
  "recent_feedback": [
    {
      "feedback": "Хорошая структура, понятные примеры, но читала со слайдов почти весь доклад",
      "platform_name": "Habr",
      "rating": 4,
      "conference": "Frontend Meetup SPb"
    },
    {
      "feedback": "Актуальная тема, хорошо подготовлена, но не хватило глубины",
      "platform_name": "YouTube",
      "rating": 3
    }
  ]
}
```
Ожидаемо: score = 3, confidence = "medium", reason про регулярность и устойчивую тематику без ярких сигналов.

### Кейс 3: «Новичок» (ожидаемый score = 2)
```json
{
  "username": "alex_novikov",
  "about": "Начинающий разработчик, хочу попробовать себя в публичных выступлениях.",
  "company": "Unknown",
  "company_role": "Junior Developer",
  "region": "Казань",
  "social_links_count": 1,
  "talks_total": 1,
  "profile_tags": ["docker", "junior"],
  "recent_talks": [
    {
      "topic": "Введение в Docker для джунов",
      "talk_date": "2026-02-10T18:00:00Z"
    }
  ],
  "recent_feedback": [
    {
      "feedback": "Понятно для новичков, но много воды, мало конкретики, читал с листа",
      "platform_name": "YouTube",
      "rating": 3
    }
  ]
}
```
Ожидаемо: score = 2, confidence = "medium", reason про единичный опыт и слабую обратную связь.

### Кейс 4: «Пустой профиль» (edge case, ожидаемый score = 1-2)
```json
{
  "username": "ghost_user",
  "talks_total": 0,
  "profile_tags": [],
  "recent_talks": [],
  "recent_feedback": []
}
```
Ожидаемо: score не выше 2 (кандидат без докладов), confidence = "low", reason про отсутствие публичных сигналов. Проверяет правило «talks_total = 0 и пустой recent_talks → не выше 2».

### Кейс 5: «Противоречивый» (для проверки рассуждений LLM)
```json
{
  "username": "dmitry_orlov",
  "about": "10 лет в ML, выступаю на конференциях с 2015 года. Автор курса по ML в проде.",
  "company": "Sber",
  "company_role": "Lead Data Scientist",
  "region": "Новосибирск",
  "social_links_count": 5,
  "talks_total": 35,
  "profile_tags": ["ml", "datascience", "python", "mlops"],
  "recent_talks": [
    {
      "topic": "ML в проде: как перестать бояться",
      "talk_date": "2025-11-15T10:00:00Z"
    }
  ],
  "recent_feedback": [
    {
      "feedback": "Глубокий опыт, отличные кейсы, но тема уже была в прошлом году",
      "platform_name": "Habr",
      "rating": 5,
      "conference": "AI Journey 2025"
    },
    {
      "feedback": "Мало нового материала, узнал немного",
      "platform_name": "Telegram",
      "rating": 3
    }
  ]
}
```
Ожидаемо: score = 3-4, confidence = "medium", reason про большой накопленный объём, но единственный доклад почти год назад и неоднородные отзывы.

### Кейс 6: «Завышенный talks_total и отзывы без рейтинга» (ожидаемый score = 3)
```json
{
  "username": "olga_kuznetsova",
  "about": "Продакт-менеджер в финтехе, рассказываю про продуктовые исследования.",
  "company": "Tinkoff",
  "company_role": "Senior Product Manager",
  "region": "Екатеринбург",
  "social_links_count": 0,
  "talks_total": 25,
  "profile_tags": ["product", "ux", "research"],
  "recent_talks": [
    {
      "topic": "Как перестать делать исследования в стол",
      "talk_date": "2026-06-05T17:00:00Z"
    },
    {
      "topic": "Продуктовые метрики для исследователя",
      "talk_date": "2025-12-12T18:00:00Z"
    }
  ],
  "recent_feedback": [
    {
      "feedback": "Живые примеры и понятная структура, спикер отвечает на вопросы по делу",
      "platform_name": "Habr"
    },
    {
      "feedback": "Интересно, но часть слайдов устарела и в конце скомкала выводы",
      "platform_name": "Telegram",
      "conference": "ProductSense"
    }
  ]
}
```
Ожидаемо: score = 3, confidence = "medium" или "low", reason не должен опираться на talks_total = 25 как на факт: видно только два доклада и отзывы без оценки. Проверяет недоверие к приблизительному агрегату и необязательность `rating`/`conference`.

## Кейсы валидации (ожидаем HTTP 422, LLM не вызывается)

### Невалидный кейс 1: rating вне диапазона 1..5
```json
{
  "username": "bad_rating_low",
  "talks_total": 1,
  "profile_tags": ["backend"],
  "recent_talks": [],
  "recent_feedback": [
    {"feedback": "Текст отзыва", "platform_name": "Habr", "rating": 0}
  ]
}
```

### Невалидный кейс 2: rating вне диапазона 1..5
```json
{
  "username": "bad_rating_high",
  "talks_total": 1,
  "profile_tags": ["backend"],
  "recent_talks": [],
  "recent_feedback": [
    {"feedback": "Текст отзыва", "platform_name": "Habr", "rating": 6}
  ]
}
```

### Невалидный кейс 3: отсутствует обязательный username
```json
{
  "talks_total": 2,
  "profile_tags": ["backend"],
  "recent_talks": [],
  "recent_feedback": []
}
```

### Невалидный кейс 4: отсутствует обязательный recent_talks
```json
{
  "username": "no_talks_field",
  "talks_total": 2,
  "profile_tags": ["backend"],
  "recent_feedback": []
}
```
