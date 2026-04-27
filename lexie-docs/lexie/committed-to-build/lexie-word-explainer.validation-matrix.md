# Lexie Word Explainer — validation matrix (LX-1)

**Date:** 2026-04-22  
**SPEC:** [lexie-word-explainer.SPEC.md](lexie-word-explainer.SPEC.md)  
**PRD:** [../prds/lexie-word-explainer.PRD.md](../prds/lexie-word-explainer.PRD.md)  
**Journeys + observability anchor (verification):** [lexie-word-explainer.journeys-and-observability.md](lexie-word-explainer.journeys-and-observability.md)

**Legend:** **C** = contract test (CI), **M** = mocked OpenAI pipeline test, **E2E** = real keys (staging, optional in CI), **J** = manual / eval, **1b** = Phase 1b (out of scope for initial Phase 1 code merge).

| ID | User journey / scenario | PRD / SPEC ref | C | M | E2E | J | Notes |
|----|------------------------|----------------|:-:|:-:|:---:|:-:|-------|
| J-1a | **Journey 1** — child asks one **simple word**; hears explanation; returns to reading | PRD J1 |  |  | x | x | e.g. “sorcerer” (PRD); **M** not required to assert vocabulary choice |
| J-2a | **Journey 2** — word + **context** in same hold | PRD J2 |  | x | x | x | **M** asserts `age_years` / `reading_level` in prompt; transcript passed through |
| J-3a | **Journey 3** — **out-of-scope** (Hogwarts) → one-line **redirect** | PRD J3 |  | x | x | x | 200 with TTS; model string per PRD |
| J-5-L0 | **Journey 5** — **Level 0** only: messy / approximate utterance, **one** PTT | PRD J5, §4 |  | x | o | x | **No** multi-PTT session; **E2E** = optional |
| J-5-1b | J5 **Levels 1–3** (oral fork, spell, kind stop) | PRD J5, SPEC §12/§15 | — | — | — | — | **1b** — not Phase 1 scope |
| J-4 | **Journey 4** — **parent** edits `age_profile` on `/admin` | PRD J4, SPEC §3.4/§3.8 | x |  | o | x | **C:** `GET /admin` 200 HTML; `GET`/`PATCH` profile 401/200 |
| P0 | `GET /health` | SPEC §3.2 | x |  | x |  |  |
| P0 | `POST /explain` **auth** in prod (401 without key) | SPEC §3.5 | x |  |  |  |  |
| P0 | `audio_too_short` &lt; ~0.4s | SPEC §3.5, §5 | x | x | o | o |  |
| P0 | `transcription_empty` (after Whisper) | SPEC §3.5, §5 | x | x |  | o |  |
| P0 | `payload_too_large` &gt; 2 MiB | SPEC §3.5 | x |  |  | o |  |
| P0 | **Error tone** — on-screen line matches §5.1 spirit | PRD, SPEC §5.1 |  |  |  | x |  |
| SLO | **p95** e2e &lt; 5s warm, short utterance | SPEC §8 |  |  | o | o |  |

`x` = in scope; `o` = optional for that layer; blank = not primary for that test type.

**PRD manual eval set (non-exhaustive):** sorcerer, phrasal-verb phrasing, “What is Hogwarts?”, &lt;0.5s silence, ~35s clip (reject path).

**How to use:** Phase 1 **merge gate** = all **C** and **M** cases implemented and passing. **E2E** and **J** for release confidence and product QA.

---

*End of document.*
