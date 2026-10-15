"""Business logic for weak-signal scoring.

All LLM calls belong here; routers stay thin.
"""

import asyncio
import logging
from typing import Any

from langchain_core.messages import HumanMessage, SystemMessage
from pydantic import ValidationError

from signals.schemas.signals import TalentRequest, TalentResponse
from signals.services.llm_services.gigachat_client import (
    get_provider_timeout,
    get_structured_scoring_runnable,
    parse_scoring_answer,
)
from signals.services.llm_services.system_prompt import SYSTEM_PROMPT
from signals.services.llm_services.user_prompt import build_prompt

logger = logging.getLogger(__name__)


class ScoreUnavailableError(RuntimeError):
    """Raised when the LLM provider cannot return a score."""


class SignalsService:
    """Scores speakers from their weak signals."""

    def __init__(self, llm: Any, timeout: float) -> None:
        self._llm = llm
        self._timeout = timeout

    async def score_talent(self, payload: TalentRequest) -> TalentResponse:
        """Return the talent score for a single speaker."""
        messages = [
            SystemMessage(content=SYSTEM_PROMPT),
            HumanMessage(content=build_prompt(payload)),
        ]

        try:
            answer = await asyncio.wait_for(
                self._llm.ainvoke(messages), timeout=self._timeout
            )
        except TimeoutError:
            logger.warning("Scoring timed out for speaker %s", payload.id)
            raise
        except Exception as exc:
            logger.warning("Scoring provider failed for speaker %s: %s", payload.id, exc)
            raise ScoreUnavailableError("Provider call failed") from exc

        try:
            scored = parse_scoring_answer(answer)
        except (ValidationError, TypeError) as exc:
            logger.warning("Unusable scoring answer for speaker %s: %s", payload.id, exc)
            raise ScoreUnavailableError("Provider answer is unusable") from exc

        return TalentResponse(
            id=payload.id,
            score=scored.score,
            reason=scored.reason,
            confidence=scored.confidence,
        )


def get_signals_service() -> SignalsService:
    """FastAPI dependency that provides the scoring service."""
    return SignalsService(
        llm=get_structured_scoring_runnable(),
        timeout=get_provider_timeout(),
    )
