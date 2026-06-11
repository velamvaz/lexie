# Lexie WX-027 — Beginner solder + multimeter guide

**Work item:** WX-027 (Solder prep + safe power documentation)  
**Meter:** MS8332C (Commercial Electric) — instructions assume **no prior multimeter experience**.

**Styled web page (diagrams + dark theme):** open [`wx-027-beginner-bench-guide.html`](wx-027-beginner-bench-guide.html) in a browser. A copy of the same HTML also lives in [`wx-027-standalone-page.md`](wx-027-standalone-page.md) (fenced block) for version control / diff convenience.

---

## Goal

1. Solder headers on **MAX98357** and **INMP441** (and optionally **XIAO**).
2. Solder speaker terminals on **MAX98357** and attach speaker wires.
3. **Verify LiPo polarity with the multimeter** and write it down **before** the first JST plug into XIAO.

**Critical:** Do not plug the battery into the XIAO until Step 10 is complete and matches Seeed’s LiPo polarity guidance.

**Seeed reference:** [XIAO ESP32S3 Getting Started](https://wiki.seeedstudio.com/xiao_esp32s3_getting_started/) (battery / polarity section).
**Parts + header type source:** [lx-4-path-a-component-kit.md](lx-4-path-a-component-kit.md).

---

## Why solder if you have a breadboard?

- Breadboards need **rigid male pins** for a reliable connection.
- Breakouts usually ship with **loose header strips** — you solder them into the PCB holes.
- The MAX98357 board typically needs a **speaker terminal block** soldered on.

Soldering here is **assembly**, not “building a custom PCB.”

---

## Tools and parts checklist

- [ ] Soldering iron + stand + sponge or brass wool  
- [ ] Rosin-core solder  
- [ ] MAX98357 + header pins + speaker terminal block  
- [ ] INMP441 + header pins  
- [ ] Optional: XIAO male headers  
- [ ] MS8332C + red/black probes  
- [ ] LiPo (keep away from iron until polarity is verified)  

---

## Figure 1 — Soldering flow (breadboard as jig)

```
  Breadboard                Module PCB              Finish joints
  (holds pins straight)     sits on pins            all pins
       |                         |                      |
       v                         v                      v
  [========]               [ MAX98357 ]            solder each
  | | | | |               or INMP441    pin: tack -> align -> all
```

**Method:** Put the **male header pins** in the breadboard, place the PCB on top, **tack one pin**, check the board is not tilted, then solder the rest.

---

## Figure 2 — Bench layout (top view, Path A kit)

Full diagram with SVG: open [`wx-027-beginner-bench-guide.html`](wx-027-beginner-bench-guide.html) and scroll to **Figure 2**.

- **Large board (830 tie-point):** main area for **XIAO**, **MAX98357**, **INMP441**, and (conceptually) speaker wiring toward the amp only.
- **Small board (400 tie-point):** extra tie points, power routing, or a **second soldering jig** while you solder headers.
- Exact hole positions are **not** fixed until **WX-029** (pin map). This figure only shows **which physical board is which** and a sane default layout.

Kit reference: [hardware-shopping-cart.md](hardware-shopping-cart.md) (Seq 6).  
**Machine-readable layout (row/column + challenges):** [lx-4-path-a-bench-layout.md](lx-4-path-a-bench-layout.md).  
**Testing phases (pass/fail):** [lx-4-path-a-bench-testing.md](lx-4-path-a-bench-testing.md).

---

## Figure 3 — MS8332C jacks (typical layout)

Most meters in this class have **three** bottom jacks:

| Jack label (typical) | Probe color | When to use for WX-027 |
|----------------------|-------------|-------------------------|
| **COM** | **Black** | Always — common reference |
| **VΩmA** (or VΩ) | **Red** | **DC voltage** polarity test (use this) |
| **10A** | — | **Do not use** for battery polarity |

**For LiPo polarity:** black → **COM**, red → **VΩmA**, dial → **DC volts**.

---

## WX-027 steps (detailed)

### Step 1 — Bench safety

1. Clear workspace; non-flammable surface.  
2. Turn on iron; let it reach temperature.  
3. Keep **LiPo away** from the soldering area.  
4. Have the multimeter nearby for later.

### Step 2 — MAX98357: solder pin header

1. Break a male header strip to match the number of holes on the amp board.  
2. Press the header **into the breadboard** so pins are vertical.  
3. Place the MAX98357 PCB on the pins so holes seat fully.  
4. **Tack one corner pin** with solder.  
5. Re-check the board is parallel to the breadboard (not twisted).  
6. Solder **every** remaining pin.  
7. Visually inspect: **no solder bridges** between adjacent pins.

### Step 3 — MAX98357: solder speaker terminal block

1. Insert terminal block into the footprint (usually two larger holes).  
2. Tack one pin; ensure the block sits **flush** to the PCB.  
3. Solder remaining pin(s).  
4. Gentle tug: block should not move.

### Step 4 — INMP441: solder pin header

Same method as Step 2 (breadboard jig → tack one pin → align → solder all).

### Step 5 — (Optional) XIAO: solder headers

If you want easy breadboard use, solder a **male header row** on the XIAO. Keep pins straight.

### Step 6 — Speaker to amp (not to XIAO JST)

1. **Strip** the ends of the speaker pigtail (remove the small white connector from the signal path — you wire to the **amp**).  
2. **Tin** the bare wire (small amount of solder on strands).  
3. Insert into **SPK+** / **SPK-** (or silkscreen equivalent) on the MAX98357 terminal block.  
4. Tighten screws; light pull test.

**Never** connect speaker wires to the **XIAO LiPo JST**.

---

## Multimeter: from zero to polarity reading

### Step 7 — Insert probes (MS8332C)

1. **Black** probe → jack labeled **COM**.  
2. **Red** probe → jack labeled **VΩmA** or **VΩ** (the one used for voltage/resistance — **not** 10A).  
3. Confirm they click in fully.

### Step 8 — Select DC voltage

1. Rotate the dial to **DC voltage** (symbol is usually **V** with a solid line and dashed line, or “DCV”).  
2. Pick a range **above** 5 V if your meter is manual-range (e.g. **20 V DC**). If auto-ranging, **DC V** is enough.

**Common mistake:** meter in **current (A)** mode — that can **short** the battery if you probe both leads like voltage. **Always use DC volts** for this test.

### Step 9 — Measure the battery leads

**Battery still not plugged into XIAO.** You are only touching the **two** battery wires (or connector pins if exposed).

1. Touch **black** probe to one conductor (bare metal or pin).  
2. Touch **red** probe to the other conductor.  
3. Read the display:

| Reading | Meaning |
|--------|---------|
| **Positive** number (e.g. 3.7–4.2) | **Red** probe is on **+**, **black** on **−** (for that orientation). |
| **Negative** number (e.g. −3.9) | Same physics, opposite probe assignment — **red** is on **−**, **black** on **+**. |
| **0.00** or unstable | Bad contact, wrong mode, or dead cell — fix before continuing. |

Write down: **Wire color A = + / −**, **Wire color B = + / −**.

### Step 10 — Match XIAO JST and only then plug

1. Open Seeed’s XIAO ESP32S3 page and find **battery connector polarity** (which side is + on the **board**).  
2. Compare to your written table from Step 9.  
3. **Only if they agree**, plug JST once. If unsure, **stop** and resolve (wrong polarity can damage the charger).

---

## WX-027 evidence (for your log)

Record yes/no (or photo):

- [ ] MAX98357 headers soldered  
- [ ] MAX98357 speaker block soldered  
- [ ] INMP441 headers soldered  
- [ ] Speaker wired to amp ± only  
- [ ] LiPo polarity documented before first plug  

---

## Stop — do not power LiPo if

- Red probe was in **10A** jack.  
- Dial was in **amps** or **resistance** by mistake.  
- Polarity table does not match XIAO JST expectation.  
- Any **solder bridge** remains on headers.  

---

*Next work item after WX-027: **WX-028** — flash MicroPython, USB REPL, Wi-Fi smoke.*
