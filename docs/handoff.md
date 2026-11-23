# Project Handoff

## Current State

`main.py` exports a FastAPI app. `GET /health` returns `{"status":"ok"}`.
`POST /ask` accepts `{"question":"..."}`, calls OpenRouter once, and returns
`{"answer":"...","model":"gpt-4o-mini"}`. Runtime dependencies are in
`requirements.txt`; test dependencies are in `requirements-dev.txt`.

The development machine runs macOS with Python 3.14.7 and Git 2.54.0.
Python 3.11 or newer is required. Git was initialized on 2026-11-22;
the initial implementation is on `feat/ask-endpoint` for pull-request review.
Contributor guidance lives in `AGENTS.md`.

## Run Locally

From the project root:

```zsh
# First-time setup only, if .venv is absent:
python3 -m venv .venv

source .venv/bin/activate
python -m pip install -r requirements.txt
```

Keep the existing OpenRouter key in macOS Keychain under the generic-password
service `OPENAI_API_KEY`. No `.env` or manual export is required. Then run:

```zsh
python -m uvicorn main:app --reload
```

Keep the server terminal open. Stop it with Ctrl+C. If port 8000 is already
in use, stop the previous server first. Alternatively use `--port 8001` and
change the URLs below. If macOS prompts for Keychain access when calling `/ask`,
allow the Python process to read this credential.

In another terminal:

```zsh
curl -i http://127.0.0.1:8000/health
curl -i http://127.0.0.1:8000/ask \
  -H 'Content-Type: application/json' \
  -d '{"question":"Say hello in one sentence."}'
```

Expected result: HTTP 200 and `{"status":"ok"}`. Interactive API documentation
is at <http://127.0.0.1:8000/docs>.

## Verification and Known Gaps

On 2026-11-22, the health endpoint passed a live HTTP check. Direct ASGI checks
also confirmed `/health` returns 200 and an unknown route returns 404.
Seventeen pytest tests passed after adding Keychain support, using mocked provider calls and
dummy credentials. They cover health, success with one call, invalid questions,
missing credentials, provider failures/timeouts, empty answers, and credential
resolution (environment precedence, Keychain success/failure, and other platforms). Run:

```zsh
python -m pip install -r requirements-dev.txt
python -m pytest -q
```

The user successfully tested `/ask` locally with the existing credential setup:
the response contained an answer and `"model":"gpt-4o-mini"`. The agent did not
inspect the real credential or make an additional paid model call.

The initial browser connection failed because the server was not running.
Starting Uvicorn resolved it. A running server is session state; verify it
again when resuming work.

## OpenRouter Configuration

The user confirmed that the macOS Keychain credential named `OPENAI_API_KEY`
contains an OpenRouter key. The current integration uses:

- Environment variable: `OPENAI_API_KEY`
- Base URL: `https://openrouter.ai/api/v1`
- Model: `openai/gpt-4o-mini` (replaces the earlier GPT-4.1 mini plan)

`python-dotenv` loads `.env` beside `main.py` at startup. Existing environment
variables take precedence. If no nonempty key is available, `credentials.py`
uses `/usr/bin/security` to read the macOS Keychain generic-password service
`OPENAI_API_KEY`, capturing output privately. Lookup failures return a safe
503 response. Other platforms require environment or `.env` configuration.
`.env.example` documents the variable with no value; `.gitignore` permits that
template while excluding `.env` secrets. Never print or commit the key.

SDK retries are disabled and the timeout is 30 seconds. Invalid questions return
422, missing credentials return 503, provider failures or empty answers return
502, and provider timeouts return 504. Upstream error details are not exposed.

## Next Work

The selected project is now a bootcamp study assistant, replacing the summer-house
reservation idea. The updated scope is in `pre-session-check-in/pre-seed-questions.md`.
The intended benefit is a connected curriculum, saved learning progress, and
targeted practice across sessions. Explanations and quizzes alone do not provide
enough distinction from a general chat interface. The first milestone covers three
bootcamp concepts: assess understanding, save results by concept, and recommend
one next exercise based on those results. A returning session must reuse the
saved history. Course-note references and review of recurring misconceptions are
part of the Demo Day goal.

The user also wants to explore a local LLM of approximately 30 billion parameters.
The model and runtime are undecided. Check hardware, memory, quantization, context
capacity, latency, and study-task quality before selecting them. Verify the full
data flow before making local-only privacy claims. Keep retrieval and saved
progress independent of the inference model.

These are planned capabilities; the current `/ask` implementation remains the
generic OpenRouter endpoint described above. First adapt it to explain a concept,
give an example, and ask one understanding-check question. Then implement the
assessment, persistence, and next-exercise milestone, add course-note grounding,
and evaluate local inference.

Review and merge the initial implementation through its pull request.
Update this handoff after material changes to setup, behavior, or verification.
