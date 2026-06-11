# Lexie — Device Integration Contract

**Version:** 1.0 (Phase 2, 2026-05-03)  
**Audience:** LX-4 firmware implementers  
**Server SPEC:** [lexie-word-explainer.SPEC.md](lexie-word-explainer.SPEC.md)  
**Server source:** [`lexie-server/`](../../../lexie-server/)

This document is the **normative API contract** for the physical Lexie device. Read this instead of the full SPEC. The SPEC remains authoritative for edge cases.

**Phase 2 hardware shape (v1):** The product is **Lexie Card** — WiFi-only, **credit-card footprint** (ISO ID-1), target **≤ ~8 mm** thick, **beside the open book** on a table or lap board (**no clip**, **no magnets** in v1). Zones (PTT, LED, mic, speaker, USB-C) and placement notes: **[`hardware/lexie-plaud-form-factor.html`](../../../hardware/lexie-plaud-form-factor.html)**. The HTTP contract below is unchanged whether the child uses the browser prototype or Lexie Card.

---

## 1. BASE_URL

```
https://lexie-server.fly.dev
```

- No trailing slash.
- Retrieved from **1Password** → Secure Note: `Lexie — production URL` (D5).
- **Never hardcode** in source. Flash at provisioning time alongside `LEXIE_DEVICE_KEY`.
- The device must store this value in non-volatile memory (flash / EEPROM) and read it at boot.

---

## 2. Liveness — `GET /health`

**Call on:** boot, Wi-Fi reconnect, or before the first explain of a session.

```
GET {BASE_URL}/health
```

**Success (200):**

```json
{"ok": true}
```

**Failure:** any non-200 status, connection refused, or timeout. On failure: show error LED / audio cue; retry with back-off. See [§8 Error codes](#8-error-codes).

---

## 3. Explain — `POST /explain`

The core endpoint. Send audio; receive MP3 audio explanation.

### Request

```
POST {BASE_URL}/explain
Content-Type: multipart/form-data
Authorization: Bearer {LEXIE_DEVICE_KEY}
```

| Field | Type | Description |
|-------|------|-------------|
| `audio` | binary file | Raw audio recording. WebM, WAV, MP4, OGG, MP3 accepted. Minimum 0.4 s; maximum 30 s; maximum body size 2 MiB. |

**Alternative auth header:** `X-Device-Key: {LEXIE_DEVICE_KEY}` (equivalent to Bearer).

### Response — success (200)

```
HTTP/1.1 200 OK
Content-Type: audio/mpeg
X-Explain-Latency-Ms: <integer>
```

Body is raw **MP3 bytes**. Play immediately. Latency header is informational (warm: ~6–7 s; target p95 &lt;5 s, aspirational).

### Response — failure (4xx / 5xx)

```json
{"error": "<code>"}
```

or (FastAPI validation errors):

```json
{"detail": {"error": "<code>"}}
```

See [§8 Error codes](#8-error-codes) for the full list and device actions.

---

## 4. Limits

| Limit | Value | Server error |
|-------|-------|-------------|
| Maximum body | 2 MiB | `413 Payload Too Large` → `payload_too_large` |
| Maximum audio duration | 30 s | `400` → `audio_too_long` |
| Minimum audio duration | 0.4 s | `400` → `audio_too_short` |
| Transcription empty | — | `400` → `transcription_empty` |

---

## 5. TLS

- **TLS 1.2 or higher** required. Fly.io issues the certificate automatically.
- Do **not** use self-signed certificates in production.
- The device TLS stack must trust the standard CA bundle (Let's Encrypt / ISRG Root X1).
- For development on a local server (`http://`): acceptable only on trusted network; never ship.

---

## 6. Auth key (`LEXIE_DEVICE_KEY`)

- Source: **1Password** → item `LEXIE_DEVICE_KEY` (same vault as `BASE_URL`).
- **Never hardcode** in firmware source or build artifacts.
- Flash at provisioning time (alongside `BASE_URL`).
- Send as `Authorization: Bearer <key>` (or `X-Device-Key: <key>`).
- If the key is wrong or missing: server returns **401** → `unauthorized`. Show error LED and prompt re-provisioning.
- Key rotation: update 1Password item; re-flash device.

---

## 7. What is NOT for the device

These endpoints are for **parent / operator** use only. The device must never call them.

| Endpoint | Purpose |
|----------|---------|
| `GET /profile`, `PATCH /profile` | Age profile read / write |
| `GET /admin` | Admin HTML UI |
| `GET /admin/telemetry/*` | Usage analytics |
| `GET /prototype/` | Browser push-to-talk prototype |

The device key (`LEXIE_DEVICE_KEY`) will be rejected on admin endpoints (they require `LEXIE_ADMIN_TOKEN`).

---

## 8. Error codes

Machine codes returned in the JSON body (SPEC §5.1). Use these for **LED** and **audio error cue** mapping on the device.

| Code | HTTP | Meaning | Suggested device action |
|------|------|---------|------------------------|
| `unauthorized` | 401 | Wrong or missing device key | Error LED; prompt re-provisioning |
| `audio_too_short` | 400 | Recording &lt; 0.4 s | Short chime; retry prompt |
| `audio_too_long` | 400 | Recording &gt; 30 s | Long chime; retry prompt |
| `transcription_empty` | 400 | No speech detected | Short chime; retry prompt |
| `unintelligible_audio` | 400 | Speech unclear | Chime; retry prompt |
| `payload_too_large` | 413 | Body &gt; 2 MiB | Error LED; check codec/compression |
| `openai_unavailable` | 502 | OpenAI down or unreachable | Wait + exponential back-off; max 3 retries |
| `rate_limited` | 429 | Too many requests | Back-off per `Retry-After` header if present |
| `internal` | 500 | Unhandled server error | Error LED; log; retry once |
| `explanation_invalid` | 500 | Pipeline returned bad JSON | Error LED; retry once |

For any error not in this list: treat as `internal`.

---

## 9. OpenAI note

The **server** calls OpenAI (Whisper for transcription, GPT for explanation, TTS for audio). The **device never calls OpenAI directly**. The device key (`LEXIE_DEVICE_KEY`) is completely separate from the OpenAI API key — the device does not need and must not have the OpenAI key.

---

## 10. Typical device session flow

```
Power on
  └─ Connect to saved Wi-Fi (home AP or hotspot)
       └─ GET /health → 200 ─── OK LED (green)
            └─ User presses button
                 └─ Record audio (0.4 s – 30 s)
                      └─ POST /explain
                           ├─ 200 → play MP3 → idle
                           └─ 4xx/5xx → error cue → idle
```

---

*This document is generated from the Phase 2 pivot plan (2026-05-03). Update when the server contract changes.*
