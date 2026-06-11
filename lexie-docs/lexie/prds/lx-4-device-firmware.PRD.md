# LX-4 — Device firmware PRD

**Feature:** LX-4 (Physical device — Phase 2)  
**Version:** 1.1 (Path B — bench execution)  
**Date:** 2026-05-22 · **Bench start:** 2026-05-22  
**Status:** **Execution** — board delivered; **WX-035** gate before any Wi‑Fi  
**Hardware PRD:** [lx-4-waveshare-device.PRD.md](lx-4-waveshare-device.PRD.md)  
**API contract:** [DEVICE-INTEGRATION.md](../committed-to-build/lexie-word-explainer.DEVICE-INTEGRATION.md)  
**Network policy:** [lx-4-network-policy.md](../../project-management/lx-4-network-policy.md)  
**Pin map:** [lexie-word-explainer.PINMAP-WAVESHARE-AUDIO.md](../committed-to-build/lexie-word-explainer.PINMAP-WAVESHARE-AUDIO.md)

---

## 0. Immediate gate (WX-035)

**Before** joining Wi‑Fi or running vendor demos:

1. Connect **USB-C data** cable only (bench power).  
2. **Full flash erase** of stock Xiaozhi / Waveshare demo image.  
3. Flash **Lexie** smoke or production image — never ship stock firmware.  
4. Optional LiPo: polarity verified per hardware PRD §7.

Normative: [lx-4-network-policy.md](../../project-management/lx-4-network-policy.md).

---

## 1. Purpose

Define **firmware behavior** for the Lexie physical device on **Waveshare ESP32-S3-AUDIO-Board**: provisioning, Wi‑Fi, HTTPS client, audio capture/playback, PTT flow, and **explicit network allowlisting**.

---

## 2. Non-goals

- Device does **not** call OpenAI  
- Device does **not** run LLM/STT/TTS  
- Device does **not** use Xiaozhi, ESPHome default cloud, or Waveshare demo AI endpoints  
- No SoftAP provisioning in Phase 2 (USB serial only — **WX-025**)

---

## 3. Runtime stack (decided direction)

| Layer | Path B choice | Notes |
|-------|---------------|-------|
| **Phase 2a smoke** | **ESP-IDF** (Waveshare examples as reference only) | Codec init ES8311/ES7210 — **WX-036** |
| **Phase 2b product** | **MicroPython** if feasible on board; else IDF | Re-evaluate after WX-036 |
| **Config** | JSON on flash filesystem | **WX-033** shape from **WX-025** |

**Rule:** Vendor example code is **reference**, not shipped. Full flash erase before Lexie image.

---

## 4. Boot sequence

```
Power on
  → Load config.json from flash
  → Wi-Fi: try networks[0..2] in order until connected
  → Optional: GET {base_url}/health → 200 (status LED)
  → Idle (await PTT)
```

On Wi‑Fi failure: retry with back-off; error LED pattern per DEVICE-INTEGRATION §8.

---

## 5. PTT session flow

Same as [DEVICE-INTEGRATION §10](../committed-to-build/lexie-word-explainer.DEVICE-INTEGRATION.md):

```
PTT press → record (0.4–30 s) → PTT release
  → POST {base_url}/explain (multipart audio, Bearer device_key)
  → 200: play MP3 bytes
  → 4xx/5xx: error cue per §8
```

**Audio format:** WAV/PCM to start (PRD open Q2); match server accepted types.

---

## 6. Provisioning (WX-025 / WX-033)

**Mechanism:** USB serial one-time setup from parent laptop.

**Config shape:**

```json
{
  "networks": [
    {"ssid": "...", "password": "..."},
    {"ssid": "...", "password": "..."},
    {"ssid": "...", "password": "..."}
  ],
  "base_url": "https://lexie-server.fly.dev",
  "device_key": "..."
}
```

**Secrets:** from 1Password at provision time; never in git.

---

## 7. Network security requirements

Normative: [lx-4-network-policy.md](../../project-management/lx-4-network-policy.md).

**Firmware MUST:**

- Parse `base_url` and restrict HTTPS client to that **host** only  
- Use TLS 1.2+ with standard CA bundle  
- Send device key only in `Authorization: Bearer` or `X-Device-Key`  
- Not embed third-party API keys  

**Firmware MUST NOT (default build):**

- Start SoftAP or BLE provisioning  
- Call URLs not derived from `base_url`  
- Run Waveshare cloud voice / Xiaozhi / DeepSeek demo endpoints  

---

## 8. Audio subsystem (Waveshare)

| Component | Role |
|-----------|------|
| **ES7210** | Mic ADC (I2S out from device perspective) |
| **ES8311** | DAC / headphone / speaker path |
| **I2C** | Codec configuration — **GPIO10/11** per [PINMAP](../committed-to-build/lexie-word-explainer.PINMAP-WAVESHARE-AUDIO.md) |

**WX-029:** Verify pin map on physical board; update PINMAP if silkscreen differs.

---

## 9. Error handling

Use [DEVICE-INTEGRATION §8](../committed-to-build/lexie-word-explainer.DEVICE-INTEGRATION.md) codes for LED/audio cues.

---

## 10. Acceptance

- [ ] `config.json` read at boot (**WX-033**)  
- [ ] Wi‑Fi connects to configured SSID only  
- [ ] `GET /health` → 200  
- [ ] `POST /explain` → play MP3 (**WX-032**)  
- [ ] Packet capture or router log shows **only** Lexie server (+ optional NTP)  
- [ ] Vendor firmware **not** present after WX-035 erase + flash  

---

## Decision log

| Date | Decision |
|------|----------|
| 2026-05-03 | WX-025 USB serial provisioning |
| 2026-05-22 | Path B: Waveshare; network allowlist; no vendor demo firmware |
| 2026-05-22 | Board delivered; §0 WX-035 gate; PINMAP draft linked; v1.1 execution |
