# Technical SPEC: Lexie Word Explainer (LX-1)

**Status:** Ready for implementation review  
**Registry ID:** LX-1  
**PRD:** [../prds/lexie-word-explainer.PRD.md](../prds/lexie-word-explainer.PRD.md)  
**Date:** 2026-04-22  
**Audience:** Parent builder / one-child deployment (not multi-tenant)

This document locks **API contracts**, **operational rules**, **edge cases**, and **test/exit criteria** for Phase 1. It does not replace the PRD for product intent.

---

## 1. System architecture and trust boundaries

### 1.1 Orchestration vs inference (no “all-local AI” claim)

- **Device (Phase 2):** WiFi only; no cellular modem. It performs **one job**: send recorded audio in an HTTP `POST` to a configured **`BASE_URL`**. It does **not** call OpenAI or the public model APIs directly.
- **Lexie server (FastAPI, your deployment):** **Orchestrates** the pipeline: calls **OpenAI** (Whisper, chat completions, TTS) with credentials stored in **server environment only**. This is the **trust boundary** for API keys.
- **Inference** (STT, text generation, TTS audio): runs in **OpenAI’s cloud** in Phase 1 unless you later swap in self-hosted models. Marketing and docs must not imply all processing happens on a home PC.
- **Single `age_profile`:** one row / document for the child. No tenant ID.

### 1.2 Connectivity (device and browser clients)

- **At home and away:** the same **public** `https://` **`BASE_URL`** (no reliance on a parent laptop process for production availability).
- **At home:** bookmark (or test browser) uses home Wi‑Fi → internet → your host.
- **Away:** bookmark joins a **parent phone’s mobile hotspot**; same `BASE_URL`.
- **TLS required** in production; platform-issued cert is sufficient for the bookmark (pinning is optional, Phase 2+).
- **Phase 2 (device):** two saved **WiFi profiles** (e.g. home + hotspot SSIDs); provisioning mechanism **TBD** (SoftAP, BLE, USB) — not implemented in this SPEC’s server work, but the server assumes **one** configured API key per family deployment.

**Not in scope for v1:** split-horizon DNS to hit a “LAN” URL at home; always use the public name.

---

## 2. Public hosting (recommended defaults)

- **Suitable PaaS:** **Fly.io**, **Railway**, or **Render** (always-on **paid** tier) or a **small VPS** (e.g. Hetzner, DO) with reverse proxy + TLS.
- **Default recommendation:** **Fly.io** with **1 shared-cpu, ≥256MB RAM** machine, **min machines = 1** to avoid **cold start** on first explain after idle.
- **Environment variables (server):** `OPENAI_API_KEY` (required), `LEXIE_DEVICE_KEY` (required in production; shared with firmware), `LEXIE_ADMIN_TOKEN` (required for `PATCH` profile and admin routes), `LEXIE_LOG_REQUESTS=0|1` (**default `0` — locked in PRD:** off until parent opts in), `LEXIE_HEADWORD_TTS=0|1` (**default `0` — locked in PRD:** meaning-only TTS; set `1` to append headword TTS, see §3.5), optional `LEXIE_CORS_ORIGINS` (see §6).
- **Cost:** expect **OpenAI** line item to dominate. Set **OpenAI usage/budget alerts** in the OpenAI dashboard. Host is a small fixed line until CPU/RAM saturation.

---

## 3. API contract

### 3.1 Conventions

- **Base path:** all paths below are relative to `BASE_URL` (no `/api` prefix required unless you choose one consistently).
- **Request ID:** server may include optional `X-Request-Id` in responses; clients may ignore.
- **JSON default encoding:** UTF-8.

### 3.2 `GET /health`

- **Auth:** none (or optional shared secret; if added, document in server README).
- **Response:** `200 application/json`  
  Example: `{"ok": true, "version": "0.1.0", "git_sha": "optional"}`

### 3.3 `GET /profile`

- **Auth:** not used by the device. For **admin** only: `Authorization: Bearer <LEXIE_ADMIN_TOKEN>` (or `X-Admin-Token: <token>`; pick one in implementation and use consistently).
- **Response:** `200` — JSON body matching `age_profile` (no secrets).

### 3.4 `PATCH /profile`

- **Auth:** `Authorization: Bearer <LEXIE_ADMIN_TOKEN>` (must not be world-readable).
- **Request:** JSON; partial update allowed: `age_years`, `reading_level`, `child_name`, `explanation_style` (if present in schema).
- **Response:** `200` with updated profile; `400` bad body; `401` if missing/invalid admin token; `429` if rate-limited (optional).

**Rate limit (recommended):** ≤ 30 `PATCH` per minute per IP to reduce brute force.

### 3.5 `POST /explain`

- **Auth (production):** required header: `Authorization: Bearer <LEXIE_DEVICE_KEY>` or `X-Device-Key: <LEXIE_DEVICE_KEY>`. **Development:** if `LEXIE_DEVICE_KEY` is unset, accept requests (document loudly in `README`).

- **Request:** `multipart/form-data`  
  - **Field name:** `audio` (REQUIRED)  
  - **Content types accepted (Phase 1):**  
    - `audio/webm` (MediaRecorder, Chrome)  
    - `audio/wav`, `audio/x-wav`  
    - `audio/mpeg` (rare)  
  - **Max part size:** **2 MiB** (implementation may reject with `413`).  
  - **Effective max audio duration (policy):** **30 seconds** — if decoded duration exceeds 30s, return `400` with JSON `{"error":"audio_too_long","max_seconds":30}`. Shorter **minimum** (see §4): if decoded duration &lt; **0.4 s** (400 ms), return `400` with `{"error":"audio_too_short"}` before calling OpenAI (saves cost).

- **Response (success):** `200`  
  - `Content-Type: ` `audio/mpeg` (MP3) **preferred** (OpenAI TTS default); or `audio/wav` if implementation uses PCM out.  
  - Body: raw bytes of the response audio. **Default behavior (`LEXIE_HEADWORD_TTS=0`, locked in PRD):** one TTS pass — the **explanation of meaning** only. **If `LEXIE_HEADWORD_TTS=1`:** TTS the explanation, then TTS the **headword** (the vocabulary target) as a short follow-on, and **concatenate** into a **single** response body (one playout for the child).  
  - Optional header: `X-Explain-Latency-Ms: <integer>` (end-to-end server time).

- **Response (error):** JSON `application/json` for machine handling where possible. Examples:  
  - `400` — `{"error":"transcription_empty"}` (Whisper returned nothing after trim)  
  - `400` — `{"error":"unintelligible_audio"}` (heuristic / empty transcript policy)  
  - `401` — `{"error":"unauthorized"}` (missing device key in prod)  
  - `413` — `{"error":"payload_too_large"}`  
  - `502` / `503` — `{"error":"openai_unavailable"}` (after retries exhausted)  
  - `500` — `{"error":"internal"}` (no stack traces in body in prod)

### 3.6 `GET /admin/usage` (optional, Phase 1+)

- **Auth:** `Authorization: Bearer <LEXIE_ADMIN_TOKEN>`.  
- **Response:** `200` JSON, e.g. `{"month":"2026-04","explain_count": 42, "cost_usd_estimated": null}`. *Cost estimate* may be `null` until token-based estimation is implemented; **OpenAI billing** remains the source of truth for money.

### 3.7 `GET /admin/metrics` (optional, for local ops app)

- **Auth:** same as admin.  
- **Response:** JSON with rolling counters if implemented (e.g. `errors_24h`, `p95_latency_ms_sampled`); may return `404` in minimal v1.

---

## 4. Transcription → logging fields (extraction model) — v1

**Strategy:** a **single** user-visible path: Whisper returns **`transcript`** (full string). That string is the **sole** input to the explanation LLM. No second pass is required in v1.

**Persistence (`explain_request` log) when logging is on:**

| Field            | v1 rule |
|------------------|--------|
| `raw_transcript` | Full Whisper text (as returned). |
| `word_or_phrase` | Copy of `raw_transcript` **trimmed** to first **200** UTF-8 characters (or full string if shorter). *Rationale: PRD field preserved without expensive NLP to split “word” vs “context”.* |
| `context_text`  | `NULL` / omitted in v1. Future: optional second model or regex could split. |

---

## 5. Edge and failure policies

| Condition | Server behavior | HTTP |
|-----------|----------------|------|
| **Silent / &lt; ~0.4 s** audio | Reject before OpenAI | `400` `audio_too_short` |
| **Transcript empty** | Do not call GPT; optional short TTS or JSON error; PRD allows gentle tone — for prototype return JSON error, browser TTS can speak fixed line later | `400` `transcription_empty` |
| **Gibberish / one token nonsense** | Still pass to model; if model returns redirect string only, TTS that; if junk, parent tunes prompt | 200 (accept) or `400` if you add a confidence gate later |
| **Not vocabulary (Hogwarts, etc.)** | Model returns **exact** PRD redirect one-liner; TTS speaks it | `200` |
| **OpenAI 429** | Exponential backoff **1–2** retries, then | `503` / `502` with `openai_unavailable` |
| **OpenAI 5xx / network** | 1–2 retries; then | `502` with JSON |
| **Per-stage timeout** | Whisper: **45 s**; chat: **30 s**; TTS: **60 s** (tunable); overall **120 s** ceiling → fail with | `503` |
| **Max output tokens (GPT)** | Cap at **200** total completion tokens; enforce `max_tokens` in API call | — |
| **TTS** | If TTS fails after success from GPT, return | `502` and log; no partial audio requirement in v1 |
| **Language** | **English** input for Phase 1; if Whisper returns obvious non-English, still process or return `200` with redirect — product choice: return `200` and let model follow PRD; SPEC allows simple “English only” note in prompt. |

**Browser prototype (not device) errors:** use `alert()` or on-screen `div` for JSON `error` field; no requirement for TTS of errors in v1. **Child-facing copy** (on-screen or future TTS) should follow the PRD’s **error tone** (calm, one idea, no stack traces) — [lexie-word-explainer.PRD.md](../prds/lexie-word-explainer.PRD.md) **§5 — Child-facing error tone**.

**Device (Phase 2):** map HTTP/JSON failure to **LED** + optional short **audio** line; copy style per same PRD section.

---

## 6. CORS, HTTPS, and getUserMedia (Phase 1 prototype)

- **Prototype (browser) must be served from a **secure context** for reliable mic access:**  
  - `http://localhost` and `http://127.0.0.1` (any port) are **allowed** in Chromium for `getUserMedia`.  
  - **`http://<LAN-IP>:port`** (e.g. `http://192.168.1.10:3000`) is often **blocked** — use **https** (e.g. `mkcert` for local TLS) or **port-forward / localhost** only, or a **Vite** dev server on `localhost` and access from the same machine.
- **Server (FastAPI):** set `CORSMiddleware` with:  
  - `allow_origins` including `http://localhost:5173`, `http://127.0.0.1:5173` (Vite), `http://localhost:3000` for the **prototype** and the **lexie-ops** app, plus any value in `LEXIE_CORS_ORIGINS` (comma-separated) for the parent’s machine. **Do not** `*` in production with credentials.  
- **ops app:** can use `Vite` `server.proxy` to same-origin (see [monitoring/lexie-ops/README.md](../../../monitoring/lexie-ops/README.md)).

---

## 7. Logging, PII, retention

- **No raw audio** in persistent storage (per PRD).  
- **Product default (locked in PRD):** `LEXIE_LOG_REQUESTS` defaults to **`0`** — **no** server-side storage of **transcript** or **explanation** text. The parent **opts in** to `1` for **tuning and debugging** (transcript + response + `latency_ms` + request id; **redact** if needed).  
- **Retention (when `LEXIE_LOG_REQUESTS=1`):** **30** days of rolling logs or database rows, then delete (configurable). Set `LEXIE_LOG_REQUESTS=0` to turn logging off.  
- **Export / delete:** out of band for v1; document “delete server DB + logs” for full removal.

---

## 8. Usage, monitoring, and SLOs

### 8.1 Usage bands (single child — for capacity planning, not pricing)

| Phase        | Explains / day (typical) | Heavy day |
|--------------|-------------------------|-----------|
| Onboarding   | 3–15                    | 25–40     |
| Habit        | 5–25                    | 40–60     |
| Steady       | 10–35                   | 60–100    |

- **Rate limit (optional):** max **30 explains / hour** per `device` key; **60 / day** soft cap (return `429` with JSON `{"error":"rate_limited"}`) — can be **disabled** via env for the parent.

### 8.2 SLOs (Phase 1)

- **p95** end-to-end (receive multipart → TTS bytes ready) **&lt; 5 s** on a **warm** instance, typical home path, for short utterances, subject to OpenAI regional latency.  
- **Uptime:** best-effort single instance; use host provider + optional external `GET /health` ping (e.g. UptimeRobot).

### 8.3 What to measure in-app

- Per request: `latency_ms`, which stage failed (`stt` / `llm` / `tts`); no raw audio.  
- **OpenAI:** org dashboard for **cost** truth; set **monthly budget alert**.  
- **Host:** provider CPU/RAM, OOM.

**Scaling:** for one child, **vertical** scale (bigger VM) only; no horizontal or K8s in v1.

---

## 9. Local parent ops app

- **Location in repo:** [monitoring/lexie-ops/](../../../monitoring/lexie-ops/) (Vite, minimal UI; [README](../../../monitoring/lexie-ops/README.md)).  
- **Purpose:** poll `GET /health` and optionally `GET /admin/usage` / `GET /admin/metrics` with `LEXIE_ADMIN_TOKEN`.  
- **CORS / proxy:** use `.env` `VITE_LEXIE_BASE_URL` and ensure server allows that origin, **or** use Vite `proxy` to avoid CORS during dev.  
- **Not a cost system:** link out to **OpenAI billing** for true spend.

---

## 10. Test plan (Phase 1)

| Layer | What |
|-------|------|
| **Contract** | `GET /health` 200; `GET/PATCH /profile` 401 without token, 200 with; `POST /explain` 401/400 cases |
| **Pipeline (mocked OpenAI)** | Inject fake STT/LLM/TTS; assert prompt includes `age_years`, `reading_level` from profile |
| **E2E (real keys, staging)** | Single word, idiom, out-of-scope sentence; measure latency |
| **Soak** | 20–50 explains sequentially; no memory runaway, no leak of secrets in logs |
| **Manual eval set** | Checklist: sorcerer, phrasal verb, “What is Hogwarts?”, &lt;0.5s silence, 35s audio |

---

## 11. Definition of done (Phase 1, commit-ready)

1. [ ] `GET /health` live on deployed **HTTPS** host.  
2. [ ] `POST /explain` works from browser and returns MP3; device key auth in production.  
3. [ ] `GET`/`PATCH /profile` with admin token.  
4. [ ] Defaults: `LEXIE_LOG_REQUESTS=0`, `LEXIE_HEADWORD_TTS=0`; no raw audio persistence.  
5. [ ] p95 &lt; 5s under test load on warm instance.  
6. [ ] CORS and prototype documented.  
7. [ ] [monitoring/lexie-ops/](../../../monitoring/lexie-ops/) fetches health against dev or deploy.

---

## 12. Known limitations (v1)

- English-primary; no diarization, no custom wake word, no on-device model.  
- No per-request human moderation; model misclassification possible — tune with eval set.  
- `word_or_phrase` / `context_text` split in logs is **not** semantically perfect (see §4).  
- Phase 2 **WiFi provisioning** not in this server release.  
- **Journey 5 (Phase 1b) — recovery cap (PRD-locked):** in multi-turn **session** mode, **at most one** Level 1 oral-fork **round** and **at most one** Level 2 letter-spell **round** after the initial PTT, then a mandatory **Level 3** “kind stop” (no further recovery prompts in that session). Implementation must **enforce** this cap; see PRD **Journey 5**.

---

## 13. Defaults summary (PRD-locked, Phase 1)

| Setting | Default | PRD / notes |
|--------|--------|-------------|
| `LEXIE_LOG_REQUESTS` | `0` | **Off** — no transcript/response DB logging until opt-in. |
| `LEXIE_HEADWORD_TTS` | `0` | **Off** — meaning TTS only; opt-in for headword TTS. |
| Journey 5 multi-turn (Phase 1b) | N/A in Phase 1 | Recovery depth cap: **1** fork + **1** spell max, then exit. |

---

## 14. Implementation order (reference)

1. Project skeleton + env + `/health`  
2. SQLite `age_profile` + seed one row + `GET`/`PATCH` + admin  
3. `POST /explain` (Whisper → GPT → TTS) + error mapping + limits  
4. Prototype static page (or Vite) for PTT  
5. **Deploy** public; verify from internet + hotspot  
6. **lexie-ops** + CORS for localhost  
7. **SPEC** accepted → merge

---

*End of SPEC.*
