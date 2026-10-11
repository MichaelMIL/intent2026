# BOM — Variant B2 (RP2040 + buttons, LEDs, RGB LEDs, GPIO header)

Date: 2026-10-06. Derived from [BOM-B.md](BOM-B.md). **Status 2026-10-11:** the built board is B2 + the add-ons chosen in `bom-deltas.md` (rev 0.2: audio jack, IR receiver, 3×AAA power path; rev 0.5: IR receiver, audio jack and the speaker (add-on 7) moved onto breakaway modules with 1×3 headers). This file is the priced baseline; `bom-deltas.md` lists what changed on top of it. Status: **priced for a 600-board production order and a 5-board prototype
order (LCSC prices re-checked 2026-10-06); not yet verified against a JLC
quote.** No display. Standard PCBA, one order. The 600-board order is 100
panels of 3×2.

Changes from B:

- **+3 user buttons** (SW2–SW4), on GPIO with internal pull-ups, so no extra resistors
- **+3 LEDs** (D3–D5) with 1 kΩ series resistors (R7–R9), **5 LEDs total**
- **+4 addressable RGB LEDs** (LED1–LED4), WS2812B-compatible, daisy-chained
  on one GPIO, each with its own 100 nF decoupling cap (C13–C16)
- **J2: 2×13 2.54 mm header footprint** breaking out every unused GPIO plus
  SWD, RUN, 3V3, GND and the RGB chain's data-out. **Left unpopulated.** Players solder their own pins.
- **All four switches use JLC basic part C318884** (5.1×5.1 mm). The 3×4 mm
  C55200589 is dropped. At 4 per board it would need 2,400 units against
  8,260 in stock.
- **Board grows from 30×24 to 30×46 mm.** That is the largest size that still
  fits the 3×2 panel inside 100×100 mm (98×98 mm panel).

Assumption: "3 LEDs" means 3 *more*, as with the buttons. If you meant 3
total, drop D4/D5 and R8/R9. That saves about $0.02 per board, and GPIO8–9 move
to the header.

## Parts

| Ref | LCSC | Part | Package | Qty/bd | Joints | Unit $ @1 | Min buy | Ext $/bd, 5 boards | Qty @600 | Unit $ @600 | Ext $/bd @600 | Lib | LCSC stock |
| --- | --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | ---: |
| U1 | C2040 | RP2040: dual Cortex-M0+, native USB | LQFN-56 (7×7) | 1 | 57 | 0.9975 | 1 | 0.9975 | 600 | 0.7383 | 0.7383 | ext | 59,068 |
| U2 | C2456211 | W25Q16JVSNIQ: 16 Mbit QSPI boot flash | SOIC-8 | 1 | 8 | 1.1388 | 1 | 1.1388 | 600 | 0.7089 | 0.7089 | ext | 16,301 |
| U3 | C35259 | ME6206A33M3G: 3.3 V LDO, 300 mA | SOT-23-3L | 1 | 3 | 0.0605 | 10 | 0.0605 | 600 | 0.0440 | 0.0440 | ext | 14,710 |
| U4 | C2827654 | USBLC6-2SC6: USB ESD array | SOT-23-6 | 1 | 6 | 0.0450 | 10 | 0.0450 | 600 | 0.0312 | 0.0312 | ext | 85,610 |
| J1 | C393939 | TYPE-C16PIN: USB-C receptacle | SMD | 1 | 16 | 0.0623 | 10 | 0.0623 | 600 | 0.0429 | 0.0429 | ext | 374,390 |
| **SW1–SW4** | **C318884** | TS-1187A-B-A-B tactile 5.1×5.1×1.5 mm: BOOTSEL + 3 user | SMD-4P | **4** | **16** | 0.0207 | 20 | 0.0828 | 2,400 | 0.0139 | 0.0556 | **basic** | 213,540 |
| L1 | C5120855 | 3.3 µH 880 mA shielded: RP2040 1V1 buck | SMD 2×1.6 | 1 | 2 | 0.0360 | 10 | 0.0360 | 600 | 0.0238 | 0.0238 | ext | **1,900** ⚠ |
| Y1 | C133334 | 12 MHz crystal, required for USB | SMD3225-4P | 1 | 4 | 0.0797 | 10 | 0.0797 | 600 | 0.0558 | 0.0558 | ext | 142,690 |
| **C1–C8, C13–C16** | C60474 | 100 nF X7R 16 V: decoupling (C13–C16 = one per RGB LED) | 0402 | **12** | **24** | 0.0048 | 100 | 0.0576 | 7,200 | 0.0030 | 0.0360 | ext | 14,839,700 |
| C9 | C7503495 | 10 µF X5R 10 V: bulk | 0805 | 1 | 2 | 0.0319 | 20 | 0.0319 | 600 | 0.0224 | 0.0224 | ext | 23,680 |
| C10 | C6119792 | 1 µF X5R 16 V | 0402 | 1 | 2 | 0.0089 | 50 | 0.0089 | 600 | 0.0071 | 0.0071 | ext | 1,095,700 |
| C11, C12 | C1548 | 15 pF C0G: crystal load | 0402 | 2 | 4 | 0.0038 | 100 | 0.0076 | 1,200 | 0.0029 | 0.0058 | basic | 809,700 |
| R1, R2 | C25905 | 5.1 kΩ 1%: USB-C CC pulldowns | 0402 | 2 | 4 | 0.0024 | 100 | 0.0048 | 1,200 | 0.0019 | 0.0038 | basic | 3,131,000 |
| R3, R4 | C25744 | 10 kΩ 1%: pullups | 0402 | 2 | 4 | 0.0034 | 100 | 0.0068 | 1,200 | 0.0027 | 0.0054 | basic | 3,766,700 |
| **R5–R9** | C11702 | 1 kΩ 1%: LED series | 0402 | **5** | **10** | 0.0019 | 100 | 0.0095 | 3,000 | 0.0012 | 0.0060 | basic | 0 LCSC / 7.0 M JLC |
| **D1–D5** | C2286 | KT-0603R red LED | 0603 | **5** | **10** | 0.0076 | 100 | 0.0380 | 3,000 | 0.0058 | 0.0290 | basic | 2,602,100 |
| **LED1–LED4** | **C52917434** | Worldsemi WS2812B-2020-V6: addressable RGB | SMD2020-4P (2×2) | **4** | **16** | 0.0919 | 5 | 0.3676 | 2,400 | 0.0571 | 0.2284 | ext | 701,530 |
| J2 | — | 2×13 2.54 mm header, **footprint only** | THT | 1 | 0 | — | — | 0 | — | 0 | 0 | — | — |
| TP1–TP3 | — | UART TX / RX / GND pads, copper only | — | 3 | 0 | — | — | 0 | — | 0 | 0 | — | — |
|  |  | **17 part types (11 extended, 6 basic)** |  |  | **188** |  |  | **$3.0353** |  |  | **$2.0444** |  |  |

Bold rows changed from B. Total change: +48 joints, +1 part type, +$0.288 in components.

**Price columns.** Prices were re-checked against LCSC `productPriceList` on
2026-10-06. Every 600-board price is unchanged.

- **Unit $ @1**: the price of a single part, which is LCSC's lowest price
  break. **Min buy** is that break's minimum order quantity.
- **5 boards**: per-board parts cost for a 5-board prototype order, which is
  JLC's minimum PCB quantity. Every part's 5-board quantity falls inside the
  lowest price break, so this is the single-part price × qty/bd.
- **@600**: the price break for the quantity actually needed, which is the
  per-board quantity × 600.

Components come to **$3.04/board for 5 boards**, 48% above the $2.04 at 600.
If LCSC minimum order quantities applied, a 5-board order's parts would cost
**$19.24**, against $15.18. JLC applies its own minimums to some parts, so
the JLC quote decides which figure is right.

## RGB LED choice — Worldsemi WS2812B-2020-V6 (C52917434)

- **Genuine Worldsemi WS2812B**, current V6 revision, 2×2 mm.
- **Driven directly from 3.3 V logic.** The classic WS2812B needs
  0.7 × VDD on the data input (3.5 V at 5 V), which a 3.3 V RP2040 output
  doesn't guarantee. The V6 datasheet gives **VIH = 0.55 × VDD**, which is
  2.75 V at 5 V. GPIO10 can therefore drive the chain directly, with no level
  shifter or supply-dropping diode.
- **Powered from VBUS (5 V), not the 3V3 LDO.** Supply range is 3.3–5.3 V.
  It draws 12 mA per channel, so four LEDs at full white take **144 mA**.
  That is within the USB budget and puts no load on the 300 mA LDO. Note that
  the 5.3 V maximum leaves little margin over USB's 5.25 V ceiling, the same
  as any WS2812B.
- **Stock: 701k**, 292× cover at 600 boards.
- **JLC lists it as "standard-only"**, as it does almost every WS2812-class
  part. It can't be assembled on the Economic tier. B2 is already on Standard,
  so this only removes Economic as a fallback.
- **Avoid the older Worldsemi parts.** WS2812B-B/T, -V5 and -XF0x are 5050
  packages with a 3.7 V minimum supply and no 0.55 × VDD threshold on their
  listings. They would need a level shifter, and the in-stock 74AHCT1G125
  parts have only about 3k available.
- The datasheet's handling notes mention "Huacaiwei", not Worldsemi, though
  LCSC lists the part as Worldsemi. If genuine Worldsemi provenance matters,
  check the reel labelling on first delivery.
- The Xinglight XL-1615RGBC-2812B clone (C5349954), costed in the previous
  revision, is $0.055/board cheaper. Its threshold is also 0.55 × VDD.

Optional, $0: leave room for a 33–100 Ω series resistor on DIN, near GPIO10.
It damps ringing on the data line. You can fit a 0 Ω link or leave it
unpopulated, but fitting a part adds a part type.

## Pin map

The RP2040 has 30 GPIO. QSPI flash, USB, crystal and SWD use dedicated pins.

| GPIO | Use |
|---|---|
| 0, 1 | UART0 TX / RX → TP1 / TP2 (the "find the console" pads, kept off the header) |
| 2, 3, 4 | SW2, SW3, SW4 to GND, internal pull-up (pull-*up* avoids RP2040 erratum E9) |
| 5–9 | D1–D5 via R5–R9, active high |
| 10 | RGB data → LED1 DIN → LED2 → LED3 → LED4 → DOUT to J2 |
| **11–29** | **J2 header**: 19 GPIO, including SPI1 (12–15), I2C0 (16/17), UART1 (20/21), ADC0–3 (26–29) |
| SW1 | BOOTSEL on QSPI_SS, unchanged from B |

J2 (26 pins): GPIO11–29 (19), SWCLK, SWDIO, RUN, 3V3, GND ×2, RGB_DOUT.
A 2×13 header is 33 mm long at 2.54 mm, so it runs along the 46 mm edge.

**RGB_DOUT on the header** lets players extend the chain with their own LED
strip, or sniff the WS2812 protocol off the last LED. VBUS is deliberately
**not** on the header. A stray 5 V jumper onto a GPIO pin would kill the RP2040.

**SWD on the header.** Breaking out SWD does not weaken anything. RP2040
firmware sits in external flash with no readout protection, so a player who
gets the flash already has the firmware. It gives players a debugger as a bonus
attack vector. If you would rather not offer it, leave SWCLK/SWDIO as test pads.

**3V3 on the header** shares the 300 mA LDO. Shorting it or loading it heavily
browns out the board. The RGB LEDs are not on this rail.

## Cost — 5-board prototype and 600 boards, 30×46 mm, Standard, header unpopulated

| Line | 5 boards: order | 5 boards: per board | 600: order | 600: per board | vs B, 5 boards | vs B, 600 |
|---|---:|---:|---:|---:|---:|---:|
| Components | $15.18 | $3.04 | $1,226.64 | $2.04 | +$0.47 | +$0.28 |
| PCB fab (5 boards: JLC 5-piece minimum, estimate. 600: $90/m², 98×98 mm panel) | $2.00 | $0.40 | $86.44 | $0.14 | — | +$0.06 |
| SMT joints (188 × $0.0016) | $1.50 | $0.30 | $180.48 | $0.30 | +$0.08 | +$0.08 |
| Setup + stencil + feeder ($33.77 + $1.53 × 17 types) | $59.78 | $11.96 | $59.78 | $0.10 | +$0.31 | — |
| Per-piece surcharge + packing ($0.98 × 5 boards / × 100 panels) | $4.90 | $0.98 | $98.00 | $0.16 | — | — |
| **Goods** | **$83.36** | **$16.67** | **$1,651.34** | **$2.75** | +$0.85 | +$0.43 |
| Shipping to Israel (estimate) | $20.00 | $4.00 | $600.00 | $1.00 | — | — |
| VAT 18% on goods + shipping | $18.60 | $3.72 | $405.24 | $0.68 | +$0.15 | +$0.08 |
| Additional expenses (no VAT applied) | — | — | $200.00 | $0.33 | — | — |
| **Total** | **$121.97** | **$24.39** | **$2,856.58** | **$4.76** | **+$1.00** | **+$0.51** |
| Total ex-VAT (if VAT is recoverable) | $103.36 | $20.67 | $2,451.34 | $4.09 | +$0.85 | +$0.44 |

If the $200 is also subject to VAT at 600, add $36.00, giving $2,892.58 ($4.82/board).

**5-board assumptions**, to check against a real JLC quote:

- **Boards:** 5 single boards, not panelised. JLC may add edge rails to a
  board this small, and that isn't priced here.
- **Shipping:** $20 is an estimate for one small parcel to Israel.
- **Additional expenses:** the $200 is for the production order, so it isn't
  applied here.
- **Cost driver:** the $59.78 setup, stencil and feeder fee is half of the
  order, so the per-board cost falls quickly with quantity.

**Headroom to $5 (600 boards): $0.24/board**, down from $0.75 in B. Where the
increase over B went:

| Addition | 5 boards, $/board incl. VAT | 600, $/board incl. VAT |
|---|---:|---:|
| 4 WS2812B + 4 caps + joints + 1 part type | +$0.86 | +$0.33 |
| Larger board (30×24 → 30×46) | — (both sizes cost the JLC minimum) | +$0.08 |
| 3 buttons, 3 LEDs, 3 resistors + joints | +$0.14 | +$0.10 |
| **Total** | **+$1.00** | **+$0.51** |

The margin is now thin. A 10% rise in component prices ($0.24 incl. VAT)
would use up all of it. The $600 shipping and $90/m² PCB lines are estimates
and could also take what is left. Get a real JLC quote before committing. It
matters more for this variant than it did for B.

## Option: have JLC fit the header — not possible within $5

JLC hand-solders through-hole parts: $3.50 per order plus $0.0173 per joint.
For J2 that is 26 joints, $0.46/board. Header part: C41375954, $0.0904 @
500+ (single: $0.1442), **1,060 in stock**.

| | 5 boards | 600 boards |
|---|---:|---:|
| Δ $/board incl. VAT (part + 26 THT joints + $3.50/order + 1 part type) | +$1.89 | +$0.65 |
| B2 total | $26.28 | **$5.41 ❌** |

To ship pins anyway, bag a loose 2×13 or 40-pin strip with each board;
they cost about $0.03–0.05 each from bulk sellers, outside the JLC order.

## Layout notes

- C318884 is 5.1×5.1 mm. Four of them, five 0603 LEDs, four RGB LEDs and J2
  are why the board is 30×46 mm. Keep SW1 (BOOTSEL) visibly separate from the
  user buttons, or label it, so players don't reflash by accident.
- SW1 changes footprint from B (3×4 → 5.1×5.1 mm).
- Place each 100 nF (C13–C16) right at its RGB LED's VDD pin. Run VBUS to
  the RGB chain from the USB side of the LDO, after the ESD array.
- All 5 plain LEDs are the same red part. Each extra colour adds a part type:
  +$1.53 per order, about $0.003/board.

## Open items (carried from B, updated)

1. **L1 stock: 1,900 on LCSC, 3.2× cover.** Unchanged. Still needs a second source.
2. **C11702 (R5–R9)**: 0 on LCSC, but the JLC parts search shows
   **7,023,873** in stock (2026-10-06). JLC assembly draws on JLC stock, so
   this looks **resolved**. Confirm on the BOM upload.
3. **Switch stock risk resolved.** C318884 is a JLC basic part with 213k
   on LCSC and 455k on JLC.
4. **Headroom is $0.24.** Get the real JLC quote before adding anything else.
5. 0.40 mm RP2040 pitch, decoupling/L1 layout, I2C EEPROM option (+$0.09
   with VAT, which would leave $0.15): unchanged from BOM-B.md items 3–6.

Sources: LCSC `productPriceList` for C318884, C2286, C11702, C52917434,
C2761795, C52941386, C60474, C41375954 (2026-10-06). WS2812B-2020-V6
datasheet (via LCSC): VIH 0.55·VDD, 12 mA/channel, VDD 3.3–5.3 V, 100 nF per
LED. JLC THT
fee: $3.50 labour + $0.0173/joint
([JLC PCBA FAQ](https://jlcpcb.com/help/article/pcb-assembly-faqs),
[techoverflow summary](https://techoverflow.net/2024/04/09/jlcpcb-pcba-assembly-price-overview/)).

---

## Add-on variants (priced 2026-10-06)

Each add-on is priced as a **per-board delta, VAT included**, at two order
sizes: a **5-board prototype** on top of B2's $24.39, and **600 boards** on
top of B2's $4.76. The delta covers:

- the LCSC price break for the quantity actually needed. For 5 boards that
  is the single-part price, except the GS2011 digits, which hit the 10+ break.
- $0.0016 per SMT joint
- $1.53 per new part type, spread over the order. That is $0.31/board at 5
  boards, so it dominates the prototype deltas.
- JLC hand-solder rates for through-hole parts: $0.0173/joint + $3.50/order
- 18% VAT on all of it

Shipping and the $200 of additional expenses are fixed, so they don't change.
Parts already on B2 (red LED C2286, 10 kΩ C25744, 1 kΩ C11702, 100 nF C60474,
10 µF C7503495) add joints but no new part type.

**Board space:** the 30×46 mm board is already full with the B2 parts. Every
add-on except the IR receiver and the audio jack probably needs a bigger
board. Moving to 47×47 mm on a 2×2 panel adds about **$0.19/board**, for extra
PCB area and 50 more panels. That cost is **not** included in the per-add-on
figures below. At 5 boards a 47×47 mm board still costs the JLC PCB minimum,
so it adds nothing there.

### Summary

| Add-on | Key part | Parts $/bd, 5 bds | Parts $/bd, 600 | Δ $/bd, 5 bds | Δ $/bd, 600 | B2 total, 5 bds | B2 total, 600 | Stock vs 600 |
|---|---|---:|---:|---:|---:|---:|---:|---|
| 3.5 mm audio jack + PWM filter | PJ-320D C431535 | 0.09 | 0.07 | +$0.85 | **+$0.10** | $25.25 | $4.87 ✅ | 56k ✅ |
| Alkaline 3×AAA power + USB/battery protection (connector only, holder not included) | HL3401 C22469449 + B5819W C7420330 + JST-PH C722761 | 0.09 | 0.07 | +$1.21 | **+$0.11** | $25.60 | $4.87 ✅ | 41k+ ✅ |
| IR receiver, 38 kHz | IRM-H638T/TR2 C91447 | 0.27 | 0.17 | +$0.69 | **+$0.22** | $25.08 | $4.98 ✅ (barely) | 143k ✅ |
| Speaker (magnetic transducer + NPN driver) | MLT-8530 C94599 | 0.24 | 0.17 | +$1.38 | **+$0.22** | $25.78 | $4.99 ✅ (barely) | 67k ✅ |
| *Alt IMU: accelerometer only* | *SC7A20HTR C19274408* | *0.30* | *0.18* | *+$0.74* | *+$0.25* | *$25.13* | *$5.01 ❌* | *104k ✅* |
| **2× 7-seg variant A**: digits built from 16× 0603 LEDs + TM1650 | C2286 ×16 + TM1650 C53198565 | 0.23 | 0.13 | +$0.73 | **+$0.26** | $25.13 | $5.02 ❌ (by 2¢) | 2.6M / 11k ✅ |
| Microphone, **PDM** (not I2S, see below) | MSM261DDB020 C27636198 | 0.66 | 0.37 | +$1.16 | **+$0.46** | $25.55 | $5.22 ❌ | 6,116 ⚠ (10×) |
| **2× 7-seg variant B**: digits built from 16× 0603 LEDs + HT16K33 + I2C level shifter | C2286 ×16 + HT16K33A C5444733 + BSS138 ×2 | 0.71 | 0.41 | +$1.69 | **+$0.62** | $26.09 | $5.38 ❌ | HT16K33 2,440 ⚠ (4.1×) |
| 2× 7-segment digits, SMD 0.2″ + TM1650 | GS2011CR-G ×2 + TM1650 | 0.89 | 0.61 | +$1.85 | **+$0.80** | $26.24 | $5.56 ❌ | digits 5,920 ⚠ (4.9×) |
| IMU, 6-axis accel + gyro | LSM6DS3TR-C C967633 | 1.55 | 1.01 | +$2.23 | **+$1.24** | $26.62 | $6.00 ❌ | 22.7k ✅ |
| OLED 0.96″ 128×64, I2C | HS96L03W2C03 C5248080 | 2.36 | 1.47 | +$4.06 | **+$1.83** | $28.45 | $6.59 ❌ | 3,149 ⚠ (5.2×) |
| *Microphone, true I2S* | *ICS-43434 C5656610* | *4.57* | *3.18* | *+$5.76* | *+$3.77* | *$30.16* | *$8.53 ❌* | *992 ❌* |

**Parts $/bd** is the cost of the add-on's own parts per board, before
joints, fees and VAT. It covers every part the add-on needs, including the
I2C pull-ups and decoupling caps.

At 5 boards the deltas are much larger, mainly because each new part type
costs $1.53 per order: $0.31/board at 5 boards against $0.003 at 600. The
through-hole OLED also pays JLC's $3.50 hand-solder fee, which is $0.70/board
at 5 boards. The $5 target applies only to the 600-board order.

### What fits under $5

B2 has only **$0.24** of headroom, so at most **one** of these fits:

- audio jack, $4.87
- IR receiver, $4.98
- speaker, $4.99
- alkaline battery power path, connector only, $4.87. With a bagged
  battery holder it comes to ≈ $5.17–5.40 ❌ (see item 8).

Any two of them go over: jack + IR is $5.08. Everything else breaks $5 on
its own. The 0603-LED 7-segment (variant A) misses by 2¢.

Ways to make room, if you want more than one add-on:

- **Drop the 4 WS2812B** (−$0.33). That alone would admit 7-seg variant A
  ($4.69) or the PDM mic ($4.89).
- **Recover VAT.** Ex-VAT, B2 is $4.09, which leaves $0.91 of headroom
  for add-ons (each costs about 15% less ex-VAT).
- **Get the real JLC quote first.** Shipping ($1.00/board) and PCB fab are
  still estimates, and they decide whether any of this fits.

Everything at once (OLED + 7-seg SMD + IR + jack + IMU + PDM mic + speaker)
comes to **≈ $9.80/board**, including the move to a 47×47 mm board.

### Part details

**1. OLED: HS96L03W2C03 (C5248080), $1.4612 @ 500+ (single: $2.3526)**
- A complete module, not a bare glass panel: 27.3×27.8 mm PCB, SSD1315
  controller, internal DC/DC, 4 pins (GND, VCC, SCL, SDA), 2.8–3.3 V. It
  needs no charge-pump passives, but it is through-hole, so JLC hand-solders
  it (4 joints + $3.50/order).
- It can sit over SMD parts like a shield, so it adds less board area than
  its size suggests. It is still the largest item here.
- The 0.91″ 128×32 HS91L02W2C01 (C5248081) costs the same, $1.4874 @ 500+ (single: $2.3526).
- **Cheap alternative, $0:** a 4-pin I2C footprint (GND/VCC/SCL/SDA) left
  unpopulated, in the standard SSD1306 breakout pinout. Players plug in their
  own module, which costs about $1.50–2 retail. This fits the hardware-hacking
  theme, but the board has no display out of the box.

**2. Two 7-segment digits + TM1650 (C22462630 ×2, C53198565): +$1.85 at 5 boards, +$0.80 at 600**
- GS2011CR-G: 0.2″ SMD single digit, common cathode, red, $0.2678 each @ 500+ (single: $0.4945).
  The two digits are 90% of the cost.
- The TM1650 ($0.0597 @ 500+, single: $0.0951) drives up to 4 digits over a 2-wire I2C-like bus. It
  runs at 3–5.5 V; run it from 3V3 so its logic levels match the RP2040. It
  needs no segment resistors (current is set in a register) and 1× 100 nF.
- The TM1650 answers on fixed addresses 0x24–0x27 and 0x34–0x37. Those don't
  clash with the OLED (0x3C) or the IMU (0x6A), so all three can share one bus.
- ⚠ Digit stock is 5,920, only 4.9× the 1,200 needed. Second-source before ordering.

**2a. 7-seg variant A: 0603-LED digits + TM1650: +$0.73 at 5 boards, +$0.26 at 600**

| Ref | LCSC | Part | Qty/bd | Joints | Unit $ @1 | Ext $/bd, 5 bds | Unit $ @600 (tier) | Ext $/bd @600 | Lib |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| D10–D25 | C2286 | KT-0603R red LED, already on the BOM, so no new part type | 16 | 32 | 0.0076 | 0.1216 | 0.0040 @ 8,000+ | 0.0640 | basic |
| U5 | C53198565 | TM1650 4-digit LED driver, 2-wire bus | 1 | 16 | 0.0951 | 0.0951 | 0.0597 @ 500+ | 0.0597 | ext |
| C | C60474 | 100 nF decoupling | 1 | 2 | 0.0048 | 0.0048 | 0.0030 | 0.0030 | ext |
| R | C25744 | 10 kΩ bus pull-ups (shared with any other I2C add-on) | 2 | 4 | 0.0034 | 0.0068 | 0.0027 | 0.0054 | basic |
|  |  | **1 new part type** |  | **54** |  | **$0.2283** |  | **$0.1321** |  |

- 5 boards: Δ = ($0.2283 parts + 54 × $0.0016 joints + $1.53/5 type fee) × 1.18 = **$0.73/board**
- 600 boards: Δ = ($0.1321 parts + 54 × $0.0016 joints + $1.53/600 type fee) × 1.18 = **$0.26/board**

- Each digit is 8 LEDs (7 segments + DP) placed in the segment shape, with
  the outline on the silkscreen. With one LED per segment the segments look
  dotted but read clearly. Two LEDs per segment (32 LEDs) looks closer to a
  real digit. It costs **$0.94 at 5 boards and $0.40 at 600**, which is
  $0.21 and $0.14 more than one LED per segment.
- The TM1650 sources segment current itself (brightness is set in a
  register), so the LEDs need no series resistors. Wire it common cathode:
  SEG pins → LED anodes, DIG1/DIG2 → cathodes. Run it from 3V3.
- No stock risk. C2286 has 2.6M in stock, the TM1650 11k, and the 10,800
  LEDs/order (18–21 per board in total) price at the 8,000+ tier.
- Footprint: two digits of 0603s come to roughly 8×12 mm each, a little
  larger than the 0.2″ SMD digits.
- CTF fit: players can sniff the TM1650's 2-wire bus with a logic analyser.
  Its 4 spare digit outputs and key-scan inputs are free for other puzzles.

**2b. 7-seg variant B: 0603-LED digits + HT16K33 + I2C level shifter: +$1.69 at 5 boards, +$0.62 at 600**

| Ref | LCSC | Part | Qty/bd | Joints | Unit $ @1 | Ext $/bd, 5 bds | Unit $ @600 (tier) | Ext $/bd @600 | Lib |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| D10–D25 | C2286 | KT-0603R red LED, already on the BOM | 16 | 32 | 0.0076 | 0.1216 | 0.0040 @ 8,000+ | 0.0640 | basic |
| U5 | C5444733 | HT16K33A-20SOP, 8×8 LED matrix driver + key scan, I2C | 1 | 20 | 0.5305 | 0.5305 | 0.3004 @ 494+ | 0.3004 | ext |
| Q1, Q2 | C78284 | BSS138 N-MOSFET, 3.3 V ↔ 5 V I2C level shift | 2 | 6 | 0.0219 | 0.0438 | 0.0149 @ 600+ | 0.0298 | ext |
| C | C60474 | 100 nF decoupling | 1 | 2 | 0.0048 | 0.0048 | 0.0030 | 0.0030 | ext |
| R | C25744 | 10 kΩ pull-ups: 2 on the 3V3 side (shared bus), 2 on the 5 V side | 4 | 8 | 0.0034 | 0.0136 | 0.0027 | 0.0108 | basic |
|  |  | **2 new part types** |  | **68** |  | **$0.7143** |  | **$0.4080** |  |

- 5 boards: Δ = ($0.7143 + 68 × $0.0016 + 2 × $1.53/5) × 1.18 = **$1.69/board**
- 600 boards: Δ = ($0.4080 + 68 × $0.0016 + 2 × $1.53/600) × 1.18 = **$0.62/board**

- **The HT16K33 needs 5 V.** Its datasheet specifies 4.5–5.5 V supply, and
  0.7 × VDD (3.5 V) input-high on SDA/SCL. Power it from VBUS. The RP2040's
  3.3 V I2C needs the standard 2-MOSFET bidirectional level shifter (BSS138
  with pull-ups on both sides), because the RP2040 isn't 5 V tolerant. Only
  the HT16K33 sits on the 5 V side, so the OLED, IMU and TM1650 stay on 3V3.
- Its row outputs source about 25 mA, so the LEDs need no series resistors.
  It defaults to address 0x70, which doesn't clash with any other add-on.
- **More capacity than two digits need.** The 20-pin part drives 8×8 = 64
  LEDs; two digits use 16. The other 48 could make an 8×6 dot-matrix area of
  0603 LEDs at about $0.0085 per LED including joints and VAT. That is the main reason
  to choose it over the TM1650. The 28-pin SSOP (C5444738, $0.3439 @ 500+, single $0.594, 6,653 in
  stock) drives 16×8 = 128 LEDs and scans 39 keys.
- Libraries: well supported, with Adafruit LED backpack drivers available
  for most platforms.
- ⚠ **Stock: SOP-20 has 2,440 (4.1× cover).** Second-source with the SSOP-28,
  which costs about $0.05/board more and needs a different footprint, so pick
  one at layout time.
- It costs $0.96/board more than variant A at 5 boards, and $0.36 more at 600. Choose it only for the extra LED
  capacity or the library support.

**3. IR receiver: IRM-H638T/TR2 (C91447), $0.1698 @ 150+ (single: $0.2611)**
- SMD 5×4 mm, 38 kHz, 2.7–5.5 V, so it runs from 3V3. Needs 1× 100 nF
  decoupling and 1 GPIO.
- A good CTF fit: players replay or decode NEC remote codes.

**4. 3.5 mm audio jack: PJ-320D (C431535), $0.037 @ 300+ (single: $0.0536)**
- SMD, about 5 pads.
- Output is RP2040 PWM through 1 kΩ + 10 nF (16 kHz low-pass), then a 10 µF
  DC block to tip and ring. New part types: the jack and the 10 nF (C15195,
  basic). The 1 kΩ and 10 µF are already on the BOM.
- Can carry SSTV, Morse, or a data-over-audio flag. It can share its GPIO
  with the speaker.

**5. IMU: LSM6DS3TR-C (C967633), $0.9986 @ 500+ (single: $1.5307)**
- ST 6-axis IMU, LGA-14 2.5×3 mm, I2C. Needs 2× 100 nF. JLC lists it as
  Standard-only, which is fine since B2 is on Standard.
- Cheaper 6-axis parts are thin or more expensive: QMI8658B is $1.49 with
  2,660 in stock, QMI8658A $2.19, BMI270 $2.63.
- **The accelerometer-only SC7A20HTR (C19274408, $0.1718 @ 500+, single $0.2871) is about 1/5 the
  delta.** For tilt, shake or tap puzzles it is enough.

**6. Microphone: PDM instead of I2S**
- **No viable I2S mic exists in JLC/LCSC stock.**
  - ICS-43434, the real I2S part: $3.18 @ 500+ (single $4.56), only **992 in stock**.
  - GSA3526 I2S: **95 in stock**.
  - MMICT390200012 (T3902): its LCSC listing doesn't say I2S, but its
    datasheet says **PDM**.
- **Recommended: MSM261DDB020 (C27636198), PDM, $0.3697 @ 500+ (single: $0.6555).**
  - 1.6–3.6 V, needs 1× 100 nF, L/R pin tied to GND.
  - Uses 2 GPIO (CLK, DATA). The RP2040 reads PDM through PIO, and an
    existing library for this is pico-microphone.
- ⚠ Stock is 6,116, 10× cover. Fine, but watch it.

**7. Speaker: MLT-8530 (C94599) + S8050 (C2146) + 1N4148W (C81598): +$1.38 at 5 boards, +$0.22 at 600**
- 8.5×8.5 mm SMD **magnetic transducer**, 2.7 kHz resonance, 80 dB, 2.5–4.5 V.
  Driven by an NPN low-side switch with a 1 kΩ base resistor and a flyback
  diode. Plays tones, melodies and crude PWM audio.
- A real 8 Ω speaker is not worth it here. It would need a class-D amp, and
  the 8 Ω speakers JLC lists are wired or through-hole with stock in the tens
  to hundreds. That would add about $1+.
- Power it from 3V3. It draws about 95 mA when on, and less at PWM duty. That
  fits in the 300 mA LDO alongside the rest, but don't add the OLED, 7-seg and
  speaker together without checking the rail.

**8. Alkaline battery power (3×AAA) with USB/battery protection: +$1.21 at 5 boards, +$0.11 at 600**

Why 3×AAA: the pack runs from about 4.8 V fresh down to about 3.0 V flat.
That stays inside the ME6206's 6 V input limit and the WS2812B-V6's
3.3–5.3 V supply range, so no new regulator is needed.

- **2×AA/AAA** falls below the flash's 2.7 V minimum and the WS2812's 3.3 V
  minimum. It would need a boost converter.
- **4×AA (6.4 V fresh) and 9 V** exceed the LDO's input limit.

Circuit: a P-MOSFET switches the battery in, and a Schottky diode feeds VSYS from USB.

```
VBUS ──|>|── VSYS ──► ME6206 LDO → 3V3
     D6 B5819W  ▲     └► LED1–LED4 WS2812 chain (moved from VBUS to VSYS)
                │
BAT+ (J3) ── Q1 PMOS (D = battery, S = VSYS)
               G ── VBUS, and R10 10 kΩ to GND
```

| Case | Behaviour |
|---|---|
| Battery only | R10 pulls the gate to GND, so Q1 is fully on. The drop is a few mV. |
| USB only | Power flows through D6, giving VSYS ≈ 4.65 V. R10 draws 0.5 mA from VBUS. |
| Both connected | VBUS holds Q1 off, so the board runs from USB. D6 stops the battery from back-feeding the USB host. |
| Battery reversed | Q1 stays off and its body diode is reverse-biased, so the board is protected. |

| Ref | LCSC | Part | Qty/bd | Joints | Unit $ @1 | Ext $/bd, 5 bds | Unit $ @600 (tier) | Ext $/bd @600 | Lib | Stock |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- | ---: |
| Q1 | C22469449 | HL3401 P-MOSFET, 30 V, 4.4 A, Vth 0.9 V, SOT-23 | 1 | 3 | 0.0280 | 0.0280 | 0.0230 @ 300+ | 0.0230 | ext | 78,420 |
| D6 | C7420330 | B5819W Schottky, 40 V, 1 A, SOD-123 | 1 | 2 | 0.0174 | 0.0174 | 0.0142 @ 500+ | 0.0142 | ext | 1,075,550 |
| R10 | C25744 | 10 kΩ gate pulldown, already on the BOM | 1 | 2 | 0.0034 | 0.0034 | 0.0027 | 0.0027 | basic | 3,766,700 |
| J3 | C722761 | JST-PH 2.0 mm 2-pin SMD vertical: battery input | 1 | 4 | 0.0404 | 0.0404 | 0.0254 @ 300+ | 0.0254 | ext | 60,380 |
|  |  | **3 new part types** |  | **11** |  | **$0.0892** |  | **$0.0653** |  |  |

- 5 boards: Δ = ($0.0892 + 11 × $0.0016 + 3 × $1.53/5) × 1.18 = **$1.21/board**
- 600 boards: Δ = ($0.0653 + 11 × $0.0016 + 3 × $1.53/600) × 1.18 = **$0.11/board**

| Variant | Δ $/bd, 5 bds | Δ $/bd, 600 | B2 total, 5 bds | B2 total, 600 |
|---|---:|---:|---:|---:|
| Power path + JST-PH connector | +$1.21 | +$0.11 | $25.60 | **$4.87 ✅** |
| + SW5 on-board power switch, MSK12C02 SPDT slide (C431540, $0.0414 @ 300+, single $0.0571, 7 joints, 180k stock) | +$1.65 | +$0.17 | $26.04 | $4.93 ✅ |
| AO3401A (C15127, JLC basic, a known brand, $0.0644 @ 500+, single $0.1026) in place of HL3401 | +$0.09 more | +$0.05 more | — | — |
| + bagged wired 3×AAA holder with switch and PH plug, **estimate**: $0.50–1.00 each for 5, $0.25–0.45 each for 600 | +$1.80 to +$2.39 | +$0.41 to +$0.64 | ≈ $26.19–26.78 | **≈ $5.17–5.40 ❌** |

- **Why a MOSFET and not a second Schottky?** A diode's 0.3–0.4 V drop on
  the battery side would cut the board off at about 1.2 V per cell, which
  wastes roughly half of an alkaline cell's capacity. With Q1, the 3V3 rail
  holds until the pack reaches about 3.5 V. Below that, the LDO is in dropout and
  passes the pack voltage through, so the board runs down to about 3.0 V.
- **Moving the WS2812 chain to VSYS:** this lets the RGB LEDs run from the
  battery. On USB they then see about 4.65 V instead of up to 5.25 V, which
  gives more margin under their 5.3 V maximum. Wire Q1's gate to the
  **connector side of VBUS**, before D6.
- **Battery holder: not available through JLC.**
  - LCSC has only single-cell AAA holders, so each board needs three.
  - Stock is in the hundreds against the 1,800 needed. The cheapest is
    BH-AAA-A1AJ001, C5290189: $0.196 @ 500+ (single $0.347), 545 in stock.
  - They are through-hole, so JLC would hand-solder them.
  - Three side by side are wider than the board.

  The practical route is a wired 3×AAA box with a switch and a JST-PH
  plug, bagged with each board. The price above is an unverified bulk
  estimate, and the holders may raise the $600 shipping estimate. Cells
  are extra: roughly $0.30–0.60 for three alkaline AAAs.
- **Staying under $5 with a holder:** drop the 4 WS2812B (−$0.33), or
  recover VAT (ex-VAT, B2 plus power path plus holder ≈ $4.43–4.63).
- **Power switch:** SW5 is only needed if the holder has no switch. At
  about 25 mA idle, the RP2040 drains a pack in under two days.
- **Battery life:** about 1,000 mAh (AAA alkaline) gives **≈ 40 h** at
  ~25 mA with the RGB LEDs off, but only **≈ 5 h** with all four at full
  white (~170 mA in total). Keep RGB brightness low on battery.
- **Board space:** J3 (8×5.4 mm), one SOT-23 and one SOD-123. The 30×46 mm
  board is already full, so this may force the 47×47 mm move (+$0.19, not
  included above).
- **GPIO:** none required. Optionally, add a VBUS-sense divider to a spare
  GPIO so firmware knows it's on battery.
- Sources: LCSC `productPriceList` for C22469449, C7420330, C722761,
  C431540, C15127 and C5290189 (2026-10-06).

### GPIO cost of each add-on

| Add-on | GPIO |
|---|---|
| I2C bus (OLED, TM1650 or HT16K33, IMU share it) | 2 |
| IR receiver | 1 |
| Audio jack PWM (shareable with speaker) | 1 |
| Speaker | 1 (or 0 if shared with the jack) |
| PDM mic | 2 |
| Battery power | 0 (1 for optional VBUS sense) |

On B2 these come out of the 19 header GPIO (GPIO11–29), and
using every add-on takes 7–8 of them.

Sources: LCSC `productPriceList` for every part above (2026-10-06).
Datasheets via LCSC: HS96L03W2C03 (4-pin I2C module, internal DC/DC),
T3902/MMICT390200012 (PDM), MSM261DDB020 (PDM, 1.6–3.6 V), TM1650. JLC THT
fee as above.
