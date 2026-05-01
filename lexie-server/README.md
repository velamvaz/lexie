# Lexie server (Phase 1)

FastAPI app for the Word Explainer: `POST /explain` (Push-to-Talk audio), profile + admin routes, health.

## Requirements

- **Python 3.11+**
- **ffmpeg** on `PATH` (used by `pydub` for audio duration and optional headword + explanation MP3 join)
- **OpenAI API** key and (for production) **device** and **admin** tokens

## Setup

**Requires Python 3.11+ on your PATH** (`python3.11`, or `python3.12` / `python3.13`). If macOS only has 3.9, install from [python.org](https://www.python.org/downloads/) or `brew install python@3.11`.

**Option A — helper script** (picks the newest 3.11+ it finds):

```bash
cd lexie-server
chmod +x scripts/bootstrap-venv.sh   # once
./scripts/bootstrap-venv.sh
source .venv/bin/activate
```

**Option B — manual**

```bash
cd lexie-server
python3.11 -m venv .venv
source .venv/bin/activate
pip install -U pip
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

## Profile API auth (WX-015)

**Set `LEXIE_ADMIN_TOKEN` in `.env` to a non-empty secret.** If it is empty, `GET /profile` returns **500** (`internal`) — the app treats missing admin config as misconfiguration, not “unauthorized.”

With the server running (`uvicorn` as above), in a second terminal:

```bash
# Expect 401 (no header)
curl -s -o /dev/null -w "%{http_code}\n" http://127.0.0.1:8000/profile

# Expect 401 (wrong token)
curl -s -o /dev/null -w "%{http_code}\n" -H "Authorization: Bearer wrong" http://127.0.0.1:8000/profile

# Expect 200 + JSON (use the same string as LEXIE_ADMIN_TOKEN in .env)
curl -s http://127.0.0.1:8000/profile -H "Authorization: Bearer YOUR_ADMIN_TOKEN"
```

Optional: `PATCH /profile` with a JSON body and `Authorization: Bearer …` to confirm updates (same admin token).

## Admin page in browser (WX-016)

1. Set **`LEXIE_ADMIN_TOKEN`** in **`.env`** (same as [WX-015](#profile-api-auth-wx-015)).
2. Start **`uvicorn`** (e.g. `http://127.0.0.1:8000`).
3. Open **`http://127.0.0.1:8000/admin`** — expect **200** and the “Lexie — child profile” form (no token in the URL).
4. Paste the admin token → **Load profile** → fields fill from **`GET /profile`**.
5. Change a field → **Save** → should show “Saved.” Reload the page, paste token again, **Load profile** → changes should persist.

The page stores the token in **`sessionStorage`** only for this tab (`lexie_admin_bearer`).

Quick check without a browser:

```bash
curl -s -o /dev/null -w "%{http_code}\n" http://127.0.0.1:8000/admin   # expect 200
```

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

## Troubleshooting

### macOS: Homebrew installed but `brew: command not found`

Homebrew’s binaries are not on your **`PATH`**. Add **`brew shellenv`** once (Apple Silicon vs Intel):

**Apple Silicon** — if `ls /opt/homebrew/bin/brew` succeeds:

```bash
echo 'eval "$(/opt/homebrew/bin/brew shellenv)"' >> ~/.zprofile
eval "$(/opt/homebrew/bin/brew shellenv)"
```

**Intel** — if `ls /usr/local/bin/brew` succeeds:

```bash
echo 'eval "$(/usr/local/bin/brew shellenv)"' >> ~/.zprofile
eval "$(/usr/local/bin/brew shellenv)"
```

Then open a new terminal or run `exec zsh -l` and check `brew --version`. Official docs: [Homebrew — Installation](https://docs.brew.sh/Installation).

## Environment

See **`.env.example`**.
