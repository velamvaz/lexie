# LX-4 — Device UX & latency SLA PRD

**Feature:** LX-4 (Physical device — Phase 2)  
**Version:** 1.1  
**Date:** 2026-05-22 · **Bench start:** 2026-05-22  
**Status:** Execution — latency re-baseline pending **WX-036** / **WX-032**
**Parent:** [lexie-word-explainer.PRD.md](lexie-word-explainer.PRD.md) §4, §8  
**Server SPEC:** [lexie-word-explainer.SPEC.md](../committed-to-build/lexie-word-explainer.SPEC.md) §8.2

---

## 1. Purpose

Document **user-experience and latency SLAs** for the Lexie device and how **Path B (Waveshare)** affects them vs Path A, Pi, or vendor firmware.

---

## 2. Child-facing UX targets (unchanged)

| Experience | Target | Source |
|------------|--------|--------|
| Pick up → ready to press PTT | **~2 s** boot class (ESP32-S3) | PRD / WX-024 boot rationale |
| Press → hear explanation | **“A few seconds”** (~3–5 s story in PRD journey) | PRD §4 |
| Single PTT → one explain (Phase 2) | One `POST /explain` | Phase 1 scope |
| Error tone | Calm, non-technical | PRD §5 / SPEC §5.1 |

**Pi Zero (~30 s boot)** remains **out of scope** for product UX.

---

## 3. Server-side SLO (unchanged by hardware path)

| SLO | Target | Observed (2026-05-01, Fly) |
|-----|--------|----------------------------|
| **p95** server e2e (audio in → TTS bytes ready) | **&lt; 5 s** warm, short utterance | **~6–7 s** (`X-Explain-Latency-Ms`, `LEXIE_HEADWORD_TTS=0`) — **documented exception** in SPEC §11 |

Hardware path (Path A vs Waveshare) **does not change** this SLO — same `BASE_URL`, same pipeline.

---

## 4. End-to-end latency budget (conceptual)

```text
T_total ≈ T_boot_session + T_record + T_upload + T_server + T_download + T_play_start
```

| Segment | Owner | Path B (Waveshare) note |
|---------|-------|-------------------------|
| **T_boot_session** | Device | Same ESP32-S3 class; codec I2C init may add **~0.1–1 s** once — measure in WX-036 |
| **T_record** | Device | User-controlled (0.4–30 s) |
| **T_upload** | Device + Wi‑Fi | WAV size; compression TBD (PRD Q2) |
| **T_server** | Lexie server | **Dominant today (~6–7 s)** |
| **T_download + T_play_start** | Device | Small vs server; ES8311 path |

**Product story “3–5 s”** requires **server latency improvement** — not switching to Waveshare alone.

---

## 5. Platform comparison (SLA impact)

| Platform | Boot SLA | Server SLA | Network control | Bench fit |
|----------|----------|------------|-----------------|-----------|
| **Path A** (XIAO + breakouts) | ✅ ESP32 | Unchanged | ✅ if Lexie firmware | High wiring friction |
| **Path B** (Waveshare + Lexie FW) | ✅ ESP32 | Unchanged | ✅ if erase + Lexie FW | **Active** |
| **Waveshare stock demo** | — | N/A | ❌ vendor cloud | **Do not use** |
| **Pi + HAT** | ❌ ~30 s | Unchanged | Configurable | Dev mule only |
| **reSpeaker Lite + Lexie** | ✅ XIAO inside | Unchanged | ✅ if Lexie FW | Alternative integrated |

---

## 6. Re-baseline required (Path B)

After **WX-036** / **WX-032**, record in work-log:

| Metric | How measured |
|--------|--------------|
| Cold boot → ready for PTT | Stopwatch / log timestamp |
| PTT release → HTTP POST started | Firmware log |
| PTT release → first audio byte | End-to-end; compare to `X-Explain-Latency-Ms` + device segments |

---

## 7. Acceptance

- [ ] Device boot remains **ESP32-class** (not Pi-class)  
- [ ] End-to-end explain succeeds with audible MP3  
- [ ] Documented server latency exception (**~6–7 s**) still tracked as Phase 1/2 parallel polish  
- [ ] No regression claim that Waveshare alone fixes p95 &lt; 5 s  

---

## Decision log

| Date | Decision |
|------|----------|
| 2026-05-22 | Path B does not relax UX SLAs; server SLO remains binding; device re-baseline added |
| 2026-05-22 | Waveshare board delivered — measure codec init + e2e after WX-036/032 |
