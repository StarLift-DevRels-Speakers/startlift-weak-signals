"""Process entry point: build the FastAPI app and serve it."""

import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI

from signals.config.app_config import get_app_config
from signals.config.gigachat_config import get_gigachat_config
from signals.routers.health import router as health_router
from signals.routers.signals import router as signals_router
from signals.services.llm_services.gigachat_client import get_gigachat_client

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """List the models available to the configured token before serving."""
    config = get_gigachat_config()
    logger.info("Scoring model: %s", config.llm_model)

    models = await get_gigachat_client().aget_models()
    model_ids = [model.id_ for model in models.data]
    logger.info("GigaChat models available to this token: %s", ", ".join(model_ids))

    yield


app = FastAPI(title="signals", version="0.1.0", lifespan=lifespan)
app.include_router(health_router)
app.include_router(signals_router)


def main() -> None:
    """Serve the API with uvicorn."""
    # Without root handlers the application loggers emit nothing, which hides
    # startup problems such as a rejected token. Configure them before serving.
    logging.basicConfig(
        level=logging.INFO,
        format="%(levelname)s %(name)s: %(message)s",
    )
    config = get_app_config()
    uvicorn.run(app, host=config.host, port=config.port)


if __name__ == "__main__":
    main()
