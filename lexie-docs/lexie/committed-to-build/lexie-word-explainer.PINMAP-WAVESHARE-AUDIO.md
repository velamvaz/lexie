# Lexie — Waveshare ESP32-S3-AUDIO-Board pin map

**Status:** Verified on bench (WX-029, 2026-05-22) — codec demo boot log + playback beeps matched draft pins  
**Hardware PRD:** [lx-4-waveshare-device.PRD.md](../prds/lx-4-waveshare-device.PRD.md)  
**Source:** [Waveshare wiki — ESP32-S3-AUDIO-Board](https://www.waveshare.com/wiki/ESP32-S3-AUDIO-Board)  
**Board:** ESP32-S3-AUDIO-Board (ESP32-S3R8, 16 MB flash, PSRAM)

---

## Audio codecs (Lexie v1)

| Bus | Signal | GPIO | Device | Notes |
|-----|--------|------|--------|-------|
| **I2C** | SDA | **10** | ES8311 + ES7210 | Shared codec config bus |
| **I2C** | SCL | **11** | ES8311 + ES7210 | |
| **I2S** | MCLK | **12** | ES8311 + ES7210 | |
| **I2S** | BCLK | **13** | ES8311 + ES7210 | |
| **I2S** | LRCLK (WS) | **14** | ES8311 + ES7210 | |
| **I2S** | DOUT | **15** | ES7210 → MCU | Mic ADC data **in** to ESP32 |
| **I2S** | DIN | **16** | MCU → ES8311 | Speaker DAC data **out** from ESP32 |

**Lexie firmware:** treat ES7210 as **capture** and ES8311 as **playback**. Do not wire Path A INMP441/MAX98357 on this bench.

---

## Product I/O (Phase 2 — TBD on bench board)

| Function | GPIO | Status |
|----------|------|--------|
| **PTT button** | TBD | Use onboard BOOT or header GPIO — assign in **WX-028** smoke firmware |
| **Status LED** | TBD | Board has RGB ring — Lexie may use one channel later; not required for WX-036 |

---

## Power

| Source | Connector | Notes |
|--------|-----------|-------|
| **USB-C** | Onboard | Bench + flash + serial — **use first** |
| **LiPo** | MX1.25 2P | **Verify polarity** with multimeter before first plug (**WX-035**) |

---

## Not used (Lexie v1)

- TF card slot  
- SPI LCD / DVP camera headers  
- BLE / Xiaozhi / vendor cloud demos  
- SoftAP provisioning  

---

## Verification checklist (WX-029)

- [x] I2C addresses for ES8311 and ES7210 match Waveshare example (typ. **0x18** / **0x40** — confirm in example code) — **ES8311 open OK in WX-036 boot log**
- [x] I2S GPIO numbers match silkscreen / schematic on **your** unit — **MCLK GPIO12** in WX-036 monitor log
- [x] Speaker header wired or external 8 Ω connected for playback tests — **beeps + WAV on KEY/BOOT**

---

## Decision log

| Date | Decision |
|------|----------|
| 2026-05-22 | Initial map from Waveshare wiki — pending physical verify on delivered board |
| 2026-05-22 | **WX-029 verified** — WX-036 Phase 1 playback; I2S MCLK GPIO12; ES8311 init OK |
