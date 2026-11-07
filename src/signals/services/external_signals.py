"""Business logic for external-candidate scoring.

All LLM calls belong here; routers stay thin. The provider client, the structured-output
runnable, and the answer parser are shared with the internal scoring service.
"""

import asyncio
import logging
from typing import Any

from langchain_core.messages import HumanMessage, SystemMessage
from pydantic import ValidationError

from signals.schemas.external import ExternalTalentRequest, ExternalTalentResponse
from signals.services.llm_services.external_system_prompt import EXTERNAL_SYSTEM_PROMPT
from signals.services.llm_services.external_user_prompt import build_external_prompt
from signals.services.llm_services.gigachat_client import (
    get_provider_timeout,
    get_structured_scoring_runnable,
    parse_scoring_answer,
)
from signals.services.signals import ScoreUnavailableError

logger = logging.getLogger(__name__)


class ExternalSignalsService:
    """Scores external speaker candidates from public signals."""

    def __init__(self, llm: Any, timeout: float) -> None:
        self._llm = llm
        self._timeout = timeout

    async def score_candidate(
        self, payload: ExternalTalentRequest
    ) -> ExternalTalentResponse:
        """Return the talent score for one external candidate."""
        messages = [
            SystemMessage(content=EXTERNAL_SYSTEM_PROMPT),
            HumanMessage(content=build_external_prompt(payload)),
        ]

        try:
            answer = await asyncio.wait_for(
                self._llm.ainvoke(messages), timeout=self._timeout
            )
        except TimeoutError:
            logger.warning("External scoring timed out for %s", payload.username)
            raise
        except Exception as exc:
            logger.warning(
                "External scoring provider failed for %s: %s", payload.username, exc
            )
            raise ScoreUnavailableError("Provider call failed") from exc

        try:
            scored = parse_scoring_answer(answer)
        except (ValidationError, TypeError) as exc:
            logger.warning(
                "Unusable external scoring answer for %s: %s", payload.username, exc
            )
            raise ScoreUnavailableError("Provider answer is unusable") from exc

        return ExternalTalentResponse(
            username=payload.username,
            score=scored.score,
            reason=scored.reason,
            confidence=scored.confidence,
        )


def get_external_signals_service() -> ExternalSignalsService:
    """FastAPI dependency that provides the external scoring service."""
    return ExternalSignalsService(
        llm=get_structured_scoring_runnable(),
        timeout=get_provider_timeout(),
    )
