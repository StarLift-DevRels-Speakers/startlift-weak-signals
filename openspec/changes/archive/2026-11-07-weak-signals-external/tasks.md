# Tasks

## 1. Внешние схемы

- [x] 1.1 Создать `src/signals/schemas/external.py`: `ExternalFeedbackItem` (`feedback` и
  `platform_name` обязательны; `rating` 1-5 и `conference` необязательны), `ExternalTalkItem`
  (`topic`, `talk_date`), `ExternalTalentRequest` (`username`, `talks_total`, `profile_tags`,
  `recent_talks`, `recent_feedback` обязательны; `about`, `company`, `company_role`, `region`
  необязательны; `social_links_count` по умолчанию 0) и `ExternalTalentResponse` (`username`,
  `score` 1-5, `reason` 1-500, `confidence`), с аннотациями и `str | None`. Проверка: импортировать
  модуль и провалидировать пример payload из спеки.
- [x] 1.2 Добавить `tests/test_external_schemas.py`: минимальный payload с пустыми списками
  докладов и отзывов, отсутствие необязательных полей, отклонение rating 0 и 6, отклонение
  отсутствующих `username`, `talks_total`, `recent_talks` и `recent_feedback`, отсутствие поля
  идентификатора в модели ответа. Проверка: `pytest tests/test_external_schemas.py -v`.

## 2. Внешние промпты

- [x] 2.1 Создать `src/signals/services/llm_services/external_system_prompt.py` с русской константой
  `EXTERNAL_SYSTEM_PROMPT`: шкала 1-5 на публичных сигналах, отсутствие отзывов снижает уверенность,
  а не оценку, кандидат без докладов ограничен оценкой 2, формат ответа JSON. Проверка: модуль
  импортируется без токена, константа содержит шкалу, ограничение для кандидата без докладов и
  формат ответа.
- [x] 2.2 Создать `src/signals/services/llm_services/external_user_prompt.py` с
  `build_external_prompt`, который выводит идентичность, публичную активность, темы, последние
  доклады и последние отзывы, а для пустых необязательных секций пишет явный маркер отсутствия.
  Проверка: сборщик возвращает текст для полностью скудного запроса и не падает.
- [x] 2.3 Добавить `make_external_request` и фикстуру `external_candidate` в `tests/conftest.py`.
  Проверка: существующая фикстура `speaker` и все текущие тесты по-прежнему проходят.
- [x] 2.4 Добавить `tests/test_external_user_prompt.py`: все секции, заполненные значения включая
  количество ссылок и рейтинг отзыва, маркеры отсутствия для скудного кандидата. Проверка:
  `pytest tests/test_external_user_prompt.py -v`.

## 3. Сервис внешней оценки

- [x] 3.1 Создать `src/signals/services/external_signals.py`: `ExternalSignalsService` (внедряемые
  runnable и таймаут, `asyncio.wait_for`, перенос username в `ExternalTalentResponse`) и
  `get_external_signals_service()`, переиспользуя `get_structured_scoring_runnable`,
  `get_provider_timeout`, `parse_scoring_answer` и `ScoreUnavailableError` без правок этих модулей.
  Проверка: модуль импортируется при отсутствии токена в окружении.
- [x] 3.2 Добавить `tests/test_external_signals_service.py` с фейковым runnable: username в ответе
  совпадает с запросом; отправленные сообщения — `EXTERNAL_SYSTEM_PROMPT`, затем построенный промпт;
  сырой mapping принимается; ошибка провайдера и ответ вне диапазона дают `ScoreUnavailableError`;
  медленный провайдер даёт `TimeoutError`; dependency-функция собирает сервис с положительным
  таймаутом. Проверка: `pytest tests/test_external_signals_service.py -v`.

## 4. Внешний эндпоинт и документация

- [x] 4.1 Создать `src/signals/routers/external.py` с `APIRouter(prefix="/signals",
  tags=["external"])` и `POST /weak-signals-external`, указать модель ответа и маппинг:
  `ScoreUnavailableError` → 502, `TimeoutError` → 504, прочее → 500, с логированием по username
  кандидата. Проверка: роутер импортируется, путь маршрута — `/signals/weak-signals-external`.
- [x] 4.2 Подключить роутер в `src/signals/__main__.py`. Проверка: запрос `TestClient` к
  `/openapi.json` показывает и `/signals/weak-signals-external`, и `/signals/weak-signals`.
- [x] 4.3 Добавить `tests/test_external_router.py` с override зависимости: 200 с формой оценки, 422
  на невалидном payload без вызова фейкового runnable, 502 на непригодном ответе, 504 на таймауте,
  500 на неожиданной ошибке, отсутствие идентификатора в теле ответа. Проверка:
  `pytest tests/test_external_router.py -v`.
- [x] 4.4 Создать каталог `docs/` и в нём `docs/API.md` на русском: `GET /health`,
  `POST /signals/weak-signals` и `POST /signals/weak-signals-external` — назначение, таблицы полей
  запроса с признаком обязательности и типами, формы вложенных объектов, примеры запросов и ответов,
  общая таблица ошибок. Проверка: сверить поле за полем таблицы с моделями Pydantic и провалидировать
  оба примера JSON против соответствующих моделей.
- [x] 4.5 Добавить строку о новом эндпоинте в таблицу эндпоинтов `README.md`. Проверка: `README.md`
  и `docs/API.md` совпадают по пути и кодам ошибок.

## 5. Интеграционная проверка

- [x] 5.1 Запустить `.\.venv\Scripts\python.exe -m pytest -v` и убедиться, что проходит весь набор,
  включая существующие тесты внутреннего эндпоинта.
- [x] 5.2 Запустить `.\.venv\Scripts\python.exe -m ruff check .` и убедиться в отсутствии замечаний.
- [x] 5.3 Убедиться через `git diff --name-only`, что `schemas/signals.py`, `services/signals.py`,
  `routers/signals.py`, `system_prompt.py` и `user_prompt.py` не изменены.

## Workflow follow-up

- Архивировать change после ревью артефактов и реализации.
