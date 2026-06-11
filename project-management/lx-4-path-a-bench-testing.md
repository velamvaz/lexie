---
schema: lexie.bench-testing
schema_version: "1.0"
kit: lx-4-path-a
status: draft
last_updated: "2026-05-06"
scope: path_a_bench_components
components:
  - cmp-mcu-xiao
  - cmp-audio-amp
  - cmp-audio-mic
  - cmp-audio-spk
  - cmp-pwr-lipo
related:
  component_kit: lx-4-path-a-component-kit.md
  bench_layout: lx-4-path-a-bench-layout.md
  bench_guide: wx-027-beginner-bench-guide.html
  work_items: [WX-027, WX-028, WX-029, WX-030, WX-031]
meter: MS8332C
---

# LX-4 Path A — Bench testing guide

What you can test **now**, what needs **wiring + code**, and how to know **pass vs fail**.

**Components:** XIAO ESP32-S3, MAX98357A amp, INMP441 mic, 8 Ω speaker, LiPo.

---

## Summary table

| Phase | Power needed | Proves | Work item |
|-------|--------------|--------|-----------|
| **1** | None | No solder shorts; headers OK | WX-027 |
| **2** | USB only (XIAO) | MCU alive; REPL / Wi‑Fi | WX-028 |
| **3** | USB + 3.3 V jumpers (optional) | Amp/mic get ~3.3 V safely | After WX-029 draft |
| **4** | USB + full I2S jumpers + code | Amp plays; mic captures | WX-030, WX-031 |
| **5** | Multimeter only (LiPo unplugged) | Battery polarity safe | WX-027 |

**Important:** Phases **1–2** can run **before** amp/mic signal wires. Phase **4** is the real proof of **correct pinning** for I2S.

---

## Before any test

- [ ] Iron and LiPo **away** from each other during solder work.
- [ ] MS8332C probes: black → **COM**, red → **VΩmA** (not **10A**).
- [ ] For **DC voltage**: dial on **DC V** (solid + dashed line), not **A** (amps).
- [ ] Speaker wired to **MAX98357 screw terminal only** — never to XIAO LiPo JST.

Reference: [wx-027-beginner-bench-guide.html](wx-027-beginner-bench-guide.html) (multimeter steps).

---

## Phase 1 — No power (multimeter resistance checks)

**Goal:** Catch solder bridges and dead shorts **before** you apply power.

**Meter setup:** Resistance **Ω** mode (or continuity beep if you prefer). Black → **COM**, red → **VΩmA**.

### 1.1 XIAO ESP32-S3 (headers soldered)

| Check | How | Pass | Fail |
|-------|-----|------|------|
| Neighbor header pins | Touch probes on **two adjacent pins** on same header row | **No beep** / very high resistance | Beep = bridge → fix solder |
| GND vs 3V3 rail pins | Probe **GND** pin and **3V3** pin (use silkscreen / pinout) | **Not** 0 Ω | 0 Ω = short → fix before USB |
| Visual | Look at all joints | Shiny cones, no blobs between pins | Bridges or dull/cold joints |

**Does not prove:** Wi‑Fi, flash, or GPIO work.

### 1.2 MAX98357A (7-pin header + screw terminal)

| Check | How | Pass | Fail |
|-------|-----|------|------|
| Neighbor pins on 7-pin header | Adjacent pins (LRC…Vin order on your board) | No beep between neighbors | Bridge → fix |
| **GND** vs **Vin** | Probe those two header pins | **Not** 0 Ω | 0 Ω → fix before power |
| Screw terminal | Tug wires after you attach speaker (later) | Secure | Loose → re-tighten |

**Pin order on your board (edge labels):** Vin, GND, SD, GAIN, DIN, BCLK, LRC — confirm on silkscreen when plugged in.

**Does not prove:** Audio output (needs I2S wires + code).

### 1.3 INMP441 (round board, 6-pin header)

| Check | How | Pass | Fail |
|-------|-----|------|------|
| All 6 pads soldered | Visual + gentle pin tug | Pins firm | Loose → re-solder |
| Neighbor pins on header | Adjacent pins on strip | No beep | Bridge → fix |
| **GND** vs **VDD** | Probe those header pins | **Not** 0 Ω | 0 Ω → fix before power |
| Pin straightness | Pins fit one breadboard row without forcing | Slides in row G (or chosen row) | Forced bend → straighten gently |

**Curve labels on your board:** L/R, WS, SCK, SD, VDD, GND.

**Does not prove:** Microphone data (needs I2S wires + code).

### Phase 1 checklist

- [ ] XIAO: no adjacent-pin bridges; GND not shorted to 3V3
- [ ] MAX98357: no adjacent-pin bridges; GND not shorted to Vin
- [ ] INMP441: 6 pins solid; GND not shorted to VDD
- [ ] Speaker **not** connected to XIAO battery jack

---

## Phase 2 — XIAO only (USB, no LiPo, no amp/mic signal wires)

**Goal:** Prove the **MCU works** over USB.

**Work item:** WX-028.

### 2.1 Setup

1. **Do not** plug LiPo into XIAO yet.
2. **Do not** require amp/mic jumpers for this phase.
3. Use a **data-capable** USB-C cable to laptop.
4. Flash **MicroPython** for **XIAO ESP32-S3** (Seeed / ESP32-S3 port per current docs).

Links: [Seeed XIAO ESP32S3 getting started](https://wiki.seeedstudio.com/xiao_esp32s3_getting_started/)

### 2.2 REPL smoke

Open serial REPL (`mpremote`, Thonny, or terminal). Run:

```python
print("ok")
```

| Result | Meaning |
|--------|---------|
| Prints `ok` | REPL alive — **pass** |
| No port / no response | Cable, driver, or flash issue — **fail** |

### 2.3 Wi‑Fi smoke (optional)

```python
import network
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
print(wlan.scan())
```

| Result | Meaning |
|--------|---------|
| Returns a list (even empty) | Wi‑Fi stack runs — **pass** |
| Exception / hang | Firmware or board issue — **fail** |

### Phase 2 checklist

- [ ] USB REPL responds
- [ ] `print("ok")` works
- [ ] Wi‑Fi scan runs (optional)

**Does not prove:** MAX98357 or INMP441 pins or audio path.

---

## Phase 3 — Power-only to amp and mic (optional)

**Goal:** Confirm **~3.3 V** reaches amp and mic **without** connecting I2S data yet.

**Prerequisite:** Draft wire plan from **WX-029** (at minimum: which holes are **3V3** and **GND** on XIAO).

**Warning:** Only do this after Phase 1 passes. Wrong wire = possible damage.

### 3.1 Minimum connections

| From XIAO | To MAX98357 | To INMP441 |
|-----------|-------------|------------|
| **3V3** | **Vin** | **VDD** |
| **GND** | **GND** | **GND** |

Use breadboard jumpers. **Do not** connect BCLK / LRCLK / DIN / SD (mic) yet unless you are running Phase 4.

### 3.2 Measure with multimeter (DC V)

Dial: **DC V**, range **20 V**. Black → **COM**, red → **VΩmA**.

| Measurement | Expected | Fail |
|-------------|----------|------|
| Vin vs GND on amp | ~**3.2–3.3 V** | 0 V, 5 V, or board hot |
| VDD vs GND on mic | ~**3.2–3.3 V** | 0 V or board hot |

### Phase 3 checklist

- [ ] ~3.3 V at amp Vin
- [ ] ~3.3 V at mic VDD
- [ ] No smoke, no excessive heat

**Does not prove:** Sound or microphone capture.

---

## Phase 4 — Full I2S tests (proves pinning + audio)

**Goal:** Real proof that amp, mic, and **wire table** are correct.

**Work items:** WX-029 (pin map) → WX-030 (out) → WX-031 (in).

### 4.1 What you must wire (conceptual)

Both peripherals share an **I2S bus** from XIAO:

| Signal | MAX98357 (typical) | INMP441 (typical) |
|--------|--------------------|-------------------|
| Bit clock | BCLK | SCK (same as BCLK) |
| Word select | LRC / LRCLK | WS |
| Data | DIN (in to amp) | SD (out from mic) |
| Power | Vin, GND | VDD, GND |
| Extra | SD (enable — often tie high), GAIN optional | L/R (often GND for left) |

**Exact XIAO GPIO numbers:** commit in WX-029 doc — not duplicated here until frozen.

### 4.2 Amp + speaker test (WX-030)

1. Wire I2S out + power per pin map.
2. Enable amp (**SD** high if your board requires it).
3. Run test tone or WAV playback from MicroPython.

| Result | Meaning |
|--------|---------|
| Clear sound from speaker | Amp path **pass** |
| Silence | Wrong BCLK/LRC/DIN, SD not enabled, or bad solder |
| Loud buzz/hum only | Possible GND issue or floating clock line |

### 4.3 Mic capture test (WX-031)

1. Wire I2S in + power per pin map.
2. Set **L/R** per board docs (often tie **L/R** to **GND**).
3. Record silence, then speak.

| Result | Meaning |
|--------|---------|
| Level changes when you talk | Mic path **pass** |
| Flat zero or constant max | Wrong WS/SCK/SD or **L/R** |
| Heavy noise, no speech | Clock or GND wiring suspect |

### Phase 4 checklist

- [ ] Pin map document exists (WX-029)
- [ ] Test tone heard on speaker (WX-030)
- [ ] Voice level changes on capture (WX-031)

**This is the only phase that fully proves “correctly pinned” for audio.**

---

## Phase 5 — LiPo polarity (before first battery plug on XIAO)

**Goal:** Avoid reverse polarity on XIAO JST.

**Work item:** WX-027 (multimeter section in bench guide).

### 5.1 Setup

- LiPo **unplugged** from XIAO.
- Meter: **DC V**, black → **COM**, red → **VΩmA**.

### 5.2 Measure

1. Black probe on one battery conductor; red on the other.
2. Read voltage:

| Reading | Meaning |
|---------|---------|
| **+3.7 to +4.2** | Red on **+**, black on **−** |
| **−3.7 to −4.2** | Red on **−**, black on **+** |
| **0.00** unstable | Bad contact, wrong mode, or dead cell |

3. Write: wire color = + / −.
4. Compare with [Seeed XIAO LiPo guidance](https://wiki.seeedstudio.com/xiao_esp32s3_getting_started/).
5. Plug JST **once** only if they **match**.

### Phase 5 checklist

- [ ] Polarity table written
- [ ] Matches Seeed board expectation
- [ ] First plug only after match

**Does not prove:** Amp or mic; only safe battery orientation.

---

## Recommended order from your current state

Assuming: **XIAO headers done**, **MAX98357 header + terminal done**, **INMP441 header in progress or done**.

| Order | Phase | Action |
|-------|-------|--------|
| 1 | **1** | Multimeter checks on all three boards |
| 2 | **WX-027 mechanical** | Finish mic header; speaker → amp **+/−** |
| 3 | **2** | USB REPL + optional Wi‑Fi on XIAO |
| 4 | **5** | LiPo polarity → first plug if OK |
| 5 | **WX-029** | Freeze jumper / GPIO table |
| 6 | **4** | Tone test (WX-030) then mic test (WX-031) |
| 7 | **3** | Optional 3.3 V-only check if you skipped before full wire |

---

## What each phase does *not* prove

| Phase | Does not prove |
|-------|----------------|
| 1 | Digital logic, I2S, or audio |
| 2 | Amp, mic, or header orientation on breadboard |
| 3 | I2S data pins or sound |
| 4 | LiPo safety (do Phase 5 separately) |
| 5 | Amp/mic function |

---

## Evidence log (copy for work-log)

```text
Date: ___________

Phase 1 — No power
[ ] XIAO adjacent pins OK   [ ] XIAO GND/3V3 OK
[ ] Amp adjacent pins OK    [ ] Amp GND/Vin OK
[ ] Mic 6-pin OK            [ ] Mic GND/VDD OK

Phase 2 — XIAO USB
[ ] REPL print("ok")        [ ] Wi-Fi scan (optional)

Phase 5 — LiPo (before first plug)
[ ] Polarity documented     [ ] Matches Seeed JST

Phase 4 — I2S (after WX-029)
[ ] Speaker tone (WX-030)   [ ] Mic capture (WX-031)
```

---

## Related files

| File | Role |
|------|------|
| [lx-4-path-a-component-kit.md](lx-4-path-a-component-kit.md) | Parts + integration rules |
| [lx-4-path-a-bench-layout.md](lx-4-path-a-bench-layout.md) | Row/column placement |
| [wx-027-beginner-bench-guide.html](wx-027-beginner-bench-guide.html) | Solder + multimeter steps |
| [work-inventory.md](work-inventory.md) | WX-027–031 tracking |

---

## Changelog

| date | change |
|------|--------|
| 2026-05-06 | Initial guide: phases 1–5, pass/fail tables, round INMP441 notes |
