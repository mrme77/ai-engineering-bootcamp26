"""Verify the UI's question, answer, usage, and error flows without paid calls."""

from pathlib import Path
from unittest.mock import Mock

import httpx
import pytest
from streamlit.testing.v1 import AppTest

APP_PATH = Path(__file__).resolve().parents[1] / "streamlit_app.py"


@pytest.fixture
def backend(monkeypatch: pytest.MonkeyPatch) -> Mock:
    """Replace HTTP requests with a known answer and reported usage."""
    monkeypatch.setenv("ASK_API_URL", "http://test-backend/")
    request = httpx.Request("POST", "http://test-backend/ask")
    post = Mock(return_value=httpx.Response(200, request=request, json={
        "answer": "Retrieval supplies relevant notes to the model.",
        "model": "gpt-4o-mini", "tokens_used": 42, "cost_usd": 0.000012,
    }))
    monkeypatch.setattr("ask_client.httpx.post", post)
    return post


def test_ui_calls_backend_and_displays_answer_and_usage(backend: Mock) -> None:
    """Only submission calls /ask and exposes both accounting fields."""
    app = AppTest.from_file(APP_PATH).run()
    assert not app.exception
    backend.assert_not_called()
    app.text_area[0].input(" Explain retrieval ")
    app.button[0].click().run()
    assert not app.exception
    assert app.subheader[0].value == "Your answer"
    assert any("Retrieval supplies" in item.value for item in app.markdown)
    assert [item.value for item in app.metric] == ["42", "$0.00001200"]
    backend.assert_called_once_with(
        "http://test-backend/ask", json={"question": "Explain retrieval"}, timeout=45.0,
    )


def test_ui_rejects_blank_question_without_request(backend: Mock) -> None:
    """Whitespace must not spend provider credits."""
    app = AppTest.from_file(APP_PATH).run()
    app.text_area[0].input("   ")
    app.button[0].click().run()
    assert app.warning
    assert not app.exception
    backend.assert_not_called()


@pytest.mark.parametrize("status", [422, 502, 503, 504, 500])
def test_ui_explains_backend_failure(backend: Mock, status: int) -> None:
    """Display useful safe errors without rendering upstream payloads."""
    backend.return_value = httpx.Response(
        status, request=httpx.Request("POST", "http://test-backend/ask"),
        json={"detail": "private upstream payload"},
    )
    app = AppTest.from_file(APP_PATH).run()
    app.text_area[0].input("Explain retrieval")
    app.button[0].click().run()
    assert not app.exception
    assert app.error
    assert "private upstream payload" not in app.error[0].value
    assert not app.metric


@pytest.mark.parametrize("failure", ["connection", "timeout", "invalid_url", "invalid_json", "invalid_usage"])
def test_ui_handles_transport_and_response_errors(backend: Mock, failure: str) -> None:
    """Handle unavailable services, timeouts, and malformed JSON safely."""
    if failure == "connection":
        backend.side_effect = httpx.ConnectError("private connection details")
    elif failure == "timeout":
        backend.side_effect = httpx.ReadTimeout("private timeout details")
    elif failure == "invalid_url":
        backend.side_effect = httpx.InvalidURL("private URL")
    elif failure == "invalid_json":
        backend.return_value = httpx.Response(
            200, request=httpx.Request("POST", "http://test-backend/ask"), text="not json",
        )
    else:
        backend.return_value = httpx.Response(
            200, request=httpx.Request("POST", "http://test-backend/ask"), json={"answer": "Missing accounting"},
        )
    app = AppTest.from_file(APP_PATH).run()
    app.text_area[0].input("Explain retrieval")
    app.button[0].click().run()
    assert not app.exception
    assert app.error
    assert "private" not in app.error[0].value
    assert not app.metric
