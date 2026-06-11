# LX-4 Path A — Canonical Component Kit

**Purpose:** One clear source of truth for the **Path A bench build**.  
**Scope:** Path A only (bring-up on breadboard).  
**Path B note:** Path B usually uses a thinner cell and no headers.

Source BOM: [hardware-shopping-cart.md](hardware-shopping-cart.md)

---

## Fixed kit for this set

| Function | Part | Qty (first build) | Primary order link | Check on receipt |
|---|---|---:|---|---|
| MCU | Seeed XIAO ESP32-S3 (base, not Sense) | 1 | [`B0BYSB66S5`](https://www.amazon.com/dp/B0BYSB66S5) | Must be **plain ESP32-S3**. No camera module. |
| Battery | LiPo 503040, JST-PH 2.0 compatible | 1 | [`B0FBJPP5G6`](https://www.amazon.com/dp/B0FBJPP5G6) | Connector fits XIAO. Verify polarity before first plug. |
| Amp | MAX98357A I2S amp breakout | 1 | [`B0DPJRLMDJ`](https://www.amazon.com/dp/B0DPJRLMDJ) | Board has I2S pins. Header strip included (or add one). |
| Speaker | 8 ohm, ~28 mm, 0.5 W | 1 | [`B0GR4HDKX1`](https://www.amazon.com/dp/B0GR4HDKX1) | Cut/strip pigtail and wire to amp `SPK+/-`. |
| Mic | INMP441 I2S mic breakout | 1 | [`B0FKFR1WFX`](https://www.amazon.com/dp/B0FKFR1WFX) | Silkscreen has I2S labels (`BCLK/LRCLK/DIN/SCK/3V3/GND` or close names). |
| Bench wiring | Breadboard + jumper kit | 1 | [`B08Y59P6D1`](https://www.amazon.com/dp/B08Y59P6D1) | Good for bench only. Not part of final product. |
| Optional jumpers | Dupont set | 0-1 | [`B0BFWR2R3Y`](https://www.amazon.com/dp/B0BFWR2R3Y) / [`B0FZL6LJDV`](https://www.amazon.com/dp/B0FZL6LJDV) | Use if headers are missing or wires are too short. |

Reference docs: [Seeed XIAO ESP32S3](https://wiki.seeedstudio.com/xiao_esp32s3_getting_started/) · [Adafruit MAX98357 guide](https://learn.adafruit.com/adafruit-max98357-i2s-class-d-mono-amp)

---

## Header type for this kit

- For **MAX98357** and **INMP441**, use **2.54 mm male pin headers**.
- This is the default for Path A breadboard bring-up.
- Female sockets are not the default for these two breakouts in this kit.
- For **XIAO**, male headers are optional for bench work.

If header strips are missing from your breakout pack, use the optional dupont kit for temporary wiring and add header strips later.

---

## Breadboard soldering jig (simple, exact wording)

Use the breadboard as a holder only.

1. Put the **long side** of the male header pins into breadboard holes.
2. Place the breakout PCB on top so the short pin ends go through PCB holes.
3. The plastic header body usually sits between breadboard and PCB.
4. Solder on the PCB pad side: tack one corner pin, check board is flat, then solder all pins.
5. Inspect for solder bridges before removing from the breadboard.

---

## Integration rules (do not skip)

- Speaker wires go to **MAX98357 `SPK+/-` only**. Never to XIAO LiPo JST.
- Battery must stay unplugged until polarity is checked with multimeter in **DC volts** mode.
- Red probe in **VΩ**/**VΩmA**, black probe in **COM**.
- Compare battery polarity with Seeed XIAO battery guidance before first plug-in.
- I2S/GPIO mapping is not frozen here. That is tracked in [work-inventory.md](work-inventory.md) under **WX-029**.

---

## Related files

- **Bench layout registry (machine-readable):** [lx-4-path-a-bench-layout.md](lx-4-path-a-bench-layout.md)
- **Bench testing guide:** [lx-4-path-a-bench-testing.md](lx-4-path-a-bench-testing.md)
- BOM and order waves: [hardware-shopping-cart.md](hardware-shopping-cart.md)
- Bench guide (Markdown): [wx-027-beginner-bench-guide.md](wx-027-beginner-bench-guide.md)
- Bench guide (HTML): [wx-027-beginner-bench-guide.html](wx-027-beginner-bench-guide.html)
- Inventory tracker: [work-inventory.md](work-inventory.md)
