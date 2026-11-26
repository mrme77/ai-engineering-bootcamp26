"""Validated request, response, and provider accounting contracts."""

from pydantic import BaseModel, ConfigDict, Field


class AskRequest(BaseModel):
    """A question with surrounding whitespace removed."""

    model_config = ConfigDict(str_strip_whitespace=True)
    question: str = Field(min_length=1)


class ProviderUsage(BaseModel):
    """Actual token usage and charge reported by OpenRouter."""

    total_tokens: int = Field(strict=True, ge=0)
    cost: float = Field(strict=True, ge=0, allow_inf_nan=False)


class AskResponse(BaseModel):
    """The answer, model, token count, and provider-reported USD charge."""

    answer: str = Field(min_length=1)
    model: str = "gpt-4o-mini"
    tokens_used: int = Field(strict=True, ge=0)
    cost_usd: float = Field(strict=True, ge=0, allow_inf_nan=False)
