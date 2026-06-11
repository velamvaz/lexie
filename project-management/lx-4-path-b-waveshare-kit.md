# LX-4 Path B — Waveshare kit (bench)

**Platform:** [Waveshare ESP32-S3-AUDIO-Board](https://www.waveshare.com/esp32-s3-audio-board.htm)  
**Decision:** [lx-4-platform-pivot-waveshare.md](lx-4-platform-pivot-waveshare.md) · **WX-034**  
**PRD:** [lx-4-waveshare-device.PRD.md](../lexie-docs/lexie/prds/lx-4-waveshare-device.PRD.md) (v1.1)  
**Status:** **Board delivered 2026-05-22** — **WX-035** in progress

---

## On hand

| # | Item | Status |
|---|------|--------|
| 1 | **ESP32-S3-AUDIO-Board** | **Delivered** |
| 2 | **USB-C data cable** | Verify data-capable before flash |
| 3 | **LiPo** | Note variant (bundled MX1.25 or use spare 503040) — **polarity before plug** |
| 4 | **Speaker** | Optional — board has speaker header |

**Do not need for Path B primary path:** breadboard, INMP441, MAX98357 (spare from Path A).

---

## What is on the board (integration map)

| Function | Chip / feature | Lexie use |
|----------|----------------|-----------|
| MCU + Wi‑Fi | ESP32-S3R8 | Same role as XIAO — Lexie client firmware |
| Mic in | Dual mics + **ES7210** | Record for `/explain` |
| Audio out | **ES8311** + amp | Play MP3 response |
| Power | USB-C + MX1.25 battery + charger | Bench + portable |
| **Not used for v1 Lexie** | RGB LEDs, TF slot, camera/LCD headers, BLE demos | Leave disabled in firmware |

**Pin map (draft):** [lexie-word-explainer.PINMAP-WAVESHARE-AUDIO.md](../lexie-docs/lexie/committed-to-build/lexie-word-explainer.PINMAP-WAVESHARE-AUDIO.md) — I2C **GPIO10/11**, I2S **MCLK 12, BCLK 13, LRCLK 14, DOUT 15, DIN 16**. Verify on board (**WX-029**).

---

## WX-035 checklist (active)

- [ ] Visual inspect — no shipping damage  
- [ ] **Do not** join home Wi‑Fi with **stock/demo** firmware  
- [ ] **Full flash erase** before any network test  
- [ ] Document battery connector polarity if using external LiPo  
- [ ] Note variant + photo in [work-log/2026-05.md](work-log/2026-05.md)

---

## Path A parts (already owned)

Keep as **spare/reference** — see [platform pivot doc](lx-4-platform-pivot-waveshare.md).

---

## Related

- [lx-4-network-policy.md](lx-4-network-policy.md)  
- [lx-4-path-b-bench-testing.md](lx-4-path-b-bench-testing.md)  
- [hardware-shopping-cart.md](hardware-shopping-cart.md) (Path A archive)
