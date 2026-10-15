# Proposal

## Why

The weak-signals endpoint is declared but not functional: `SignalsService.score_talent` raises
`NotImplementedError`, the GigaChat settings module is a draft that does not even import (no
`pydantic-settings` dependency, token env var named `GIGA_TOKEN`), the LLM client is absent, and the
user prompt module imports `app.schemas.signals`, a path that does not exist in this repository. The
request/response schemas and both prompts are already written and are treated as fixed inputs.

## What Changes

- Implement speaker scoring through GigaChat Ultra: build the system and user messages from the
  existing prompts, request structured output with `with_structured_output(TalentLLMResponse)`, and
  return `TalentResponse` to the router.
- Complete the settings layer: `BaseConfig` base class, `GigaChatConfig` (token from
  `GIGACHAT_TOKEN`, model `GigaChat-3-Ultra`, `base_url`, `scope`, `verify_ssl_certs=False`,
  `max_tokens=5000`, temperature `0.1`), and `AppConfig` for uvicorn host and port.
- Add a thin GigaChat client factory (a single client, built from settings, passed into the service).
- Fix the broken import in the user prompt module so `build_prompt` is importable; the prompt text
  itself and the system prompt stay byte-for-byte unchanged.
- On application startup, call `aget_models()` and log the returned model list. No validation of the
  configured model against that list, and no failure when the call succeeds but the model is absent.
- Add `GET /health`.
- Add runtime dependencies (`pydantic-settings`, `langchain-gigachat`) and dev dependencies
  (`pytest`, `ruff`), plus minimal tests: prompt building, service behavior with a fake structured
  LLM, and the endpoint with an overridden dependency.
- Fix `Dockerfile` so it installs from the existing `pyproject.toml` and runs `python -m signals`,
  and document the resulting service in `README.md`.

Out of scope: retries, LangChain callbacks, request tracing, additional LLM providers, changes to
`system_prompt.py`, changes to the prompt text in `user_prompt.py`, and changes to
`schemas/signals.py`.

## Capabilities

### New Capabilities

- `weak-signals-scoring`: scoring one speaker from weak signals — request contract, LLM structured
  output usage, response contract, and failure mapping to HTTP status codes.
- `service-health`: liveness endpoint exposing application and configured-model status.
- `llm-configuration`: environment-driven settings for the GigaChat client and the HTTP server, plus
  the startup model listing.

### Modified Capabilities

None. The repository has no existing specs.

## Impact

- Code: `src/signals/config/` (`base_config.py`, `gigachat_config.py`, `app_config.py`),
  `src/signals/services/` (`signals.py`, `llm_services/`), `src/signals/routers/` (`health.py`),
  `src/signals/__main__.py`, `src/signals/services/llm_services/user_prompt.py` (import only),
  new `tests/`.
- API: `POST /signals/weak-signals` becomes functional; `GET /health` is added. Request and response
  shapes are unchanged from `schemas/signals.py`.
- Dependencies: `pydantic-settings`, `langchain-gigachat` (pulls `gigachat` and `langchain-core`);
  dev: `pytest`, `ruff`.
- Configuration: the GigaChat token env var becomes `GIGACHAT_TOKEN`; all other GigaChat settings use
  the `GIGACHAT_` prefix and server settings use the `SIGNALS_` prefix.
- Infrastructure: `Dockerfile` is rewritten; `README.md` gains run, configuration, and endpoint
  documentation.
