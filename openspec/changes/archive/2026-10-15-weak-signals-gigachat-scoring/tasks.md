# Tasks

## 1. Dependencies and test setup

- [x] 1.1 Add `pydantic-settings` and `langchain-gigachat` to `[project].dependencies` in `pyproject.toml`; verify with `uv sync` that the lock resolves and `.\.venv\Scripts\python.exe -c "import pydantic_settings, langchain_gigachat"` succeeds
- [x] 1.2 Add `pytest` and `ruff` as dev dependencies; verify `.\.venv\Scripts\python.exe -m pytest --version` and `.\.venv\Scripts\python.exe -m ruff --version` both report a version
- [x] 1.3 Configure pytest in `pyproject.toml` (test path `tests/`, and the asyncio mode the service tests need); verify a placeholder test is collected and reported as passed, then remove the placeholder

## 2. Settings layer

- [x] 2.1 Implement `BaseConfig` in `src/signals/config/base_config.py` as the shared pydantic-settings base (environment source, ignore unknown variables); verify a test subclass reads a value from the environment
- [x] 2.2 Rewrite `src/signals/config/gigachat_config.py`: token read from `GIGACHAT_TOKEN` (no alias workaround needed any more), `ultra_base_url`, `ultra_scope`, `llm_model` defaulting to `GigaChat-3-Ultra`, `llm_temperature` 0.1, `llm_max_tokens` 5000, `verify_ssl_certs` defaulting to `False`, and legacy aliases `GIGACHAT_COLLECT_FORM_MODEL` / `_TEMPERATURE` / `_MAX_TOKENS` still accepted; fix the copy-pasted field descriptions; verify a test asserts defaults with an empty environment and asserts each override, including one legacy alias
- [x] 2.3 Verify that a missing `GIGACHAT_TOKEN` raises a settings validation error rather than defaulting to an empty secret, via a test that clears the variable
- [x] 2.4 Implement `AppConfig` in `src/signals/config/app_config.py` for host and port under the `SIGNALS_` prefix, defaults `0.0.0.0` and `8000`; verify a test asserts defaults and one override

## 3. Fix the prompt module import

- [x] 3.1 Replace the broken `app.schemas.signals` import in `src/signals/services/llm_services/user_prompt.py` with the project path, leaving the prompt text untouched; verify `.\.venv\Scripts\python.exe -c "from signals.services.llm_services.user_prompt import build_prompt"` succeeds
- [x] 3.2 Add tests for `build_prompt` covering a fully populated speaker and a speaker with empty optional lists; verify the rendered text contains the profile, activity, quality, achievements, demand, talks, feedback, and mentions sections and that empty lists render as the absence marker

## 4. GigaChat client factory

- [x] 4.1 Implement the client factory in `src/signals/services/llm_services/gigachat_client.py`: build one client from settings (model, temperature, max_tokens, base URL, scope, TLS verification, token as `credentials`) and expose it as a process-wide singleton; verify a test builds the client from overridden settings and asserts the resulting attributes match them, with no network access
- [x] 4.2 Expose the structured-output runnable built from the client and `TalentLLMResponse`, plus the provider timeout used by the service; verify a test asserts the runnable is constructed from the expected schema without invoking it

## 5. Scoring service

- [x] 5.1 Implement `SignalsService.score_talent` in `src/signals/services/signals.py`: build the system and user messages from the fixed prompts, invoke the structured-output runnable under the timeout, and return `TalentResponse` carrying the request id; verify a test with a fake runnable returns the id, score, reason, and confidence from the model answer
- [x] 5.2 Map provider and parsing failures to `ScoreUnavailableError` and leave the timeout as `TimeoutError`; verify tests with a fake runnable that raises on the provider call and one that returns unparseable output both produce `ScoreUnavailableError`, and that a slow fake produces `TimeoutError`
- [x] 5.3 Make the FastAPI dependency provide a service wired to the configured runnable; verify a test resolves the dependency and that `pyproject`-installed imports are used (no network call required at import time)

## 6. Health endpoint and startup model listing

- [x] 6.1 Add `GET /health` in `src/signals/routers/health.py` returning liveness and the configured model name, without calling the provider; verify a router test (or `TestClient`) asserts HTTP 200 and the model name in the body
- [x] 6.2 Wire the health router and a FastAPI lifespan into `src/signals/__main__.py`: on startup call `aget_models()` on the configured client, log the returned model ids, and let a failing call abort startup; verify a test with a fake client asserts the ids are logged, that a missing configured model still starts the app, and that a raising fake prevents startup
- [x] 6.3 Serve with the host and port from `AppConfig` instead of hardcoded values; verify the values are read from the settings instance

## 7. Integration verification and documentation

- [x] 7.1 Run `.\.venv\Scripts\python.exe -m pytest -v` and `.\.venv\Scripts\python.exe -m ruff check .`; verify both pass with no failures
- [x] 7.2 Smoke-test the real provider: start the service with a real `GIGACHAT_TOKEN`, confirm the startup log lists the models, and post one realistic `TalentRequest`; verify the response is a 200 with the request id and a score from 1 to 5, and record which client argument (`credentials` or `access_token`) was required
- [x] 7.3 Rewrite `Dockerfile` to install from the existing `pyproject.toml` with `uv sync`, copy `src/`, and run `python -m signals`; verify the image builds and, started with the token supplied at run time, answers `GET /health` with 200
- [x] 7.4 Document in `README.md`: the endpoint contract, the `GIGACHAT_*` and `SIGNALS_*` variables with `GIGACHAT_TOKEN` as the only required one, the local run command, the token's long-lived nature, and that TLS verification is disabled by default; verify each environment variable named in the README exists in the settings modules

## Workflow follow-up

- Archive the change once the smoke test and review requirements are satisfied.
