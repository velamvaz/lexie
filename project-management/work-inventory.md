# Lexie work inventory (elaborated)

**Last updated:** 2026-04-22  

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

**Today:** No `WX-*` row in [`registry.md`](registry.md) is set to **`in_progress`**.

**How to start work:** (1) Pick the next item (often **WX-002** or **WX-001**). (2) In `registry.md`, set **Status** to `in_progress` and **Updated** to today’s date (`YYYY-MM-DD`). (3) Append one line to the current month file under [`work-log/`](work-log/) (e.g. `work-log/2026-04.md`) describing what you started. (4) When finished, set **Status** to `done` (or `blocked` / `cancelled` with **Notes**), bump **Updated**, and append another work-log line with outcome or commit hash.

---

## Section C — Planned next (WX-001, WX-002, WX-003)

### WX-002 — Device and admin tokens in 1Password (A6 / A7)

**Objective:** Create two **long random** secrets, store them only in 1Password, and prepare to paste them into **gitignored** `.env` (local) or host secrets (production)—never commit them.

**Steps:**

1. On a trusted machine, generate two distinct values (e.g. `openssl rand -hex 32` twice).
2. Save **`LEXIE_DEVICE_KEY`** in 1Password (prototype / future firmware); label clearly.
3. Save **`LEXIE_ADMIN_TOKEN`** in a **separate** item or field; used for `/admin` and `GET`/`PATCH` `/profile` only.
4. Do **not** paste these into chat, tickets, or screenshots.

**Done when:** Both values exist in 1Password per **V2**; master checklist **A6** and **A7** can be ticked; you can copy them into `lexie-server/.env` for local testing.

**Depends on:** Nothing technical—can run before or in parallel with **WX-003**. **WX-001** (full M0 auth checks) is easier once **WX-002** is done so `.env` can include real device and admin tokens.

---

### WX-003 — Verify tests on Python 3.11 or newer

**Objective:** Confirm the contract test suite passes on a supported Python (**3.11+** per `pyproject.toml`; runtime stack needs **3.10+**).

**Steps:**

1. Install **Python 3.11+** (e.g. from python.org, Homebrew, or `pyenv`).
2. `cd lexie-server && python3.11 -m venv .venv && source .venv/bin/activate`
3. `pip install -e ".[dev]"` (or `pip install --upgrade pip` first if needed).
4. `pytest -v`
5. *(Optional follow-up, not required to close WX-003)*: add a GitHub Actions workflow that runs `pytest` on `push`/`pull_request` with `python-version: "3.11"`—document in [`lexie-server/README.md`](../lexie-server/README.md) if added.

**Done when:** `pytest` exits **0** on your machine; note any **ffmpeg** requirement for future integration tests (duration/pydub) in README if you hit environment issues.

**Depends on:** Nothing blocking; can run before **WX-001**.

---

### WX-001 — Part C (M0) local smoke

**Objective:** Prove the stack works **on your laptop** with a **real** `OPENAI_API_KEY` (and tokens after **WX-002**) before relying on a public URL.

**Steps (maps to checklist C1–C6):**

1. **C1 — `.env`:** Copy [`lexie-server/.env.example`](../lexie-server/.env.example) to **`lexie-server/.env`** (gitignored). Fill `OPENAI_API_KEY` from 1Password; add `LEXIE_DEVICE_KEY` and `LEXIE_ADMIN_TOKEN` when **WX-002** is done; set `LEXIE_DATA_DIR` if needed.
2. **C2 — Run server:** `uvicorn lexie_server.main:app --reload --host 0.0.0.0 --port 8000` from `lexie-server/`. Open `GET http://127.0.0.1:8000/health` → **200** JSON with `"ok": true`.
3. **C3 — Profile API:** `GET /profile` without `Authorization` → **401**. With `Authorization: Bearer <LEXIE_ADMIN_TOKEN>` → **200** and profile JSON. Optionally `PATCH` a field and verify response.
4. **C4 — Admin page:** Browser `GET http://127.0.0.1:8000/admin` → **200** HTML. Paste admin token (e.g. via page flow / sessionStorage per template), load/save profile, refresh.
5. **C5 — Explain:** Use **`/prototype/`** or `curl`/client to `POST /explain` with a short audio clip and device auth header → **200** `audio/mpeg` (or **400** with JSON for too-short/unintelligible per SPEC).
6. **C6 — No raw audio on disk:** With **`LEXIE_LOG_REQUESTS=0`** (default), confirm you are not persisting uploaded audio blobs to disk; optional DB logging only stores metadata/transcript policy per SPEC §7.

**Done when:** C1–C6 are satisfied on your side; master checklist **Part C** can be ticked.

**Depends on:** **WX-003** recommended first (green tests); **WX-002** for realistic auth during C3–C5 (or use empty device key only where SPEC allows dev bypass).

---

## Section D — Future milestones (master checklist Parts C–J and extras)

The following restates [**lexie-word-explainer.MASTER-CHECKLIST.md**](../lexie-docs/lexie/committed-to-build/lexie-word-explainer.MASTER-CHECKLIST.md) items with **what**, **why it matters**, and **typical dependency**. Part **C** step-by-step is **WX-001** (Section C); items below add context or post-M0 scope.

### Dev workflow: V4, V5

| Item | What | Why it matters | Typical owner / dependency |
|------|------|----------------|----------------------------|
| **V4** | Copy secrets from 1Password into **gitignored** `.env` locally; on deploy, paste into **host** secret UI—1Password stays canonical. | Prevents secrets in git and keeps a single source of truth. | You; before **WX-001** / production. |
| **V5** | *(Optional)* 1Password CLI (`op run`) to inject env without leaving secrets in shell history. | Safer local and CI patterns. | Optional anytime. |

### Optional setup: A3, A4, A5

| Item | What | Why it matters | Typical owner / dependency |
|------|------|----------------|----------------------------|
| **A3** | Choose a **host** (Fly, Railway, Render, VPS); account + payment if needed. | Required before **Part D** deploy. | You. |
| **A4** | *(Optional)* Custom **domain** + know where **DNS** is managed—or use host subdomain only. | Clean URLs and later firmware config. | You; can follow **D1**. |
| **A5** | *(Optional)* External **uptime** (e.g. UptimeRobot) for public `/health`. | Alerts when the service is down. | After **D2**. |

### Part C (M0) — checklist cross-reference

| Item | What | Why it matters | Typical owner / dependency |
|------|------|----------------|----------------------------|
| **C1** | Local `.env` with real keys from vault. | Safe dev and parity with prod secrets pattern. | **WX-001** |
| **C2** | `uvicorn` + `/health` **200**. | Confirms process and routing. | **WX-001** |
| **C3** | `/profile` **401** without admin; **200** with Bearer. | Validates admin gate. | **WX-001** + **WX-002** |
| **C4** | `/admin` HTML + token + save profile. | Parent journey locally. | **WX-001** |
| **C5** | `POST /explain` returns audio or structured error. | Core product path. | **WX-001**; **ffmpeg** on PATH if pipeline needs it |
| **C6** | No raw audio files on disk; default logging off. | Privacy per SPEC §7. | **WX-001** |

### Part D (M1) — Public HTTPS and reachability (WX-006)

| Item | What | Why it matters | Typical dependency |
|------|------|----------------|---------------------|
| **D1** | Deploy app to host; bind env in **dashboard/secrets**, not only laptop `.env`. | Production serving. | **A3**, **WX-001** complete locally |
| **D2** | `https://<BASE_URL>/health` → **200**. | Confirms TLS and routing. | **D1** |
| **D3** | Hit `/health` from **phone on cellular**. | Rules out home-only networking issues. | **D2** |
| **D4** | *(Optional)* External uptime ping to `/health`. | Operations visibility. | **D2**, **A5** |
| **D5** | Store **BASE_URL** in 1Password for firmware/bookmarks. | Stable reference for clients. | **D2** |

### Part E (M2) — Child browser path (WX-007)

| Item | What | Why it matters | Typical dependency |
|------|------|----------------|---------------------|
| **E1** | Set **`LEXIE_CORS_ORIGINS`** for prototype origin (e.g. `http://localhost:5173`); redeploy. | Browser `fetch` from another origin works. | **D1** if not localhost-only |
| **E2** | Open prototype in **secure context** (localhost/HTTPS); grant **mic**. | `getUserMedia` requirements per SPEC §6. | **E1** |
| **E3** | Device key only via header (not query string) per README. | Avoids leaking token in URLs/logs. | **WX-002** |
| **E4** | J1-style test (“sorcerer”); latency ~**&lt; 5 s** warm per SPEC §8.2. | Validates UX target. | **E2**, warm request |
| **E5** | J2 word+context, J3 “What is Hogwarts?” — redirect tone acceptable. | PRD journeys. | **E4** |
| **E6** | On failure, follow [**RUNBOOK**](../lexie-docs/lexie/committed-to-build/lexie-word-explainer.RUNBOOK.md) §1 A→E. | Consistent triage. | Any E# failure |

### Part F (M3) — Parent admin on real host (WX-008)

| Item | What | Why it matters | Typical dependency |
|------|------|----------------|---------------------|
| **F1** | Open `https://<BASE_URL>/admin` (no token in URL). | Safe admin entry. | **D2** |
| **F2** | Paste admin token; load profile. | Auth flow on prod. | **F1**, **WX-002** |
| **F3** | Change `age_years` / `reading_level`; save; persist after refresh. | Profile storage on host. | **F2** |
| **F4** | Next explain reflects new profile (hear or inspect with logging). | End-to-end profile → prompt. | **F3**, **C5** on host |

### Part G (M4) — E2E shakedown (WX-009)

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

### Part H (M5) — Steady operation (WX-010)

| Item | What | Why it matters | Typical dependency |
|------|------|----------------|---------------------|
| **H1** | **`LEXIE_LOG_REQUESTS=0`** in production; reset after debug. | Privacy default. | **D1** |
| **H2** | OpenAI budget alert still on; note $/explain after a week. | Cost control. | **A2**, traffic |
| **H3** | Host sized to avoid long **cold** first explain (min instances / RUNBOOK §4). | Latency SPEC. | **D1** |
| **H4** | Re-read [**journeys-and-observability**](../lexie-docs/lexie/committed-to-build/lexie-word-explainer.journeys-and-observability.md) §3 — default privacy expectations. | Align ops with product. | Before wide use |

### Part I — lexie-ops (optional) (WX-011)

| Item | What | Why it matters | Typical dependency |
|------|------|----------------|---------------------|
| **I1** | `cd monitoring/lexie-ops && npm install`. | Local monitor app. | Node |
| **I2** | `.env` from `.env.example`; set `VITE_LEXIE_BASE_URL` or proxy per README. | Points UI at your server. | **D2** optional |
| **I3** | `npm run dev`; ping `/health` → **200** JSON. | Confirms wiring. | **I2** |
| **I4** | If CORS error, add origin on server or use proxy mode. | Browser safety rules. | **E1** |

### Part J — Definition of done (SPEC §11) (WX-012)

| Item | What | Why it matters | Typical dependency |
|------|------|----------------|---------------------|
| **J1** | SPEC §11 items 1–9 for **your** environment (HTTPS, admin, explain, profile, defaults, p95, CORS docs, ops health, tests). | Formal Phase 1 exit. | **D–H** as applicable |
| **J2** | Child-facing error copy / PRD error tone on at least one synthetic failure. | Trust and clarity. | **G4** / errors |
| **J3** | No secrets in repos, screenshots, chat, URLs; 1Password canonical. | Security. | Ongoing |

**SPEC reference:** [`lexie-word-explainer.SPEC.md`](../lexie-docs/lexie/committed-to-build/lexie-word-explainer.SPEC.md) §10–11.

---

## Quick index: `WX-*` → milestone

| WX | Focus |
|----|--------|
| WX-001 | M0 local smoke (Part C) |
| WX-002 | A6/A7 tokens in 1Password |
| WX-003 | Pytest on 3.11+ |
| WX-004 | PM folder *(done)* |
| WX-005 | `lexie-server` Part B *(done)* |
| WX-006 | Part D M1 public deploy |
| WX-007 | Part E M2 browser/CORS/mic |
| WX-008 | Part F M3 admin on host |
| WX-009 | Part G M4 manual eval |
| WX-010 | Part H M5 ops |
| WX-011 | Part I lexie-ops optional |
| WX-012 | Part J final sign-off |

See [`registry.md`](registry.md) for status and dates.
