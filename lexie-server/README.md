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

Pipeline **simulations** (call order, duration gate, payload limit, request logging): [`tests/test_pipeline_simulation.py`](tests/test_pipeline_simulation.py) and explain-related tests in [`tests/test_api.py`](tests/test_api.py).

## Performance and privacy (`POST /explain`)

**Latency (what dominates)**  
Each successful explain does **three sequential OpenAI calls**: **Whisper** (audio → text), **chat** (JSON explanation), **TTS** (text → MP3). Wall time is roughly the **sum** of those round-trips plus local work. They cannot be parallelized on a single utterance: chat needs the transcript first; TTS needs the explanation text first.

**CPU / local work**  
- **Duration check** uses **pydub** (and **ffmpeg/ffprobe**) on the uploaded bytes **before** Whisper. That decodes audio once to enforce min/max duration and avoid Whisper cost on bad clips; the same bytes are sent to Whisper afterward (tradeoff: extra decode vs. cheaper rejects).  
- **`LEXIE_HEADWORD_TTS=1`**: second **TTS** call plus **MP3 concat** (decode + re-encode). Default is **off**; turn on only when you need headword audio.  
- **`POST /explain`** constructs a new **`OpenAI` client per request**. Overhead is usually small compared to API latency; revisit only if you measure high QPS and profile it.  
- Retries in the pipeline use **`time.sleep`** in the **sync** route, which **blocks a worker** under rate limits; fine at low concurrency.

**Privacy / logging**  
- **`LEXIE_LOG_REQUESTS=0`** (default): no `explain_request` rows are written after a successful explain.  
- **`LEXIE_LOG_REQUESTS=1`**: appends a diagnostic row with **raw transcript** and **response text** (and timing). Use only for short-lived debugging; do not leave on in production with real child audio/transcripts.  
- Normal **`POST /explain`** handling keeps upload bytes **in memory**; it does **not** write raw audio to disk as part of that path.

**Payload limit**  
Request bodies larger than **2 MiB** get **413** `payload_too_large` before the pipeline runs (see tests).

## Deploy (M1 / WX-006)

Goal: **`https://<BASE_URL>/health` → 200** with TLS (checklist **D2**). Use your host’s **secret UI** for **`OPENAI_API_KEY`**, **`LEXIE_DEVICE_KEY`**, **`LEXIE_ADMIN_TOKEN`** — not only a laptop **`.env`**.

### Docker image (recommended baseline)

The repo includes a **`Dockerfile`** with **Python 3.11** and **`ffmpeg`** (required for **`POST /explain`**). Build from **`lexie-server/`**:

```bash
cd lexie-server
docker build -t lexie-server .
docker run --rm -p 8000:8000 \
  -e OPENAI_API_KEY="…" \
  -e LEXIE_DEVICE_KEY="…" \
  -e LEXIE_ADMIN_TOKEN="…" \
  -e PORT=8000 \
  lexie-server
```

Then **`curl -s http://127.0.0.1:8000/health`**.

**SQLite on ephemeral disks:** the image sets **`LEXIE_DATA_DIR=/data`**. On Fly.io, Railway, Render, etc., attach a **persistent volume** (or mount) at **`/data`** so **`lexie.db`** survives restarts. Alternatively set **`LEXIE_DATABASE_URL`** to a managed Postgres/MySQL URL if you move off file SQLite.

**Platform `PORT`:** the default **`CMD`** reads **`PORT`** (Render/Fly/Heroku-style). Your reverse proxy or platform should set **`PORT`** if not **8000**.

**CORS:** set **`LEXIE_CORS_ORIGINS`** to the exact origin(s) that will call the API in the browser (comma-separated), e.g. your prototype or static site URL. For same-host **`/prototype`**, include your public **`https://<BASE_URL>`** if browsers treat it as a distinct origin in your setup.

### Fly.io

1. Install the CLI: [Fly.io install](https://fly.io/docs/hands-on/install-flyctl/), then **`fly auth login`**.
2. **`cd lexie-server`**. Edit **`fly.toml`**: set **`app`** to a name that is not already taken on Fly (or run **`fly launch`** once from this directory; it can create the app and align **`fly.toml`**).
3. **`fly deploy`** — the **`[mounts]`** block uses **`initial_size = "1gb"`** so the first deploy can create a volume named **`lexie_data`** in **`primary_region`** if none exists. SQLite then lives under **`/data`** (see **`LEXIE_DATA_DIR`** in the **`Dockerfile`**). If you prefer to create the volume yourself: **`fly volumes create lexie_data --region iad --size 1`** (region must match **`primary_region`**), then deploy.
4. **Secrets** (replace values; do not commit them):

   ```bash
   fly secrets set \
     OPENAI_API_KEY="…" \
     LEXIE_DEVICE_KEY="…" \
     LEXIE_ADMIN_TOKEN="…" \
     LEXIE_CORS_ORIGINS="https://<your-app>.fly.dev"
   ```

   Add any other vars from **`.env.example`** you need (e.g. **`LEXIE_LOG_REQUESTS`**, model overrides). **`PORT`** and **`LEXIE_DATA_DIR`** are already set in the image / **`fly.toml`**; you normally do not override them.

5. **URL:** **`https://<app>.fly.dev`** (or a custom domain after **`fly certs add`**). Verify **`curl -sS https://<app>.fly.dev/health`**.

To save cost at very low traffic, you can later switch **`auto_stop_machines`** / **`min_machines_running`** in **`fly.toml`** at the price of cold starts before **`POST /explain`**.

### After deploy (manual checks)

1. **`curl -sS https://<BASE_URL>/health`** — JSON with **`"ok": true`**.  
2. From **phone on cellular** (checklist **D3**): open or curl **`/health`**.  
3. Store **`BASE_URL`** in 1Password (**D5**).

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

### Admin: “Load profile” fails

- **`Error 401`** — The token in the box does **not** match **`LEXIE_ADMIN_TOKEN`** in the server’s **`.env`** (no extra spaces; restart **`uvicorn`** after editing **`.env`**).
- **`Error 500`** with `internal` — **`LEXIE_ADMIN_TOKEN`** is **empty** in **`.env`** (set a non-empty value), or the DB has no profile row (rare on first run; restart after a clean **`data/`** if you moved DB files).

Check from a terminal (same machine, same port):

```bash
curl -s -H "Authorization: Bearer YOUR_TOKEN" http://127.0.0.1:8000/profile
```

Expect JSON with `child_name`, etc. If this works but the browser does not, use the **same URL** you opened for **`/admin`** (e.g. don’t mix **`localhost`** and **`127.0.0.1`** if cookies/storage ever differ—usually both work when the server matches).

## Environment

See **`.env.example`**.
