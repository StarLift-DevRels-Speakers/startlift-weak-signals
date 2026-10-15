FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_LINK_MODE=copy \
    UV_COMPILE_BYTECODE=1 \
    PATH="/app/.venv/bin:$PATH"

COPY --from=ghcr.io/astral-sh/uv:0.13.1 /uv /uvx /bin/

WORKDIR /app

# Install the locked dependency set first so it survives source-only changes.
COPY pyproject.toml uv.lock README.md ./
RUN uv sync --frozen --no-dev --no-install-project

COPY src ./src
RUN uv sync --frozen --no-dev

EXPOSE 8000

# The authorization key is supplied at run time (GIGACHAT_TOKEN); never bake it in.
CMD ["python", "-m", "signals"]

# Liveness only: the provider credentials are checked once at startup.
HEALTHCHECK --interval=30s --timeout=3s --start-period=20s --retries=3 \
    CMD ["python", "-c", "import os, urllib.request; port = os.environ.get('SIGNALS_PORT', '8000'); urllib.request.urlopen(f'http://127.0.0.1:{port}/health', timeout=2)"]
