# Lexie — phased delivery (LX-1, documentation)

**Date:** 2026-04-22  
**PRD:** [../prds/lexie-word-explainer.PRD.md](../prds/lexie-word-explainer.PRD.md)  
**SPEC:** [lexie-word-explainer.SPEC.md](lexie-word-explainer.SPEC.md)

This file ties **phases** to **documentation** and the **suggested** implementation order. It is **not** a substitute for the PRD or SPEC.

| Phase | What the product is | What the *build* unlocks | Key doc / spec |
|-------|---------------------|---------------------------|---------------|
| **Phase 1 (MVP)** | Single-PTT explain; **one** `age_profile`; public HTTPS; admin HTML; browser prototype; device key; **Journey 5 only at Level 0** | Child can ask words in one press; parent can edit profile | SPEC §1–11, §14–16; validation matrix; PRD J1–4, J5 L0 only |
| **Phase 1b** | **Journey 5** full cascade (L1–L3) with **server-side session/turns** and recovery cap | Disambiguation across multiple PTTs | PRD J5, SPEC §12/§15 (future contract revision) |
| **Phase 2** | Physical **device** on WiFi | Same API to `BASE_URL` | Out of this SPEC’s server v1; firmware registry |

**Overlap (allowed):** you may maintain **lexie-ops** and the **PRD** while the FastAPI app is in progress. **Normative** behavior lives in the **SPEC** once it is “ready for implementation review.”

## First-run order (family / builder)

Anchor: PRD **“First run (Phase 1 — family / builder)**” and SPEC §2 (env) + §3.2–3.8. **Suggested sequence:**

1. **Host** — choose provider; public DNS + TLS.  
2. **Secrets** — set `OPENAI_API_KEY`, `LEXIE_DEVICE_KEY`, `LEXIE_ADMIN_TOKEN` on the server.  
3. **Deploy** app; verify `GET /health` over HTTPS.  
4. **Profile** — open `GET /admin`, enter admin token, set `age_profile` (or rely on server seed, then correct).  
5. **Browser prototype** — open allowed origin, grant mic, PTT a test word.  
6. **Ops (optional)** — [monitoring/lexie-ops/README.md](../../../monitoring/lexie-ops/README.md) to watch health.

**If something fails** after this sequence: [lexie-word-explainer.RUNBOOK.md](lexie-word-explainer.RUNBOOK.md) (triage: `/health` → CORS / keys → optional short debug logging).

**Milestone order, testing focus, and ROM monthly costs (host + OpenAI):** [lexie-word-explainer.BUDGET-AND-ROLLOUT.md](lexie-word-explainer.BUDGET-AND-ROLLOUT.md).

**Single tick-list for everything in order (accounts → deploy → E2E):** [lexie-word-explainer.MASTER-CHECKLIST.md](lexie-word-explainer.MASTER-CHECKLIST.md).

## Dependencies

- **OpenAI** API availability and billing.  
- **CORS** / secure context for the prototype (SPEC §6).  
- **SPEC** + validation matrix for **“done”** (SPEC §11).

---

*End of document.*
