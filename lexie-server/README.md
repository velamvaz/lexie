# Lexie server (Phase 1)

FastAPI app for the Word Explainer: `POST /explain` (Push-to-Talk audio), profile + admin routes, health.

## Requirements

- **Python 3.11+**
- **ffmpeg** on `PATH` (used by `pydub` for audio duration and optional headword + explanation MP3 join)
- **OpenAI API** key and (for production) **device** and **admin** tokens

## Setup

```bash
cd lexie-server
python3.11 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
cp .env.example .env
# Set OPENAI_API_KEY and optional LEXIE_DEVICE_KEY / LEXIE_ADMIN_TOKEN
```

## Run (development)

```bash
uvicorn lexie_server.main:app --reload --host 0.0.0.0 --port 8000
```

- `GET /health` — liveness
- `GET|PATCH /profile` — admin-only (`Authorization: Bearer <LEXIE_ADMIN_TOKEN>`)
- `POST /explain` — device auth (`LEXIE_DEVICE_KEY` unset = accept all keys in dev)
- `GET /admin` — HTML admin (browser; uses profile API with token from `sessionStorage`)
- `GET /prototype/` — static PTT client (multipart upload)

SQLite DB file defaults to `<LEXIE_DATA_DIR>/lexie.db` unless `LEXIE_DATABASE_URL` is set.

## Tests

```bash
pytest
```

The suite mocks the explain pipeline; it does not call OpenAI. CI should install **ffmpeg** or use mocks for audio-length checks if you add more integration tests.

## Environment

See **`.env.example`**.
