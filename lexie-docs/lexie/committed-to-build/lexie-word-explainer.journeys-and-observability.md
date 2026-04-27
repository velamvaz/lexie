# Lexie Word Explainer — user journeys (anchor) and observability (LX-1)

**Date:** 2026-04-22  
**PRD (source of journeys):** [../prds/lexie-word-explainer.PRD.md](../prds/lexie-word-explainer.PRD.md) **§4**  
**Contract & SLOs:** [lexie-word-explainer.SPEC.md](lexie-word-explainer.SPEC.md)  
**API & data:** [lexie-word-explainer.API-and-data-model.md](lexie-word-explainer.API-and-data-model.md)  
**Budget & rollout milestones:** [lexie-word-explainer.BUDGET-AND-ROLLOUT.md](lexie-word-explainer.BUDGET-AND-ROLLOUT.md)  
**Validation ↔ tests:** [lexie-word-explainer.validation-matrix.md](lexie-word-explainer.validation-matrix.md)

This document **anchors** product journeys on the **same** APIs, entities, and ops signals as the SPEC — so elaboration on journeys does **not** silently break the implementation model. It also makes **observability use cases** explicit (what a parent *can* see vs what is **privacy-limited** by default).

---

## 1. Verification: journeys vs Phase 1 design (no contract break)

| Check | Result |
|-------|--------|
| **J1–J3** need one `POST /explain` + `age_profile` in the LLM path | **OK** — `GET` profile on server for each explain; device only calls `POST /explain` + `GET /health` (PRD). |
| **J2** (context in one hold) | **OK** — full Whisper transcript is the only input to the model (SPEC §4); no separate `context_text` field required in v1. |
| **J3** (constraint guard) | **OK** — model + system prompt; same 200 + TTS as other successes. |
| **J4** (parent edits profile) | **OK** — `GET /admin` + `GET`/`PATCH /profile` + one `age_profile` row. |
| **J5 Level 0** (messy audio, one PTT) | **OK** — single `POST /explain`; no session. |
| **J5 Levels 1–3** (fork, spell, kind stop) | **Not Phase 1** — requires session / turn model (PRD, SPEC §15). **No conflict:** design defers it; data model does not need session tables until 1b. |
| **Observability default** (`LEXIE_LOG_REQUESTS=0`) | **OK** for privacy; **limited** post-hoc debugging without opt-in (see §4). |
| **Entity model** | **`age_profile`** + optional **`explain_request`** when logging on — supports all **Phase 1** journeys; no extra tables required. |

**Conclusion:** Elaborating PRD user journeys **does not** require changing the **normative** API or SQLite shape for Phase 1. Phase 1b (J5 multi-turn) is a **separate** SPEC revision when implemented.

---

## 2. Journey map (APIs, data, phase)

| Journey | Actor | Product outcome (PRD) | **Primary HTTP** | **Other** | **Data read** | **Data write (Phase 1)** | Phase |
|---------|--------|------------------------|------------------|-----------|---------------|---------------------------|--------|
| **J1** Simple word | Child | Hears short explanation; back to reading | `POST /explain` | `GET /health` (device/ops) | `age_profile` | `explain_request` **only if** `LEXIE_LOG_REQUESTS=1` | 1 |
| **J2** Context-augmented | Child | Richer, story-grounded answer | `POST /explain` | same | `age_profile` + transcript in prompt | same logging rule | 1 |
| **J3** Out-of-scope | Child | Warm redirect, no lecture | `POST /explain` (200 + TTS) | — | `age_profile` | same | 1 |
| **J4** Parent profile | Parent | Explanations track child’s age/level | `GET`/`PATCH /profile` | `GET /admin` | — | `age_profile` | 1 |
| **J5 L0** Noisy / approximate speech | Child | One best explanation from messy utterance | `POST /explain` | — | `age_profile` + transcript | same logging rule | 1 |
| **J5 L1–3** Recovery cascade | Child | Fork → spell → kind stop (bounded) | TBD: session + multiple `POST`s or dedicated route | — | (future) session state + profile | (future) — | **1b** |

**Child-facing errors** (any journey): HTTP JSON `error` codes + on-screen / future device copy per **SPEC §5.1** (transport failures are **not** the same as J5 “kind stop” copy — PRD *Child-facing error tone*).

---

## 3. Observability: use cases (what you need to run and debug)

These are the **practical** questions a builder or parent has. They are **not** all answerable in-app when **`LEXIE_LOG_REQUESTS=0`** (the locked default) — by design, for the child’s privacy (SPEC §7).

### 3.1 Use case → signal (what to use)

| Use case (question) | Journey it relates to | **Always / usually available** (LOG **off**) | **When `LEXIE_LOG_REQUESTS=1` (opt-in)** | **Not in v1 (honest limit)** |
|---------------------|------------------------|-----------------------------------------------|------------------------------------------|------------------------------|
| “Is the server up?” | All (device boot, parent checks) | **`GET /health`**, UptimeRobot / host probes; [lexie-ops](../../../monitoring/lexie-ops/README.md) (currently polls `/health` only) | Same |  |
| “Is my deploy the version I think?” | Ops | **`GET /health`** `version` / `git_sha` (if you add them) | — |  |
| “Roughly how many explains this month?” (capacity / “is this normal?”) | J1–J3, J5 L0 | **`GET /admin/usage`** (SPEC **optional**); *or* host metrics if you add a counter without PII | **`COUNT` on `explain_request`** in DB for period | Exact cost: **OpenAI dashboard** (SPEC), not Lexie alone |
| “p95 / latency for explains” | J1, J2, SLO | **Host metrics** or `X-Explain-Latency-Ms` sampling in logs; optional **`GET /admin/metrics`** | `latency_ms` in **`explain_request`** + aggregates | Per-journey A/B “funnel” — not required |
| “This one explain failed — what happened?” | Any | **Structured app logs** ( level, `request_id`, `stage: stt|llm|tts`, **no** raw audio); HTTP status + `error` for client | **Transcript + response** text in `explain_request` (PII — **redact** in shared logs) | Automatic ticket routing |
| “Did the profile save?” | J4 | **`PATCH /profile` 200** + re-`GET` in admin UI | N/A; profile row in DB is the source of truth | Full audit log of *who* changed *what* and when (separate from `updated_at` if you need it later) |
| “J5 recovery didn’t work” | J5 L1+ | *N/A in Phase 1* — L1+ not shipped | *Phase 1b* + session data |  |

**Rule of thumb:** **Route-level** and **SLO** observability come from **health, headers, optional admin metrics, and host CPU/RAM**. **Content-level** forensics (what was said) require **opt-in logging** or the parent reproducing the issue in a test environment.

### 3.2 What journeys do *not* imply (avoid scope creep)

| Do **not** assume the product will (Phase 1) | Why |
|---------------------------------------------|-----|
| Track “which journey” in analytics | Journeys are **documentation and test** anchors, not a server-side `journey_id` field. |
| Child-facing dashboards | Out of scope (PRD admin is parent-only, one-pager). |
| Real-time per-child speech analytics | Raw audio is **not** stored (PRD, SPEC). |

### 3.3 Alignment with SPEC §8.3 (“What to measure in-app”)

SPEC asks for: **`latency_ms`**, **stage of failure** (`stt` / `llm` / `tts`), no raw audio. The table above is **the same** requirement, **mapped to parent questions**. Implementation detail: log those fields in **server stdout** (or a log drain) with **`LEXIE_LOG_REQUESTS=0`**, and treat **transcript/response in DB** as **additional** PII (opt-in).

---

## 4. How this ties to the validation matrix

| Validation row (examples) | Journey | Observability note |
|--------------------------|---------|-------------------|
| **J-1a – J-3a** | J1, J2, J3 | E2E can measure **end-to-end latency**; **J** = qualitative “sounds like PRD” |
| **J-4** | J4 | Confirms **admin + profile** path; for ops, profile **read** is only after **Bearer** |
| **J-5-L0** | J5 (Phase 1 slice) | **No** session_id in API — don’t add observability that assumes L1+ |
| **P0** health / auth / errors | All | Drives **uptime** and **error-code** use cases in §3.1 |
| **SLO p95** | J1, J2 | Ties to **`X-Explain-Latency-Ms`** and SPEC §8.2 |

Full matrix: [lexie-word-explainer.validation-matrix.md](lexie-word-explainer.validation-matrix.md).

---

## 5. Suggested follow-ups (optional, not blockers)

1. **lexie-ops** — add optional `GET /admin/usage` (or manual link) when the server implements it; today only **`/health`** is required by the in-repo app.  
2. **Runbook** — see [lexie-word-explainer.RUNBOOK.md](lexie-word-explainer.RUNBOOK.md) (triage: `/health` → CORS / keys → short opt-in `LEXIE_LOG_REQUESTS=1` for forensics, then off).  
3. **Phase 1b** — extend this file with **session** observability (turn counter, cap enforcement) when the SPEC defines the contract.

---

*End of document.*
