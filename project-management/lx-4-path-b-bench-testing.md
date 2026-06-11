# LX-4 Path B — Bench testing (Waveshare)

**Platform:** Waveshare ESP32-S3-AUDIO-Board  
**PRD:** [lx-4-waveshare-device.PRD.md](../lexie-docs/lexie/prds/lx-4-waveshare-device.PRD.md) (v1.1)  
**Network policy:** [lx-4-network-policy.md](lx-4-network-policy.md)  
**Path A equivalent (archive):** [lx-4-path-a-bench-testing.md](lx-4-path-a-bench-testing.md)  
**Current phase:** **Phase 0 — WX-035** (board delivered 2026-05-22)

---

## Phase 0 — Reject vendor firmware (WX-035) ← **you are here**

| Step | Pass |
|------|------|
| Board received; photos in work-log | [x] |
| **Full flash erase** before joining Wi‑Fi | [x] 2026-05-22 — `erase_flash` OK |
| Confirm **no** Xiaozhi / Waveshare cloud demo running | [x] flash empty |

**Fail if:** board left on stock firmware talking to vendor services.

---

## Phase 1 — USB + toolchain (WX-028)

| Step | Pass |
|------|------|
| USB-C **data** cable; serial/REPL or `idf.py monitor` | ✓ |
| Flash **Lexie** test image (not vendor demo) | ✓ |
| `print("ok")` or equivalent | ✓ |

---

## Phase 2 — Codec smoke (WX-036)

| Step | Pass |
|------|------|
| ES7210: record short clip to buffer/file | ✓ |
| ES8311: play tone or loopback | ✓ |
| Levels sane; no excessive noise/hum | ✓ |

---

## Phase 3 — Wi‑Fi + power

| Step | Pass |
|------|------|
| Join **one** test AP (hardcoded OK before WX-033) | ✓ |
| Optional: 3.7 V LiPo — polarity verified before plug | ✓ |
| ~3.3 V rails stable (no overheating) | ✓ |

---

## Phase 4 — Lexie server E2E (WX-032)

| Step | Pass |
|------|------|
| `config.json` provisioned (**WX-033**) | ✓ |
| `GET /health` → 200 | ✓ |
| `POST /explain` → MP3 plays on speaker | ✓ |
| **Automated 10× stress** (`./tools/wx032-reliability.sh`) | ✓ `pass=10 fail=0` (2026-06-09) |
| One manual PTT smoke (product build, stress off) | ✓ (2026-06-09) |
| Router log: **only** Lexie host (+ optional NTP) | ✓ |

---

## Phase 5 — UX latency sample (optional)

Record boot → PTT → first audio byte; compare to [lx-4-device-ux-sla.PRD.md](../lexie-docs/lexie/prds/lx-4-device-ux-sla.PRD.md).

---

## Evidence log

```text
Date: ___________
WX-035 erase vendor FW: [ ]
WX-028 USB/toolchain:    [ ]
WX-036 codec smoke:      [ ]
WX-033 provisioned:      [ ]
WX-032 /explain E2E:     [x]  ← 10/10 2026-06-09 (log wx032-stress-20260609-205200.txt)
WX-032 PTT smoke:        [x]  ← manual PTT OK 2026-06-09
Network allowlist check: [ ]
```
