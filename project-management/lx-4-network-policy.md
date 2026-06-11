# LX-4 — Device network policy (normative)

**Applies to:** Path B (Waveshare) and any ESP32-S3 Lexie firmware  
**Provisioning design:** **WX-025** · **Contract:** [DEVICE-INTEGRATION.md](../lexie-docs/lexie/committed-to-build/lexie-word-explainer.DEVICE-INTEGRATION.md)  
**PRD:** [lx-4-device-firmware.PRD.md](../lexie-docs/lexie/prds/lx-4-device-firmware.PRD.md)

---

## Principle

The Lexie device is a **dumb HTTPS client**. It connects only to **Wi‑Fi networks the parent configured** and talks only to **the host in `BASE_URL`**. It **never** calls OpenAI or vendor AI clouds directly.

---

## Required behavior

```yaml
wifi:
  mode: sta_only
  ssids: from config.json networks[]  # max 3 profiles per WX-025
  softap_provisioning: false  # Phase 2 default; Phase 3 optional

tls:
  hosts_allowed:
    - host: parsed_from config.base_url  # e.g. lexie-server.fly.dev
  paths_allowed:
    - GET /health
    - POST /explain
  min_version: TLS1.2
  ca_bundle: standard  # Let's Encrypt / ISRG Root X1

secrets:
  device_key: from config.json  # never in git source
  openai_key_on_device: forbidden

forbidden_defaults:
  - xiaozhi.me
  - vendor_ota_urls
  - esphome_api_unless_explicitly_added
  - hardcoded_third_party_llm_apis
```

---

## Waveshare-specific rules

1. **Never ship** Waveshare **demo / AI speaker** firmware to the child.  
2. **Full flash erase** before first Lexie firmware flash (**WX-035**).  
3. **Disable** unused subsystems in Lexie build: BLE pairing, cloud voice demos, optional RGB/camera/LCD network features.  
4. **Optional NTP** (`pool.ntp.org` or single pool) — allowed only if required for TLS cert validation; document in firmware README.

---

## Provisioning (WX-025 / WX-033)

Parent runs **USB serial** script once. Written to flash:

```json
{
  "networks": [
    {"ssid": "HomeWiFi", "password": "..."},
    {"ssid": "Parent1Hotspot", "password": "..."},
    {"ssid": "Parent2Hotspot", "password": "..."}
  ],
  "base_url": "https://lexie-server.fly.dev",
  "device_key": "..."
}
```

Firmware tries SSIDs **in order** on boot. No captive portal in Phase 2.

---

## Verification (before child use)

| Check | Pass |
|-------|------|
| Router logs / sniffer after boot | Only Lexie server host (+ optional NTP) |
| `POST /explain` works | 200 + MP3 |
| No traffic to xiaozhi / openai from device IP | Confirmed |

See [lx-4-path-b-bench-testing.md](lx-4-path-b-bench-testing.md).

---

## Defense in depth (optional)

Home router: allow device MAC **only** outbound to Lexie server IP/hostname.

---

## Changelog

| Date | Change |
|------|--------|
| 2026-05-22 | Initial policy — Waveshare Path B pivot (WX-034) |
