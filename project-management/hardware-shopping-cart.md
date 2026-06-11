# Lexie hardware — structured order list

**Phase 2 (LX-4) — Lexie Card v1 electronics**  
**Active bench (2026-05-22):** **Path B — Waveshare** — [lx-4-path-b-waveshare-kit.md](lx-4-path-b-waveshare-kit.md) · **WX-034**  
**Path A (archive / spare parts):** sections below — [lx-4-path-a-component-kit.md](lx-4-path-a-component-kit.md)  
**Decisions:** [work-inventory.md](work-inventory.md) **WX-024** *(amended)* · **WX-034** · **WX-025** (USB provisioning)  
**Mechanical target:** [hardware/lexie-plaud-form-factor.html](../hardware/lexie-plaud-form-factor.html) **§1b** (XY plan in mm + Z-height budget)  
**Last updated:** 2026-05-22

---

## Path B — on bench (Waveshare)

| # | Item | Status |
|---|------|--------|
| 1 | **ESP32-S3-AUDIO-Board** | **Delivered 2026-05-22** |
| 2 | **USB-C data cable** | Verify data-capable |
| 3 | **LiPo / speaker** | Per variant — see [lx-4-path-b-waveshare-kit.md](lx-4-path-b-waveshare-kit.md) |

**Active:** [WX-035](work-inventory.md#wx-035--path-b-unbox--erase-vendor-firmware) — **full flash erase** before home Wi‑Fi. Do **not** run stock Xiaozhi/demo firmware.

**Do not need for Path B primary path:** breadboard, INMP441, MAX98357 (already owned = spare).

Full checklist: [lx-4-path-b-waveshare-kit.md](lx-4-path-b-waveshare-kit.md).

---

## Path A — archive (parts on hand)

---

## Status key

| Symbol | Meaning |
|--------|---------|
| ✅ | Specific SKU / listing chosen — use as written |
| 🔍 | Pick a listing (search terms + constraints below) |
| ⏸️ | Optional / defer until bench path works |

---

## Two build paths (pick one budget mindset)

| Path | Goal | LiPo | Typical thickness |
|------|------|------|---------------------|
| **A — Bring-up (recommended first)** | Firmware, `/health`, `/explain`, audio path on bench | **503040** (~5 mm) | **~9–11 mm** with breakouts + headers — OK for breadboard / “fat” prototype shell |
| **B — v1 Lexie Card shell** | Match PRD **≤ ~8 mm** | Cell **≤ ~3.5 mm** + no headers + custom or flush PCB | Order **after** Path A works |

Path **A** is the default ordering below. Path **B** reuses the same electronics except you swap the cell (and usually integration style).

---

## Amazon US suggested ASINs (seq 4-6)

These are **examples** from a quick catalog search — **re-check title, photos, stock, and recent reviews** before checkout. Amazon listings change often.

### Seq **4** — Speaker (**8 Ω**, small, for MAX98357)

| Priority | ASIN | Product sketch | Notes |
|----------|------|----------------|--------|
| A | [**`B0GR4HDKX1`**](https://www.amazon.com/dp/B0GR4HDKX1) | **MECCANIXITY** 2× **28 mm** Ø × **~5 mm** H, **8 Ω 0.5 W**, **100 mm** leads, **1.25 mm** plug | **Ordered (you).** Twister **Size = 28 mm**. Strip/tin to **MAX98357 ±**; **never** into XIAO **LiPo** jack. |
| A2 | [**`B0826551ZZ`**](https://www.amazon.com/dp/B0826551ZZ) | **uxcell** 2× **28 mm** round, **8 Ω 1 W**, pigtail (**PH 2.0** or **1.25 mm 2P** — see listing) | Alt.; **1 W** — don’t run amp at max. |
| B | [**`B0DG5N9JFF`**](https://www.amazon.com/dp/B0DG5N9JFF) | 4× **28 mm** metal, **8 Ω 0.5 W** | Good match when in stock. |
| C | [**`B0GHNCSVF4`**](https://www.amazon.com/dp/B0GHNCSVF4) | **20 × 30 × ~5 mm** oval, **8 Ω 1 W** | Matches **~30×20** grille zone when in stock. |
| D | [**`B0F5Q31GYY`**](https://www.amazon.com/dp/B0F5Q31GYY) | **20×** small **8 Ω 1 W** with 2-pin | Budget multipack. |
| E | [**`B0D3HDMRBH`**](https://www.amazon.com/dp/B0D3HDMRBH) | Multi-size picker | Pick **28–30 mm**, **8 Ω**, **0.5–1 W** in dropdown. |
| F | [**`B0D7S8FFKY`**](https://www.amazon.com/dp/B0D7S8FFKY) | **DWEII** 4× **8 Ω 1 W** “cavity” mini + **JST-PH 1.25 mm** 2P | **OK for bench** if round **28 mm** parts are OOS. **Not** the same outline as **uxcell `B0826551ZZ`** — check **length × width × height** in the listing; cavity drivers are often **smaller cube** than 28 mm round. Still **cut pigtail → bare wire** to **MAX98357 ±**; **never** plug into XIAO **LiPo** jack. |

### Seq **5** — **INMP441** I²S breakout

| Priority | ASIN | Notes |
|----------|------|--------|
| A | [**`B0FKFR1WFX`**](https://www.amazon.com/dp/B0FKFR1WFX) | **Qoroos** **3×** INMP441, I²S, “supports ESP32” — **ordered (you)**; **use 1**, keep 2 spares. On receipt, confirm silkscreen **BCLK / LRCLK / DIN / SCK / 3V3 / GND** (names vary slightly) and wire to XIAO **I²S** pins per your frozen pin map + [Seeed XIAO ESP32S3 docs](https://wiki.seeedstudio.com/xiao_esp32s3_getting_started/). |
| B | [**`B0GDRZ3KPX`**](https://www.amazon.com/dp/B0GDRZ3KPX) | ANKROYU-style generic INMP441 board |
| C | [**`B0GDYSY75R`**](https://www.amazon.com/dp/B0GDYSY75R) | AUNMAS INMP441 |
| D | [**`B0GHQHCY62`**](https://www.amazon.com/dp/B0GHQHCY62) | Funien INMP441 |

**Skip for now:** [MakerHawk `B0CZ6G6CWX`](https://www.amazon.com/dp/B0CZ6G6CWX) showed **Currently unavailable** when spot-checked — use only if it comes back in stock.

### Seq **6** — Breadboard + jumpers

| Priority | ASIN | Product sketch | Notes |
|----------|------|----------------|--------|
| A | [**`B0C1VDKPW2`**](https://www.amazon.com/dp/B0C1VDKPW2) | **830 + 400** tie breadboard + **U-shape** solid jumpers + ribbon | One cart line for “start wiring.” |
| A2 | [**`B08Y59P6D1`**](https://www.amazon.com/dp/B08Y59P6D1) | **BOJACK:** **830** + **400** tie boards (**multiple boards**) + **126** flexible breadboard jumpers | **Good kit (you).** Shop-only; never ships inside Lexie. **Gap:** XIAO often needs **soldered pin headers** **or** a **dupont F–M / M–M ribbon** pack to reach the breadboard — add [`B0BFWR2R3Y`](https://www.amazon.com/dp/B0BFWR2R3Y) or [`B0FZL6LJDV`](https://www.amazon.com/dp/B0FZL6LJDV) if you have no headers yet. |
| B | [**`B0BFWR2R3Y`**](https://www.amazon.com/dp/B0BFWR2R3Y) | **560 pc** M/M, M/F, F/F dupont | Good if you already have a breadboard. |
| C | [**`B0FZL6LJDV`**](https://www.amazon.com/dp/B0FZL6LJDV) | **240** F–M ribbon jumpers | Handy with **female** pins on breakouts / XIAO socket setups. |

---

## Order waves (do in this sequence)

### Wave 0 — Already have (no cart line)

| Step | Item | Notes |
|------|------|--------|
| 0.1 | **Data-capable USB-C cable** | Must carry **data** (not charge-only) for flash + **WX-025** provisioning |
| 0.2 | **1Password** | `BASE_URL`, `LEXIE_DEVICE_KEY` ready when you run provisioning (see D5 in inventory) |
| 0.3 | **Laptop** with USB port | For `mpremote` / serial + Python provision script |

---

### Wave 1 — MCU (validate first)

| Seq | Part | Qty | Est. | Link / how to order | Status |
|-----|------|-----|------|---------------------|--------|
| **1** | **Seeed XIAO ESP32-S3** (base, **not** Sense) | 1–2 | ~$17 | [Amazon — `B0BYSB66S5`](https://www.amazon.com/Seeed-Studio-ESP32S3-Supports-Arduino/dp/B0BYSB66S5) (same ASIN as `/dp/B0BYSB66S5`) · [Seeed store — ground truth SKU](https://www.seeedstudio.com/XIAO-ESP32S3-p-5627.html) | ✅ |

**Stop gate:** Power from USB, flash MicroPython, `print("ok")` / WiFi scan sketch. Second board optional if you want a spare.

---

### Wave 2 — Power path (after MCU works)

| Seq | Part | Qty | Est. | Link / how to order | Status |
|-----|------|-----|------|---------------------|--------|
| **2** | **Single-cell LiPo** — Path A: **503040** (~3.7 V, **~400–650 mAh**, **~5 mm** thick, **30 × 40 mm**) | 1 | ~$6–10 | **Example (you):** [Nzzz 620 mAh 503040, JST PH 2.0 mm — `B0FBJPP5G6`](https://www.amazon.com/dp/B0FBJPP5G6) · or search: `503040 lipo JST-PH 2.0` — **must match XIAO JST PH 2.0 mm** | ✅ |
| **2b** | ⏸️ Thinner cell (Path B only) | 0–1 | varies | 🔍 e.g. `402535` / `303450` class — **measure thickness**; mAh tradeoff | ⏸️ |

**Stop gate:** With a **multimeter**, confirm **+ / −** against [Seeed XIAO LiPo polarity](https://wiki.seeedstudio.com/xiao_esp32s3_getting_started/) before first plug. Wrong polarity can damage the charger.

---

### Wave 3 — Audio out (speaker + I²S amp)

| Seq | Part | Qty | Est. | Link / how to order | Status |
|-----|------|-----|------|---------------------|--------|
| **3** | **MAX98357A** I²S amp breakout | 1 (kits often 2×) | ~$5–8 | **Reference:** [Adafruit #3006](https://www.adafruit.com/product/3006) · **Example (you):** [2× MAX98357A I²S breakout — `B0DPJRLMDJ`](https://www.amazon.com/dp/B0DPJRLMDJ) — generic; use Adafruit [MAX98357 guide](https://learn.adafruit.com/adafruit-max98357-i2s-class-d-mono-amp) for **BCLK / LRCLK / DIN** wiring; check **GAIN** / **SD** pads on your silkscreen | ✅ |
| **4** | **Speaker** — small **8 Ω**, ~**0.5–1 W**, target **~28–30 mm** (thin / round OK) | 1 | ~$3–8 | **Example (you):** [MECCANIXITY 28 mm 8 Ω 0.5 W, 2 pcs — `B0GR4HDKX1`](https://www.amazon.com/dp/B0GR4HDKX1) (twister **Size = 28 mm**; **1.25 mm** plug — strip for MAX98357 **±**) · alts: [Amazon US suggested ASINs (seq 4-6)](#amazon-us-suggested-asins-seq-4-6) | ✅ |

**Stop gate:** Play a test tone or WAV from XIAO through amp into speaker (even before mic).

---

### Wave 4 — Audio in (microphone)

| Seq | Part | Qty | Est. | Link / how to order | Status |
|-----|------|-----|------|---------------------|--------|
| **5** | **INMP441** (or equivalent **I²S MEMS** breakout for 3.3 V) | 1 (kits often 3×) | ~$5–12 | **Example (you):** [Qoroos 3× INMP441 — `B0FKFR1WFX`](https://www.amazon.com/dp/B0FKFR1WFX) · alts: [Amazon US suggested ASINs (seq 4-6)](#amazon-us-suggested-asins-seq-4-6) · confirm **BCLK / LRCLK / DIN / SCK / 3V3 / GND** on the board you open | ✅ |

**Stop gate:** Record silence + voice; levels sane, no clipping on tap.

---

### Wave 5 — Bench / integration (non-BOM but order with Wave 3–4 if you need)

| Seq | Part | Qty | Est. | Notes | Status |
|-----|------|-----|------|--------|--------|
| **6** | Solderless breadboard + jumpers (+ dupont **if** no XIAO headers) | 1 kit | ~$5–15 | **Example (you):** [BOJACK 830+400 + 126 jumpers — `B08Y59P6D1`](https://www.amazon.com/dp/B08Y59P6D1) · add dupont F–M/M–M if needed: [seq 6 table](#amazon-us-suggested-asins-seq-4-6) | ✅ |
| **7** | Silicone wire 22–26 AWG (short kit) | 1 | ~$5 | Cleaner than long jumpers for audio | ⏸️ |
| **8** | **JST PH 2.0 pigtail** (if cell has wrong connector) | 0–1 | ~$2 | Only if listing photo ≠ XIAO plug | ⏸️ |

---

### Wave 6 — Enclosure / mechanical (after firmware + audio proven)

| Seq | Part | Notes |
|-----|------|--------|
| **9** | Filament / resin / SLA | For [lexie-plaud-form-factor.html](../hardware/lexie-plaud-form-factor.html) shells or tray |
| **10** | Silicone bump feet | Optional anti-slip per spec |

---

## Master line list (copy into a spreadsheet)

| Order | SKU / description | Qty | Path | Status |
|-------|-------------------|-----|------|--------|
| 1 | XIAO ESP32-S3 | 1–2 | A + B | ✅ |
| 2 | USB-C data cable | 1 | A + B | verify stash |
| 3 | 503040 LiPo JST-PH 2.0 compatible | 1 | A | ✅ e.g. `B0FBJPP5G6` |
| 4 | MAX98357A breakout | 1 | A + B | ✅ e.g. `B0DPJRLMDJ` |
| 5 | 8 Ω speaker ~28–30 mm | 1 | A + B | ✅ `B0GR4HDKX1` |
| 6 | INMP441 I²S breakout | 1 | A + B | ✅ `B0FKFR1WFX` (3-pack) |
| 7 | Breadboard + jumpers | 1 | A | ✅ `B08Y59P6D1` (+ dupont if needed) |
| 8 | Thinner LiPo (≤3.5 mm) | 1 | B only | ⏸️ |

---

## Quick checklist (print / tick in cart)

- [ ] **Wave 1:** Amazon **Style/Color** = **ESP32S3** base board — **not** “ESP32S3 Sense”; matches [Seeed XIAO ESP32S3](https://www.seeedstudio.com/XIAO-ESP32S3-p-5627.html) photos
- [ ] **Wave 2:** LiPo **connector** matches XIAO; **polarity** verified before plug
- [ ] **Wave 3:** Amp is **I²S** (not analog-only “class D” with no I²S in)
- [ ] **Wave 4:** Mic breakout is **3.3 V** logic (XIAO GPIO domain)
- [ ] **Cables:** At least one **known-good data** USB-C cable in the bin

---

## Notes (read once)

### Amazon `B0BYSB66S5` — pick the **right** XIAO (this is the usual mistake)

That ASIN is Seeed’s **official** Amazon listing; it is a **multi-variant** (“twister”) page. **WX-024** needs the **plain XIAO ESP32-S3** — same product as [Seeed’s XIAO ESP32S3 store page](https://www.seeedstudio.com/XIAO-ESP32S3-p-5627.html) (**no** camera, **not** “Sense”).

**Before you click Buy:**

1. Use the **Color** / **Style** dropdown (wording varies by region).
2. Select **`ESP32S3`** / **XIAO ESP32S3** — the **base** board only.
3. **Do not** select **`ESP32S3 Sense`** — that is a **different** board (camera + different layout); Lexie does not use it for v1.
4. **Do not** select **ESP32C3**, **ESP32C6**, **MG24**, etc.

**Quick visual:** The correct board is a small flat rectangle with **USB-C** and **no** big camera module sticking up. If you see **OV2640 / camera** in the title or hero image, you’re on **Sense** — back up and change the variant.

---

- **Z-height:** Path **A** with **503040** is expected to be **thicker than 8 mm** until you move to Path **B** (thinner cell, no headers, tighter PCB). See **§1b** in the form-factor HTML — do not block firmware on the thin shell.
- **INMP441:** Prototype on a **breakout**; move to SMD on a custom PCB only when you commit to Path B.
- **MAX98357:** Adafruit **#3006** documents pin names that map cleanly to XIAO I²S pins (wire order still needs your pin map from Seeed wiki).
- **Spares:** One extra **XIAO** or one extra **speaker** saves a week if ESD / wrong polarity happens.

---

## After everything arrives

1. **Polarity** — LiPo vs XIAO JST (document with a phone photo in your build log).  
2. **Wire table** — One row: XIAO pin → INMP441 / MAX98357 / button / LED (add when you freeze pinout).  
3. **First smoke** — USB 5 V only → then LiPo → then I²S lines last (avoid hot-plugging signal into powered mic).

---

*When you lock a 🔍 row to a specific URL, paste it into this file and flip status to ✅ so the next order stays reproducible.*
