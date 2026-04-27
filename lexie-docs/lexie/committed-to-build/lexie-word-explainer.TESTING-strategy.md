# Lexie Word Explainer — testing strategy (LX-1 Phase 1)

**Date:** 2026-04-22  
**SPEC:** [lexie-word-explainer.SPEC.md](lexie-word-explainer.SPEC.md)  
**Validation map:** [lexie-word-explainer.validation-matrix.md](lexie-word-explainer.validation-matrix.md)

## 1. Pyramid

| Layer | Intent | When it runs | Gate for merge? |
|-------|--------|--------------|-----------------|
| **Contract (HTTP + auth + status codes)** | Prove routes and JSON/bytes shapes; no real OpenAI | Every CI | **Yes** |
| **Pipeline (mocked I/O)** | STT/LLM/TTS replaced with fakes; assert **prompt** uses profile, **TTS** call count vs `LEXIE_HEADWORD_TTS` | Every CI | **Yes** |
| **E2E (real API keys)** | Full path to MP3; latency smoke | Staging, release branch, on-demand | **No** (optional) if keys not in secret store |
| **Soak / manual** | Leaks, memory, UX eval | Ad hoc, pre-release | **No** |

## 2. Tooling (implementation-agnostic)

- **Framework:** `pytest` + `httpx` `ASGITransport` (or `TestClient`) for FastAPI.
- **OpenAI shims:** patch `openai` client, or run a **local mock HTTP** server, or dependency-inject a `transcribe/complete/tts` protocol with **fake** return values. Goal: no network in default CI.
- **DB:** in-memory SQLite or **temp** file; **seed** one `age_profile` row; override env so `LEXIE_DEVICE_KEY` / `LEXIE_ADMIN_TOKEN` are known in tests.
- **Artifacts:** on failure, print response body and **redact** any accidental token in logs (never log full Bearer).

## 3. What “mocked pipeline” must prove (minimum)

1. `age_years` and `reading_level` (and optional `explanation_style`) from DB appear in the model **messages** (or the assembled prompt string).
2. `LEXIE_HEADWORD_TTS=0` → exactly **one** TTS call (or one stub invocation).
3. `LEXIE_HEADWORD_TTS=1` with JSON `{ "explanation_text", "headword" }` → **two** TTS calls, concatenation order explanation → headword.
4. Whisper path receives bytes that match uploaded fixture size (smoke, not full binary equality).

## 4. E2E (real keys) checklist

- Host `BASE_URL` over HTTPS.  
- One J1, one J2, one J3 scenario; optional messy utterance (J5 L0) without session.  
- **Do not** commit keys; use CI **secrets** only if the pipeline is extended.

**Exit:** SPEC §10 + [validation matrix](lexie-word-explainer.validation-matrix.md) columns **C** + **M** + documented optional E2E.

---

*End of document.*
