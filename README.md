# signals

Microservice of a conference-speaker-search product. The weak-signals block scores a speaker from
secondary signals and returns a talent score.

Stateless HTTP endpoint: request in, LLM scoring out. No persistence.

## Endpoints

| Method | Path | Purpose |
|---|---|---|
| `POST` | `/signals/weak-signals` | Score one speaker |
| `GET` | `/health` | Liveness and the configured scoring model |

`POST /signals/weak-signals` takes one speaker with numeric features and free-text context, and
returns the score for that speaker:

```json
{
  "id": 42,
  "score": 4,
  "reason": "Regular speaker with strong recent feedback and visible growth.",
  "confidence": "high"
}
```

`score` is an integer from 1 to 5, `confidence` is `low`, `medium`, or `high`, and `id` is copied
from the request. Failures are reported as `502` when the provider answer is unusable, `504` on a
provider timeout, and `500` for an unexpected internal error. Provider messages, tokens, and stack
traces are never returned.

## Configuration

Copy the sample and fill in the token:

```bash
cp .env.example .env
```

| Variable | Default | Required | Purpose |
|---|---|---|---|
| `GIGACHAT_TOKEN` | — | yes | Long-lived GigaChat authorization key. The service does not start without it |
| `GIGACHAT_ULTRA_BASE_URL` | `https://api.giga.chat/v1` | no | Endpoint for ultra models |
| `GIGACHAT_ULTRA_SCOPE` | `GIGACHAT_API_PERS` | no | Authorization scope |
| `GIGACHAT_LLM_MODEL` | `GigaChat-3-Ultra` | no | Model used for scoring |
| `GIGACHAT_LLM_TEMPERATURE` | `0.1` | no | Sampling temperature |
| `GIGACHAT_LLM_MAX_TOKENS` | `5000` | no | Response token limit |
| `GIGACHAT_VERIFY_SSL_CERTS` | `false` | no | TLS certificate verification. Disabled as a development default; re-enable outside development |
| `GIGACHAT_TIMEOUT` | `60.0` | no | Provider request timeout, seconds |
| `SIGNALS_HOST` | `0.0.0.0` | no | Interface the server binds to |
| `SIGNALS_PORT` | `8000` | no | Port the server listens on |

The legacy names `GIGACHAT_COLLECT_FORM_MODEL`, `GIGACHAT_COLLECT_FORM_TEMPERATURE`, and
`GIGACHAT_COLLECT_FORM_MAX_TOKENS` are still accepted for the three prompt settings.

A local `.env` file in the working directory is read automatically. The token is held as a secret
and never written to logs; keep `.env` out of version control.

`GIGACHAT_TOKEN` is an authorization key, not a pre-obtained access token: the SDK exchanges it for
an access token at `ngw.devices.sberbank.ru:9443/api/v2/oauth` and refreshes it on its own. The key
itself is long-lived and never rotated by the service. If it is revoked, startup fails and the
service stops serving.

## Run

```bash
uv sync
uv run python -m signals
```

The server binds to `SIGNALS_HOST:SIGNALS_PORT` (`0.0.0.0:8000` by default). Startup logs the scoring
model and every model available to the token; a failing model-list request aborts startup, so a
rejected key is visible before the first scoring request.

## Test

```bash
uv run pytest -v
uv run ruff check .
```

The suite is offline: the LLM is replaced by fakes, and no test needs a token or network access.

## Docker

```bash
docker build -t signals .
docker run --rm -p 8000:8000 --env-file .env signals
```

The image installs the locked dependency set and runs `python -m signals`. The authorization key is
supplied at run time and is never baked into the image: `.env` is excluded from the build context, so
pass it with `--env-file .env` or `-e GIGACHAT_TOKEN=<key>`. The image declares a healthcheck that
polls `GET /health` on `SIGNALS_PORT`.

## Deployment

The stand runs the service next to `starlift-backend` with `docker compose`. The service joins the
backend's bridge network `java-speaker-net` under the alias `signals`, so the backend reaches it at
`http://signals:8000` (`WEAK_SIGNALS_BASE_URL`). The port is also published on `127.0.0.1:8000` of the
host for debugging. Deploy the backend first: its compose project creates the network.

```bash
docker compose up -d --build
```

On push to `main` the workflow `.github/workflows/deploy.yml` deploys on the self-hosted runner. The
checkout deletes untracked files, so the settings live on the stand outside the runner's work folder,
in `~/starlift/env/weak-signals.env` (same keys as `.env.example`); the workflow copies it to `.env`
before starting the container.
