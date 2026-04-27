# Lexie Word Explainer — budget (ROM) and rollout milestones (LX-1)

**Date:** 2026-04-22  
**Audience:** Parent builder / one-child deployment  
**Contract & SLOs:** [lexie-word-explainer.SPEC.md](lexie-word-explainer.SPEC.md) (§2 hosting, §8 usage and SLOs)  
**First run order:** [phased-delivery-plan.md](phased-delivery-plan.md)  
**When things break:** [lexie-word-explainer.RUNBOOK.md](lexie-word-explainer.RUNBOOK.md)  
**Test mapping:** [lexie-word-explainer.validation-matrix.md](lexie-word-explainer.validation-matrix.md) · [lexie-word-explainer.TESTING-strategy.md](lexie-word-explainer.TESTING-strategy.md)

**Important:** Dollar figures below are **rough order of magnitude (ROM)** for planning. **OpenAI and host prices change** — always confirm on [OpenAI API pricing](https://openai.com/api-pricing/) and your provider’s page before you budget. The **OpenAI usage dashboard** is the source of truth for API spend (SPEC §2, §8.3).

---

## 1. Rollout milestones: what to build, what to test, in order

| Milestone | What you stand up | What you prove (testing) | Doc tie-in |
|-----------|-------------------|----------------------------|------------|
| **M0 — Local** | App on laptop; no public URL | `GET /health`; `POST /explain` with key; `GET`/`PATCH` `/profile`; `GET /admin` | Contract + mocked pipeline (TESTING strategy); no TLS/CORS yet |
| **M1 — Public HTTPS** | Host + DNS + TLS; `BASE_URL` works from internet | `https://…/health` **200** from home + phone (cellular); optional external ping (UptimeRobot, etc.) | RUNBOOK §1 A–B; SPEC §3.2, §8.2 |
| **M2 — Child browser path** | Prototype origin + `LEXIE_CORS_ORIGINS` + device key in client | One full **J1–J3** style run: multipart audio → MP3; check latency vs **p95 &lt; 5 s** warm (SPEC §8.2) | Validation matrix J-1a–J-3a; SPEC §6 secure context for mic |
| **M3 — Parent admin** | Admin token in page; profile save | **J4:** `GET /admin` 200; `GET`/`PATCH` profile 401 without token, 200 with | SPEC §3.8; matrix J-4 |
| **M4 — E2E shakedown** | Staging or prod with real **OpenAI** key | PRD eval set: sorcerer, phrasal, Hogwarts, `audio_too_short`, long clip; error copy §5.1 on forced failures | Matrix “Manual eval set”; optional E2E in TESTING strategy |
| **M5 — Steady ops** | Budget alert in OpenAI; logging default **off** | `LEXIE_LOG_REQUESTS=0`; short opt-in logging only for debug (then off) | RUNBOOK §2; journeys & observability §3 |

**Merge gate (when code exists):** automated **contract** + **mocked pipeline** green; E2E manual for release confidence (TESTING strategy).

---

## 2. Services and who bills you

| Service | Purpose | Typical billing model | Notes (SPEC) |
|---------|---------|------------------------|--------------|
| **App host** (e.g. Fly.io, Railway, Render, or small VPS) | Always-on FastAPI + TLS termination | **Fixed** monthly on small tier | §2: prefer **min machines = 1** to limit cold first explain |
| **Domain** | Human-readable `BASE_URL` | **~$10–15/year** (amortize mentally) | — |
| **DNS** | Point name → host | Often **$0** (provider / Cloudflare) | — |
| **TLS** | HTTPS | **$0** (Let’s Encrypt or host-managed) | — |
| **OpenAI API** | Whisper + chat + TTS | **Pay per use** (dominant variable cost) | Set **monthly budget alert** in org; ChatGPT **subscription** is separate — you need **API** keys for the server |
| **Uptime monitor** (optional) | External `GET /health` | **$0** free tier or low monthly | SPEC §8.2 |
| **lexie-ops** (local) | Dev machine polls health | **$0** | [monitoring/lexie-ops/README.md](../../../monitoring/lexie-ops/README.md) |

There is no separate “Lexie platform” fee in this design: **host + domain (annual) + OpenAI usage** (+ optional monitor).

---

## 3. Usage anchor (not a price)

From SPEC §8.1 (single child, capacity planning):

| Phase (habit) | Explains / day (typical) | Heavy day |
|-----------------|--------------------------|-----------|
| Onboarding | 3–15 | 25–40 |
| Habit | 5–25 | 40–60 |
| Steady | 10–35 | 60–100 |

Use these to **estimate monthly explain count** = (typical daily band) × ~30, then multiply by your **empirical $/explain** from the OpenAI dashboard after a week of use (§4).

---

## 4. ROM monthly budget (how to think about it)

**Fixed (typical for a tiny always-on app):** **~$5–15/month** for the host (varies by provider and region). **Domain** averages **~$1/month** if you spread **~$12/year** over 12 months.

**Variable (almost always largest):** **OpenAI** ≈ *monthly explain count* × *average all-in cost per explain* (Whisper + one chat completion + TTS; **two TTS** if `LEXIE_HEADWORD_TTS=1`).

- **Per explain** depends on: audio **duration** (Whisper is often priced per **minute** of audio), **model** and **max_tokens** for the chat step, and **TTS character count** (and model tier). A **practical planning band** for a short child utterance and a short answer is on the order of **a few cents to ~$0.15** per full explain, before any discounting or model changes — **do not** treat that as a guarantee; **measure**.

**Order-of-magnitude total (one child, “normal” reading use per SPEC bands):**

- **Light month** (low use + host): often **~$5–25/month** if API use is small.  
- **Typical habit / steady** month: often **tens of dollars** combined, with **OpenAI** as the main line.  
- **Heavy** month (high daily volume, longer answers, or **headword TTS** on): **OpenAI** can move into **$50+** or higher — use **alerts** and the usage dashboard.

**Formula (for your own sheet):**  
`monthly_estimate ≈ host_fixed + domain/12 + (explains_per_month × measured_cost_per_explain)`.

**Calibration:** after deploy, run **10–20** real explains, read **cost** in the [OpenAI usage / billing](https://platform.openai.com/) view, and divide by count to get a **measured** per-explain number for *your* prompts and audio lengths.

---

## 5. Cost control (short list)

1. **OpenAI:** org **budget cap / alert**; pick **efficient** chat and TTS models per your implementation; keep `max_tokens` and audio duration limits as in SPEC.  
2. **Host:** right-size VM; avoid **sleeping** to zero on free tiers if the SPEC’s first-interaction experience matters.  
3. **Logging:** keep **`LEXIE_LOG_REQUESTS=0`** unless debugging (RUNBOOK §2) — saves DB growth and PII risk, not primarily OpenAI $.

---

## 6. Related

- **SLO and what to measure:** [lexie-word-explainer.SPEC.md](lexie-word-explainer.SPEC.md) §8.3  
- **Observability without overspending on tools:** [lexie-word-explainer.journeys-and-observability.md](lexie-word-explainer.journeys-and-observability.md) §3  

---

*End of document.*
