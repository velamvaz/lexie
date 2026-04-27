# Lexie Word Explainer — master checklist (Phase 1 builder)

**Date:** 2026-04-22  
**Use this as your single execution list** for: accounts → implement → local test → public deploy → browser + admin → E2E → ops.  
**Stuck?** [lexie-word-explainer.RUNBOOK.md](lexie-word-explainer.RUNBOOK.md) (triage order).  
**ROM costs & M0–M5 overview:** [lexie-word-explainer.BUDGET-AND-ROLLOUT.md](lexie-word-explainer.BUDGET-AND-ROLLOUT.md) · [phased-delivery-plan.md](phased-delivery-plan.md)  
**Spec exit criteria (normative):** [lexie-word-explainer.SPEC.md](lexie-word-explainer.SPEC.md) §10–11

**Reality check:** this repo (Lexie) currently has **no FastAPI `lexie-server` package in-tree** — Part B is “implement or import the app,” then run this checklist. If the server already lives in another repo, start at **Part C (M0)** with that code.

**Convention:** copy this file or tick boxes in your editor. Items marked **(you)** require your account / billing / domain — a collaborator cannot do them for you.

---

## Part A — Accounts and one-time setup **(you)**

- [ ] **A1** — Create or use an [OpenAI Platform](https://platform.openai.com/) account; enable **API** billing (ChatGPT **Plus** is **not** the same as API access).
- [ ] **A2** — In OpenAI: create an **API key**; store in a password manager; set a **monthly budget / alert** (SPEC §2, [BUDGET-AND-ROLLOUT](lexie-word-explainer.BUDGET-AND-ROLLOUT.md) §4).
- [ ] **A3** — Choose a **host** (e.g. Fly, Railway, Render, or a VPS) and create an account; add a payment method if the tier requires it.
- [ ] **A4** — (Optional) Register a **domain** and note where **DNS** is managed (or use the host’s subdomain only).
- [ ] **A5** — (Optional) Create a free **external uptime** account (e.g. UptimeRobot) for `GET /health` against your public URL later.

**Secrets to generate and never commit to git (rotating strings):**

- [ ] **A6** — Generate **`LEXIE_DEVICE_KEY`** (long random string) — for browser prototype and future firmware.  
- [ ] **A7** — Generate **`LEXIE_ADMIN_TOKEN`** (separate long random) — for `/admin` and `GET`/`PATCH` `/profile` only.

---

## Part B — Implement the server (per SPEC §14–16)

- [ ] **B1** — Create or open the **FastAPI** app project (Python) matching [lexie-word-explainer.SPEC.md](lexie-word-explainer.SPEC.md) and [lexie-word-explainer.API-and-data-model.md](lexie-word-explainer.API-and-data-model.md) (or accept a pre-built image).
- [ ] **B2** — Wire **`OPENAI_API_KEY`**, **`LEXIE_DEVICE_KEY`**, **`LEXIE_ADMIN_TOKEN`**, `LEXIE_LOG_REQUESTS=0`, `LEXIE_HEADWORD_TTS=0`, optional `LEXIE_CORS_ORIGINS` (see SPEC §2).
- [ ] **B3** — **SQLite** `age_profile` + optional `explain_request` when `LEXIE_LOG_REQUESTS=1`; seed one profile row; migrations or `create_all` per data-model doc.
- [ ] **B4** — Implement routes: `GET /health`, `GET`/`PATCH` `/profile`, `POST` `/explain`, `GET` `/admin` (HTML) per SPEC §3.  
- [ ] **B5** — `POST /explain` pipeline: Whisper → GPT (JSON when needed) → TTS; size/duration limits and error JSON per SPEC §3.5, §5.  
- [ ] **B6** — Prototype static page (or Vite) that records audio and `POST`s with **Bearer** device key (dev UX per SPEC §6).  
- [ ] **B7** — **Automated tests:** contract + mocked OpenAI pipeline (see [lexie-word-explainer.TESTING-strategy.md](lexie-word-explainer.TESTING-strategy.md)); merge when green.

---

## Part C — **M0** Local smoke (no public internet)

- [ ] **C1** — `cd` to server project; set env vars locally (`.env` not in git) with **real** `OPENAI_API_KEY` for a quick manual test, or use mocks for CI-only.  
- [ ] **C2 — Start the app (e.g. `uvicorn ...`); open **`GET` `http://127.0.0.1:<port>/health`** → `200` JSON.  
- [ ] **C3 — `GET`/`PATCH` `/profile` with `Authorization: Bearer <LEXIE_ADMIN_TOKEN>`; confirm `401` without header, `200` with.  
- [ ] **C4 — `GET` `/admin` → `200` `text/html`; in browser, paste admin token, save profile, reload.  
- [ ] **C5 — `POST` `/explain` with a short audio file or prototype → `200` `audio/*` (or `400` with clear JSON for too-short clip).  
- [ ] **C6** — Confirm there is *no* raw audio on disk (SPEC §7); `LEXIE_LOG_REQUESTS=0` default.  

---

## Part D — **M1** Public HTTPS and reachability

- [ ] **D1 — **Deploy** the app to the host; bind env vars in the **host** dashboard or secrets (not only `.env` on laptop).  
- [ ] **D2 — Confirm **`https://<BASE_URL>/health`** returns `200` (RUNBOOK step A).  
- [ ] **D3 — From **phone** on **cellular** (not only home Wi‑Fi), open the same `/health` URL.  
- [ ] **D4 — (Optional) Add external **uptime** ping to `/health`.  
- [ ] **D5 — Note **`BASE_URL`** in your password doc for firmware / bookmarks later.

---

## Part E — **M2** Child browser path (CORS, mic, device key)

- [ ] **E1 — Set `LEXIE_CORS_ORIGINS` to include the **prototype** origin (e.g. `http://localhost:5173`) and redeploy.  
- [ ] **E2 — Open prototype in a **secure context** (localhost or HTTPS per SPEC §6); grant **microphone**.  
- [ ] **E3 — Configure **device key** in prototype the way the server README says (header only; not in query string).  
- [ ] **E4 — Run a **J1**-style test (e.g. “sorcerer”); hear MP3; check rough latency vs **&lt; 5 s** warm (SPEC §8.2) after a warm request.  
- [ ] **E5 — Run **J2** (word + context) and **J3** (“What is Hogwarts?”) per PRD; confirm redirect tone is acceptable.  
- [ ] **E6 — If something fails, follow RUNBOOK §1 A→E before deep debugging.

---

## Part F — **M3** Parent admin (journey 4) on the real host

- [ ] **F1 — On **`https://<BASE_URL>/admin`**, open the page (no token in URL).  
- [ ] **F2 — Paste **admin token**; load profile.  
- [ ] **F3 — Change `age_years` and/or `reading_level`; **Save**; re-open or refresh and confirm **persisted**.  
- [ ] **F4 — Next explain uses new profile** (hear difference or inspect prompt only if logging is temporarily on in private — RUNBOOK §2).

---

## Part G — **M4** E2E shakedown (manual eval set)

Use [validation matrix](lexie-word-explainer.validation-matrix.md) “Manual eval set” and PRD examples.

- [ ] **G1 — **Sorcerer** (J1) — short word, clear audio.  
- [ ] **G2 — **Phrasal / multi-word** phrasing.  
- [ ] **G3 — “What is Hogwarts?”** (J3) — warm redirect, audible.  
- [ ] **G4 — &lt; ~0.4 s clip** — expect `400` and **calm** UI per SPEC §5.1 (not raw `error` to child if UI maps copy).  
- [ ] **G5 — Long clip** (~&gt;30 s policy) or **&gt;2 MiB** part — expect reject per SPEC.  
- [ ] **G6 — (Optional) Messy / approximate utterance (J5 L0)** — one PTT, **no** session.  
- [ ] **G7 — **Forced failure path:** toggle wrong device key once → `401` / friendly message path.

---

## Part H — **M5** Steady operation and cost

- [ ] **H1** — `LEXIE_LOG_REQUESTS=0` in production by default; if you used `1` for debug, set back to `0`.  
- [ ] **H2 — **OpenAI** budget alert still configured; note “measured $/explain” from dashboard after a week.  
- [ ] **H3 — **Host** sized with **min machines = 1** (or equivalent) to avoid long cold first explain (SPEC §2, RUNBOOK §4).  
- [ ] **H4 — Re-read** [lexie-word-explainer.journeys-and-observability.md](lexie-word-explainer.journeys-and-observability.md) §3 so expectations match **default privacy** (no DB transcript by default).

---

## Part I — **lexie-ops** (optional local monitor)

Repo path: `Lexie/monitoring/lexie-ops/` (from workspace root).

- [ ] **I1 — `cd monitoring/lexie-ops` → `npm install`.  
- [ ] **I2 — `cp .env.example .env`** and set `VITE_LEXIE_BASE_URL=https://<BASE_URL>` (or use Vite proxy per [README](../../../monitoring/lexie-ops/README.md)).  
- [ ] **I3 — `npm run dev`**, open the printed URL, click ping — see **`200`** and JSON from `/health`.  
- [ ] **I4 — If CORS error, add origin to `LEXIE_CORS_ORIGINS` on server or use **proxy** mode in README.

---

## Part J — **Definition of done (SPEC §11) — final sign-off**

- [ ] **J1 — [SPEC §11](lexie-word-explainer.SPEC.md) items 1–9 satisfied for your environment (HTTPS, admin, explain, profile, defaults, p95, CORS docs, ops can hit health, tests as applicable).  
- [ ] **J2 —** Child-facing error copy and PRD **error tone** verified on at least one synthetic failure.  
- [ ] **J3 —** No secrets in public repos, screenshots, or URLs.

---

*End of checklist. Update the date if you change ordering or add host-specific steps.*
