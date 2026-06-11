# WX-036 — Codec smoke (ES8311 + ES7210)

**Board:** Waveshare ESP32-S3-AUDIO-Board  
**Prereq:** WX-028 done (USB + Wi‑Fi OK on MicroPython)  
**Why ESP-IDF:** Generic MicroPython has **no** ES8311/ES7210 drivers — codec smoke uses **ESP-IDF** (reference only; not Lexie product firmware yet).

---

## Goal

| Step | Pass |
|------|------|
| **Play** | Hear beep or WAV on speaker (ES8311) |
| **Record** | ES7210 captures non-silent audio when you speak |
| **Levels** | No harsh clipping on normal speech |

---

## One-time setup (Mac)

### Option A — VS Code (Waveshare recommended)

1. Install [VS Code](https://code.visualstudio.com/)
2. Extension: **Espressif IDF** → **Install ESP-IDF** → pick **v5.4.1** or **5.5.x**
3. Target: **esp32s3**

### Option B — Command line

```bash
./tools/wx036-install-idf.sh
```

Then each new terminal:

```bash
source ~/esp/esp-idf/export.sh
```

---

## Phase 1 — Playback smoke (ES8311)

Uses community **screen-less** Waveshare demo (beep + optional WAV on BOOT):

```bash
./tools/wx036-clone-demo.sh
source ~/esp/esp-idf/export.sh
cd firmware/wx036-reference/esp32-s3-audio-board-starter
idf.py set-target esp32s3
idf.py build
idf.py -p /dev/cu.usbmodem101 flash monitor
```

**On board after flash:**

| Button | Expected |
|--------|----------|
| **KEY1** | Beep ~440 Hz |
| **KEY2** | Beep ~660 Hz |
| **KEY3** | Beep ~880 Hz |
| **BOOT** | Plays `sample.wav` from SPIFFS (if bundled) |

**Pass Phase 1:** You hear at least one beep on the speaker.

Exit monitor: **Ctrl+]**

---

## Phase 2 — Record smoke (ES7210)

Phase 1 demo **does not** include mic. For **record**, use Waveshare’s full demo:

1. Download **ESP32-S3-AUDIO-Board Demo** from [Waveshare wiki](https://www.waveshare.com/wiki/ESP32-S3-AUDIO-Board) (Resources → Demo).
2. Open **`Demo/ESP-IDF/esp_sr_02`** (voice / mic test) or **`factory_01`** in VS Code.
3. Build + flash over USB only.
4. **Do not** leave stock demo on home Wi‑Fi — bench USB test, then erase + return to Lexie firmware when done.

**Pass Phase 2:** Serial log shows mic levels / wake word, or you hear echo/record behavior per that demo’s README.

---

## Pin map (Lexie reference)

See [PINMAP-WAVESHARE-AUDIO.md](../lexie-docs/lexie/committed-to-build/lexie-word-explainer.PINMAP-WAVESHARE-AUDIO.md):

- I2C **GPIO10/11**
- I2S **MCLK 12, BCLK 13, LRCLK 14, DOUT 15, DIN 16**
- Speaker amp enable via **TCA9555** expander (Waveshare demos handle this)

---

## After WX-036

1. **Full flash erase** or re-flash Lexie MicroPython: `./tools/flash-micropython.sh`
2. Continue **WX-029** (pin verify) → **WX-033** → **WX-032**

---

## Troubleshooting

| Issue | Fix |
|-------|-----|
| Flash fails | BOOT + RESET → download mode → flash again |
| No serial in monitor | Tap RESET; check port `ls /dev/cu.usb*` |
| No sound | Volume in demo defaults ~60%; speaker connected to header |
| Build errors | `idf.py fullclean` then rebuild; IDF **5.4.1+** |

---

## Evidence log

```text
Date: ___________
Phase 1 beep heard:     [ ] KEY1 / KEY2 / KEY3
Phase 2 mic/record:     [ ]
Notes:
```
