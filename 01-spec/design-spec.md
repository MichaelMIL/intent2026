# Intent 2026 PCB — Design Specification (rev 0.3, 2026-10-08)

**rev 0.5 (2026-10-11):** the IR receiver, the audio jack and a new speaker are **breakaway soda-can modules** (13 × 22 mm) under the pedestal (56 × 124 mm blank; the top of the badge is a header sign box holding the lanyard holes, the cabinet stands on two feet, logo/marquee/key letters are exposed copper — BUILD-NOTES items 12–13), each with a 1×3 header that plugs into a socket on the main board. See §3.11 and `00-bom/bom-deltas.md` rev 0.5.

**rev 0.3:** board **56 × 100 mm** vending-machine outline, **two** lanyard holes, INTENT logo (white silk) + summit tagline on the front, team names + QR reserve on the back, add-ons: audio jack, IR receiver, 3×AAA battery power path. Power switch: on the battery box; SW5 pads kept on the board, DNP.

Source BOM: `00-bom/BOM-B2.md` (variant B2). Recommended BOM changes are in `00-bom/bom-deltas.md`
and are **assumed applied** in this spec (marked Δ).

## 1. Board

| Item | Value |
|---|---|
| Size | **56 × 100 mm** bounding box, portrait. Outline = vending-machine silhouette (see §1.1). 2-up on a 100 × 120 panel for the 600 run |
| Layers | 2 (F.Cu / B.Cu) |
| Thickness | 1.6 mm |
| Copper | 1 oz |
| Solder mask | **Purple** |
| Silkscreen | White |
| Surface finish | HASL lead-free (default). ENIG optional if the 0.4 mm pitch RP2040 gives paste problems — JLC assembles RP2040 on HASL routinely |
| Min track / space | 0.15 / 0.15 mm (RP2040 fan-out), 0.2 mm elsewhere |
| Min via | 0.3 mm drill / 0.6 mm pad |
| Corners | 3 mm radius on body, 2 mm on pedestal |
| Lanyard | **H1, H2: Ø 4.0 mm plated holes** at (12, 5.5) and (44, 5.5) in the header sign box (rev 0.5 outline rework; was (10, 6) / (46, 6)). Either one takes a single lanyard clip; both take a strap. 1.5 mm copper-free ring, no parts within 3 mm |
| Panel (600 run) | single boards or 2-up (160 × 140) — JLC decides; irregular outline → tab-routed, not V-score |

### 1.1 Outline (edge cuts)
```
        ┌────────────┐ ← header sign box x 7–49 × y 0–9 with the two lanyard holes (rev 0.5 rework; was a R 6 rounded top)
        │ INTENT logo│   y 8–25   white silk logo + "2026 · THE SECURITY SUMMIT FOR RESEARCHERS / BY RESEARCHERS"
        │  WINDOW    │   y 26–60  RGB shelf, RP2040 "prize", BOOTSEL "service key"
        │ CREDIT ■■■ │   y 62–79  5 LEDs + keypad A/B/C
        │ ▯▯▯    ◻   │   y 80–90  three expansion slots J5–J7 (IR, AUDIO, SPK), USB-C (right edge), power path
        └──┐      ┌──┘
           │ FOOT │     y 90–100, x 8–48 (pedestal 40 mm wide)
           └─┬──┬──┬┘
         ┌───┴┐┌─┴──┐┌┴───┐   y 102–124  breakaway cans IR | AUDIO | SPK, 13 × 22 mm (4 mm tabs at x 12/28/44, mouse bites at y 100)
         └────┘└────┘└────┘
```
Full width 56 mm from y 0 to 90; pedestal 40 mm wide for the last 10 mm. rev 0.5: three 13 × 22 mm soda-can modules hang 2 mm below the pedestal on 4 mm tabs (blank 56 × 124 mm); after snapping them off the badge is the 56 × 100 mm silhouette again. Battery box (wired 3×AAA with switch, ≈ 50 × 36 × 14 mm) taped on the **back**, cells along the long axis, x 10–46, y 26–76 — clear of J2's through-hole pins (x < 8).

## 2. Power tree

```
USB-C J1 VBUS ──┬── D6 B5819W ──┐
                │  (Schottky)   │
                └── Q1 gate     ├── VSYS ──┬── C9 10 µF ── U3 ME6206A33 ── 3V3 ──┬── C20 1 µF
                    R10 10k→GND │          │                                    ├── RP2040 IOVDD ×6, USB_VDD, ADC_AVDD, VREG_VIN
J3 BAT+ (3×AAA) ── [SW5] ── Q1 HL3401 PMOS ─┘          ├── 5V_RGB → LED1..4 (C13..16)    ├── U2 flash, R3/R4, J2 3V3, slots J5–J7 pin 2 (IR module ≈ 1 mA, speaker module ≤ 95 mA when sounding)
                   (D→S)                               └── R15/R16 10k+10k → VBUS_SENSE → GPIO29/ADC3 (from VBUS, before D6)

RP2040 VREG_VOUT (1.1 V) ── C10 1 µF ── DVDD ×2
```

- VSYS = 4.65 V on USB, 3.0–4.8 V on battery. LDO, RGB chain and everything else hang off VSYS.
- Both present: VBUS holds Q1 off → runs on USB, D6 blocks back-feed into the host. Battery reversed: Q1 body diode reverse-biased → safe.
- VBUS and VSYS are **not** on J2.
- VBUS_SENSE lets firmware know it is on battery (dim RGB, sleep). 10k/10k from VBUS → 2.5 V at the ADC pin. Uses GPIO29.
- Power switch is on the battery box (cheaper: a wired 3×AAA box with switch costs about the same as one without, while SW5 on-board is ≈ +$0.17/board incl. VAT at 600). SW5 footprint stays on the back, DNP, bridged by a 0 Ω/solder jumper so a box without a switch still works.
- Budget on 3V3: RP2040 ≈ 50 mA, flash 10 mA, IR module 1 mA, speaker module ≤ 95 mA (pulsed), red LEDs 10 mA, header ≤ 100 mA → OK on 300 mA. RGB chain ≤ 144 mA on VSYS. Battery life ≈ 40 h RGB-off, ≈ 5 h full white.

## 3. Net list (schematic in text)

Reference designators follow BOM-B2. Δ = added/changed by `bom-deltas.md`.

### 3.1 USB-C (J1, TYPE-C-16PIN, USB 2.0 only)

| J1 pin | Net | Notes |
|---|---|---|
| A4,A9,B4,B9 VBUS | VBUS | |
| A1,A12,B1,B12 GND, shell | GND | |
| A5 CC1 | CC1 → R1 5.1 kΩ → GND | UFP (device) pull-down |
| B5 CC2 | CC2 → R2 5.1 kΩ → GND | |
| A6/B6 D+ | USB_DP_CONN | both D+ pins tied together |
| A7/B7 D− | USB_DM_CONN | both D− pins tied together |
| A8/B8 SBU | NC | |

ESD: U4 USBLC6-2SC6 — pin 1 I/O1 = USB_DP_CONN, pin 3 I/O2 = USB_DM_CONN, pin 5 VBUS, pin 2 GND, pins 4/6 are the pass-through of 1/3 (use them for the MCU side or leave NC).
Then **R11, R12 27 Ω (Δ)** in series: USB_DP_CONN → R11 → USB_DP → RP2040 pin 47; USB_DM_CONN → R12 → USB_DM → pin 46.
(27 Ω series resistors are required by the Raspberry Pi RP2040 hardware design guide; BOM-B2 omits them.)

### 3.2 RP2040 (U1, LQFN-56)

| Pin | Name | Net |
|---|---|---|
| 1, 10, 22, 33, 42, 49 | IOVDD | 3V3 — 100 nF at each pin (C1..C5 + 1 Δ) |
| 23, 50 | DVDD | 1V1 — C10 1 µF near pin 50, 100 nF near pin 23 (Δ) |
| 44 | VREG_VIN | 3V3 — 100 nF |
| 45 | VREG_VOUT | 1V1 |
| 48 | USB_VDD | 3V3 — 100 nF |
| 43 | ADC_AVDD | 3V3 — 100 nF (optionally through a ferrite/0 Ω later; not in BOM) |
| 57 | GND pad | GND — ≥ 9 thermal vias to B.Cu ground |
| 19 | TESTEN | GND |
| 20 | XIN | Y1 pin 1 (+ C11 15 pF to GND) |
| 21 | XOUT | **R13 1 kΩ (Δ)** → Y1 pin 3 (+ C12 15 pF to GND) |
| 24 | SWCLK | J2 |
| 25 | SWDIO | J2 |
| 26 | RUN | R4 10 kΩ → 3V3; also J2 |
| 46 | USB_DM | via R12 |
| 47 | USB_DP | via R11 |
| 51 | QSPI_SD3 | U2 pin 7 (/HOLD / IO3) |
| 52 | QSPI_SCLK | U2 pin 6 (CLK) |
| 53 | QSPI_SD0 | U2 pin 5 (DI / IO0) |
| 54 | QSPI_SD2 | U2 pin 3 (/WP / IO2) |
| 55 | QSPI_SD1 | U2 pin 2 (DO / IO1) |
| 56 | QSPI_SS | U2 pin 1 (/CS); R3 10 kΩ → 3V3; SW1 BOOTSEL → **R14 1 kΩ (Δ)** → GND |

Crystal Y1 12 MHz, SMD3225: pins 2 and 4 = GND.
Flash U2 W25Q16JV: pin 8 VCC = 3V3 with 100 nF (C6), pin 4 GND.

### 3.3 GPIO map

| GPIO | Pin | Net / function |
|---|---|---|
| 0 | 2 | UART0_TX → TP1 |
| 1 | 3 | UART0_RX → TP2 |
| 2 | 4 | SW4 "C" → GND (internal pull-up) — rev 0.4: swapped with GPIO4 for layout |
| 3 | 5 | SW3 → GND |
| 4 | 6 | SW2 "A" → GND |
| 5 | 7 | R5 1 kΩ → D1 anode; D1 cathode → GND |
| 6 | 8 | R6 → D2 |
| 7 | 9 | R7 → D3 |
| 8 | 11 | R8 → D4 |
| 9 | 12 | R9 → D5 |
| 10 | 13 | RGB_DIN → LED1 DIN (optional 33–100 Ω series pad, DNP, Δ) |
| 11 | 14 | AUDIO_PWM → J6 pin 3 (AUDIO slot). On the audio module: R17 1 kΩ → C21 10 nF → GND; → C22 10 µF → J4 tip + ring (see §3.7, §3.11) |
| 12–15 | 15–18 | J2 (SPI1) |
| 16–21 | 27–32 | J2 (I2C0 on 16/17, UART1 on 20/21) |
| 22 | 34 | IR_OUT ← J5 pin 3 (IR slot; U5 IRM-H638T on the IR module, see §3.8, §3.11) |
| 23, 24 | 35, 36 | J2 |
| 25 | 37 | SPK_PWM → J7 pin 3 (SPK slot, speaker module); also J2 pin 15 |
| 26–28 | 38–40 | J2 (ADC0–2) |
| 29 | 41 | VBUS_SENSE (ADC3) ← R15/R16 divider |

TP3 = GND pad next to TP1/TP2.

### 3.4 RGB chain (LED1–LED4, WS2812B-2020-V6)

Pinout (2020-4P): 1 DOUT, 2 GND, 3 DIN, 4 VDD (verify against the LCSC datasheet before layout — some reels differ).
VDD = 5V_RGB = VSYS (after D6/Q1, so the LEDs run on battery too; ≈ 4.65 V on USB), 100 nF (C13–C16) at each VDD pin.
GPIO10 → LED1 DIN; LED1 DOUT → LED2 DIN → LED3 → LED4; LED4 DOUT → RGB_DOUT → J2.

### 3.5 J2 header (2×13, 2.54 mm, THT, DNP)

Pin 1 is top-left (square pad), odd pins left column, even pins right column, numbered top to bottom.

| Pin | Net | Pin | Net |
|---|---|---|---|
| 1 | 3V3 | 2 | GND |
| 3 | GPIO12 (SPI1 RX) | 4 | GPIO13 (SPI1 CSn) |
| 5 | GPIO14 (SPI1 SCK) | 6 | GPIO15 (SPI1 TX) |
| 7 | GPIO16 (I2C0 SDA) | 8 | GPIO17 (I2C0 SCL) |
| 9 | GPIO18 | 10 | GPIO19 |
| 11 | GPIO20 (UART1 TX) | 12 | GPIO21 (UART1 RX) |
| 13 | GPIO23 | 14 | GPIO24 |
| 15 | SPK_PWM (GPIO25, shared with the SPK slot) | 16 | GPIO26 (ADC0) |
| 17 | GPIO27 (ADC1) | 18 | GPIO28 (ADC2) |
| 19 | RGB_DOUT | 20 | GND |
| 21 | SWCLK | 22 | SWDIO |
| 23 | RUN | 24 | GND |
| 25 | GND | 26 | GND |

15 free GPIO (GPIO11, 22, 25, 29 are taken by the AUDIO slot, IR slot, SPK slot and VBUS sense; GPIO25 is still on the header as SPK_PWM).

Power pins at the ends, GND on both ends: a player who plugs a ribbon in backwards shorts 3V3-to-GND at worst (LDO current-limits), never 5 V onto a GPIO.

### 3.6 Switches

SW1–SW4: TS-1187A (5.1 × 5.1 mm, 4 pads; pads 1-2 and 3-4 are internally paired — wire across the diagonal).
SW1 = BOOTSEL (QSPI_SS via R14 1 kΩ to GND). SW2–SW4 = user, direct to GND.

### 3.7 Audio jack (J4, PJ-320D, 3.5 mm TRRS) — on the AUDIO module (rev 0.5)

rev 0.5: J4, R17, C21, C22 sit on the audio breakaway module (nets AUM_PWM, AUM_FILT, AUM_OUT, AUM_GND). The module header P2 carries 1 = GND, 2 = n.c., 3 = PWM and mates with J6. The circuit below is unchanged.

GPIO11 (PWM, ≥ 100 kHz carrier) → R17 1 kΩ → node A; C21 10 nF node A → GND (fc ≈ 16 kHz); C22 10 µF node A → J4 tip **and** ring1 (mono on both ears); J4 sleeve and ring2 → GND. Detect-switch pads: NC.
Output into 32 Ω headphones is ≈ 0.1 Vpp (3.3 V PWM behind the 1 kΩ source: 3.3 × 32/1032), a moderate listening level; the 10 µF block gives a 500 Hz high-pass into 32 Ω. (rev 0.4 correction: an earlier draft claimed ≈ 1 Vpp.) R18 series pad was not added in the KiCad stage.

### 3.8 IR receiver (U5, IRM-H638T/TR2, 38 kHz) — on the IR module (rev 0.5)

rev 0.5: U5, R19, C23, C24 sit on the IR breakaway module (nets IRM_3V3, IRM_VCC, IRM_OUT, IRM_GND). P1: 1 = GND, 2 = 3V3, 3 = OUT, mates with J5. Plugged in, the module stands upright, so the lens looks sideways.

**rev 0.4 correction — real pinout (LCSC/EasyEDA + KiCad agree): pin 1, 2 = GND, pin 3 = OUT → GPIO22, pin 4 = VCC.** Old text: Pin 1 OUT → GPIO22 (open-collector output with internal pull-up; active low). Pin 2 GND. Pin 3 VCC = 3V3 through R19 100 Ω with C23 100 nF + C24 10 µF at the pin (datasheet RC filter; 100 Ω is a new basic part type — or use 0 Ω/skip the R and keep just 100 nF + 10 µF, both on the BOM).
(rev 0.3 text: mount in the "coin area" on the front face, lens facing out. Superseded by the module.) Keep the plugged-in module ≥ 10 mm from the WS2812B LEDs (their light can blind it).

### 3.9 Battery power path

| Ref | Part | Connection |
|---|---|---|
| J3 | JST-PH 2-pin SMD vertical | pin 1 BAT+, pin 2 GND. Silk: "3×AAA  +  −" |
| SW5 | MSK12C02 slide switch (optional) | in series with BAT+ before Q1 |
| Q1 | HL3401 P-MOSFET SOT-23 | D = BAT+ (after SW5), S = VSYS, G = VBUS (connector side, before D6) |
| R10 | 10 kΩ | Q1 gate → GND |
| D6 | B5819W Schottky SOD-123 | anode VBUS, cathode VSYS |
| R15, R16 | 10 kΩ, 10 kΩ | VBUS → R15 → VBUS_SENSE → R16 → GND; VBUS_SENSE → GPIO29 |

### 3.7 Decoupling summary (after Δ)

| Cap | Where |
|---|---|
| C1–C5, C17 | 100 nF, one per RP2040 IOVDD pin (6) |
| C6 | 100 nF, U2 flash VCC |
| C7 | 100 nF, USB_VDD (pin 48) |
| C8 | 100 nF, ADC_AVDD (pin 43) |
| C18 | 100 nF, VREG_VIN (pin 44) |
| C19 | 100 nF, DVDD pin 23 |
| C10 | 1 µF, VREG_VOUT / DVDD pin 50 |
| C9 | 10 µF, VBUS at LDO input |
| C20 | 1 µF, LDO output (3V3) — ME6206 requires ≥ 1 µF out |
| C13–C16 | 100 nF, one per WS2812B |
| C23, C24 | 100 nF + 10 µF, IR receiver VCC (IR module) |
| C21 | 10 nF, audio low-pass (audio module) |
| C22 | 10 µF, audio DC block (audio module) |
| C25 | 10 µF, speaker module bulk |

100 nF total: 16 (was 12). 1 µF total: 2 (was 1). No new part types.

### 3.11 Expansion slots and breakaway modules (rev 0.5)

Three identical ports on the main board, coin area, x 4.5 / 11.5 / 18.5, y 82.5–87.5 (1×3 THT sockets, pins along y, pin 1 at the top):

| Slot | Ref | Pin 1 | Pin 2 | Pin 3 | Module |
|---|---|---|---|---|---|
| IR | J5 | GND | 3V3 | IR_OUT (GPIO22) | P1 + U5, R19, C23, C24 |
| AUDIO | J6 | GND | 3V3 | AUDIO_PWM (GPIO11) | P2 + R17, C21, C22, J4 |
| SPK | J7 | GND | 3V3 | SPK_PWM (GPIO25) | P3 + R20 1 k, R21 10 k, Q2 S8050, LS1 MLT-8530, D7 1N4148W, C25 10 µF |

Power in the middle: a module plugged in backwards swaps GND and signal; 3V3 can never land on a GPIO. The slots are not keyed, so the firmware treats each slot as its fixed function.

Speaker module: GPIO25 → R20 1 kΩ → Q2 base (R21 10 kΩ to ground keeps it off while the pin floats at reset); Q2 emitter → ground; collector → LS1 (−); LS1 (+) → 3V3; D7 cathode to 3V3, anode to the collector (flyback); C25 across 3V3/ground. Drive with a 2.7 kHz square wave at 50 % duty (resonance); ≤ 95 mA pulsed from the 3V3 LDO.

Mechanics: the three modules (soda cans 13 × 22 mm, R 2.2 corners) hang 2 mm under the pedestal at y 102–124 on 4 mm wide tabs with four 0.5 mm mouse-bite holes (1.0 mm pitch) on the pedestal edge line, so the badge edge stays clean and the stub remains on the module. No copper crosses a tab: every module has its own ground net and pour. Since 2026-10-29 the module SAO headers (P1–P3) are SMD on the can backs, so a module plugs in face-up and lies flat over the badge, about 7.5 mm above it, with its body extending up from the socket (BUILD-NOTES item 23).

### 3.8 Removed from BOM-B2

- **L1 (3.3 µH)** — the RP2040 has an internal *linear* 1.1 V regulator and needs no inductor. The inductor belongs to the RP2350. Dropping L1 also removes the only low-stock part (1,900 units). See `bom-deltas.md`.

## 4. Fab / assembly notes for JLCPCB

- Order: PCB + Standard PCBA, top side only. All SMD except the six 1×3 headers (J5–J7, P1–P3), which JLC hand-solders ($3.50/order + $0.0173/joint), or leave them DNP and bag loose headers. J2 and TP1–TP3 unpopulated. The breakaway modules are part of the same board outline (tab-routed); do not panelise them separately. Battery box (wired 3×AAA with switch + PH plug) sourced separately and taped to the back.
- Irregular outline: provide Edge.Cuts with ≥ 1 mm internal radii; JLC routes it, slightly more PCB cost than a rectangle of the same bbox.
- Prototype: 10 boards (user request; JLC minimum is 5 → order 10, assemble 10).
- Silkscreen artwork (vending machine) is on F.Silkscreen only; keep 0.15 mm min line width, no silk over pads.
- Component rotations in the CPL file must be checked against JLC's part orientation for U1, U2, U3, U4, LED1–4, D1–5 — JLC's rotation convention differs from KiCad for several LCSC parts. Verify in the JLC preview before paying.

## 5. References
- Raspberry Pi, *Hardware design with RP2040* (minimal design example: 27 Ω USB series R, 1 kΩ XOUT series R, 1 µF on VREG_VOUT, 100 nF per supply pin, 12 MHz crystal with 15 pF loads).
- Worldsemi WS2812B-2020-V6 datasheet (via LCSC).
- ME6206 datasheet: 1 µF ceramic in/out minimum.

(These are from memory; I don't have search access here, so verify pin numbers against the actual datasheets before the KiCad stage — I will re-check every pin when building the symbols.)
