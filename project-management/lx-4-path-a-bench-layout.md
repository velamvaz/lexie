---
schema: lexie.bench-layout
schema_version: "1.0"
kit: lx-4-path-a
status: draft
last_updated: "2026-05-06"
scope: bench_bringup_only
pin_map_frozen: false
pin_map_work_item: WX-029
solder_work_item: WX-027
human_guide_html: wx-027-beginner-bench-guide.html
component_kit: lx-4-path-a-component-kit.md
bom: hardware-shopping-cart.md
---

# LX-4 Path A — Bench layout registry (machine-readable)

Structured reference for agents and humans: **components**, **breadboard rules**, **default placements**, and **layout challenges**.

---

## 1. Breadboard model

```yaml
breadboards:
  - id: bb-main
    role: primary_prototype
    type: 830_tie_point
    order_asin: B08Y59P6D1
    use_for:
      - xiao
      - max98357
      - inmp441
      - power_rail_distribution
  - id: bb-aux
    role: spare_or_jig
    type: 400_tie_point
    order_asin: B08Y59P6D1
    use_for:
      - header_soldering_jig
      - extra_jumpers
      - optional_second_layout
```

### 1.1 Coordinate system

```yaml
coordinates:
  row_letters_top_half: [A, B, C, D, E]
  row_letters_bottom_half: [F, G, H, I, J]
  column_labels_top: [0, 5, 10, 15, 20, 25, 30, 35]  # printed; unlabeled holes exist between
  column_labels_bottom: [60, 55, 50, 45, 40, 35, 30, 25]  # printed; reversed print direction
  center_gap: true  # E not connected to F across gap
  power_rails:
    top_edge: { minus: blue, plus: red }
    bottom_edge: { plus: red, minus: blue }
```

### 1.2 Connectivity rules (normative)

```yaml
connectivity:
  - rule: column_strip_top
    description: Holes A–E at the same column index are electrically connected.
  - rule: column_strip_bottom
    description: Holes F–J at the same column index are electrically connected.
  - rule: no_cross_gap
    description: Row E and row F are not connected across the center ravine.
  - rule: power_rails_separate
    description: Edge +/− rails are separate from the A–J grid until jumpered.
```

---

## 2. Component registry

| component_id | function | part_name | qty | asin | on_breadboard | header |
|--------------|----------|-----------|-----|------|---------------|--------|
| `cmp-mcu-xiao` | mcu | Seeed XIAO ESP32-S3 (not Sense) | 1 | B0BYSB66S5 | yes | optional_male_7x2 |
| `cmp-pwr-lipo` | battery | 503040 LiPo JST-PH 2.0 | 1 | B0FBJPP5G6 | no | n/a |
| `cmp-audio-amp` | i2s_amp_out | MAX98357A breakout | 1 | B0DPJRLMDJ | yes | required_male_7x1 |
| `cmp-audio-spk` | speaker | 8Ω ~28 mm | 1 | B0GR4HDKX1 | no | wire_to_amp_only |
| `cmp-audio-mic` | i2s_mic_in | INMP441 breakout | 1 | B0FKFR1WFX | yes | required_male_6x1 |
| `cmp-bb-main` | tool | 830 breadboard | 1 | B08Y59P6D1 | n/a | n/a |
| `cmp-bb-aux` | tool | 400 breadboard | 1 | B08Y59P6D1 | n/a | n/a |
| `cmp-acc-terminal` | accessory | 2-pin screw terminal | 1 | with_amp_kit | no | solder_on_amp_pcb |
| `cmp-acc-header` | accessory | 2.54 mm male pin strips | several | loose | n/a | consumable |

### 2.1 `cmp-mcu-xiao`

```yaml
component_id: cmp-mcu-xiao
orientation:
  component_side: up
  readable_label: "Seeed Studio XIAO ESP32S3"
  usb_c: toward_bench_edge_for_cable_access
header:
  type: male_2.54mm
  rows: 2
  pins_per_row: 7
  total_pins: 14
breadboard_mount:
  straddle_center_gap: true
  suggested_rows: { side_a: E, side_b: F }
  suggested_columns: [25, 24, 23, 22, 21, 20, 19]  # draft; confirm at WX-029
not_on_breadboard:
  - lipo_jst_directly_to_holes
```

### 2.2 `cmp-audio-amp` (MAX98357A)

```yaml
component_id: cmp-audio-amp
orientation:
  component_side: up
  readable_label: "MAX98357A I2S Amp"
header:
  type: male_2.54mm
  rows: 1
  pins: 7
  edge: bottom_when_readable
  silkscreen_left_to_right: [LRC, BCLK, DIN, GAIN, SD, GND, Vin]
speaker_output:
  type: screw_terminal_block
  solder_pads: [SPK_minus, SPK_plus]  # silkscreen - and + on PCB top
  connects_to: cmp-audio-spk
  never_connect_to: cmp-mcu-xiao.lipo_jst
breadboard_mount:
  breadboard_id: bb-main
  row: G
  columns_left_to_right: [55, 54, 53, 52, 51, 50, 49]
  pin_to_column:
    LRC: 55
    BCLK: 54
    DIN: 53
    GAIN: 52
    SD: 51
    GND: 50
    Vin: 49
solder_jig:
  same_coordinates_as_mount: true
  long_pin_into_hole: true
  short_pin_through_pcb: true
```

### 2.3 `cmp-audio-mic` (INMP441)

```yaml
component_id: cmp-audio-mic
orientation:
  component_side: up
  mic_port: up_or_outward
header:
  type: male_2.54mm
  rows: 1
  pins: 6
  silkscreen_left_to_right: [SCK, SD, WS, L/R, GND, VDD]  # user board; names may vary slightly
breadboard_mount:
  breadboard_id: bb-main
  row: G
  columns_left_to_right: [45, 44, 43, 42, 41, 40]  # draft; leave gap from amp
  pin_to_column:
    SCK: 45
    SD: 44
    WS: 43
    L/R: 42
    GND: 41
    VDD: 40
solder_jig:
  same_coordinates_as_mount: true
```

### 2.4 `cmp-audio-spk`

```yaml
component_id: cmp-audio-spk
on_breadboard: false
wire_to:
  target: cmp-audio-amp
  terminals: screw_terminal
  polarity:
    red: SPK_plus
    black: SPK_minus
```

### 2.5 `cmp-pwr-lipo`

```yaml
component_id: cmp-pwr-lipo
on_breadboard: false
connect_to:
  target: cmp-mcu-xiao
  connector: jst_ph_2.0
preconditions:
  - multimeter_dc_volts_polarity_documented
  - matches_seeed_xiao_lipo_guidance
work_item_gate: WX-027
```

---

## 3. Default layout map (830 main board, top view)

```yaml
layout_map:
  breadboard_id: bb-main
  modules:
    - component_id: cmp-audio-amp
      anchor: { row: G, column_start: 55, column_end: 49 }
    - component_id: cmp-audio-mic
      anchor: { row: G, column_start: 45, column_end: 40 }
    - component_id: cmp-mcu-xiao
      anchor: { rows: [E, F], column_start: 25, column_end: 19 }
  off_board_nearby:
    - component_id: cmp-audio-spk
      note: wire_only_to_amp_screw_terminal
    - component_id: cmp-pwr-lipo
      note: on_table_until_polarity_ok
  aux_board:
    breadboard_id: bb-aux
    role: jig_or_spare_ties
```

ASCII (not to scale):

```text
[830 bb-main — bottom half columns 60 ← → 25]

  col:  60    55    50    45    40    25    19
        |     |     |     |     |     |     |
  G     | MAX98357 (7) | INMP441 (6) |     |
  E/F   |              |             | XIAO (straddle gap)
```

---

## 4. Layout challenges (explicit)

| challenge_id | problem | why_it_hurts | mitigation |
|--------------|---------|--------------|------------|
| `lay-ch-01` | Headers not pre-soldered | Loose pins; wrong angle | Use breadboard jig; see `solder_jig` per component |
| `lay-ch-02` | Pin direction confusion | Long vs short end reversed | Long → breadboard hole; short → PCB hole; plastic between |
| `lay-ch-03` | Single-row vs dual-row | XIAO spans gap; amp/mic are one row | Do not force amp across gap |
| `lay-ch-04` | Center gap isolation | E not tied to F | XIAO must straddle; jumpers cross gap later |
| `lay-ch-05` | Two I2S peripherals | Shared BCLK/LRCLK wiring clutter | WX-029 pin map; keep amp and mic in same column band |
| `lay-ch-06` | Speaker not a PCB module | No row/column for speaker | Screw terminal on amp only |
| `lay-ch-07` | LiPo vs breadboard rails | User may plug battery into +/− rails | LiPo only to XIAO JST after polarity check |
| `lay-ch-08` | Amp Vin/GND vs rail +/− | Same words, different nodes | Document wires in WX-029; rails optional |
| `lay-ch-09` | 830 vs 400 boards | Wrong board for main stack | `bb-main` = 830; `bb-aux` = jig/spare |
| `lay-ch-10` | Column labels skip numbers | Holes exist between 55 and 50 | Count 7 adjacent holes in one row letter |
| `lay-ch-11` | Solder jig position ≠ final | Moved after soldering | Coordinates above match both jig and mount |
| `lay-ch-12` | Silkscreen name variance | INMP441 labels differ by vendor | Match by function; confirm with meter/wx-029 |

---

## 5. Header and orientation (machine rules)

```yaml
header_rules:
  default_type: male_2.54mm
  required_for:
    - cmp-audio-amp
    - cmp-audio-mic
  optional_for:
    - cmp-mcu-xiao
  female_socket_on_breakouts: false  # path_a_default
orientation_rules:
  - id: ori-01
    rule: component_side_faces_up
  - id: ori-02
    rule: readable_silkscreen_not_mirrored
  - id: ori-03
    rule: solder_on_pcb_pad_side_after_jig
```

---

## 6. Work item boundaries

```yaml
work_items:
  WX-027:
    delivers:
      - headers_soldered
      - amp_speaker_terminal_soldered
      - speaker_wired_to_amp
      - lipo_polarity_documented
    does_not_deliver:
      - i2s_gpio_pin_map
  WX-029:
    delivers:
      - xiao_to_amp_wire_table
      - xiao_to_mic_wire_table
      - frozen_gpio_assignments
    updates:
      - this_file_pin_map_frozen: true
```

---

## 7. Related files

| file | role |
|------|------|
| [lx-4-path-a-component-kit.md](lx-4-path-a-component-kit.md) | Parts list + integration rules |
| [hardware-shopping-cart.md](hardware-shopping-cart.md) | ASINs and order waves |
| [wx-027-beginner-bench-guide.html](wx-027-beginner-bench-guide.html) | Human steps + Figure 2 SVG |
| [wx-027-beginner-bench-guide.md](wx-027-beginner-bench-guide.md) | Human steps (Markdown) |
| [lx-4-path-a-bench-testing.md](lx-4-path-a-bench-testing.md) | Phased pass/fail tests (no power → USB → I2S → LiPo) |
| [work-inventory.md](work-inventory.md) | WX-027 / WX-029 tracking |

---

## 8. Changelog

| date | change |
|------|--------|
| 2026-05-06 | Initial registry: components, bb-main placements G-55..49 (amp), G-45..40 (mic), E/F XIAO draft, layout challenges table |
