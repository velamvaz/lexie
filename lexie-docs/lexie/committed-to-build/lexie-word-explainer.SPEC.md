# Technical SPEC: Lexie Word Explainer (LX-1)

**Status:** Ready for implementation review  
**Registry ID:** LX-1  
**PRD:** [../prds/lexie-word-explainer.PRD.md](../prds/lexie-word-explainer.PRD.md)  
**Related (Phase 1 planning):** [lexie-word-explainer.MASTER-CHECKLIST.md](lexie-word-explainer.MASTER-CHECKLIST.md) **(builder: accounts → deploy → E2E)** · [lexie-word-explainer.API-and-data-model.md](lexie-word-explainer.API-and-data-model.md) **(API catalog, entities, SQLite, metadata)** · [lexie-word-explainer.journeys-and-observability.md](lexie-word-explainer.journeys-and-observability.md) **(PRD journeys ↔ APIs ↔ observability)** · [lexie-word-explainer.BUDGET-AND-ROLLOUT.md](lexie-word-explainer.BUDGET-AND-ROLLOUT.md) **(ROM costs, rollout milestones + testing)** · [lexie-word-explainer.RUNBOOK.md](lexie-word-explainer.RUNBOOK.md) **(operator triage)** · [lexie-word-explainer.validation-matrix.md](lexie-word-explainer.validation-matrix.md) · [lexie-word-explainer.TESTING-strategy.md](lexie-word-explainer.TESTING-strategy.md) · [phased-delivery-plan.md](phased-delivery-plan.md)  
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
- **Cost:** expect **OpenAI** line item to dominate. Set **OpenAI usage/budget alerts** in the OpenAI dashboard. Host is a small fixed line until CPU/RAM saturation. **Rollout milestones and ROM budget:** [lexie-word-explainer.BUDGET-AND-ROLLOUT.md](lexie-word-explainer.BUDGET-AND-ROLLOUT.md).

---

## 3. API contract

### 3.1 Conventions

- **Base path:** all paths below are relative to `BASE_URL` (no `/api` prefix required unless you choose one consistently).
- **Request ID:** server may include optional `X-Request-Id` in responses; clients may ignore.
- **JSON default encoding:** UTF-8.

**Deeper reference:** per-route bodies, error unions, `age_profile` / `explain_request` DDL and JSON Schemas, optional headers, and CORS preflight notes — [lexie-word-explainer.API-and-data-model.md](lexie-word-explainer.API-and-data-model.md).

### 3.2 `GET /health`

- **Auth:** none (or optional shared secret; if added, document in server README).
- **Response:** `200 application/json`  
  Example: `{"ok": true, "version": "0.1.0", "git_sha": "optional"}`

### 3.3 `GET /profile`

- **Auth:** not used by the device. For **admin** only: `Authorization: Bearer <LEXIE_ADMIN_TOKEN>`. (Implementations **SHOULD** use the Bearer form only; avoid inventing a second ad-hoc header in Phase 1.)
- **Response:** `200` — JSON body matching `age_profile` (no secrets), UTF-8.

**Example 200 body** (illustrative; field order not normative):

```json
{
  "child_name": "Alex",
  "age_years": 6,
  "reading_level": "advanced for age",
  "explanation_style": "short sentences, concrete examples"
}
```

- `explanation_style` may be `null` (JSON `null` or key omitted; pick one in implementation and document; clients **SHOULD** accept `null` as “no custom style hints”).

**Errors:** `401` `{"error":"unauthorized"}` if the admin `Authorization` header is missing/invalid. Unauthenticated `GET` is **rejected in production** (no public read of the child’s name/age).

### 3.4 `PATCH /profile`

- **Auth:** `Authorization: Bearer <LEXIE_ADMIN_TOKEN>` (must not be world-readable).
- **Request:** `application/json`; **partial** update: any subset of `age_years` (integer, typical range 4–12), `reading_level` (string, non-empty after trim), `child_name` (string, non-empty after trim; **PII** — do not log in request access logs if avoidable), `explanation_style` (string or `null` to clear). Unknown keys **MAY** be ignored with `200` or rejected with `400` — **pick one and document** (recommended: ignore unknown keys to ease forward evolution).
- **Response:** `200` with the **full** current profile in the same shape as `GET /profile`; `400` bad body (type/range/empty string where forbidden); `401` if missing/invalid admin token; `429` if rate-limited (optional).

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

**Headword source (when `LEXIE_HEADWORD_TTS=1`):** The model **MUST** return **structured** output so `headword` is explicit (not inferred by splitting free text from a separate TTS run). **Normative pattern:** use **OpenAI `response_format` for JSON** (e.g. JSON object with at least `explanation_text: string` and `headword: string`). The server: (1) validates JSON; (2) TTS `explanation_text` first; (3) TTS `headword` second; (4) concatenates MP3 bytes. If the model returns empty `headword` after a successful `explanation_text`, **MAY** fall back to a single TTS of explanation only, or return `400` with `explanation_invalid` — **document the chosen behavior** in server README. When `LEXIE_HEADWORD_TTS=0`, the same chat completion may still be JSON with only `explanation_text` (simplest single code path) or free text; either way, only the meaning line is TTS’d.

- **Response (error):** JSON `application/json` for machine handling where possible. Examples:  
  - `400` — `{"error":"transcription_empty"}` (Whisper returned nothing after trim)  
  - `400` — `{"error":"unintelligible_audio"}` (heuristic / empty transcript policy)  
  - `401` — `{"error":"unauthorized"}` (missing device key in prod)  
  - `413` — `{"error":"payload_too_large"}`  
  - `502` / `503` — `{"error":"openai_unavailable"}` (after retries exhausted)  
  - `500` — `{"error":"internal"}` (no stack traces in body in prod)  
  - `400` — `{"error":"explanation_invalid"}` — if `response_format` JSON is required and parsing fails, or `explanation_text` is empty, or (when `LEXIE_HEADWORD_TTS=1`) `headword` is missing/invalid per implementation rules (see §3.5 headword text).

### 3.6 `GET /admin/usage` (optional, Phase 1+)

- **Auth:** `Authorization: Bearer <LEXIE_ADMIN_TOKEN>`.  
- **Response:** `200` JSON, e.g. `{"month":"2026-04","explain_count": 42, "cost_usd_estimated": null}`. *Cost estimate* may be `null` until token-based estimation is implemented; **OpenAI billing** remains the source of truth for money.

### 3.7 `GET /admin/metrics` (optional, for local ops app)

- **Auth:** same as admin.  
- **Response:** JSON with rolling counters if implemented (e.g. `errors_24h`, `p95_latency_ms_sampled`); may return `404` in minimal v1.

### 3.8 `GET /admin` — parent **HTML** one-pager (required for Phase 1)

- **Purpose (PRD-locked):** a **single** mobile-tolerant form to view/edit the lone `age_profile`. Not a child dashboard, not analytics.
- **Auth pattern (normative for v1):** The **first** `GET /admin` **MUST** return `200` **without** a secret (so the parent can open the page). **Saving** uses **`PATCH /profile`** from **JavaScript** in that page, with `Authorization: Bearer <LEXIE_ADMIN_TOKEN>` in the `fetch` call only (token entered in a field on the page, or pasted once and kept in `sessionStorage` for that browser session). **MUST NOT** require the admin token in the page URL (no `?token=` in bookmarks). The server does **not** need server-side “admin sessions” or cookies for Phase 1 if the client stores the token in `sessionStorage` and sends the Bearer header on `GET /profile` / `PATCH` only.  
- **Response:** `200` `text/html; charset=utf-8` with embedded or linked CSS, minimal JS for `GET`+`PATCH`+status messages, and fields: `child_name`, `age_years`, `reading_level`, `explanation_style` (optional textarea). On load, if `sessionStorage` has a token, auto-fetch profile; else show “enter admin token” before loading profile.  
- **CORS:** same-origin to the admin page as the API; no CORS preflight for same-origin. If a separate static host is used, **MUST** allow that origin.  
- **A11y:** large tap targets, readable type; `label`+`id` for inputs.

**Implementation note (non-normative):** FastAPI can serve this with `Jinja2Templates` + one template, or `FileResponse` to a checked-in `admin.html` under a `static/` or `template/` path.

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

### 5.1 `error` code → child-adjacent copy (prototype and device)

**Normative for tone** (per PRD): short, calm, one idea, no stack traces. The **server** body uses machine codes below; the **UI** maps them to these **display strings** (tune later; keep length similar).

| `error` (API) | Suggested on-screen / future device line (English) |
|---------------|------------------------------------------------------|
| `unauthorized` | We couldn’t connect. Ask a grown-up to check the bookmark. |
| `audio_too_short` | That was a little too short. Try the button again. |
| `audio_too_long` | That was a little too long. Say one word, then let go. |
| `transcription_empty` | I didn’t catch that. Try again, a little closer. |
| `unintelligible_audio` | I didn’t quite hear that. Try again. |
| `payload_too_large` | That recording is too big. Try a shorter try. |
| `openai_unavailable` | Lexie is taking a break. Try again in a little bit. |
| `rate_limited` | Too many tries. Wait a little, then try again. |
| `internal` | Something went wrong. Try again, or ask a grown-up. |
| `explanation_invalid` | I couldn’t get that one ready. Try asking again, a little bit slower. |

**Browser prototype (not device) errors:** use `alert()` or on-screen `div` for the human line from the table (not raw wire codes to the child). No requirement for TTS of errors in v1. Match PRD *Child-facing error tone* (transport / technical failures): [lexie-word-explainer.PRD.md](../prds/lexie-word-explainer.PRD.md) §5.

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

**Journey-anchored observability (parent / builder questions):** which user journeys need which signals (`/health`, optional explain volume, opt-in `explain_request` rows, **not** “which journey” analytics) — [lexie-word-explainer.journeys-and-observability.md](lexie-word-explainer.journeys-and-observability.md) **§3**.

**Scaling:** for one child, **vertical** scale (bigger VM) only; no horizontal or K8s in v1.

---

## 9. Local parent ops app

- **Location in repo:** [monitoring/lexie-ops/](../../../monitoring/lexie-ops/) (Vite, minimal UI; [README](../../../monitoring/lexie-ops/README.md)).  
- **Purpose:** poll `GET /health` and optionally `GET /admin/usage` / `GET /admin/metrics` with `LEXIE_ADMIN_TOKEN`.  
- **CORS / proxy:** use `.env` `VITE_LEXIE_BASE_URL` and ensure server allows that origin, **or** use Vite `proxy` to avoid CORS during dev.  
- **Not a cost system:** link out to **OpenAI billing** for true spend.

---

## 10. Test plan (Phase 1)

| Layer | What | Traceability |
|-------|------|----------------|
| **Contract (automated)** | `GET /health` 200; `GET /admin` 200 `text/html`; `GET`/`PATCH /profile` 401 without `Authorization: Bearer <LEXIE_ADMIN_TOKEN>`, 200/204-shaped success with full body on 200; `POST /explain` 401 without device key in prod, `400` for `audio_too_short` (or fixture &lt; 0.4s), 413 for oversized part | [validation matrix](lexie-word-explainer.validation-matrix.md) — rows marked **C** |
| **Pipeline (OpenAI mocked)** | Fake STT → known transcript; fake LLM (fixed `explanation_text` / JSON with `headword` when `LEXIE_HEADWORD_TTS=1`); fake TTS returns bytes. Assert: prompt or assembled messages include `age_years` and `reading_level` from SQLite-backed profile; TTS call count 1 or 2 per `LEXIE_HEADWORD_TTS` | [TESTING strategy](lexie-word-explainer.TESTING-strategy.md) §2 |
| **E2E (real keys, staging, optional in CI)** | Journeys 1–3 + Level-0: single word, idiom, out-of-vocabulary but on-topic, parent redirect; measure p95; **not** a merge gate for open-source if keys unavailable | [validation matrix](lexie-word-explainer.validation-matrix.md) — **E2E** |
| **Soak** | 20–50 `POST /explain` sequentially; RSS/handles stable; grep logs for accidental `OPENAI` / token leaks | ad hoc |
| **Manual / eval** | [validation matrix](lexie-word-explainer.validation-matrix.md) “Manual eval set” (sorcerer, phrasal, Hogwarts, &lt;0.5s silence, long clip) | J — manual |

**Exit criteria (merge gate for Phase 1 app code, excluding optional E2E with real keys):** all **contract** + **pipeline (mocked)** tests green; E2E manual pass logged once per release candidate.

---

## 11. Definition of done (Phase 1, commit-ready)

**Aligned to PRD Phase 1 acceptance** (operational, not a legal guarantee):

1. [x] `GET /health` live on deployed **HTTPS** `BASE_URL` (or staging equivalent).  
2. [x] `GET /admin` returns a usable one-pager; parent can `GET`/`PATCH` `age_profile` with `LEXIE_ADMIN_TOKEN` (never in URL).  
3. [x] `POST /explain` works from browser prototype: returns MP3; `Authorization: Bearer` device key in production.  
4. [x] `GET`/`PATCH /profile` behavior matches this SPEC; SQLite holds one profile row, seeded for first test.  
5. [x] Defaults: `LEXIE_LOG_REQUESTS=0`, `LEXIE_HEADWORD_TTS=0`; no raw audio persistence.  
6. [x] p95 &lt; 5s on warm path for short utterances (SLO in §8).  
7. [x] CORS, prototype, and [first-run](phased-delivery-plan.md#first-run-order) documented; child-facing error copy follows §5.1.  
8. [x] [monitoring/lexie-ops/](../../../monitoring/lexie-ops/) can fetch `GET /health` against dev or deploy.  
9. [x] Automated **contract** + **mocked-pipeline** tests (§10) pass; optional real-key E2E at release candidate.

**Builder sign-off (`lexie-server.fly.dev`, 2026-05-01, WX-012):** Items **1–5** and **7–9** verified per project work-log. Item **6:** §8.2 p95 **&lt; 5 s** is **not** met on the current OpenAI-backed warm path — observed **`X-Explain-Latency-Ms`** ~**6–7 s** with `LEXIE_HEADWORD_TTS=0` (Fly + default models). Item **6** is marked complete **with this documented exception**; improving latency is a follow-up (region, VM tier, models, prompts), not a blocker for the rest of Phase 1 acceptance on this host.

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

## 14. Implementation order (reference, code)

1. Project skeleton + env + `/health`  
2. SQLite `age_profile` + seed one row + `GET`/`PATCH` + `GET /admin` HTML + admin CORS as needed  
3. `POST /explain` (Whisper → GPT → TTS) + error mapping (§3.5, §5) + headword JSON path when `LEXIE_HEADWORD_TTS=1` (§3.5)  
4. Prototype static page (or Vite) for PTT  
5. **Deploy** public; verify from internet + hotspot  
6. **lexie-ops** + CORS for localhost  
7. **Contract** + **pipeline (mocked)** tests; optional E2E.  
8. **SPEC** + validation matrix accepted → merge

---

## 15. Phase 1b (Journey 5) — out of scope for Phase 1 code, normative in product

- **Not implemented** in the first app merge unless explicitly scheduled. The **PRD-locked** recovery cap (at most one Level 1 fork round, one Level 2 spell, then forced Level 3) applies when multi-turn or session is added.  
- **Forward-looking (non-binding) API hint:** a future `POST /explain` (or a sibling `POST /session/turn`) **may** accept `session_id` + `turn` metadata; the server **must** then enforce the recovery depth server-side. No stable contract until a separate SPEC revision.

---

## 16. Phase 1 server — implementation blueprint (specification, not this repo’s code)

This section is **authoritative** for *what* the Phase 1 Python service **should** contain. It does **not** require one file per bullet; it requires **testable** behavior and clear boundaries.

### 16.1 Suggested package layout (monolith)

| Path / module | Responsibility |
|---------------|-----------------|
| `app/main.py` | `FastAPI` app instance, middleware (CORS, optional `X-Request-Id`, 2 MiB body size for `/explain` route), `include_router` for `health`, `profile`, `explain`, `static_admin`. |
| `app/config.py` | `pydantic-settings` (or similar): `OPENAI_API_KEY`, `LEXIE_DEVICE_KEY`, `LEXIE_ADMIN_TOKEN`, `LEXIE_LOG_REQUESTS`, `LEXIE_HEADWORD_TTS`, `LEXIE_CORS_ORIGINS` (list), DB path, optional rate limits. Fail fast in production if required secrets are missing. |
| `app/db.py` + `app/models.py` | SQLAlchemy 2.0 (or aiosqlite) engine; **one** `age_profile` table with columns matching §3.3/PRD: `id` (integer PK, single row) or one row with fixed `id=1` — `child_name`, `age_years`, `reading_level`, `explanation_style` (nullable). **Optional** `explain_request` table if/when `LEXIE_LOG_REQUESTS=1` (per §7), not required for `LOG=0` default. |
| `app/deps.py` | FastAPI `Depends` callables: `require_admin` (parse `Authorization: Bearer` vs `settings.lexie_admin_token`); `require_device` (same for `LEXIE_DEVICE_KEY`; dev skip if env unset, logged once). |
| `app/routers/health.py` | `GET /health` JSON. |
| `app/routers/profile.py` | `GET`/`PATCH /profile` with `require_admin`, validation, PATCH partial merge, 429 if rate-limited. |
| `app/routers/explain.py` | `POST /explain`: `UploadFile` → **duration** check (e.g. `pydub`, `wave`, or `ffprobe` subprocess) → `openai` Whisper → `build_explanation` (LLM) → TTS; stream or buffer MP3; return `Response` with `media_type="audio/mpeg"`. |
| `app/services/explain_pipeline.py` | Single place for: timeouts (§5), retry policy for 429/5xx, `LEXIE_HEADWORD_TTS` branching, JSON parse for `explanation_text` / `headword`. |
| `app/services/tts.py` | If headword: two TTS calls, concatenate with `pydub` or raw MP3 byte join if the same format. |
| `app/templates/admin.html` or `app/static/admin.html` | One-page admin per §3.8; `fetch` with Bearer, `sessionStorage` for token. |
| `prototype/` (sibling to `app/`) or `app/static/prototype/` | Browser PTT demo: `getUserMedia`, `MediaRecorder`, `POST` to `/explain` with device key in header from **prompt** or `localStorage` in dev. |

### 16.2 SQLite and migrations

- **DB file:** e.g. `./data/lexie.db` from env, created on first write. **Backup:** parent copies the file; no export UI in v1.  
- **Migrations:** Alembic, or for minimal v1 `create_all` on boot with a one-time “if no row, insert default `age_profile`” seed.  
- **Seeded defaults:** e.g. `age_years: 6`, `child_name: "Child"`, `reading_level: "grade-level"` so first `GET /profile` after admin auth is not empty (PRD: profile before first child test).  
- **Reference DDL and entity diagrams:** [lexie-word-explainer.API-and-data-model.md](lexie-word-explainer.API-and-data-model.md) §2–3.

### 16.3 Explain pipeline (in-order)

1. **Validate** multipart, field `audio`, size ≤ 2 MiB.  
2. **Decode** duration: if &lt; 0.4s → 400 `audio_too_short` (§3.5); if &gt; 30s → 400 `audio_too_long` (§3.5).  
3. **Whisper** (timeout §5) → `raw_transcript`; if empty after trim → 400.  
4. **Load** `age_profile` from DB (if missing row → 500 `internal` or 503, documented).  
5. **LLM** with system+user content per PRD prompt; **if** `LEXIE_HEADWORD_TTS=1`, **request JSON** with `explanation_text` and `headword` (see §3.5). **Max tokens** per §5.  
6. **TTS** explanation; optionally second TTS for headword; concatenate.  
7. **Optional** logging row when `LEXIE_LOG_REQUESTS=1` (redact, retention §7).  
8. **Return** bytes + optional `X-Explain-Latency-Ms`.  

### 16.4 Prototype serving

- **Option A:** `StaticFiles` at `/` or `/prototype` serving `index.html` + `app.js` from a directory in repo.  
- **Option B:** Vite in `monitoring/lexie-ops` style but under `lexie-prototype/`, dev server on localhost, `VITE_LEXIE_BASE_URL` + `VITE_LEXIE_DEVICE_KEY` for local only (document **never** ship device key in client in production — production prototype should prompt per session or use env-injected at build for **staging** only).

### 16.5 Test package layout (when code exists)

- `tests/conftest.py` — in-memory or temp-file SQLite, test client, env overrides, fake OpenAI.  
- `tests/test_contract_*.py` — §10 “Contract” row.  
- `tests/test_pipeline_*.py` — mocked OpenAI returns fixed transcripts/JSON/bytes.  
- `pytest.ini` with asyncio mode if using async app.

**PRD journey ↔ automated tests:** [lexie-word-explainer.validation-matrix.md](lexie-word-explainer.validation-matrix.md).

---

## 17. Related planning documents (authoritative for process)

| File | Role |
|------|------|
| [lexie-word-explainer.validation-matrix.md](lexie-word-explainer.validation-matrix.md) | Journey and Level IDs → C / M / E2E / manual, PRD section refs |
| [lexie-word-explainer.TESTING-strategy.md](lexie-word-explainer.TESTING-strategy.md) | Pyramid, CI gates, mocking strategy |
| [lexie-word-explainer.API-and-data-model.md](lexie-word-explainer.API-and-data-model.md) | API catalog, entity model, reference SQLite, headers/metadata |
| [lexie-word-explainer.journeys-and-observability.md](lexie-word-explainer.journeys-and-observability.md) | PRD journeys vs Phase 1 contract; observability use cases; privacy limits |
| [lexie-word-explainer.RUNBOOK.md](lexie-word-explainer.RUNBOOK.md) | Health → CORS → keys → optional debug logging; symptom table |
| [lexie-word-explainer.BUDGET-AND-ROLLOUT.md](lexie-word-explainer.BUDGET-AND-ROLLOUT.md) | ROM monthly cost (host + OpenAI); M0–M5 rollout and what to test |
| [lexie-word-explainer.MASTER-CHECKLIST.md](lexie-word-explainer.MASTER-CHECKLIST.md) | Single ordered checklist: accounts, implement, M0–M5, DoD, lexie-ops |
| [phased-delivery-plan.md](phased-delivery-plan.md) | Phases, dependencies, first-run, overlap with [PRD](../prds/lexie-word-explainer.PRD.md) |

---

*End of SPEC.*
