# AGENTS.md

## Role
You are a Python developer for this project. Reply briefly, focus on technical substance.

## Communication
- **Always respond to the user in Russian.**
- Write all artifacts in English: source code, identifiers, docstrings, comments, prompts, logs, commit messages, and every file in the repository, including this one and `README.md`.
- Be concise. No filler words. No greetings, no closing remarks.
- Code examples over long explanations.

## Project Overview
`signals` is a microservice of a conference-speaker-search product. The weak-signals block finds promising speakers. 

## Architecture
It is a stateless HTTP endpoint with a layered architecture and no repository/persistence layer: request in, LLM scoring out.
Stack: FastAPI + an LLM client (GigaChat or DeepSeek, selected by env). Packaged in Docker; later it becomes one service of a larger docker compose.

## Project Layout
The project is a `src`-layout package.

- `src/signals/__main__.py` — process entry point: builds the FastAPI app, runs the startup model
  listing, and serves it.
- `src/signals/routers/` — API layer. One router per feature.
  - `routers/signals.py` — weak-signals endpoint.
  - `routers/health.py` — liveness endpoint.
- `src/signals/services/` — business logic. All LLM calls live here.
  - `services/signals.py` — scoring orchestration.
  - `services/llm_services/` — prompts (`system_prompt.py`, `user_prompt.py`) and the GigaChat
    client factory (`gigachat_client.py`).
- `src/signals/config/` — settings loaded from env vars, one module per concern:
  `base_config.py` (`BaseConfig`), `gigachat_config.py` (`GigaChatConfig`, `get_gigachat_config()`),
  `app_config.py` (`AppConfig`, `get_app_config()`). Each config module exposes a cached getter; do
  not instantiate settings at import time, because the token is required and would break imports.
- `src/signals/schemas/` — Pydantic request/response models.
  - `schemas/signals.py` — `TalentRequest`, `TalentLLMResponse`, `TalentResponse`, `Influence`;
    fixed inputs, do not change without an explicit request.
- `tests/` — pytest suite, offline: fakes replace the LLM, no token or network needed.
- `pyproject.toml`, `uv.lock` — project metadata and locked deps (`uv_build` backend, distribution
  `signals`).

**Rule:** routers parse and validate the request, then call a service. Logic stays in services. Schemas are data only.

## Tech Stack

- Python: `>=3.11` in `pyproject.toml`, `.python-version` pins `3.11`; the Docker image uses 3.12.
- Package manager: `uv`.
- FastAPI + Uvicorn, bind address from `SIGNALS_HOST` / `SIGNALS_PORT` (defaults `0.0.0.0:8000`).
- LLM client: `langchain-gigachat` wrapping `gigachat`; the scoring model is `GigaChat-3-Ultra` and
  the token comes from `GIGACHAT_TOKEN`. DeepSeek is mentioned as an option in the product plan but
  is not implemented.
- `dependencies` in `pyproject.toml` holds fastapi, uvicorn, pydantic-settings, and
  langchain-gigachat. Do not assume an import works because it is mentioned in this file; check
  `pyproject.toml`.

## Commands

Single entry point, identical locally and in the container. There is no autoreload: restart the server manually after edits.

Canonical command and the agent-environment equivalent:

| Canonical | In the agent environment |
|---|---|
| `python -m signals` | `.\.venv\Scripts\python.exe -m signals` (from the repo root) |
| `uv run pytest -v` | `.\.venv\Scripts\python.exe -m pytest -v` |
| `uv run ruff check .` | `.\.venv\Scripts\python.exe -m ruff check .` |
| `uv add <package>` | `.\.venv\Scripts\uv.exe add <package>` |

Notes:
- `pytest` and `ruff` are installed as dev dependencies; `uv run ruff …` / `uv run pytest …` work.
- Run commands from the repository root. Sources live under `src/`, so `src` must be importable (editable install via `uv sync`).
- `uv` needs a writable cache: if `uv add` fails with `Could not acquire lock` on the user-level
  cache, set `UV_CACHE_DIR=.uv-cache` for the command.

## Docker

`Dockerfile` installs the locked dependency set with `uv sync --frozen` and runs `python -m signals`.
The GigaChat token is supplied at run time (`GIGACHAT_TOKEN`) and is never baked into the image.
Docker is not available in the agent environment, so image builds are verified by the user.

## Code Style — Zen of Python
Apply these when writing or reviewing code:
- Beautiful is better than ugly.
- Explicit is better than implicit.
- Simple is better than complex.
- Readability counts.
- Errors should never pass silently.

Typing: annotate all public functions and models; prefer `str | None` over `Optional[str]`. Comments must be brief.

## Architecture Assessment (Before Any Change)
Before modifying code, evaluate architecture fit:

1. **Does this change fit the current architecture?** If yes, proceed.
2. **If no, can the architecture adapt slightly?** A small refactor is OK. State what and why.
3. **If a large architectural change is needed,** stop and ask the user first.

**Do not** silently reshape the architecture for one feature. State the assessment, propose the minimal change, then implement.
