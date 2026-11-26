"""HTTP client for the study assistant backend, without provider credentials."""

import httpx
from pydantic import ValidationError

from api_models import AskResponse


def request_answer(api_url: str, question: str) -> AskResponse:
    """Call the backend once and validate its answer and accounting.

    Args:
        api_url: The backend base URL, configured on the Streamlit server.
        question: The learner's question.

    Returns:
        The validated answer and reported usage.

    Raises:
        ValueError: If the backend fails or returns an invalid response.
    """
    try:
        response = httpx.post(
            f"{api_url.rstrip('/')}/ask",
            json={"question": question},
            timeout=45.0,
        )
        response.raise_for_status()
        return AskResponse.model_validate(response.json())
    except httpx.TimeoutException as exc:
        raise ValueError("The request timed out. Check the backend before trying again; the call may have been charged.") from exc
    except httpx.HTTPStatusError as exc:
        messages = {
            422: "Enter a nonempty question and try again.",
            503: "The backend is missing its OpenRouter key. Configure OPENAI_API_KEY on the backend.",
            502: "The provider response failed validation or could not be completed. Check the backend logs; the call may have been charged.",
            504: "The model request timed out. Check the backend before trying again; the call may have been charged.",
        }
        raise ValueError(messages.get(exc.response.status_code, "The backend could not complete the request. Check its logs.")) from exc
    except (httpx.RequestError, httpx.InvalidURL) as exc:
        raise ValueError("Cannot reach the backend. Start FastAPI and check ASK_API_URL.") from exc
    except (ValidationError, ValueError) as exc:
        raise ValueError("The backend returned an invalid answer or usage report. Check its /ask response.") from exc
