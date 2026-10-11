# Recommended changes to BOM-B2 (rev 0.1, 2026-10-08)

Found while turning the BOM into a schematic. None of these change the $5 target meaningfully
(net effect ≈ +$0.01/board at 600, and one low-stock part is removed).

| # | Change | Why | Cost impact @600 |
|---|---|---|---|
| 1 | **Remove L1** (C5120855, 3.3 µH) | RP2040 has an internal linear 1.1 V LDO; it needs 1 µF on VREG_VOUT, not an inductor. The inductor is an RP2350 requirement. Removes the 1,900-stock risk item. | −$0.024, −1 part type, −2 joints |
| 2 | **Add R11, R12: 27 Ω 1% 0402** (**C25100** — C25105 is actually 33 Ω, corrected 2026-10-08) | USB D+/D− series termination per RP2040 hardware design guide. | +$0.004, +1 part type (basic, no feeder fee), +4 joints |
| 3 | **Add R13: 1 kΩ** on XOUT (C11702, already on BOM) | Crystal drive-level limiting per RP2040 guide. | +$0.001, +2 joints |
| 4 | **Add R14: 1 kΩ** between BOOTSEL switch and GND (C11702) | Matches the Pico reference; protects QSPI_SS driver when button is held during flash access. | +$0.001, +2 joints |
| 5 | **100 nF: 12 → 16** (C60474) | One cap per RP2040 supply pin (6 IOVDD + 2 DVDD/VREG + USB + ADC) + flash + 4 RGB. BOM-B2's 8 is two short. | +$0.012, +8 joints |
| 6 | **1 µF: 1 → 2** (C6119792) | ME6206 LDO needs ≥ 1 µF on its output; BOM-B2 has no output cap on 3V3. | +$0.007, +2 joints |
| 7 | *Optional:* 0402 pad on GPIO10 → LED1 DIN, DNP | Place for a 33–100 Ω damping resistor. Fit 0 Ω or bridge if ringing shows up. | $0 |

Net: part types 17 → 17 (−L1, +27 Ω). Joints 188 → 206 (+18 × $0.0016 = +$0.03/board). Components ≈ +$0.00.

## Not changed, but check before ordering
- WS2812B-2020-V6 pinout: confirm DIN/DOUT/VDD/GND pad order on the LCSC datasheet; the mockup assumes 1=DOUT, 2=GND, 3=DIN, 4=VDD.
- USBLC6-2SC6 pass-through pins (4, 6) are used on the MCU side so the ESD part sits in-line.
- Purple solder mask: confirm no surcharge / lead-time change on the JLC quote.

---

# rev 0.2 — add-ons (user decision 2026-10-08)

| Ref | LCSC | Part | Qty | New type? | Notes |
|---|---|---|---|---|---|
| J4 | C431535 | PJ-320D 3.5 mm jack | 1 | yes (ext) | audio out, GPIO11 |
| C21 | C15195 | 10 nF 0402 | 1 | yes (basic) | PWM low-pass |
| C22 | C7503495 | 10 µF 0805 | 1 | no | DC block |
| R17 | C11702 | 1 kΩ | 1 | no | filter |
| U5 | C91447 | IRM-H638T/TR2 IR receiver | 1 | yes (ext) | GPIO22 |
| C23 / C24 | C60474 / C7503495 | 100 nF / 10 µF | 1+1 | no | IR VCC filter |
| Q1 | C22469449 | HL3401 PMOS | 1 | yes (ext) | battery switch |
| D6 | C7420330 | B5819W Schottky | 1 | yes (ext) | USB → VSYS |
| R10, R15, R16 | C25744 | 10 kΩ | 3 | no | gate pull-down, VBUS sense divider |
| J3 | C722761 | JST-PH 2-pin SMD | 1 | yes (ext) | battery |
| SW5 | C431540 | MSK12C02 slide switch | 1 (optional) | yes (ext) | only if the battery box has no switch |
| H1, H2 | — | Ø4.0 mm plated holes (rev 0.3: two holes) | 2 | — | lanyard |

Part types: 17 → 23 (24 with SW5). Joints: 206 → ≈ 240.

## Cost reality check (600 boards, VAT incl., rough)
BOM-B2's $5 target assumed 30×46 mm. At 80×140 mm:

| Item | 30×46 (B2) | 80×140 + add-ons |
|---|---:|---:|
| Components + joints | $2.34 | ≈ $2.80 |
| PCB fab (≈ $90/m², irregular outline +10 %) | $0.14 | ≈ $1.10 |
| Setup/stencil/feeders, per board | $0.10 | $0.12 |
| Shipping (board mass 3 g → ≈ 35 g; 600 pcs ≈ 21 kg) | $1.00 | ≈ $1.8–2.5 |
| Battery box, wired, with switch (outside JLC) | — | $0.25–0.45 |
| AAA cells ×3 (optional) | — | $0.30–0.60 |
| **≈ Total per board** | **$4.76** | **≈ $7.5–8.5** |

If $5 still matters, the lever is size: **100 × 56 mm** (same silhouette, 2-up in a 100×120 panel) cuts PCB to ≈ $0.50 and shipping back to ≈ $1.20 → ≈ $6. Nothing else moves the number much. Decide before the KiCad stage; shrinking later means re-doing the layout.

---

# rev 0.5 — IR, audio and speaker become breakaway modules (user decision 2026-10-11)

The IR receiver and the audio jack leave the main board, a speaker (BOM-B2 add-on 7) is added, and all three
sit on **breakaway sub-boards under the pedestal** (same PCB, tab-routed, 4 mm tabs with mouse bites, no copper
across the tabs). Each module carries a 1×3 pin header and plugs into a matching 1×3 socket on the main board.
Pinout on every port: **1 = GND (square pad), 2 = 3V3, 3 = signal**; power in the middle, so a module plugged
in backwards swaps GND and signal and never puts 3V3 on a GPIO. Board blank grows from 56 × 100 to 56 × 118 mm.

| Ref | LCSC | Part | Qty | New type? | Where | Notes |
|---|---|---|---|---|---|---|
| J5, J6, J7 | C541850 | XFCN PM254V-11-03-H85, 1×3 2.54 mm female header, THT | 3 | yes (ext) | main board, coin area | slots IR / AUDIO / SPK; GPIO22 / 11 / 25 |
| P1, P2, P3 | C49257 | BOOMELE 2.54-1×3P pin header, THT | 3 | yes (ext) | one per module | mates with J5–J7 |
| U5, R19, C23, C24 | as before | IR receiver + RC filter | 1+1+1+1 | no | **IR module** | nets renamed IRM_* |
| J4, R17, C21, C22 | as before | audio jack + PWM filter | 1+1+1+1 | no | **audio module** | nets AUM_*; P2 pin 2 (3V3) unused |
| LS1 | C94599 | MLT-8530 SMD magnetic transducer, 2.7 kHz, 16 Ω | 1 | yes (ext) | **speaker module** | 95 mA max, runs from 3V3 |
| Q2 | C2146 | S8050 NPN, SOT-23 | 1 | yes (basic) | speaker module | low-side switch |
| D7 | C81598 | 1N4148W, SOD-123 | 1 | yes (basic) | speaker module | flyback. **LCSC stock showed 300 on 2026-10-11, check JLC stock or pick another 1N4148W** |
| R20 | C11702 | 1 kΩ | 1 | no | speaker module | base resistor |
| R21 | C25744 | 10 kΩ | 1 | no | speaker module | base pull-down (quiet at reset) |
| C25 | C7503495 | 10 µF 0805 | 1 | no | speaker module | local bulk for the coil pulses |

Part types: 23 → 28 (+5: two headers, transducer, S8050, 1N4148W). Joints: ≈ 240 → ≈ 262 SMD + **18 THT**
(the headers are hand-soldered by JLC: $3.50 per order + $0.0173 per joint).

GPIO: GPIO25 is taken for the speaker (it stays on J2 pin 15 as a shared signal). 15 GPIO remain free on J2.

## Cost impact (rough, 600 boards, VAT incl.)

| Item | Δ $/board |
|---|---:|
| 3 sockets ($0.07) + 3 pin headers ($0.01) | ≈ +$0.24 |
| THT hand-solder, 18 joints | ≈ +$0.31 |
| Transducer, S8050, 1N4148W, 10 k, 1 k, 10 µF + 14 SMD joints | ≈ +$0.26 |
| 5 new part types ($1.53 each per order) + $3.50 THT setup | ≈ +$0.02 |
| PCB blank 56 × 118 instead of 56 × 100 (+18 % area, more routing) | ≈ +$0.10 |
| **Total** | **≈ +$0.9–1.0** |

At 10 boards the fixed fees dominate: 5 × $1.53 + $3.50 ≈ $11 per order, so ≈ +$2.5/board. Prices are LCSC
single-piece figures converted from CNY on 2026-10-11 and not a JLC quote. **Cheaper option:** leave J5–J7 and
P1–P3 unpopulated (DNP, like J2) and bag loose headers; that removes the THT fee and the two header part types
(≈ −$0.55/board) but the badge then needs soldering before any module works.

## Why this shape
- The modules hang under the pedestal, so the badge keeps its 56 × 100 silhouette after snapping them off; the
  mouse bites sit on the pedestal edge, so the stub stays on the module, not on the badge.
- Module nets have their own names (IRM_, AUM_, SPM_). Nothing is connected across the tabs, so DRC on the
  panel is meaningful and the modules work only when plugged in, which is the point.
- Vertical sockets: a plugged-in module stands up like a product in the window. The IR lens and the sound port
  then face sideways. If you prefer modules lying flat and facing forward, swap P1–P3 for right-angle pin
  headers (same pads, `PinHeader_1x03_P2.54mm_Horizontal`); nothing else changes.
- The transducer footprint wires its two dummy pads crosswise to the two lead pads, so a 180° placement error
  only reverses the coil. A 90° error leaves both leads on one net: silent, but nothing is damaged.
