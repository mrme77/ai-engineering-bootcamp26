"""Test API behavior with mocked model calls and no real credentials."""

from unittest.mock import Mock

import httpx
import pytest
from fastapi.testclient import TestClient
from openai import APIConnectionError, APITimeoutError

import main


@pytest.fixture
def model_client(monkeypatch: pytest.MonkeyPatch) -> Mock:
    """Replace the SDK client and provide a dummy environment credential."""
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    constructor = Mock()
    constructor.return_value.__enter__ = Mock(return_value=constructor.return_value)
    constructor.return_value.__exit__ = Mock(return_value=False)
    constructor.return_value.chat.completions.create.return_value = Mock(
        choices=[Mock(message=Mock(content="Hello!"))],
        usage=Mock(model_dump=Mock(return_value={"total_tokens": 25, "cost": 0.0000045})),
    )
    monkeypatch.setattr(main, "OpenAI", constructor)
    return constructor


def test_health_returns_ok() -> None:
    """Keep the health endpoint independent of model availability."""
    response = TestClient(main.app).get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_ask_returns_answer_with_one_model_call(model_client: Mock) -> None:
    """Use OpenRouter syntax upstream and the requested model label downstream."""
    create = model_client.return_value.chat.completions.create

    response = TestClient(main.app).post("/ask", json={"question": " Hello "})

    assert response.status_code == 200
    assert response.json() == {
        "answer": "Hello!", "model": "gpt-4o-mini",
        "tokens_used": 25, "cost_usd": 0.0000045,
    }
    model_client.assert_called_once_with(
        api_key="test-key", base_url="https://openrouter.ai/api/v1",
        max_retries=0, timeout=30.0,
    )
    create.assert_called_once_with(
        model="openai/gpt-4o-mini", messages=[{"role": "user", "content": "Hello"}],
    )


@pytest.mark.parametrize("payload", [{}, {"question": "   "}, {"question": 42}])
def test_ask_rejects_invalid_question(payload: dict[str, object], model_client: Mock) -> None:
    """Reject invalid input before constructing an API client."""
    assert TestClient(main.app).post("/ask", json=payload).status_code == 422
    model_client.assert_not_called()


def test_ask_reports_missing_key(monkeypatch: pytest.MonkeyPatch, model_client: Mock) -> None:
    """Explain missing configuration without calling the provider."""
    monkeypatch.setattr(main, "get_api_key", lambda: None)
    response = TestClient(main.app).post("/ask", json={"question": "Hello"})
    assert response.status_code == 503
    assert "OPENAI_API_KEY" in response.json()["detail"]
    model_client.assert_not_called()


@pytest.mark.parametrize("timeout, status", [(False, 502), (True, 504)])
def test_ask_handles_provider_failure(model_client: Mock, timeout: bool, status: int) -> None:
    """Return a safe error and never retry a failed call."""
    request = httpx.Request("POST", "https://openrouter.ai/api/v1/chat/completions")
    error = APITimeoutError(request=request) if timeout else APIConnectionError(request=request)
    create = model_client.return_value.chat.completions.create
    create.side_effect = error
    response = TestClient(main.app).post("/ask", json={"question": "Hello"})
    assert response.status_code == status
    assert "test-key" not in response.text
    create.assert_called_once()


@pytest.mark.parametrize("choices", [[], [Mock(message=Mock(content=None))]])
def test_ask_handles_empty_answer(model_client: Mock, choices: list[Mock]) -> None:
    """Report unusable provider responses instead of returning empty answers."""
    model_client.return_value.chat.completions.create.return_value = Mock(choices=choices)
    response = TestClient(main.app).post("/ask", json={"question": "Hello"})
    assert response.status_code == 502


@pytest.mark.parametrize("usage", [
    None, {}, {"total_tokens": 25}, {"cost": 0.1},
    {"total_tokens": -1, "cost": 0.1},
    {"total_tokens": 25, "cost": -0.1},
    {"total_tokens": 25, "cost": float("nan")},
    {"total_tokens": 25, "cost": float("inf")},
    {"total_tokens": True, "cost": 0.1},
    {"total_tokens": 25, "cost": "0.1"},
])
def test_ask_rejects_missing_or_invalid_accounting(
    model_client: Mock, usage: dict[str, object] | None,
) -> None:
    """Do not invent a zero charge when provider accounting is unusable."""
    completion = model_client.return_value.chat.completions.create.return_value
    completion.usage = None if usage is None else Mock(model_dump=Mock(return_value=usage))
    response = TestClient(main.app).post("/ask", json={"question": "Hello"})
    assert response.status_code == 502
    assert "usage accounting" in response.json()["detail"]
    model_client.return_value.chat.completions.create.assert_called_once()


def test_ask_accepts_zero_cost_from_real_sdk_usage(model_client: Mock) -> None:
    """Preserve OpenRouter's extra cost field through the OpenAI SDK object."""
    from openai.types.chat import ChatCompletion

    model_client.return_value.chat.completions.create.return_value = ChatCompletion.model_validate({
        "id": "test", "created": 0, "object": "chat.completion",
        "model": "openai/gpt-4o-mini",
        "choices": [{"index": 0, "finish_reason": "stop", "message": {"role": "assistant", "content": "Hello!"}}],
        "usage": {"prompt_tokens": 20, "completion_tokens": 5, "total_tokens": 25, "cost": 0},
    })
    response = TestClient(main.app).post("/ask", json={"question": "Hello"})
    assert response.status_code == 200
    assert response.json()["cost_usd"] == 0
    assert response.json()["tokens_used"] == 25
