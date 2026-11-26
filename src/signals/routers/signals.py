"""Weak-signals endpoint: parse the request, delegate to SignalsService."""

import logging
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from signals.schemas.signals import TalentRequest, TalentResponse
from signals.services.signals import (
    ScoreUnavailableError,
    SignalsService,
    get_signals_service,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/signals", tags=["signals"])


@router.post(
    "/weak-signals",
    response_model=TalentResponse,
    summary="Score one speaker from weak signals",
)
async def get_weak_signals(
    payload: TalentRequest,
    service: Annotated[SignalsService, Depends(get_signals_service)],
) -> TalentResponse:
    """Return the talent score for a single speaker."""
    try:
        return await service.score_talent(payload)
    except ScoreUnavailableError as exc:
        logger.warning("Scoring unavailable for speaker %s: %s", payload.id, exc)
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Scoring provider unavailable",
        ) from exc
    except TimeoutError as exc:
        logger.warning("Scoring timed out for speaker %s", payload.id)
        raise HTTPException(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            detail="Scoring provider timed out",
        ) from exc
    except Exception as exc:
        logger.exception("Unexpected scoring failure for speaker %s", payload.id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal scoring error",
        ) from exc
