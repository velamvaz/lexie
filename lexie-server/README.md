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

## First manual smoke (WX-014)

Goal: prove the process runs on your machine and **`GET /health`** returns **200** (checklist C1–C2). You do **not** need a valid `OPENAI_API_KEY` for `/health` (add it before **`POST /explain`** in WX-017).

1. Finish **Setup** above (venv + `pip install -e ".[dev]"`).
2. `cp .env.example .env` — optional edits for now; defaults create `./data/` for SQLite.
3. Start: `uvicorn lexie_server.main:app --reload --host 127.0.0.1 --port 8000`
4. In another terminal: `curl -s http://127.0.0.1:8000/health` — expect JSON with `"ok": true`.

When that works, mark **WX-014** done in [`project-management/registry.md`](../project-management/registry.md) and continue with **WX-015** (`/profile` auth).

## Tests (preflight / WX-013)

Contract tests use **mocks** for the explain pipeline; they do **not** call OpenAI. Requires **Python 3.11+**.

```bash
cd lexie-server
python3.11 -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -e ".[dev]"
pytest -v
```

**CI:** On push/PR, [`.github/workflows/lexie-server-pytest.yml`](../.github/workflows/lexie-server-pytest.yml) runs the same suite on **Python 3.11** (Ubuntu). Check the **Actions** tab on GitHub after you push.

For integration tests that hit **pydub** / real audio duration, install **ffmpeg** on the runner or keep those tests mocked.

## Environment

See **`.env.example`**.
