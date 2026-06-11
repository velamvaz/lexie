# LX-4 — Waveshare device hardware PRD

**Feature:** LX-4 (Physical device — Phase 2)  
**Version:** 1.1 (Path B — hardware on bench)  
**Date:** 2026-05-22 · **Bench start:** 2026-05-22 (board delivered)  
**Status:** **Execution** — Waveshare board on hand; **WX-035** active (erase vendor FW before Wi‑Fi)  
**Parent product PRD:** [lexie-word-explainer.PRD.md](lexie-word-explainer.PRD.md)  
**Pivot record:** [lx-4-platform-pivot-waveshare.md](../../project-management/lx-4-platform-pivot-waveshare.md)  
**Pin map:** [lexie-word-explainer.PINMAP-WAVESHARE-AUDIO.md](../committed-to-build/lexie-word-explainer.PINMAP-WAVESHARE-AUDIO.md)

---

## 1. Purpose

Define the **hardware platform** for Lexie device firmware bring-up using **Waveshare ESP32-S3-AUDIO-Board**: integrated Wi‑Fi MCU, dual microphones, audio codec/amp, speaker path, and battery — without breadboard breakout assembly.

**Server contract unchanged:** [DEVICE-INTEGRATION.md](../committed-to-build/lexie-word-explainer.DEVICE-INTEGRATION.md).

---

## 2. Goals

| Goal | Metric |
|------|--------|
| **Voice in** | Record child utterance (0.4–30 s) as WAV/PCM for `POST /explain` |
| **Voice out** | Play MP3 response from server |
| **Connectivity** | Wi‑Fi STA to home or parent hotspot |
| **Power** | USB-C bench + optional LiPo portable |
| **Network sovereignty** | No vendor cloud — see [lx-4-network-policy.md](../../project-management/lx-4-network-policy.md) |
| **Boot UX** | ESP32-class fast boot (~2 s order of magnitude) |

**Mechanical:** Lexie Card (ID-1, ≤8 mm) remains the **long-term product vision**; Path B bench **does not block** on card thickness.

---

## 3. Platform decision

### 3.1 Chosen (2026-05-22)

| Item | Choice |
|------|--------|
| **Board** | [Waveshare ESP32-S3-AUDIO-Board](https://www.waveshare.com/esp32-s3-audio-board.htm) |
| **MCU** | ESP32-S3R8 (dual-core, Wi‑Fi 2.4 GHz, BLE capable — **BLE off in Lexie firmware**) |
| **Mic front-end** | Dual digital mics + **ES7210** ADC |
| **Speaker path** | **ES8311** DAC + onboard amp + speaker header |
| **Storage** | 16 MB flash, PSRAM (onboard) |
| **Power** | USB-C; MX1.25 2P LiPo charge path |

### 3.2 Rejected for primary path

| Option | Why rejected |
|--------|--------------|
| **Path A** (XIAO + INMP441 + MAX98357 + breadboard) | High assembly friction; superseded for active bench |
| **Raspberry Pi + audio HAT** | ~30 s boot — fails pick-up-and-press UX |
| **Stock Xiaozhi / ESPHome / vendor AI demos** | Unintended cloud connections |

### 3.3 Amended (not erased)

**WX-024 (2026-05-03):** XIAO + discrete I2S — **amended by WX-034**. History preserved in git and Path A docs.

---

## 4. BOM (Path B)

See [lx-4-path-b-waveshare-kit.md](../../project-management/lx-4-path-b-waveshare-kit.md).

| Item | Status |
|------|--------|
| **ESP32-S3-AUDIO-Board** | **On hand** (delivered 2026-05-22) |
| **USB-C data cable** | Required for flash — verify data-capable |
| **LiPo** (bundled or spare 503040) | Optional until portable test — **polarity first** |
| **8 Ω speaker** | Optional if using onboard speaker header |

Path A parts (XIAO, breakouts, breadboard) remain **spare only**.

---

## 5. Out of scope (board features — v1 Lexie)

Disable or ignore in firmware unless explicitly needed later:

- RGB ring LEDs (status LED may reuse one channel later — TBD)
- TF card slot
- SPI LCD / DVP camera headers
- Vendor offline voice / cloud LLM demos
- Bluetooth LE provisioning

---

## 6. Bench milestones (WX)

**Order:** **WX-035** → **WX-028** → **WX-036** → **WX-029** → **WX-033** → **WX-032**

| ID | Milestone | Status |
|----|-----------|--------|
| WX-034 | Platform pivot + PRD set | **done** |
| **WX-035** | Unbox; **erase vendor firmware**; polarity check | **in progress** ← **start here** |
| WX-028 | USB REPL / flash toolchain; Wi‑Fi smoke | backlog |
| WX-036 | ES8311/ES7210 record + playback smoke | backlog |
| WX-029 | Pin map verified on physical board | backlog (draft: [PINMAP](../committed-to-build/lexie-word-explainer.PINMAP-WAVESHARE-AUDIO.md)) |
| WX-033 | USB provisioning `config.json` | backlog |
| WX-032 | End-to-end `/health` + `/explain` + MP3 play | backlog |

---

## 7. First session (WX-035 — before Wi‑Fi)

1. **USB-C only** — inspect board; note variant (LiPo bundled or not).  
2. **Do not** join home Wi‑Fi on **stock/demo** firmware.  
3. **Full flash erase** — then flash Lexie or smoke image only.  
4. If using LiPo: multimeter polarity on MX1.25 **before** plug.

Details: [lx-4-path-b-bench-testing.md](../../project-management/lx-4-path-b-bench-testing.md) Phase 0.

---

## 8. Acceptance (hardware bench)

- [ ] Board powers from USB-C; REPL or serial log responds  
- [ ] Record + playback loop on device (WX-036) before server E2E  
- [ ] LiPo charges safely; polarity documented before first battery use  
- [ ] No vendor cloud traffic after Lexie firmware flash (network policy)  
- [ ] One successful `POST /explain` with audible MP3 (WX-032)

---

## 9. References

- [Waveshare wiki — ESP32-S3-AUDIO-Board](https://www.waveshare.com/wiki/ESP32-S3-AUDIO-Board)  
- [lx-4-device-firmware.PRD.md](lx-4-device-firmware.PRD.md)  
- [lx-4-device-ux-sla.PRD.md](lx-4-device-ux-sla.PRD.md)  
- [lx-4-path-b-bench-testing.md](../../project-management/lx-4-path-b-bench-testing.md)

---

## Decision log

| Date | Decision |
|------|----------|
| 2026-05-03 | WX-024: XIAO + discrete I2S (Path A) |
| 2026-05-22 | WX-034: Pivot to Waveshare Path B; shape flexible; network sovereignty required |
| 2026-05-22 | **Board delivered** — bench execution starts; PRD v1.1; WX-035 active |
