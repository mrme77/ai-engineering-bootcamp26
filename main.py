"""FastAPI health check and one-shot OpenRouter question answering."""

import logging
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from openai import APIError, APITimeoutError, OpenAI
from pydantic import ValidationError

from api_models import AskRequest, AskResponse, ProviderUsage
from credentials import get_api_key

load_dotenv(Path(__file__).with_name(".env"))

logger = logging.getLogger(__name__)

app = FastAPI()


@app.get("/health")
def health() -> dict[str, str]:
    """Return the application's health status."""
    return {"status": "ok"}


@app.post("/ask", response_model=AskResponse)
def ask(request: AskRequest) -> AskResponse:
    """Answer a question with one OpenRouter request and no SDK retries."""
    api_key = get_api_key()
    if not api_key:
        raise HTTPException(
            status_code=503,
            detail="OPENAI_API_KEY is unavailable. Check macOS Keychain access or set the environment variable.",
        )

    try:
        with OpenAI(
            api_key=api_key,
            base_url="https://openrouter.ai/api/v1",
            max_retries=0,
            timeout=30.0,
        ) as client:
            completion = client.chat.completions.create(
                model="openai/gpt-4o-mini",
                messages=[{"role": "user", "content": request.question}],
            )
    except APITimeoutError as exc:
        logger.warning("OpenRouter request timed out")
        raise HTTPException(status_code=504, detail="The model request timed out.") from exc
    except APIError as exc:
        # Log only the error type to avoid exposing credentials or upstream payloads.
        logger.error("OpenRouter request failed: %s", type(exc).__name__)
        raise HTTPException(
            status_code=502,
            detail="OpenRouter request failed. Check your API key, credit, and connection.",
        ) from exc

    answer = completion.choices[0].message.content if completion.choices else None
    if not answer or not answer.strip():
        raise HTTPException(status_code=502, detail="The model returned no text answer.")
    try:
        usage = ProviderUsage.model_validate(
            completion.usage.model_dump() if completion.usage is not None else None
        )
    except ValidationError as exc:
        logger.warning("OpenRouter response contained missing or invalid usage accounting")
        raise HTTPException(
            status_code=502,
            detail="The model returned missing or invalid usage accounting. The call may still have been charged.",
        ) from exc
    return AskResponse(answer=answer, tokens_used=usage.total_tokens, cost_usd=usage.cost)
