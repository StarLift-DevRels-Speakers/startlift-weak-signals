"""External-candidate endpoint: parse the request, delegate to ExternalSignalsService."""

import logging
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from signals.schemas.external import ExternalTalentRequest, ExternalTalentResponse
from signals.services.external_signals import (
    ExternalSignalsService,
    get_external_signals_service,
)
from signals.services.signals import ScoreUnavailableError

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/signals", tags=["external"])


@router.post(
    "/weak-signals-external",
    response_model=ExternalTalentResponse,
    summary="Score one external candidate from public signals",
)
async def get_weak_signals_external(
    payload: ExternalTalentRequest,
    service: Annotated[ExternalSignalsService, Depends(get_external_signals_service)],
) -> ExternalTalentResponse:
    """Return the talent score for one external speaker candidate."""
    try:
        return await service.score_candidate(payload)
    except ScoreUnavailableError as exc:
        logger.warning("Scoring unavailable for %s: %s", payload.username, exc)
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Scoring provider unavailable",
        ) from exc
    except TimeoutError as exc:
        logger.warning("Scoring timed out for %s", payload.username)
        raise HTTPException(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            detail="Scoring provider timed out",
        ) from exc
    except Exception as exc:
        logger.exception("Unexpected scoring failure for %s", payload.username)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal scoring error",
        ) from exc
