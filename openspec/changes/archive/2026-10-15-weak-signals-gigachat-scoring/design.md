# Design

## Context

See `proposal.md` for motivation. Current state that shapes the approach:

- `schemas/signals.py` is complete and is a fixed input: `TalentRequest` (profile, numeric features,
  free-text lists), `TalentLLMResponse` (`score` 1-5, `reason` 1-500 chars, `confidence` literal),
  `TalentResponse` (the LLM shape plus `id`).
- `services/llm_services/system_prompt.py` holds `SYSTEM_PROMPT` and
  `services/llm_services/user_prompt.py` holds `build_prompt(speaker)`; both are fixed and their text
  must not change. `user_prompt.py` currently imports `app.schemas.signals`, a path that does not
  exist in this repository, so it cannot be imported at all.
- `services/signals.py` defines `ScoreUnavailableError` and a stub `score_talent`; the router already
  maps `ScoreUnavailableError` to 502, `TimeoutError` to 504, and anything else to 500, so the
  failure contract is already declared at the API boundary.
- `config/gigachat_config.py` is a draft that cannot be imported: it subclasses a missing
  `BaseConfig` and needs `pydantic-settings`, which is not a dependency.
- `pyproject.toml` declares only `fastapi` and `uvicorn`; no LLM client, no test tooling.
- `Dockerfile` is scaffolding from another project and cannot build this package.
- The repository has no OpenSpec specs yet and no tests.

## Goals / Non-Goals

**Goals:**

- Make `POST /signals/weak-signals` return a real score with a minimal, layered implementation that
  honours the existing router and schema contracts.
- Keep the configuration surface explicit: one required secret, everything else defaulted.
- Keep the LLM exchange testable without network access or credentials.

**Non-Goals:**

- No retries, no LangChain callbacks, no request/trace propagation, no prompt caching.
- No second provider; the provider is chosen by a dedicated config module, not a provider switch.
- No change to the prompt text, the schema module, or the router's error mapping.
- No model validation against the catalogue returned at startup.
- No batch scoring, no persistence, no authentication on the endpoints.

## Decisions

### Structured output on the LangChain wrapper

Use `GigaChat(...).with_structured_output(<scoring function schema>)` in its default
`function_calling` mode, and pass the returned runnable as the single LLM dependency of the service.

- `TalentLLMResponse` already is exactly the shape the system prompt demands, so the schema doubles
  as the structured-output contract; no second model is introduced, and the prompt stays untouched.
- The installed `langchain-gigachat` 0.5.1 rejects a schema without a non-empty description, and
  `TalentLLMResponse` carries none. Since the schema module is a fixed input, the factory describes
  the function itself and passes the model's own JSON schema as its parameters, then validates the
  returned mapping back into `TalentLLMResponse`. The alternative — adding a docstring to the schema
  module — was rejected because that module is fixed by the user.
- The `method="json_schema"` alternative (native `response_format`, `strict=True`) is documented as
  beta and model-dependent. It is the fallback if the model rejects function calling, but it is not
  the default because a rejected request would surface as a scoring outage.
- `include_raw=True` was considered so that a parsing failure could be told apart from a transport
  failure; not used, because the router already collapses both into 502 and the extra structure has
  no consumer yet.

### Credentials are passed as `credentials`

The token from configuration is passed to the client as `credentials`. The provider SDK documents
`credentials` as an authorization key and `access_token` as a pre-obtained token; the reference
project passes the token through `credentials`, and the ultra example does the same. The configured
value is base64 authorization data, so this argument is the correct one: the SDK exchanges it for an
access token at `ngw.devices.sberbank.ru:9443/api/v2/oauth` (observed HTTP 200) and refreshes it on
its own.

A wrong-format value fails before any API call and surfaces as `BadRequestError: Can't decode
'Authorization' header`, which is how the earlier dummy-token probe behaved. A pre-obtained JWT
would instead need `access_token`; nothing else in the factory changes.

### Token validation at startup by listing models

At startup the application calls `aget_models()` on the scoring client and logs the returned model
identifiers, then serves. No comparison against the configured model and no branching on the result.

- This surfaces an invalid or expired key or an unreachable provider before the first scoring
  request, which is the failure mode that would otherwise stay invisible.
- Logging without validating matches the intended behaviour: the catalogue is informational, so an
  unusual or missing model name does not block startup.
- The application loggers have no handlers when uvicorn starts the app, so the entry point calls
  `logging.basicConfig` before `uvicorn.run`. Without it the model list, the scoring model, and the
  provider-failure warnings were all emitted into a void — this was observed during live testing,
  where `aget_models()` succeeded but printed nothing.
- `aget_models()` depends on neither the configured model nor the ultra scope: a probe with the
  scoring client and with a scopeless base-model client returned the same catalogue. No second
  client is needed for discovery.

### Single client behind a cached factory

A thin factory builds the client once from settings and returns the same instance for the process
lifetime. `GigaChat` holds a connection pool and a token lifecycle, so rebuilding it per request
would add an OAuth round trip per call. The service receives the resulting runnable through its
constructor, which keeps the FastAPI dependency overridable in tests. With one provider in the
project, the factory is a module function rather than a registry or provider abstraction.

### Timeout and failure mapping

Two layers, with the outer layer owning the HTTP contract:

- The client is configured with the provider request timeout from settings.
- The service wraps the LLM call in `asyncio.wait_for` with the same budget and lets `TimeoutError`
  propagate; the router already maps it to 504.
- Provider errors and structured-output parsing failures are converted into `ScoreUnavailableError`
  in the service, producing 502.
- Anything else propagates and becomes 500. Provider messages are logged, never returned.

### Settings layering

`BaseConfig` is a shared `BaseSettings` subclass; `GigaChatConfig` reads the `GIGACHAT_` prefix with
an alias for the token field, and `AppConfig` reads the `SIGNALS_` prefix. Each module exposes one
module-level settings instance. The prompt-related legacy field names from the reference project
(`collect_form_model`, `collect_form_temperature`, `collect_form_max_tokens`) are honoured as field
aliases so an existing `.env` keeps working.

## Risks / Trade-offs

- [`credentials` does not accept a pre-obtained access token] → confirmed during implementation: the
  SDK requires base64 authorization data on that argument and sends it to the OAuth endpoint, so a
  JWT must go through `access_token`. The factory keeps one auth argument, and which one it is is
  settled by the live smoke test before this change is archived.
- [The token is long-lived and never refreshed, so revocation or expiry appears as a startup failure
  or a 502] → accepted; startup listing makes the condition explicit and the README records it.
- [Certificate verification is disabled by configuration] → tracked as an explicit setting rather
  than hardcoded in the factory, so it can be re-enabled for a shared environment without a code
  change; the README states that it is a development default.
- [`TalentLLMResponse` carries no field descriptions, so function-calling mode sends only field names
  and types to the model] → the fixed system prompt defines all semantics and the fixed user message
  repeats the requested JSON shape; the schema is a documented fixed input, so this is accepted and
  re-checked on the first live response.
- [`max_tokens = 5000` is far above the expected answer size] → it removes truncation as a failure
  mode at the cost of a higher provider-side ceiling; no truncation is expected for this output.
- [The configured model name is never verified against the catalogue] → a typo surfaces as a provider
  error on the first scoring request; the startup log prints the catalogue next to the configured
  name, which makes the mismatch visible.
- [The repository has no test tooling, so this change introduces the first pytest setup] → keep the
  suite to three focused modules, driven by a fake LLM, so it stays fast and offline.

## Migration Plan

- Deploy: add `GIGACHAT_TOKEN` to the environment (a local `.env` is read through the settings
  layer), install the new dependencies, start the process with `python -m signals`.
- Rollback: the endpoint is new behaviour with no persisted state; reverting the commit restores the
  stub, and removing the token from the environment is sufficient to stop provider usage.
- Container: the image is rebuilt from the existing `pyproject.toml`; the token is supplied at run
  time and is never baked into the image. The README documents the expected `SIGNALS_` and
  `GIGACHAT_` variables.

## Open Questions

None. The only deferrable detail is whether `credentials` alone is sufficient for the pre-obtained
token, and it is verified by a live request during implementation rather than left open.
