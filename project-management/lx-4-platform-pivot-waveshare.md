# LX-4 platform pivot — Path A → Path B (Waveshare)

**Decision date:** 2026-05-22  
**Status:** **Execution** — Waveshare board **delivered**; **WX-035** in progress  
**Supersedes for active bench work:** Path A ([`lx-4-path-a-component-kit.md`](lx-4-path-a-component-kit.md))  
**Preserves:** Server contract, UX SLOs, network policy intent, WX-025 provisioning shape

---

## Summary

Lexie **Phase 2 device bring-up** moves from **discrete breakouts on breadboard** (XIAO + INMP441 + MAX98357) to **Waveshare ESP32-S3-AUDIO-Board** — an integrated ESP32-S3 board with dual mics, codec (ES8311/ES7210), speaker header, battery management, and Wi‑Fi.

**Unchanged:**

- **LX-1 server** — `POST /explain`, OpenAI on server only  
- **[DEVICE-INTEGRATION.md](../lexie-docs/lexie/committed-to-build/lexie-word-explainer.DEVICE-INTEGRATION.md)** — HTTPS to `BASE_URL` only  
- **WX-025** — USB serial provisioning, `config.json`, 3 Wi‑Fi profiles  
- **Boot-class UX** — ESP32-S3 (~2 s), not Pi (~30 s)  
- **Network sovereignty** — only chosen SSIDs + only Lexie server host (no vendor AI cloud)

**Changed:**

- **Hardware assembly** — no breadboard header soldering path for primary bring-up  
- **Audio stack** — ES8311 (out) + ES7210 (in) via I2C/I2S, not INMP441/MAX98357  
- **Enclosure** — shape/thickness **flexible** for bench; Lexie Card mechanical doc is **target**, not gate for Path B  
- **Firmware** — likely **ESP-IDF or hybrid** for codec init (Waveshare examples); MicroPython remains goal if port feasible  

---

## Why (conversation capture, 2026-05-22)

| Driver | Notes |
|--------|--------|
| **Integration pain** | Breadboard, header orientation, round INMP441 — high friction for builder |
| **Same product needs** | Wi‑Fi MCU + digital mic + speaker + HTTPS to Lexie server |
| **Pre-built kits explored** | Pi+HAT (rejected: boot), Xiaozhi/ESPHome (rejected: vendor cloud), **Waveshare** (accepted with **full flash erase + Lexie firmware**) |
| **Shape secondary** | User: card thickness not blocking bench path |
| **Network control #1** | User: no unintended connections — **stock Waveshare demo firmware must not ship** |
| **UX SLAs** | Server p95 &lt;5 s (observed ~6–7 s) unchanged; device boot SLA preserved on ESP32-S3 |

---

## Path A disposition (parts already purchased)

| Part | Disposition |
|------|-------------|
| XIAO ESP32-S3 (headers soldered) | **Spare / reference** — not primary LX-4 bench |
| MAX98357 + terminal + speaker wiring | **Spare** — audio path lessons apply |
| INMP441 (round, partial) | **Spare** |
| Breadboard kit | **Shop tool** — optional jig only |
| 503040 LiPo | **Reuse** if connector fits Waveshare MX1.25/JST — **verify polarity** before plug |

Path A docs remain for history: [`lx-4-path-a-component-kit.md`](lx-4-path-a-component-kit.md), [`wx-027-beginner-bench-guide.html`](wx-027-beginner-bench-guide.html).

---

## Path B primary docs (new)

| Doc | Role |
|-----|------|
| [lexie-docs/lexie/prds/lx-4-waveshare-device.PRD.md](../lexie-docs/lexie/prds/lx-4-waveshare-device.PRD.md) | Hardware + bench PRD |
| [lexie-docs/lexie/prds/lx-4-device-firmware.PRD.md](../lexie-docs/lexie/prds/lx-4-device-firmware.PRD.md) | Firmware, network, provisioning |
| [lexie-docs/lexie/prds/lx-4-device-ux-sla.PRD.md](../lexie-docs/lexie/prds/lx-4-device-ux-sla.PRD.md) | Device-side UX/latency SLAs |
| [lx-4-path-b-waveshare-kit.md](lx-4-path-b-waveshare-kit.md) | BOM + order checklist |
| [lx-4-network-policy.md](lx-4-network-policy.md) | Allowlist rules (normative for firmware) |
| [lx-4-path-b-bench-testing.md](lx-4-path-b-bench-testing.md) | Path B test phases |
| [lexie-word-explainer.PINMAP-WAVESHARE-AUDIO.md](../lexie-docs/lexie/committed-to-build/lexie-word-explainer.PINMAP-WAVESHARE-AUDIO.md) | GPIO / I2S / I2C pin map (WX-029) |

---

## Work items

| ID | Title | Status |
|----|-------|--------|
| **WX-034** | Platform pivot — Waveshare Path B (decision + PRD set) | **done** (this doc + PRDs) |
| **WX-027** | Path A solder prep | **superseded** by Path B — partial work kept as spare |
| **WX-035** | Path B unbox + erase vendor firmware | **in progress** (board delivered) |
| **WX-036** | Path B codec audio smoke (ES8311/ES7210) | **backlog** |
| **WX-028–033** | Retarget to Waveshare (see [work-inventory.md](work-inventory.md) § D3) | **backlog** (updated) |

**Suggested order:** **WX-035** → **WX-028** → **WX-036** → **WX-029** → **WX-033** → **WX-032**.

---

## Risks accepted

1. **Vendor demo firmware** phones home if flashed and left — mitigated by **full erase + Lexie image only**.  
2. **Codec driver effort** higher than bare I2S breakouts — accepted for integration speed.  
3. **MicroPython** on Waveshare not guaranteed day one — ESP-IDF acceptable for WX-036 smoke.  
4. **Path A sunk cost** — parts remain useful as spares, not wasted for learning.

---

## Related

- Prior platform lock: **WX-024** (2026-05-03) — **amended** by **WX-034**, not deleted from history  
- [Waveshare product page](https://www.waveshare.com/esp32-s3-audio-board.htm) · [Wiki](https://www.waveshare.com/wiki/ESP32-S3-AUDIO-Board)
