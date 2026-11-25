# syntax=docker/dockerfile:1

# Both stages must use the same Python version and distribution for venv portability.
FROM python:3.12-slim-bookworm AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/app/.venv/bin:$PATH"

WORKDIR /app

FROM base AS build
ENV UV_LINK_MODE=copy \
    UV_PYTHON_DOWNLOADS=never

COPY --from=ghcr.io/astral-sh/uv:0.13.1 /uv /bin/uv

# Install the locked dependency set first so it survives source-only changes.
COPY pyproject.toml uv.lock README.md ./
RUN --mount=type=cache,id=starlift-uv,target=/root/.cache/uv,sharing=locked \
    uv sync --frozen --no-dev --no-install-project

COPY src ./src
RUN --mount=type=cache,id=starlift-uv,target=/root/.cache/uv,sharing=locked \
    uv sync --frozen --no-dev --no-editable

FROM base AS runtime
RUN groupadd --system --gid 10001 appuser \
    && useradd --system --uid 10001 --gid appuser --home-dir /app --shell /usr/sbin/nologin appuser

# The wheel installation includes signals; source, uv and its cache stay in build.
COPY --from=build /app/.venv /app/.venv
USER appuser

EXPOSE 8000

# The authorization key is supplied at run time (GIGACHAT_TOKEN); never bake it in.
CMD ["python", "-m", "signals"]

# Liveness only: the provider credentials are checked once at startup.
HEALTHCHECK --interval=30s --timeout=3s --start-period=20s --retries=3 \
    CMD ["python", "-c", "import os, urllib.request; port = os.environ.get('SIGNALS_PORT', '8000'); urllib.request.urlopen(f'http://127.0.0.1:{port}/health', timeout=2)"]
