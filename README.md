# Bootcamp study lab

A FastAPI backend and neon green Streamlit interface for asking bootcamp questions
through OpenRouter using `openai/gpt-4o-mini`.

## Run locally

Use Python 3.11 or newer. From the repository root:

```zsh
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements-dev.txt
```

Set `OPENAI_API_KEY` to your **OpenRouter** key in the environment or an ignored
root `.env` file. On macOS, the existing Keychain service `OPENAI_API_KEY` is
also supported. `.env.example` contains variable names and local defaults only.
Never commit or share your key.

Start the backend:

```zsh
python -m uvicorn main:app --reload
```

In another terminal, from the same repository root:

```zsh
source .venv/bin/activate
python -m streamlit run streamlit_app.py
```

Open <http://localhost:8501>. Submit a question to see its answer, token usage,
and cost. Streamlit calls FastAPI over HTTP; it does not call OpenRouter directly.
`ASK_API_URL` defaults to `http://127.0.0.1:8000`. Configure it privately on the
Streamlit server when using a deployed backend. Environment values override `.env`.

## API contract

`GET /health` returns `{"status":"ok"}` without provider access.

```zsh
curl -sS http://127.0.0.1:8000/ask \
  -H 'Content-Type: application/json' \
  -d '{"question":"What is retrieval augmented generation?"}'
```

Example response shape, with illustrative usage values:

```json
{
  "answer": "Retrieval supplies relevant context to a model before it answers.",
  "model": "gpt-4o-mini",
  "tokens_used": 42,
  "cost_usd": 0.000012
}
```

`tokens_used` is OpenRouter's `usage.total_tokens`, including input and output.
`cost_usd` is the provider-reported `usage.cost`, rather than a local estimate.
See [OpenRouter usage accounting](https://github.com/OpenRouterTeam/docs/blob/main/cookbook/administration/usage-accounting.mdx).
Missing or invalid accounting returns 502, even if an answer was generated.
Such calls may still incur charges. The app does not retry model requests.

Invalid questions return 422, missing credentials return 503, provider or response
failures return 502, and model timeouts return 504. Interactive docs are at `/docs`.

## Verification and weekly work

```zsh
python -m pytest -q
```

Tests mock provider calls and HTTP requests, including the Streamlit form, answers,
usage reporting, and error states. They require no real keys or paid requests.

[Week 1](week1/README.md) tracks the submission requirements. `week2/` through
`week5/` are reserved for later coursework. [The handoff](docs/handoff.md) records
verification and remaining work.

Render deployment and live submission proof remain outstanding. Set the
OpenRouter key as `OPENAI_API_KEY` in the backend's hosting environment; it cannot
use your Mac's Keychain. Submit deployed URLs privately in Maven, keeping them
out of this repository and public screenshots. Verify wallet settings separately.
