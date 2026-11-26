# Week 1

The current Week 1 application remains at the repository root: `main.py`,
`credentials.py`, `requirements.txt`, and `tests/`. See
[the handoff](../docs/handoff.md) for local setup and previous verification.

## Submission checklist

Status reviewed on 2026-11-26. Account settings and live services were not checked.

- [ ] Confirm this repository is a fork of the official Week 1 starter.
- [x] Implement local FastAPI `/health` and `/ask` endpoints. The handoff records
  a successful local model call.
- [x] Ignore `.env` and local `.env` variants. Only `.env.example` is tracked.
- [x] Provider decision: the user chose to retain OpenRouter on 2026-11-26.
  `.env` loading is supported; the documented local setup uses macOS Keychain.
- [x] Return `answer`, `tokens_used`, and `cost_usd` from `/ask`, retaining `model`.
  Usage and cost come from OpenRouter's response and are validated.
- [ ] Deploy to Render with `OPENAI_API_KEY` in its environment and verify a
  public HTTPS endpoint.
- [ ] Capture a successful live `/ask` curl response with all required fields.
- [x] Build a neon green Streamlit UI that calls `/ask` and displays usage and cost.
- [ ] Capture a successful real-provider UI screenshot for submission.
- [ ] Verify auto-recharge is off and configure a $5 to $10 budget with an alert
  in the provider account.
- [ ] Submit the live URL privately in Maven. Do not put the deployment URL in
  this repository, public posts, or public screenshots.

## Optional work

- Add `force_bad` to demonstrate output validation.
- Explain the model choice and per-call cost.
- Project setup and API documentation are now in the root README.
- Prepare a LinkedIn post with screenshots only, excluding secrets and the live URL.

When asking for debugging help, include the full error after removing credentials
and other private values.
