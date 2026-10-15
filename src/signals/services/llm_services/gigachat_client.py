"""GigaChat client factory.

One client instance is shared for the whole process: it holds the provider
connection pool and the credential lifecycle, so rebuilding it per request
would add an authorization round trip to every scoring call.
"""

from functools import lru_cache
from typing import Any

from langchain_gigachat import GigaChat
from pydantic import BaseModel

from signals.config.gigachat_config import GigaChatConfig, get_gigachat_config
from signals.schemas.signals import TalentLLMResponse

SCORING_TOOL_DESCRIPTION = (
    "Talent score of one conference speaker, from the supplied weak signals."
)


def build_gigachat_client(config: GigaChatConfig) -> GigaChat:
    """Build a chat client from settings without performing any request."""
    return GigaChat(
        model=config.llm_model,
        temperature=config.llm_temperature,
        max_tokens=config.llm_max_tokens,
        base_url=config.ultra_base_url,
        scope=config.ultra_scope,
        verify_ssl_certs=config.verify_ssl_certs,
        timeout=config.timeout,
        credentials=config.token.get_secret_value(),
    )


@lru_cache
def get_gigachat_client() -> GigaChat:
    """Return the process-wide GigaChat client."""
    return build_gigachat_client(get_gigachat_config())


def build_scoring_tool_schema(model: type[BaseModel] = TalentLLMResponse) -> dict[str, Any]:
    """Describe ``model`` as a function the provider can be forced to call.

    The provider client requires a non-empty description, and the fixed
    response schema carries none, so the description is supplied here rather
    than by editing the schema module.
    """
    return {
        "type": "function",
        "function": {
            "name": model.__name__,
            "description": SCORING_TOOL_DESCRIPTION,
            "parameters": model.model_json_schema(),
        },
    }


def parse_scoring_answer(answer: Any) -> TalentLLMResponse:
    """Validate a raw model answer against the fixed scoring schema."""
    if isinstance(answer, TalentLLMResponse):
        return answer
    if isinstance(answer, BaseModel):
        answer = answer.model_dump()
    if not isinstance(answer, dict):
        raise TypeError(f"Expected a scoring object, got {type(answer).__name__}")

    return TalentLLMResponse.model_validate(answer)


@lru_cache
def get_structured_scoring_runnable() -> Any:
    """Return the runnable that calls the provider with the scoring function."""
    return get_gigachat_client().with_structured_output(build_scoring_tool_schema())


def get_provider_timeout() -> float:
    """Return the provider budget the scoring service enforces."""
    return get_gigachat_config().timeout


__all__ = [
    "SCORING_TOOL_DESCRIPTION",
    "build_gigachat_client",
    "build_scoring_tool_schema",
    "get_gigachat_client",
    "get_provider_timeout",
    "get_structured_scoring_runnable",
    "parse_scoring_answer",
]
