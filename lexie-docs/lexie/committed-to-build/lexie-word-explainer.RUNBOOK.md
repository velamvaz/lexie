# Lexie Word Explainer — operator runbook (LX-1 Phase 1)

**Audience:** Parent builder / family deploy — **not** a 24/7 NOC playbook.  
**Contract:** [lexie-word-explainer.SPEC.md](lexie-word-explainer.SPEC.md) · **Observability context:** [lexie-word-explainer.journeys-and-observability.md](lexie-word-explainer.journeys-and-observability.md) §3

Use this when **something does not work**: child hears nothing, browser prototype fails, or admin cannot save the profile.

---

## 1. Quick triage (do in order)

| Step | Action | If OK | If not OK |
|------|--------|-------|-----------|
| **A** | From **your laptop**, open `https://<BASE_URL>/health` (Phase 1 must be **HTTPS** in production). Expect **`200`** JSON with `"ok": true` (or equivalent). | Continue | Fix deploy, DNS, TLS, or process crash — **host/provider first**. |
| **B** | Optional: run [lexie-ops](../../../monitoring/lexie-ops/README.md) against the same `BASE_URL` (set `VITE_LEXIE_BASE_URL`). Confirms browser can reach the host from your network. | Continue | Same as A, or **CORS** (step D). |
| **C** | **Prototype / browser:** confirm page is **secure context** for mic — see SPEC §6 (`localhost`/`127.0.0.1` OK; raw LAN `http://` often blocks `getUserMedia`). | Continue | Use HTTPS (e.g. **mkcert**), **localhost** testing, or tunnel. |
| **D** | **`POST /explain`:** production requires **`Authorization: Bearer <LEXIE_DEVICE_KEY>`** (or `X-Device-Key` per implementation). If **401** `unauthorized` → key missing/wrong in client or env. **Dev:** server may accept requests with no key when `LEXIE_DEVICE_KEY` is unset — **documented in server README only**. | Continue | Align env + client header. |
| **E** | **Admin:** open `GET /admin`, paste **`LEXIE_ADMIN_TOKEN`** in the page (sessionStorage), then **`GET`/`PATCH` `/profile`**. **401** → wrong/missing token. **Never** put the token in the URL (SPEC §3.8). | Continue | Rotate token in server env if leaked; update admin page input. |
| **F** | **Still stuck on one failed explain** — default **`LEXIE_LOG_REQUESTS=0`**: you **do not** have transcript/explanation in the DB. See **§2** (short opt-in debug). | — | — |

---

## 2. Short opt-in debug (PII — use privately)

1. On a **staging** or **private** deployment only, set **`LEXIE_LOG_REQUESTS=1`** (SPEC §7).  
2. Reproduce one failing **`POST /explain`**.  
3. Inspect **`explain_request`** rows (or app logs that include **request id** + **stage** `stt` / `llm` / `tts`) — **redact** before sharing.  
4. Set **`LEXIE_LOG_REQUESTS=0`** again when finished.  
5. For **cost** questions, use the [OpenAI usage dashboard](https://platform.openai.com/usage) — Lexie does not replace billing (SPEC §8–9).

**Do not** leave logging on longer than needed: rows contain **transcript and response text** (child-related PII).

---

## 3. Symptom → likely cause

| Symptom | Likely cause | Check |
|--------|----------------|--------|
| **Immediate JSON error** after record (e.g. `audio_too_short`) | Clip &lt; ~0.4 s or release timing | Longer hold; SPEC §3.5 |
| **`transcription_empty`** | Silence, wrong mic, too quiet | Mic permission, level, environment |
| **`openai_unavailable` / 502 / 503** | OpenAI outage, rate limit, network | OpenAI status; retries in SPEC §5 |
| **Works on laptop, not on phone to same host** | **CORS** or **non-secure context** | SPEC §6; add origin to `LEXIE_CORS_ORIGINS` |
| **Admin saves “fail”** | **401** admin token; **network** to `PATCH` | DevTools → failed `fetch` |
| **Child hears nothing but 200** | Client audio playback bug, or wrong `Content-Type` | Browser / prototype code |

---

## 4. SLO reminder

- **p95** e2e **&lt; 5 s** on a **warm** instance (SPEC §8.2) — cold start on cheap tiers can add seconds; set **min machines = 1** (or equivalent) on your host.  
- **Uptime** checks: external ping on **`GET /health`**.

---

## 5. Related

- **First run (ordered steps):** [phased-delivery-plan.md](phased-delivery-plan.md) (first-run section)  
- **Error codes → calm child copy:** [lexie-word-explainer.SPEC.md](lexie-word-explainer.SPEC.md) §5.1  
- **Test matrix (what to automate):** [lexie-word-explainer.validation-matrix.md](lexie-word-explainer.validation-matrix.md)

---

*End of document.*
