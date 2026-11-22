# Repository Guidelines

## Project Structure & Module Organization

`docs/handoff.md` records setup, verification, known gaps, and next steps. Update it after material changes.

`main.py` exports the FastAPI `app`, with `GET /health` and `POST /ask`. Runtime dependencies are in `requirements.txt`; test dependencies are in `requirements-dev.txt`. `tests/` contains pytest tests. `pre-session-check-in/` holds preparation notes. `.venv/` is the local, ignored environment. No static assets exist.

## Build, Test, and Development Commands

Run commands from the repository root using Python 3.11 or newer:

```zsh
python3 -m venv .venv                # Create the environment if absent
source .venv/bin/activate           # Activate it on macOS/zsh
python -m pip install -r requirements.txt
python -m uvicorn main:app --reload # Start the development server
```

No build step is required. With the server running, use `curl http://127.0.0.1:8000/health` to verify the health response. Interactive API documentation is available at `/docs`.

## Coding Style & Naming Conventions

Use four-space indentation, `snake_case` for functions and modules, and `PascalCase` for classes. Add type hints to parameters, return values, and class attributes. Use Google-style docstrings for modules, classes, and functions. Prefer `pathlib.Path` for filesystem paths and specific exception handlers with meaningful errors. Keep route handlers focused; consider splitting modules approaching 150 lines. No formatter or linter is configured.

## Testing Guidelines

Install test dependencies with `python -m pip install -r requirements-dev.txt`; run `python -m pytest`. Use files named `tests/test_*.py` and descriptive functions such as `test_health_returns_ok`. Mock provider calls so tests require no real credentials or paid requests. Cover success, validation, missing credentials, and provider failures. No coverage threshold is configured.

## Commit & Pull Request Guidelines

Use conventional prefixes such as `feat:`, `fix:`, and `docs:`. Ask before committing. Submit AI changes on a branch through a pull request for human review. Describe changes and validation, link relevant issues, and include this trailer in commits and PR bodies:

```text
Co-Authored-By: Sasamen <sasamen@users.noreply.github.com>
```

## Security & Configuration

Never commit credentials. `credentials.py` reads `OPENAI_API_KEY` from the environment, then falls back on macOS to the Keychain generic-password service `OPENAI_API_KEY`. `python-dotenv` optionally loads the root `.env`; existing environment values take precedence. Keychain users need no `.env`. Never print keychain output. `.gitignore` excludes secrets but permits `.env.example`. `/ask` uses `https://openrouter.ai/api/v1`, model `openai/gpt-4o-mini`, and no SDK retries. `/health` requires no key.
