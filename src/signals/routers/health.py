"""Liveness endpoint.

The provider credentials are already exercised once at startup, so this
endpoint answers from the process state and never calls the provider.
"""

from fastapi import APIRouter
from pydantic import BaseModel

from signals.config.gigachat_config import get_gigachat_config

router = APIRouter(tags=["health"])


class HealthResponse(BaseModel):
    status: str
    model: str


@router.get("/health", response_model=HealthResponse, summary="Service liveness")
async def get_health() -> HealthResponse:
    """Report that the service is serving and which model it will call."""
    return HealthResponse(status="ok", model=get_gigachat_config().llm_model)
