# Lexie work inventory (elaborated)

**Last updated:** 2026-05-03 (**WX-011** Part I lexie-ops **done**; optional **WX-006** D3/D5 remain)  

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

## Section B — In progress

**M0 (Part C) complete:** [**WX-014**](registry.md)–[**WX-018**](registry.md) **done** (local `.env` + health, profile auth, `/admin`, real **`POST /explain`**, privacy C6).

**Active:** none — optional manual follow-ups: [**WX-006**](registry.md) **D3** / **D5** only.

**Done recently:** [**WX-011**](registry.md) — Part I lexie-ops (**2026-05-03**). [**WX-012**](registry.md) — Part J SPEC §11 (**2026-05-01**). [**WX-010**](registry.md) — M5 **Part H**. [**WX-009**](registry.md) — M4 **Part G**. [**WX-008**](registry.md) — **`/admin`**. [**WX-007**](registry.md) — M2 prototype. [**WX-021**](registry.md) — telemetry. [**WX-006**](registry.md) — Fly. **WX-018** — C6 closed.

**How to move work:** Edit [`registry.md`](registry.md) (**Status**, **Updated**), append a line to [`work-log/`](work-log/).

---

## Section C — Planned next (M0 **done**; follow-on WX-006+)

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
| **D5** | Store **BASE_URL** in 1Password for firmware/bookmarks. | Stable reference for clients. | **D2** |

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

See [`registry.md`](registry.md) for status and dates.
