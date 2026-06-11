# Lexie — AI word explainer (Lexie Card)

Lexie is **Lexie Card** — a thin, **WiFi**-connected physical device about the **size of a credit card** that sits **beside the open book** (not clipped to pages in v1). The child **presses and holds** to talk, speaks a word (or a word with context), and Lexie responds with a clear, age-appropriate spoken explanation.

## Why Lexie Exists

Advanced young readers — like a 6-year-old working through Harry Potter — frequently encounter vocabulary that is beyond their current understanding. Stopping to find a dictionary breaks the reading flow and can be discouraging. Lexie keeps the magic alive by answering in the moment, in language the child actually understands.

## What Lexie Does (and Only Does)

- Listens for a word or short phrase after the button is pressed
- Explains the word at the child's current reading/age level
- Accepts optional context ("what does 'sorcerer' mean when Harry Potter is at school?")
- Grows with the child — explanation complexity tracks the child's age profile

Lexie is deliberately constrained. It does not browse the internet, answer general questions, tell stories, play games, or do anything except explain words.

## Repo Layout

```
lexie-docs/
  README.md                         — this file
  REGISTRY.md                       — feature index (prefix: LX)
  lexie/
    prds/                           — product requirements (*.PRD.md)
    committed-to-build/             — finalized specs (*.SPEC.md)
    decisions/                      — meeting notes and summaries
    architecture/                   — technical design docs
```

## Feature Lifecycle

```
IDEA → PRD → SPEC → IN PROGRESS → SHIPPED
```

## Document Naming

| Suffix | Location | Example |
|--------|------------|---------|
| `.PRD.md` | `prds/` | `lexie-word-explainer.PRD.md` |
| `.SPEC.md` | `committed-to-build/` | `lexie-word-explainer.SPEC.md` |
| `.SUMMARY.md` | `decisions/` | `2026-04-08-kickoff.SUMMARY.md` |

## System Overview

```
[Button Press] → [MEMS Mic] → [Device Firmware]
                                    │
                 WiFi (home or parent hotspot) / HTTPS POST /explain
                                    │
                 [Lexie server — public host you deploy, e.g. Fly/Railway]
                                    │
                   ┌────────────────┼────────────────┐
             Whisper (STT)    GPT-4o (explain)   TTS (speak)   ← OpenAI APIs
                                    │
                    [One age profile — SQLite / app DB]
                                    │
                        [Audio response → Speaker]
```

Develop with `uvicorn` on a laptop; **production** is the deployed URL (not a home machine you must keep awake).

## Phases

| Phase | Description | Status |
|-------|-------------|--------|
| 1 | FastAPI + OpenAI pipeline, **deployed HTTPS host**, browser prototype | **SPEC ready** — [committed-to-build/lexie-word-explainer.SPEC.md](lexie/committed-to-build/lexie-word-explainer.SPEC.md) |
| 2 | **Lexie Card** — ESP32-S3 firmware (**Waveshare** bench board), ID-1 footprint, same `/explain` API · [lx-4-waveshare-device.PRD.md](lexie/prds/lx-4-waveshare-device.PRD.md) · [hardware/lexie-plaud-form-factor.html](../hardware/lexie-plaud-form-factor.html) | Active (LX-4) |
| 3 | OTA firmware, optional wake word / hardening (server already public in Phase 1) | Future |

## Related Artifacts

- [**Lexie Card** v1 spec (HTML)](../hardware/lexie-plaud-form-factor.html) — canonical Phase 2 mechanical layout (ID-1, ≤ 8 mm, beside the book, no magnets)  
- [Device design exploration (HTML)](lexie/architecture/device-design-exploration.html) — earlier UX exploration; v1 hardware story is **Lexie Card** above
- [Lexie Word Explainer — **Master checklist (builder)**](lexie/committed-to-build/lexie-word-explainer.MASTER-CHECKLIST.md) · [API & data model](lexie/committed-to-build/lexie-word-explainer.API-and-data-model.md) — entities, reference DDL, metadata · [Journeys & observability](lexie/committed-to-build/lexie-word-explainer.journeys-and-observability.md) · [Budget & rollout (ROM, milestones)](lexie/committed-to-build/lexie-word-explainer.BUDGET-AND-ROLLOUT.md) · [Runbook (operator triage)](lexie/committed-to-build/lexie-word-explainer.RUNBOOK.md) · [validation matrix](lexie/committed-to-build/lexie-word-explainer.validation-matrix.md) · [testing strategy](lexie/committed-to-build/lexie-word-explainer.TESTING-strategy.md) · [phased delivery](lexie/committed-to-build/phased-delivery-plan.md) — support [SPEC](lexie/committed-to-build/lexie-word-explainer.SPEC.md)
