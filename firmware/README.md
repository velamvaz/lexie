# Lexie device firmware (Path B — Waveshare)

**Board:** Waveshare ESP32-S3-AUDIO-Board  
**PRD:** [lx-4-waveshare-device.PRD.md](../lexie-docs/lexie/prds/lx-4-waveshare-device.PRD.md)  
**Pin map:** [PINMAP-WAVESHARE-AUDIO.md](../lexie-docs/lexie/committed-to-build/lexie-word-explainer.PINMAP-WAVESHARE-AUDIO.md)

---

## Tooling (installed on dev Mac)

| Tool | Purpose |
|------|---------|
| `python3 -m esptool` | Flash / erase |
| `python3 -m mpremote` | REPL, run scripts |
| `./tools/erase-waveshare.sh` | WX-035 full erase |
| `./tools/flash-micropython.sh` | WX-028 flash MicroPython |
| `./tools/wx028-check-repl.sh` | WX-028 REPL smoke |
| `./tools/wx028-wifi-smoke.sh` | WX-028 Wi-Fi scan / join |
| `./tools/wx033-provision.sh` | WX-033 write `config.json` (MicroPython path) |
| `./tools/wx033-check-config.sh` | WX-033 read back config (no secrets) |
| `./tools/wx033-provision-idf.sh` | WX-033 stage `config.json` + stress WAV into SPIFFS (ESP-IDF) |
| `./tools/wx032-build.sh` | WX-032 build Lexie ESP-IDF firmware |
| `./tools/wx032-flash.sh` | WX-032 flash |
| `./tools/wx032-capture-stress-wav.sh` | Generate `stress_phrase.wav` for automated E2E |
| `./tools/wx032-stress.py` | Monitor serial; grade `LEXIE_E2E: SUMMARY` |
| `./tools/wx032-reliability.sh` | Provision + build + flash + 10× stress gate |

**Firmware binary:** `firmware/bin/ESP32_GENERIC_S3-SPIRAM_OCT-20250415-v1.25.0.bin` (MicroPython **v1.25.0**, octal PSRAM — matches this board).

---

## WX-035 — Erase vendor firmware ✓

Completed 2026-05-22 — `erase_flash` OK. Do not re-run unless reflashing vendor image.

---

## WX-028 — MicroPython + REPL + Wi-Fi

### 1. Flash (already done on bench)

```bash
./tools/flash-micropython.sh /dev/cu.usbmodem101
```

### 2. Exit download mode → run MicroPython

After **any** `esptool` or flash step, the board may sit in **“waiting for download”**. To run firmware:

1. **Release BOOT** (do not touch it).
2. **Tap RESET once** — or unplug/replug USB **without** holding BOOT.
3. Wait **2 seconds**.

### 3. REPL smoke

```bash
./tools/wx028-check-repl.sh /dev/cu.usbmodem101
```

**Pass:** prints `lexie_repl_ok micropython ...`

### 4. Wi-Fi smoke

Scan only (no secrets):

```bash
./tools/wx028-wifi-smoke.sh
```

Join your AP (replace SSID/password — **not** committed to git):

```bash
./tools/wx028-wifi-smoke.sh 'YourSSID' 'YourPassword'
```

**Pass:** `wifi_ok ('192.168.x.x', ...)`

---

## WX-033 — USB provisioning (`config.json`)

**Prereq:** MicroPython flashed (**WX-028**). Values from **1Password** — never commit real config.

### 1. Create local config (gitignored)

```bash
cp firmware/config.example.json config.local.json
# Edit: SSIDs, passwords, device_key from 1Password
```

### 2. Write to device

```bash
./tools/wx033-provision.sh config.local.json
```

**Pass:** prints `config_ok` with network count and `base_url`.

### 3. Verify read-back

```bash
./tools/wx033-check-config.sh
```

**Pass:** `config_ok N network(s) https://lexie-server.fly.dev` and `device_key_set True`

Re-run provisioning whenever Wi‑Fi or keys change.

---

## WX-032 — Lexie E2E firmware (ESP-IDF)

**Project:** `firmware/lexie-waveshare-idf`  
**Contract:** [DEVICE-INTEGRATION.md](../lexie-docs/lexie/committed-to-build/lexie-word-explainer.DEVICE-INTEGRATION.md)

### Automated reliability gate (10× E2E)

Default build runs **stress test mode** at boot (`CONFIG_LEXIE_STRESS_TEST=y`): replays `stress_phrase.wav` from SPIFFS 10 times — no PTT.

```bash
# One-time: create stress WAV if missing
./tools/wx032-capture-stress-wav.sh lumos

# Close any serial monitor first, then:
./tools/wx032-reliability.sh /dev/cu.usbmodem101
```

**Pass:** script exits 0 and serial shows `LEXIE_E2E: SUMMARY pass=10 fail=0`.  
**Logs:** `project-management/logs/wx032-stress-*.txt`

On failure, re-run with `--loop` for last `FAIL stage=…` line.

### Product PTT mode

Disable stress test in menuconfig (`Lexie Configuration` → uncheck **Run automated E2E stress test at boot**), rebuild, flash:

```bash
cd firmware/lexie-waveshare-idf && idf.py menuconfig
./tools/wx032-build.sh && ./tools/wx032-flash.sh /dev/cu.usbmodem101
```

### Build + flash (manual)

```bash
# Uses config.local.json (staged into SPIFFS at build time)
./tools/wx032-build.sh
./tools/wx032-flash.sh /dev/cu.usbmodem101
```

**ESP-IDF activate** (if not using scripts): Python 3.11 — see `wx032-build.sh`.

### On device

1. Boot → load `config.json` from SPIFFS → join Wi‑Fi (profiles in order)
2. `GET /health` → must return 200
3. Serial log: `Ready — hold BOOT, speak a word, release`
4. **Hold BOOT** → speak a word (~0.5–10 s) → **release**
5. Device `POST /explain` → plays MP3 on speaker

**Error:** low beep (220 Hz).

### Re-provision Wi‑Fi / key

```bash
./tools/wx033-provision-idf.sh config.local.json
./tools/wx032-build.sh && ./tools/wx032-flash.sh
```

MicroPython `wx033-provision.sh` is for the MicroPython smoke path only.

---

## Milestone order

**WX-035** ✓ → **WX-028** ✓ → **WX-036** ✓ → **WX-029** ✓ → **WX-033** ✓ → **WX-032** ✓

**WX-036 guide:** [wx-036-codec-smoke-guide.md](../project-management/wx-036-codec-smoke-guide.md)

---

## Notes

- **Codec (ES8311/ES7210):** not in generic MicroPython — **WX-036** will use ESP-IDF or custom module.
- **Port name** changes on replug (`usbmodem101`, `1101`, …) — always `ls /dev/cu.usb*`.
