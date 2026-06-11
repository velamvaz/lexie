# Lexie work inventory (elaborated)

**Last updated:** 2026-06-09 — **Phase 1 complete; Phase 2 (LX-4) active** — **WX-032** **done**; **WX-034** **done**; **Waveshare board delivered**; **WX-035** **done**  

**Canonical status** for each `WX-*` row lives in [`registry.md`](registry.md). This document is the **elaborated narrative**: objectives, steps, acceptance, and roadmap context. When they disagree, **registry wins** for current status; refresh this file when scope changes.

---

## Section A — Completed

### WX-004 — Project management folder

**What was done:** Introduced a dedicated **`project-management/`** area for execution tracking separate from product **`LX-*`** entries in [`lexie-docs/REGISTRY.md`](../lexie-docs/REGISTRY.md). Added [`SCHEMA.md`](SCHEMA.md) (field definitions), [`registry.md`](registry.md) (work table with `WX-*` ids), [`work-log/`](work-log/) (append-only monthly narrative), [`items/TEMPLATE.md`](items/TEMPLATE.md) for optional deep dives, and [`README.md`](README.md) (conventions).

**Where:** [`project-management/`](../project-management/) at monorepo root.

**Evidence:** Git commit `c93390f` (`chore(pm): add project-management schema, WX registry, work-log`); root [`README.md`](../README.md) links here; [`lexie-docs/REGISTRY.md`](../lexie-docs/REGISTRY.md) points to `WX-*` execution work.

---

### WX-005 — Phase 1 FastAPI server (Part B)

**What was done:** Implemented the **Lexie Word Explainer** backend as a Python package under **`lexie-server/`**: configuration via environment ([`lexie_server/config.py`](../lexie-server/lexie_server/config.py)), SQLite + SQLAlchemy ([`db.py`](../lexie-server/lexie_server/db.py), [`models_orm.py`](../lexie-server/lexie_server/models_orm.py)), auth helpers ([`deps.py`](../lexie-server/lexie_server/deps.py)), OpenAI pipeline ([`services/pipeline.py`](../lexie-server/lexie_server/services/pipeline.py)), audio duration ([`audioutil.py`](../lexie-server/lexie_server/audioutil.py)), prompts ([`prompts.py`](../lexie-server/lexie_server/prompts.py)), FastAPI app ([`main.py`](../lexie-server/lexie_server/main.py)), contract tests ([`tests/`](../lexie-server/tests/)), operator admin HTML ([`templates/admin.html`](../lexie-server/lexie_server/templates/admin.html)), PTT browser prototype ([`static_prototype/`](../lexie-server/lexie_server/static_prototype/)), [`README.md`](../lexie-server/README.md) and [`.env.example`](../lexie-server/.env.example).

**Evidence:** Git commit `b1d6a85` (`feat(lexie-server): Phase 1 FastAPI Word Explainer API`); master checklist Part **B1–B7** marked complete in [`lexie-word-explainer.MASTER-CHECKLIST.md`](../lexie-docs/lexie/committed-to-build/lexie-word-explainer.MASTER-CHECKLIST.md).

**Part B mapping (B# → artifact):**

| Checklist | Implementation |
|-----------|----------------|
| **B1** | FastAPI app package [`lexie-server/`](../lexie-server/), aligned with SPEC and API-and-data-model docs. |
| **B2** | [`config.py`](../lexie-server/lexie_server/config.py) + [`.env.example`](../lexie-server/.env.example) + [`README.md`](../lexie-server/README.md) for `OPENAI_API_KEY`, `LEXIE_DEVICE_KEY`, `LEXIE_ADMIN_TOKEN`, `LEXIE_LOG_REQUESTS`, `LEXIE_HEADWORD_TTS`, `LEXIE_CORS_ORIGINS`. |
| **B3** | [`models_orm.py`](../lexie-server/lexie_server/models_orm.py) `AgeProfile`, `ExplainRequest`; [`db.py`](../lexie-server/lexie_server/db.py) `create_tables`, `seed_profile_if_empty`; lifespan in [`main.py`](../lexie-server/lexie_server/main.py). |
| **B4** | Routers: [`health.py`](../lexie-server/lexie_server/routers/health.py) `/health`, [`profile.py`](../lexie-server/lexie_server/routers/profile.py) `/profile`, [`explain.py`](../lexie-server/lexie_server/routers/explain.py) `/explain`, [`admin.py`](../lexie-server/lexie_server/routers/admin.py) `/admin`; [`usage.py`](../lexie-server/lexie_server/routers/usage.py) admin usage. |
| **B5** | [`pipeline.py`](../lexie-server/lexie_server/services/pipeline.py): Whisper → chat JSON → TTS; limits in `explain` route and pipeline; errors as JSON per SPEC. |
| **B6** | [`static_prototype/index.html`](../lexie-server/lexie_server/static_prototype/index.html); mounted at `/prototype` in [`main.py`](../lexie-server/lexie_server/main.py). |
| **B7** | [`tests/test_api.py`](../lexie-server/tests/test_api.py), [`tests/conftest.py`](../lexie-server/tests/conftest.py); mocked pipeline for `/explain`. |

---

### Vault and accounts (checklist-only — no WX id)

**V1 — Private vault:** A **Personal/Private** 1Password vault exists for Lexie secrets so access is under your control.

**V2 — Item per secret type:** Structure for items such as **Lexie — OpenAI API**, **`LEXIE_DEVICE_KEY`**, **`LEXIE_ADMIN_TOKEN`** (or Secure Notes / custom fields) so each secret type has a clear home.

**V3 — Revoke exposed keys:** Any API key that appeared in chat or other unsafe channels was **revoked**; only the current value stored in 1Password remains valid.

**A1 — OpenAI account:** OpenAI Platform account with **API** billing enabled (ChatGPT Plus ≠ API).

**A2 — API key + budget:** API key created and stored per **V2**; **monthly budget / alerts** configured in the OpenAI dashboard per SPEC and [`lexie-word-explainer.BUDGET-AND-ROLLOUT.md`](../lexie-docs/lexie/committed-to-build/lexie-word-explainer.BUDGET-AND-ROLLOUT.md).

---

## Section B — Phase status

**Phase 1 complete (2026-05-03).** LX-1 server shipped and signed off: SPEC §11 done, 32 tests green, Fly live, ops settled, lexie-ops verified. Full history in [Section A](#section-a--completed) and [work-log](work-log/).

**Phase 2 active — LX-4 hardware track.** Bridge (**WX-022**–**WX-025**) **done**; **WX-034** Path B pivot **done**; **WX-026** **done**; active bench [**WX-035** → **WX-028** → **WX-036** → **WX-029** → **WX-033** → **WX-032**](registry.md) ([Section D3](#section-d3--lx-4-bench-execution-path-b-waveshare)). Path A archive: [Section D2](#section-d2--lx-4-bench-execution-path-a--archive). See [Section D](#section-d--phase-2-hardware-track-lx-4).

**Parallel non-blocking software polish** (no gate on hardware): latency SLO, validation G2–G7, Phase 1b Journey 5. See [Section E](#section-e--parallel-software-polish).

**How to move work:** Edit [`registry.md`](registry.md) (**Status**, **Updated**), append a line to [`work-log/`](work-log/).

---

## Section C — Phase 1 planned items (archive)

**Superseded (see registry):** **WX-001** and **WX-003** were broad umbrellas; execution is now **WX-013** (pytest) and **WX-014–WX-018** (checklist C1–C6 steps). Do **not** reopen WX-001 / WX-003.

### WX-002 — Device and admin tokens in 1Password (A6 / A7) *(registry: done, 2026-05-02)*

**Objective:** Create two **long random** secrets, store them only in 1Password, and prepare to paste them into **gitignored** `.env` (local) or host secrets (production)—never commit them.

**What was done:** 1Password CLI authenticated; **Private**/**Shared** vaults available; **OpenAI API** credential and device/admin material live in the vault and are copied into **`lexie-server/.env`** for local dev only (gitignored).

**Steps:**

1. On a trusted machine, generate two distinct values (e.g. `openssl rand -hex 32` twice).
2. Save **`LEXIE_DEVICE_KEY`** in 1Password (prototype / future firmware); label clearly.
3. Save **`LEXIE_ADMIN_TOKEN`** in a **separate** item or field; used for `/admin` and `GET`/`PATCH` `/profile` only.
4. Do **not** paste these into chat, tickets, or screenshots.

**Done when:** Both values exist in 1Password per **V2**; master checklist **A6** and **A7** can be ticked; you can copy them into `lexie-server/.env` for local testing.

**Depends on:** Nothing technical—can run before or in parallel with **WX-013**–**WX-018**. **WX-015**–**WX-017** are easier once **WX-002** is done so `.env` has real device and admin tokens.

---

### WX-013 — Preflight: pytest on Python 3.11 or newer *(done)*

**Objective:** Prove automated contract tests pass (mocked explain; **no** live OpenAI).

**Steps:**

1. Install **Python 3.11+** (python.org, Homebrew, or `pyenv`).
2. `cd lexie-server && python3.11 -m venv .venv && source .venv/bin/activate` (Windows: `.venv\Scripts\activate`).
3. `pip install -U pip && pip install -e ".[dev]"`.
4. `pytest -v`.

**Done when:** `pytest` exits **0**. **CI:** [`.github/workflows/lexie-server-pytest.yml`](../.github/workflows/lexie-server-pytest.yml) runs the same on **Ubuntu** / **Python 3.11** on push and PR (paths: `lexie-server/**`). Confirm the workflow is **green** on `main` after push.

**Depends on:** Nothing. **Complete before WX-014** so regressions show up before manual M0.

---

### WX-014 — M0: dotenv, server, and health (C1–C2)

**Objective:** Run the app locally with secrets from 1Password and confirm the process is healthy.

**Steps:**

1. Copy [`lexie-server/.env.example`](../lexie-server/.env.example) to **`lexie-server/.env`**. Set **`OPENAI_API_KEY`**; set **`LEXIE_DATA_DIR`** if needed; add device/admin tokens when **WX-002** is done.
2. `uvicorn lexie_server.main:app --reload --host 0.0.0.0 --port 8000` from `lexie-server/`.
3. `GET http://127.0.0.1:8000/health` → **200** JSON, `"ok": true`.

**Done when:** C1–C2 satisfied.

**Depends on:** **WX-013** done. **WX-002** optional for this step (no profile/explain auth yet).

---

### WX-015 — M0: profile admin auth (C3)

**Objective:** Verify admin-only access to `/profile`.

**Steps:**

1. `GET /profile` with no `Authorization` → **401**.
2. `GET /profile` with `Authorization: Bearer <LEXIE_ADMIN_TOKEN>` → **200** and JSON body.
3. Optionally `PATCH /profile` with a small change and verify response.

**Done when:** C3 satisfied.

**Depends on:** **WX-014**; **`LEXIE_ADMIN_TOKEN`** in `.env` (typically **WX-002**).

---

### WX-016 — M0: admin HTML (C4)

**Objective:** Exercise the browser admin page against a running server.

**Steps:**

1. Open `http://127.0.0.1:8000/admin` → **200** `text/html`.
2. Paste admin token (per [`admin.html`](../lexie-server/lexie_server/templates/admin.html) / `sessionStorage` flow), load profile, save, refresh and confirm persistence.

**Done when:** C4 satisfied.

**Depends on:** **WX-014**; **WX-002** for token.

---

### WX-017 — M0: `POST /explain` real pipeline (C5)

**Objective:** End-to-end Whisper → chat → TTS (or clear **400** JSON for bad input).

**Steps:**

1. Ensure **`ffmpeg`** is on **`PATH`** (pydub duration / MP3 handling).
2. Use **`/prototype/`** or another client; send **`POST /explain`** with `multipart` field **`audio`**, plus **`Authorization: Bearer <LEXIE_DEVICE_KEY>`** if `LEXIE_DEVICE_KEY` is set (**WX-002**).
3. Expect **200** `audio/mpeg` with MP3 bytes, or **400** with JSON for too-short / empty transcript / policy per SPEC.

**Done when:** C5 satisfied at least once with acceptable audio.

**Depends on:** **WX-014**; **WX-002** if device key enforcement is on; **WX-013** recommended first.

---

### WX-018 — M0: privacy — no raw audio on disk (C6) *(registry: done, 2026-05-03)*

**Objective:** Confirm default behavior matches SPEC §7 (no raw uploads persisted as files).

**Steps:**

1. Keep **`LEXIE_LOG_REQUESTS=0`** (default).
2. After **WX-017**, confirm you are not writing uploaded blobs to disk as part of normal operation; DB rows (if any) should match logging policy in SPEC / data-model doc.

**Done when:** C6 satisfied; master checklist **Part C** can be ticked when **WX-014**–**WX-018** are all **done**.

**Depends on:** **WX-017** (or a skipped explain if you only verify logging flags—prefer running explain once).

**What was done:** [`explain.py`](../lexie-server/lexie_server/routers/explain.py) reads upload into memory only; pipeline uses **`BytesIO`** / OpenAI APIs — no audio **`open()`** for persistence. [`README.md`](../lexie-server/README.md) documents defaults and **`LEXIE_LOG_REQUESTS`**. Contract tests: no **`explain_request`** row when logging off; one row when on; **no `*.webm` / `*.wav` / `*.mp3`** under **`LEXIE_DATA_DIR`** after mocked **`POST /explain`**.

---

## Section D — Future milestones (master checklist Parts C–J and extras)

The following restates [**lexie-word-explainer.MASTER-CHECKLIST.md**](../lexie-docs/lexie/committed-to-build/lexie-word-explainer.MASTER-CHECKLIST.md) items with **what**, **why it matters**, and **typical dependency**. Part **C** step-by-step is **WX-013**–**WX-018** (Section C); items below add context or post-M0 scope.

### Dev workflow: V4, V5

| Item | What | Why it matters | Typical owner / dependency |
|------|------|----------------|----------------------------|
| **V4** | Copy secrets from 1Password into **gitignored** `.env` locally; on deploy, paste into **host** secret UI—1Password stays canonical. | Prevents secrets in git and keeps a single source of truth. | You; before **WX-014** / production. |
| **V5** | *(Optional)* 1Password CLI (`op run`) to inject env without leaving secrets in shell history. | Safer local and CI patterns. | Optional anytime. |

### Optional setup: A3, A4, A5

| Item | What | Why it matters | Typical owner / dependency |
|------|------|----------------|----------------------------|
| **A3** | Choose a **host** (Fly, Railway, Render, VPS); account + payment if needed. | Required before **Part D** deploy. | **Fly.io** — recorded under **WX-019**; see [`lexie-server/fly.toml`](../lexie-server/fly.toml). |
| **A4** | *(Optional)* Custom **domain** + know where **DNS** is managed—or use host subdomain only. | Clean URLs and later firmware config. | You; can follow **D1**. |
| **A5** | *(Optional)* External **uptime** (e.g. UptimeRobot) for public `/health`. | Alerts when the service is down. | After **D2**. |

### Part C (M0) — checklist cross-reference

| Item | What | Why it matters | Typical owner / dependency |
|------|------|----------------|----------------------------|
| **C1** | Local `.env` with real keys from vault. | Safe dev and parity with prod secrets pattern. | **WX-014** |
| **C2** | `uvicorn` + `/health` **200**. | Confirms process and routing. | **WX-014** |
| **C3** | `/profile` **401** without admin; **200** with Bearer. | Validates admin gate. | **WX-015** + **WX-002** |
| **C4** | `/admin` HTML + token + save profile. | Parent journey locally. | **WX-016** |
| **C5** | `POST /explain` returns audio or structured error. | Core product path. | **WX-017**; **ffmpeg** on PATH |
| **C6** | No raw audio files on disk; default logging off. | Privacy per SPEC §7. | **WX-018** *(done)* |

### Part D (M1) — Public HTTPS and reachability (WX-006) *(registry: done — D2 met, 2026-05-04)*

**Live:** **`https://lexie-server.fly.dev`** — **`GET /health`** returns **200** JSON with **`"ok": true`** (checklist **D2**).

**Repo:** [`Dockerfile`](../lexie-server/Dockerfile), [`.dockerignore`](../lexie-server/.dockerignore), [`fly.toml`](../lexie-server/fly.toml), [README — Deploy / Fly](../lexie-server/README.md#deploy-m1--wx-006). **Still on you:** set **`fly secrets`** for real **`POST /explain`** / admin (**`OPENAI_API_KEY`**, **`LEXIE_DEVICE_KEY`**, **`LEXIE_ADMIN_TOKEN`**, **`LEXIE_CORS_ORIGINS`** including `https://lexie-server.fly.dev` if the browser calls from that origin); **D3** phone on cellular **`/health`**; **D5** store **`BASE_URL`** in 1Password.

| Item | What | Why it matters | Typical dependency |
|------|------|----------------|---------------------|
| **D1** | Deploy app to host; bind env in **dashboard/secrets**, not only laptop `.env`. | Production serving. | **A3**, **M0** complete locally |
| **D2** | `https://<BASE_URL>/health` → **200**. | Confirms TLS and routing. | **D1** |
| **D3** | Hit `/health` from **phone on cellular**. | Rules out home-only networking issues. | **D2** |
| **D4** | *(Optional)* External uptime ping to `/health`. | Operations visibility. | **D2**, **A5** |
| **D5** | Store **BASE_URL** in 1Password for Lexie Card firmware / provisioning. | Stable reference for clients. | **D2** |

### Part E (M2) — Child browser path (WX-007) *(registry: done, 2026-05-04)*

**Execution:** Open **`https://<BASE_URL>/prototype/`** on Fly (e.g. **`https://lexie-server.fly.dev/prototype/`**); paste **`LEXIE_DEVICE_KEY`**; hold-to-talk. Same-origin requests avoid CORS configuration for that URL. Full steps: [README — Child browser prototype (M2 / WX-007)](../lexie-server/README.md#child-browser-prototype-m2--wx-007). **E4–E6** (latency journeys, runbook) remain **ad hoc** (validation matrix / journeys).

| Item | What | Why it matters | Typical dependency |
|------|------|----------------|---------------------|
| **E1** | Set **`LEXIE_CORS_ORIGINS`** for prototype origin (e.g. `http://localhost:5173`); redeploy. | Browser `fetch` from another origin works. | **D1** if not localhost-only |
| **E2** | Open prototype in **secure context** (localhost/HTTPS); grant **mic**. | `getUserMedia` requirements per SPEC §6. | **E1** |
| **E3** | Device key only via header (not query string) per README. | Avoids leaking token in URLs/logs. | **WX-002** |
| **E4** | J1-style test (“sorcerer”); latency ~**&lt; 5 s** warm per SPEC §8.2. | Validates UX target. | **E2**, warm request |
| **E5** | J2 word+context, J3 “What is Hogwarts?” — redirect tone acceptable. | PRD journeys. | **E4** |
| **E6** | On failure, follow [**RUNBOOK**](../lexie-docs/lexie/committed-to-build/lexie-word-explainer.RUNBOOK.md) §1 A→E. | Consistent triage. | Any E# failure |

### Part F (M3) — Parent admin on real host (WX-008) *(registry: done, 2026-05-04)*

**Done:** **`https://lexie-server.fly.dev/admin`** — **F1–F4** verified (token in page only, load/save/refresh, explain reflects profile). Checklist: [README — Parent admin on production (M3 / WX-008)](../lexie-server/README.md#parent-admin-on-production-m3--wx-008).

| Item | What | Why it matters | Typical dependency |
|------|------|----------------|---------------------|
| **F1** | Open `https://<BASE_URL>/admin` (no token in URL). | Safe admin entry. | **D2** |
| **F2** | Paste admin token; load profile. | Auth flow on prod. | **F1**, **WX-002** |
| **F3** | Change `age_years` / `reading_level`; save; persist after refresh. | Profile storage on host. | **F2** |
| **F4** | Next explain reflects new profile (hear or inspect with logging). | End-to-end profile → prompt. | **F3**, **C5** on host |

### Part G (M4) — E2E shakedown (WX-009) *(registry: **done** — 2026-05-05)*

**Outcome recorded:** **G1** (short word / **`/prototype/`**) verified on **`https://lexie-server.fly.dev`** after **`LEXIE_HEADWORD_TTS=0`** on Fly and in [`.env.example`](../lexie-server/.env.example); pipeline timing investigation showed second headword TTS + concat was ~**2.7 s** of prior ~**11 s** server time; prod warm sample **`X-Explain-Latency-Ms`** ~**6227**. Deploy: commit **`41448e1`**. Remaining matrix rows **G2–G7** are still valid checks; run **ad hoc** or when hardening for a wider release.

**Execution:** Run Part **G** rows against **`https://lexie-server.fly.dev`** (**`/prototype/`**, **`/admin`** as needed). Map scenarios to [`lexie-word-explainer.validation-matrix.md`](../lexie-docs/lexie/committed-to-build/lexie-word-explainer.validation-matrix.md). [**RUNBOOK**](../lexie-docs/lexie/committed-to-build/lexie-word-explainer.RUNBOOK.md) for failures.

| Item | What | Why it matters | Typical dependency |
|------|------|----------------|---------------------|
| **G1** | **Sorcerer** — short word, clear audio. | Baseline J1. | **E4** |
| **G2** | Phrasal / multi-word. | Coverage of utterance types. | **G1** |
| **G3** | “What is Hogwarts?” — warm redirect, audible. | J3. | **G1** |
| **G4** | ~**0.4 s** clip → **400**; calm UX per SPEC §5.1 if UI maps copy. | Error path. | Prototype or device UI |
| **G5** | Long clip or **&gt;2 MiB** → reject per SPEC. | Abuse/size limits. | **G1** |
| **G6** | *(Optional)* Messy utterance (J5 L0), one PTT. | Real kid audio. | **G1** |
| **G7** | Wrong device key → **401** / friendly path. | Security UX. | **WX-002** |

Validation detail: [`lexie-word-explainer.validation-matrix.md`](../lexie-docs/lexie/committed-to-build/lexie-word-explainer.validation-matrix.md).

### Part H (M5) — Steady operation (WX-010) *(registry: **done** — 2026-05-07)*

| Item | What | Why it matters | Typical dependency |
|------|------|----------------|---------------------|
| **H1** | **`LEXIE_LOG_REQUESTS=0`** in production; reset after debug. | Privacy default. | **D1** |
| **H2** | OpenAI budget alert still on; note $/explain after a week. | Cost control. | **A2**, traffic |
| **H3** | Host sized to avoid long **cold** first explain (min instances / RUNBOOK §4). | Latency SPEC. | **D1** |
| **H4** | Re-read [**journeys-and-observability**](../lexie-docs/lexie/committed-to-build/lexie-word-explainer.journeys-and-observability.md) §3 — default privacy expectations. | Align ops with product. | Before wide use |

### Part I — lexie-ops (optional) (WX-011) *(registry: **done** — 2026-05-03)*

| Item | What | Why it matters | Typical dependency |
|------|------|----------------|---------------------|
| **I1** | `cd monitoring/lexie-ops && npm install`. | Local monitor app. | Node |
| **I2** | `.env` from `.env.example`; set `VITE_LEXIE_BASE_URL` or proxy per README. | Points UI at your server. | **D2** optional |
| **I3** | `npm run dev`; ping `/health` → **200** JSON. | Confirms wiring. | **I2** |
| **I4** | If CORS error, add origin on server or use proxy mode. | Browser safety rules. | **E1** |

**Recorded 2026-05-03:** Part I **I1–I4** closed. [`monitoring/lexie-ops/README.md`](../monitoring/lexie-ops/README.md) documents **Point at production** — **`VITE_PROXY_TARGET=https://lexie-server.fly.dev`** (or your **`BASE_URL`**) so the browser uses same-origin **`/__lexie/health`** and Vite proxies to Lexie (**no `LEXIE_CORS_ORIGINS`** change). Smoke: **`GET http://127.0.0.1:5175/__lexie/health`** → **200** with Fly JSON.

### Part J — Definition of done (SPEC §11) (WX-012) *(registry: **done** — 2026-05-01)*

| Item | What | Why it matters | Typical dependency |
|------|------|----------------|---------------------|
| **J1** | SPEC §11 items 1–9 for **your** environment (HTTPS, admin, explain, profile, defaults, p95, CORS docs, ops health, tests). | Formal Phase 1 exit. | **D–H** as applicable |
| **J2** | Child-facing error copy / PRD error tone on at least one synthetic failure. | Trust and clarity. | **G4** / errors |
| **J3** | No secrets in repos, screenshots, chat, URLs; 1Password canonical. | Security. | Ongoing |

**Recorded 2026-05-01:** [SPEC §11](../lexie-docs/lexie/committed-to-build/lexie-word-explainer.SPEC.md) checkboxes updated in-repo. Prod smoke: **`https://lexie-server.fly.dev`** **`GET /health`** **200**; **`GET /admin`** **200**; **`GET /prototype/`** **200**; **`POST /explain`** without device key **401**. **`pytest`** **32** passed. **lexie-ops:** `VITE_PROXY_TARGET=https://lexie-server.fly.dev` + Vite **`/__lexie/health`** → **200** JSON. **§8.2:** warm **`X-Explain-Latency-Ms`** remains ~**6–7 s** with **`LEXIE_HEADWORD_TTS=0`** — **documented exception** vs p95 **&lt;5 s** (OpenAI path / Fly); tune later. **J2:** [`static_prototype/index.html`](../lexie-server/lexie_server/static_prototype/index.html) maps API / FastAPI **`detail.error`** to SPEC **§5.1** display strings.

**SPEC reference:** [`lexie-word-explainer.SPEC.md`](../lexie-docs/lexie/committed-to-build/lexie-word-explainer.SPEC.md) §10–11.

---

### WX-019 — M1 ops: record Fly and capacity plan in PM *(registry: done, 2026-05-04)*

**Objective:** Lock execution choices in PM so deploy and observability work stay aligned.

**Recorded:**

- **Host (A3):** **Fly.io** — app config in **[`lexie-server/fly.toml`](../lexie-server/fly.toml)** (`primary_region`, **`[mounts]`** → **`/data`**, **`[http_service.checks]`** → **`/health`**, **`min_machines_running = 1`** to limit cold starts on **`POST /explain`**).
- **Capacity:** target **~100 explains in the first 10 days**, then titrate using OOM / latency / OpenAI usage (see **[BUDGET-AND-ROLLOUT](../lexie-docs/lexie/committed-to-build/lexie-word-explainer.BUDGET-AND-ROLLOUT.md)** and [Part H — steady operation](#part-h-m5--steady-operation-wx-010)).
- **Platform metrics (no code):** Fly **[Prometheus query API](https://fly.io/docs/monitoring/metrics/)** at `https://api.fly.io/prometheus/<org-slug>/` (instant + range queries; **MetricsQL**); managed Grafana **[fly-metrics.net](https://fly-metrics.net)**; built-in series (`fly_app_http_*`, `fly_instance_memory_*`, **`fly_instance_exit_oom`**, **`fly_volume_*`**); optional app **`[metrics]`** scrape in `fly.toml`; **[Logs API](https://fly.io/docs/monitoring/logs-api-options/)** for stdout. Runbook + in-app telemetry: **WX-021** ([README § Observability](../lexie-server/README.md#observability-wx-021)).

**Done when:** This section + registry row exist; team agrees Fly remains default host until explicitly changed.

---

### WX-020 — DB-backed explain telemetry *(registry: done, 2026-05-04)*

**Objective:** Persist **privacy-safe** per-request telemetry for **`POST /explain`** in SQLite (same DB as profile), **separate** from **`explain_request`** (which holds PII when **`LEXIE_LOG_REQUESTS=1`**).

**Schema (concept):** `explain_telemetry` — `request_id`, `created_at`, `http_status`, low-cardinality **`outcome`**, **`failed_stage`** (`duration` / `stt` / `llm` / `tts` / `upload` / null), stage **milliseconds** (`duration_check_ms`, `whisper_ms`, `chat_ms`, `tts_ms`, `headword_ms`, `concat_ms`), **`total_ms`**, **`upload_bytes_bucket`**, **`audio_content_class`**. **No** transcript, explanation text, or audio.

**Config:** **`LEXIE_STORE_TELEMETRY=1`** to enable inserts (default **off** in **`.env.example`**). Independent of **`LEXIE_LOG_REQUESTS`**.

**Implementation:** [`lexie_server/models_orm.py`](../lexie-server/lexie_server/models_orm.py) **`ExplainTelemetry`**; [`pipeline.py`](../lexie-server/lexie_server/services/pipeline.py) returns **`ExplainPipelineResult`** with **`PipelineTimings`**; [`explain.py`](../lexie-server/lexie_server/routers/explain.py) writes one row per request when enabled; tests in **`tests/test_api.py`**, **`tests/test_pipeline_simulation.py`**.

**Done when:** `pytest` green; README documents flag and retention (prune old rows periodically on small Fly volumes).

---

### WX-021 — Telemetry dashboards and Fly platform runbook *(registry: done, 2026-05-04)*

**Objective:** **Custom admin** dashboards reading **`explain_telemetry`** (aggregate JSON) and a **runbook** for Fly’s Prometheus API + **`fly-metrics.net`**.

**Delivered:** [`lexie_server/routers/telemetry.py`](../lexie-server/lexie_server/routers/telemetry.py) — **`GET /admin/telemetry/summary`**, **`/recent`**, **`/count`** (admin Bearer); [`admin.html`](../lexie-server/lexie_server/templates/admin.html) — “Explain telemetry” buttons + JSON output; [README — Observability (WX-021)](../lexie-server/README.md#observability-wx-021) — Fly query base URL, auth header forms, example series, logs link, optional **`[metrics]`** note. Tests: [`tests/test_telemetry.py`](../lexie-server/tests/test_telemetry.py).

---

---

## Section D — Phase 2: Hardware track (LX-4)

### WX-022 — Connectivity de-risk: D3 + hotspot + D5 *(registry: done, 2026-05-03)*

**Objective:** Prove the server is reachable from **beyond home Wi-Fi** — the network path the future device will actually use (SPEC §1.2, PRD connectivity section).

**Steps:**

| Step | What | Passes when |
|------|------|-------------|
| **D3** | Phone, Wi-Fi off, cellular on — open `https://lexie-server.fly.dev/health` | **200** JSON `{"ok":true}` |
| **Hotspot stretch** | Phone hotspot on; laptop joins that Wi-Fi; open `/health` and optionally `/prototype/` for one explain | **200** health; explain plays audio |
| **D5** | Save exact `BASE_URL` in 1Password (Secure Note: "Lexie — production URL") | Note saved |

**Why hotspot matters:** the device is a Wi-Fi client that routes through the parent's phone hotspot when away from home — not a cellular device itself. Testing from a laptop on hotspot is a closer simulation than cellular browser alone.

**Recorded (2026-05-03):** D3 cellular `/health` → **200** ✓. Hotspot (laptop on phone hotspot) `/health` → **200** ✓. D5 `BASE_URL` saved in 1Password. WX-006 tail closed. LX-4 device connectivity de-risked.

---

### WX-023 — Firmware handoff doc

**Objective:** A concise, normative API reference for **LX-4 firmware implementers** — so hardware work can begin without needing to read the full SPEC.

**File:** [`lexie-docs/lexie/committed-to-build/lexie-word-explainer.DEVICE-INTEGRATION.md`](../lexie-docs/lexie/committed-to-build/lexie-word-explainer.DEVICE-INTEGRATION.md)

**Sections:** `BASE_URL` (from 1Password D5); `GET /health` liveness; `POST /explain` shape, auth header, response; limits (2 MiB, 30 s, 0.4 s); TLS requirements; `LEXIE_DEVICE_KEY` sourcing and flash-at-provisioning note; what is **not** for the device (`/profile`, `/admin`, `/admin/telemetry/*`); SPEC §5.1 error codes for LED/audio mapping; OpenAI note (server calls OpenAI; device never does).

**Done when:** file exists and is linked from [SPEC](../lexie-docs/lexie/committed-to-build/lexie-word-explainer.SPEC.md) header or [README](../lexie-server/README.md).

---

### WX-024 — LX-4 platform decision and bringup scaffold *(registry: done, 2026-05-03)*

**Objective:** Decide hardware platform, audio transport, and create a minimal scaffold so firmware development can begin.

**Decided (2026-05-03):**

| Decision | Choice | Rationale |
|----------|--------|-----------|
| **Platform** | **Seeed XIAO ESP32-S3** (~$8) | 21×17.5 mm — smallest ESP32-S3 board; USB-C LiPo charging built-in; JST battery connector; I2S pins native; fits inside **Lexie Card** ID-1 shell (see [`hardware/lexie-plaud-form-factor.html`](../hardware/lexie-plaud-form-factor.html)); ~2 s boot vs ~30 s for Pi Zero |
| **Audio (mic)** | **INMP441** I2S MEMS mic | Tiny (4×3 mm); I2S native; no USB audio hat needed |
| **Audio (amp + speaker)** | **MAX98357A** I2S amp + slim 8Ω 0.5W speaker (~30×20 mm) | Wires directly to XIAO I2S pins; no extra hat |
| **Battery** | **503040** thin LiPo ~400 mAh | 5 mm thick, 30×40 mm — fits **Lexie Card** ≤ ~8 mm stack; charges via USB-C on XIAO |
| **Firmware language** | **MicroPython** | Sufficient for button → record → HTTP POST → play; avoids C++ for Phase 2 |
| **Audio transport** | **WAV/PCM** to start | Simplest; evaluate Opus compression if latency is a concern after real-device testing |

**Pi Zero 2W rejected** primarily on **boot time** (~30 s Linux boot is a product-level problem for Lexie Card — a child picks it up and expects immediate PTT).

**Amended (2026-05-22, WX-034):** Active bench platform is **Waveshare ESP32-S3-AUDIO-Board** (Path B). Table above is **historical Path A lock**; parts remain spare. See [lx-4-platform-pivot-waveshare.md](lx-4-platform-pivot-waveshare.md) and [lx-4-waveshare-device.PRD.md](../lexie-docs/lexie/prds/lx-4-waveshare-device.PRD.md).

---

### WX-025 — WiFi provisioning design for LX-4 device *(registry: done, 2026-05-03)*

**Objective:** Define how home + hotspot SSIDs and `BASE_URL` are stored on the device (PRD open question 7).

**Decided (2026-05-03):**

**Mechanism: USB serial, one-time setup.** Parent connects XIAO to laptop via USB-C (same cable used for charging), runs a short Python provisioning script that writes a JSON config file to the XIAO's onboard flash (8 MB filesystem). Re-run only if credentials change.

**Config shape stored in flash (`config.json`):**

```json
{
  "networks": [
    {"ssid": "HomeWiFi",       "password": "..."},
    {"ssid": "Parent1Hotspot", "password": "..."},
    {"ssid": "Parent2Hotspot", "password": "..."}
  ],
  "base_url": "https://lexie-server.fly.dev",
  "device_key": "..."
}
```

**3 network profiles:** home AP + 2 parent hotspots (two parents with separate phones). Firmware tries SSIDs in order on boot until one connects — device auto-switches between home and whichever hotspot is available; no child interaction required.

**`BASE_URL` and `device_key`** sourced from 1Password at provisioning time; never hardcoded in firmware source.

**Phase 3 upgrade path:** SoftAP provisioning (device becomes a temporary AP; parent fills a browser form) for a more polished out-of-box setup experience — does not need to be built for Phase 2.

---

## Section D2 — LX-4 bench execution (Path A — archive)

**Status:** **Superseded 2026-05-22** by [Section D3](#section-d3--lx-4-bench-execution-path-b-waveshare) (**WX-034**). Docs retained for history and spare parts.

**Assumption:** BOM parts received (XIAO ESP32-S3, LiPo, MAX98357, INMP441, speaker, breadboard, dupont, soldering kit). **Normative API:** [`lexie-word-explainer.DEVICE-INTEGRATION.md`](../lexie-docs/lexie/committed-to-build/lexie-word-explainer.DEVICE-INTEGRATION.md). **Depends on:** [Seeed XIAO ESP32S3 wiki](https://wiki.seeedstudio.com/xiao_esp32s3_getting_started/) for pinout and LiPo polarity.

**Original order:** **WX-026** → **WX-027** → **WX-028** → **WX-029** → (**WX-030** and **WX-031** in either order) → **WX-033** → **WX-032**.

**Scaffold:** There is no `firmware/` tree yet; **WX-028** acceptance should introduce a minimal MicroPython layout (e.g. `firmware/` + README); **WX-033** may add a host script under e.g. `tools/` (document in the same README).

### WX-026 — Unbox + inventory + verify ordered SKUs *(registry: done, 2026-05-05)*

**Objective:** Confirm the shipment matches the intended Lexie M1 bench BOM before soldering or powering from LiPo.

**Evidence:** [`items/WX-026.md`](items/WX-026.md).

| Step | What | Passes when |
|------|------|-------------|
| **Inventory** | Lay out boards, cell, speaker, breadboard kit, dupont, iron | Nothing missing for first wiring pass |
| **XIAO** | Visual + silkscreen / listing | **Plain XIAO ESP32-S3** — **not** “Sense” (no camera module) |
| **Polarity prep** | Do **not** plug LiPo into XIAO until **WX-027** | — |

**Done when:** Checklist ticked; optional photo or one-line note in [work-log](work-log/2026-05.md).

---

### WX-027 — Solder prep + safe power documentation *(registry: superseded, 2026-05-22)*

**Status:** **Superseded** — partial work done (XIAO headers, MAX98357 + terminal); round INMP441 not finished. Path B active.

**Objective:** Make breakouts breadboard-ready and eliminate LiPo polarity ambiguity.
**Normative parts context:** [lx-4-path-a-component-kit.md](lx-4-path-a-component-kit.md) (Path A fixed kit, header type, jig wording).  
**Bench layout (machine-readable):** [lx-4-path-a-bench-layout.md](lx-4-path-a-bench-layout.md).

| Step | What | Passes when |
|------|------|-------------|
| **Solder** | Male headers on **MAX98357** and **INMP441**; speaker wires to amp **±** (strip pigtail, not LiPo JST) | Joints solid; no bridged pins |
| **XIAO** | Optional: solder pin headers for breadboard / dupont | Matches your wiring plan |
| **LiPo** | Multimeter **DC V** (red lead in **VΩ** jack); compare leads to [Seeed LiPo guidance](https://wiki.seeedstudio.com/xiao_esp32s3_getting_started/) | Table or photo: which wire is **+** / **−** vs JST orientation **before** first battery plug |

**Done when:** Amp and mic usable on breadboard; polarity documented; first LiPo plug only after sign-off.

---

### WX-028 — Flash MicroPython + USB REPL + WiFi smoke *(registry: backlog)*

**Objective:** Prove the XIAO is a programmable Wi-Fi device over a **data-capable** USB-C cable.

| Step | What | Passes when |
|------|------|-------------|
| **Firmware** | Flash MicroPython build appropriate for **XIAO ESP32-S3** (Seeed / generic ESP32-S3 port per current docs) | REPL responds over USB |
| **Tooling** | `mpremote` or serial terminal | Can run a one-liner (e.g. `print`, WiFi scan) |
| **WiFi** | Join **one** known AP (SSID/password hardcoded for this milestone is OK) | `wlan.isconnected()` true or equivalent |

**Done when:** REPL + WiFi smoke documented; repo contains initial **`firmware/`** (or agreed path) + **README** with flash steps and versions.

---

### WX-029 — Freeze I2S / GPIO pin map + breadboard wire table *(registry: backlog)*

**Objective:** One committed source of truth for wiring — avoids rework when two I2S peripherals share the MCU.

| Step | What | Passes when |
|------|------|-------------|
| **Research** | Map **BCLK / WS (LRCLK) / data** for **MAX98357** (DIN) and **INMP441** (SD/DOUT) to XIAO GPIOs per ESP32-S3 I2S capabilities | Table drafted |
| **Document** | Add file under e.g. [`lexie-docs/lexie/committed-to-build/`](../lexie-docs/lexie/committed-to-build/) (**`lexie-word-explainer.PINMAP-XIAO-ESP32S3.md`**) or `firmware/README.md` | Merged to `main`; linked from DEVICE-INTEGRATION or firmware README |
| **Extras** | Note **3V3 / GND**, INMP441 **L/R** if applicable, **MAX98357 GAIN / SD** | Clear for implementer |

**Done when:** Pin map merged; **WX-030** / **WX-031** wiring follows it.

---

### WX-030 — I2S out: MAX98357 + speaker playback *(registry: backlog)*

**Objective:** Validate the output chain (digital → amp → speaker) per **WX-024** transport (WAV/PCM first).

| Step | What | Passes when |
|------|------|-------------|
| **Wire** | Per **WX-029** | Power and I2S to amp |
| **Software** | MicroPython: I2S TX + buffer to amp | Audible **test tone** or short WAV |
| **Level** | Avoid clipping / overheating on **0.5 W** speaker | Sane volume |

**Done when:** Reliable sound from the physical speaker on command.

---

### WX-031 — I2S in: INMP441 capture *(registry: backlog)*

**Objective:** Validate microphone path before HTTP upload.

| Step | What | Passes when |
|------|------|-------------|
| **Wire** | Per **WX-029** | Mic clocks and data in |
| **Software** | MicroPython: I2S RX; record short sample | File or buffer with non-silent audio when speaking |
| **Levels** | Inspect peak / RMS roughly | No permanent clipping on normal speech |

**Done when:** Repeatable capture; ready to wrap as **`audio`** for **`POST /explain`**.

---

### WX-033 — USB provisioning: write `config.json` to flash (WX-025 shape) *(registry: backlog)*

**Objective:** Replace hardcoded Wi-Fi and secrets in source with flash-backed config as designed in **WX-025**.

| Step | What | Passes when |
|------|------|-------------|
| **Shape** | JSON: `networks[]`, `base_url`, `device_key` | Matches **WX-025** example |
| **Host** | Script (e.g. Python + `mpremote` copy or VFS write) writes **`config.json`** | Parent can run from laptop; values from 1Password, not committed |
| **Device** | Boot code loads JSON, connects using stored SSIDs order | Connects without embedding passwords in `.py` source |

**Done when:** One documented provisioning run; firmware reads config at boot.

---

### WX-032 — Device TLS: GET /health + POST /explain + play MP3 *(registry: done)*

**Objective:** End-to-end Lexie path on hardware per [`DEVICE-INTEGRATION.md`](../lexie-docs/lexie/committed-to-build/lexie-word-explainer.DEVICE-INTEGRATION.md).

| Step | What | Passes when |
|------|------|-------------|
| **TLS** | `GET {base_url}/health` | **200** `{"ok": true}` |
| **Explain** | `POST {base_url}/explain` multipart **`audio`**, `Authorization: Bearer` or `X-Device-Key` | **200** `audio/mpeg`; play on device |
| **Auth** | Wrong or missing key | **401** / `unauthorized` handled per §8 |
| **Config** | `base_url` and `device_key` from **WX-033** | No production secrets in git |
| **Stress** | `./tools/wx032-reliability.sh` | `LEXIE_E2E: SUMMARY pass=10 fail=0` ✓ (2026-06-09) |

**Done when:** Automated 10× stress pass ✓ (2026-06-09) + manual PTT smoke ✓ (2026-06-09).

---

## Section D3 — LX-4 bench execution (Path B — Waveshare)

**Platform:** [Waveshare ESP32-S3-AUDIO-Board](https://www.waveshare.com/esp32-s3-audio-board.htm)  
**Decision:** [lx-4-platform-pivot-waveshare.md](lx-4-platform-pivot-waveshare.md) · **WX-034**  
**PRDs:** [lx-4-waveshare-device.PRD.md](../lexie-docs/lexie/prds/lx-4-waveshare-device.PRD.md) · [lx-4-device-firmware.PRD.md](../lexie-docs/lexie/prds/lx-4-device-firmware.PRD.md) · [lx-4-device-ux-sla.PRD.md](../lexie-docs/lexie/prds/lx-4-device-ux-sla.PRD.md)  
**Kit / order:** [lx-4-path-b-waveshare-kit.md](lx-4-path-b-waveshare-kit.md)  
**Testing phases:** [lx-4-path-b-bench-testing.md](lx-4-path-b-bench-testing.md)  
**Network policy:** [lx-4-network-policy.md](lx-4-network-policy.md)

**Suggested order:** **WX-035** → **WX-028** → **WX-036** → **WX-029** → **WX-033** → **WX-032**.

**Scaffold:** No `firmware/` tree yet; **WX-028** introduces minimal layout + README (ESP-IDF or MicroPython per feasibility); **WX-033** host script under e.g. `tools/`.

### WX-035 — Path B unbox + erase vendor firmware *(registry: in_progress, 2026-05-22 — board delivered)*

**Objective:** Receive Waveshare board safely; **never** run stock Xiaozhi/demo firmware on home Wi‑Fi.

| Step | What | Passes when |
|------|------|-------------|
| **Unbox** | Visual inspect; note variant (with/without bundled LiPo) | Photo optional in [work-log](work-log/2026-05.md) |
| **Erase** | **Full flash erase** before network join | Vendor demo image gone |
| **Polarity** | If using external LiPo: multimeter **DC V** on MX1.25 connector | **+ / −** documented before first battery plug |
| **Policy** | Read [lx-4-network-policy.md](lx-4-network-policy.md) | Understand allowlist before Wi‑Fi test |

**Done when:** Board ready for Lexie firmware only; no vendor cloud traffic.

---

### WX-028 — Flash toolchain + USB REPL + WiFi smoke *(Path B)* *(registry: backlog)*

**Objective:** Prove Waveshare is a programmable Wi‑Fi device over **data-capable** USB-C.

| Step | What | Passes when |
|------|------|-------------|
| **Prereq** | **WX-035** complete | Vendor FW erased |
| **Toolchain** | ESP-IDF (Waveshare examples as **reference**) or MicroPython if port exists | Serial monitor / REPL responds |
| **Flash** | Lexie smoke image (not vendor demo) | Boot log shows Lexie or test app |
| **WiFi** | Join **one** known AP (hardcoded OK for milestone) | Connected |

**Done when:** REPL/monitor + WiFi smoke documented; initial **`firmware/`** + README with flash steps.

---

### WX-036 — Path B codec audio smoke (ES8311/ES7210) *(registry: backlog)*

**Objective:** Validate integrated audio path before HTTP upload — replaces Path A **WX-030** + **WX-031**.

| Step | What | Passes when |
|------|------|-------------|
| **Init** | I2C config ES8311 + ES7210 per Waveshare wiki | Codecs respond |
| **Record** | ES7210: short clip to buffer/file | Non-silent when speaking |
| **Play** | ES8311: tone or loopback | Audible on speaker header |
| **Levels** | No clipping on normal speech | Sane RMS/peak |

**Done when:** Repeatable record + playback; ready for **`POST /explain`** wrap.

---

### WX-029 — Freeze codec / I2S / GPIO pin map *(Path B)* *(registry: backlog)*

**Objective:** One committed pin map for Waveshare — ES8311, ES7210, I2S, PTT/LED (future).

| Step | What | Passes when |
|------|------|-------------|
| **Research** | Waveshare wiki + schematic: I2C **GPIO10/11**, I2S **MCLK/BCLK/LRCLK/DIN/DOUT** | Table drafted |
| **Document** | [`lexie-word-explainer.PINMAP-WAVESHARE-AUDIO.md`](../lexie-docs/lexie/committed-to-build/lexie-word-explainer.PINMAP-WAVESHARE-AUDIO.md) (draft — verify on board) | Merged; linked from firmware README |
| **Verify** | Cross-check against physical board silkscreen | Matches receipt |

**Done when:** Pin map merged; **WX-036** / **WX-032** follow it.

---

### WX-033 — USB provisioning: write `config.json` to flash (WX-025 shape) *(registry: backlog)*

**Unchanged from Path A** — same JSON shape; flash path may use ESP-IDF partition or MicroPython VFS.

| Step | What | Passes when |
|------|------|-------------|
| **Shape** | JSON: `networks[]`, `base_url`, `device_key` | Matches **WX-025** |
| **Host** | Script writes **`config.json`** | Values from 1Password |
| **Device** | Boot loads JSON, tries SSIDs in order | No passwords in source |

**Done when:** One documented provisioning run on Waveshare.

---

### WX-032 — Device TLS: GET /health + POST /explain + play MP3 *(registry: done)*

**Unchanged objective** — end-to-end Lexie on hardware per [`DEVICE-INTEGRATION.md`](../lexie-docs/lexie/committed-to-build/lexie-word-explainer.DEVICE-INTEGRATION.md).

| Step | What | Passes when |
|------|------|-------------|
| **TLS** | `GET {base_url}/health` | **200** |
| **Explain** | `POST {base_url}/explain` multipart **`audio`** | **200** `audio/mpeg`; play via ES8311 |
| **Network** | Router log or capture | Only Lexie host (+ optional NTP) per [network policy](lx-4-network-policy.md) |
| **Config** | From **WX-033** | No secrets in git |

**Done when:** `./tools/wx032-reliability.sh` reports `LEXIE_E2E: SUMMARY pass=10 fail=0` ✓; manual PTT smoke ✓ (2026-06-09).

---

## Section E — Parallel software polish (non-blocking)

These do **not** gate hardware work. Open a WX item only if a real device test produces a concrete reproducible failure.

| Item | What | When |
|------|------|------|
| **Latency SLO** | Chase SPEC §8.2 p95 &lt; 5 s (region, VM tier, model, prompt) | After real device reveals what latency feels like in use |
| **Validation G2–G7** | Full validation matrix (phrasal, Hogwarts, short clip, long clip, wrong key) | Any time; no gate |
| **Phase 1b / Journey 5** | Multi-turn + recovery cap (SPEC §15); defined but not yet built | After hardware validated and in-use |

---

## Quick index: `WX-*` → milestone

| WX | Focus |
|----|--------|
| WX-001 | *(cancelled — use WX-014–018)* |
| WX-002 | A6/A7 tokens in 1Password *(done)* |
| WX-003 | *(cancelled — use WX-013)* |
| WX-004 | PM folder *(done)* |
| WX-005 | `lexie-server` Part B *(done)* |
| WX-006 | Part D M1 public deploy *(done — `https://lexie-server.fly.dev`)* |
| WX-007 | Part E M2 browser/CORS/mic *(done)* |
| WX-008 | Part F M3 admin on host *(done)* |
| WX-009 | Part G M4 manual eval *(done — baseline + latency)* |
| WX-010 | Part H M5 ops *(done)* |
| WX-011 | Part I lexie-ops *(done 2026-05-03)* |
| WX-012 | Part J SPEC §11 sign-off *(done 2026-05-01)* |
| WX-013 | Preflight pytest 3.11+ *(done; CI + local 3.11+)* |
| WX-014 | M0 C1–C2 `.env` + health *(done)* |
| WX-015 | M0 C3 profile auth *(done)* |
| WX-016 | M0 C4 `/admin` browser *(done)* |
| WX-017 | M0 C5 `POST /explain` *(done)* |
| WX-018 | M0 C6 privacy *(done)* |
| WX-019 | M1 ops — Fly + capacity recorded in PM *(done)* |
| WX-020 | DB `explain_telemetry` *(done)* |
| WX-021 | Admin telemetry UI + Fly runbook *(done)* |
| WX-022 | Phase 2 connectivity de-risk D3 + hotspot + D5 *(done)* |
| WX-023 | Firmware handoff doc DEVICE-INTEGRATION.md *(done)* |
| WX-024 | LX-4 platform decision + bringup scaffold *(done)* |
| WX-025 | WiFi provisioning design *(done)* |
| WX-026 | Unbox + inventory + verify SKUs *(done)* |
| WX-027 | Solder prep *(Path A — superseded)* |
| **WX-034** | **Platform pivot — Waveshare Path B + PRD set** *(done)* |
| **WX-035** | **Path B unbox + erase vendor firmware** *(in progress — board delivered)* |
| **WX-028** | **Flash toolchain + USB REPL + WiFi smoke (Path B)** *(backlog)* |
| **WX-036** | **Path B codec smoke ES8311/ES7210** *(backlog)* |
| **WX-029** | **Waveshare pin map (Path B)** *(backlog)* |
| WX-030 | I2S out MAX98357 *(Path A — cancelled)* |
| WX-031 | I2S in INMP441 *(Path A — cancelled)* |
| **WX-033** | **USB provisioning `config.json` (WX-025 shape)** *(backlog)* |
| **WX-032** | **Device TLS `/health` + `/explain` + play MP3** *(backlog)* |

See [`registry.md`](registry.md) for status and dates.
