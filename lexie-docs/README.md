# Lexie — AI-Powered Smart Bookmark

Lexie is a physical clip-on bookmark that helps children understand words they encounter while reading. The child presses a button, speaks a word (or a word with context), and Lexie responds with a clear, age-appropriate spoken explanation.

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
| 2 | ESP32-S3 or Pi Zero 2W firmware + physical bookmark | Future |
| 3 | OTA firmware, optional wake word / hardening (server already public in Phase 1) | Future |

## Related Artifacts

- [Device design exploration (HTML)](lexie/architecture/device-design-exploration.html) — Phase 2 hardware form factor exploration (open in a browser)
