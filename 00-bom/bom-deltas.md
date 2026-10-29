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
in backwards swaps GND and signal and never puts 3V3 on a GPIO. Board blank grows from 56 × 100 to 56 × 124 mm (cans 13 × 22 mm).

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
| PCB blank 56 × 124 instead of 56 × 100 (+24 % area, more routing) | ≈ +$0.12 |
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

---

# rev 0.6 — review against the RP2040 hardware design guide (2026-10-17)

User review + kicad-happy run (report: `01-spec/rp2040-review-2026-10-17.md`). Applied in `design.py` and the
schematic; the PCB is **not** re-laid out yet (new footprints: J1, U3, U6, J5–J7, P1–P3; new parts C26–C29, R22,
R23, SW6). TP1–TP3 stay (user decision).

| Ref | Change | LCSC | Why |
|---|---|---|---|
| C18 | 100 nF → **1 µF** | C6119792 | guide §2.1.3: 1 µF on VREG_VIN |
| C10 | 1 µF → **100 nF** | C60474 | now only DVDD pin 50 |
| C26 | **new** 1 µF on +1V1 | C6119792 | guide §2.1.3: 1 µF on VREG_VOUT |
| Y1 | C133334 (CL 20 pF) → **Abracon ABM8-272-T3** | **C20625731** | guide §2.3.1 crystal; CL 10 pF matches the 15 pF loads + 1k. Same 3225 footprint |
| U3 | ME6206A33M3G → **AP2112K-3.3TRG1** (SOT-23-5, EN tied to VIN) | **C51118** | 600 mA instead of a 200 mA-class LDO. C23380830 is a different maker under the same MPN |
| C20 | 1 µF → **10 µF 0805** | C7503495 | LDO output bulk |
| J1 | TYPE-C-16PIN C393939 → **HRO TYPE-C-31-M-12** | **C165948** | user's proven part; stock KiCad footprint |
| C27, C28 | **new** 1 µF + 100 nF on VBUS | C6119792, C60474 | there was no VBUS capacitor (kicad-happy UC-001 / DC-002) |
| SW6 | **new** RESET button, RUN → GND | C318884 | battery users can reach BOOTSEL without unplugging |
| U6, C29 | **new** SN74LV1T34DBVR on VSYS + 100 nF | **C100024**, C60474 | RGB data buffer: DIN swings to VSYS, so VIH = 0.7·VDD is met at any VSYS (it was 3.3 V vs ≈ 3.2 V on USB) |
| J5–J7 | 1×3 socket → **2×3 socket (SAO)** | **C541853** | SAO pinout 1 3V3, 2 GND, 3 SDA, 4 SCL, 5 GPIO1, 6 GPIO2 |
| P1–P3 | 1×3 header → **2×3 header (SAO)** | **C65114** | plain header: a shrouded 2×3 is wider than the 13 mm can |
| R22, R23 | **new** 4.7 kΩ I²C pull-ups | C25900 (basic) | SAO I²C0 on GPIO12/13 |

RGB, option not taken: there is no addressable LED on LCSC/JLC rated for a 3.0–3.3 V supply. The lowest are
SK6805-EC20 (C2890036, 3.5–5.5 V, 4 in stock), WS2812B-MINI-V3 3535 (3.5 V) and the rest at 3.7 V+; the
"3 V" XL-2835/5050RGBC-KS parts are self-flashing, not addressable. So the LEDs stay on VSYS
(WS2812B-2020-V6, 944k stock) with the buffer, and firmware stops them when VSYS < ≈ 3.7 V.

Part types: −0 replaced (crystal, LDO, USB-C, socket, header) + 2 new (SN74LV1T34, 4.7 kΩ basic).
Joints: +7 SMD parts (≈ +16 joints) and THT 18 → 36 joints (2×3 instead of 1×3).
Cost @600 (LCSC single-piece, rough): crystal +$0.25, LDO +$0.12, buffer +$0.18, sockets/headers +$0.05,
caps/resistors/switch +$0.05, extra THT joints +$0.31 → **≈ +$0.95/board**. With the THT parts shipped DNP
the THT line drops out.

## rev 0.6b — SAO connectors to SMT, keyed option checked (2026-10-18)

| Ref | Was (THT) | Now (SMT) | LCSC | Stock / price (LCSC, 2026-10-18) |
|---|---|---|---|---|
| J5–J7 | PM254V-12-06-H85 C541853 | **HC-PM254-5.0H-2x3PS-02A**, 2×3 SMD socket, 5.0 mm tall | **C42163131** | 7,625 / $0.116 |
| P1–P3 | 2.54-2*3P C65114 | **PZ254-2-03-S**, 2×3 SMD pin header | **C3294461** | 14,540 / $0.080 (100+: $0.063) |

Footprints: KiCad `PinSocket_2x03_P2.54mm_Vertical_SMD` / `PinHeader_2x03_P2.54mm_Vertical_SMD` (pads splay
outward, ≈ 8 mm across the two rows). Check the land pattern against both datasheets during the PCB re-layout.
The socket is wider than the 1×3 THT one, so the 7 mm socket pitch on the main board will not hold; J5–J7 need
re-placing. Alternates: socket C41397152 (HX PM2.54-2x3P TP, 3,830), header C780054 (XKB X6521WVS-2x03H, 5,330).

Effect: no THT parts left except J2 (DNP), so JLC's hand-solder fee ($3.50/order + 36 joints ≈ $0.62/board)
goes away; the six connectors become ordinary SMT placements (≈ +$0.10/board for the parts vs THT).
Net vs rev 0.6: ≈ **−$0.5/board** at 600.

**Keyed option (checked, not applied):**
- Keyed SMT box headers exist: **BH254VS-6P C492445** (XFCN, 4,800, $0.16; 5,100+: $0.086) and HX NJ2.54-2x3P
  TP-CE C22438045 (1,150, $0.33). Body 15.27 × 8.8 mm (10.5 mm across the pads).
- There is **no board-mount keyed female** to mate with them on LCSC/JLC (the keyed mate is the IDC ribbon
  connector). A plain 2×3 socket fits inside the shroud but the cavity is ≈ 13 mm long for a 7.6 mm socket, so it
  locates nothing: no orientation key and no offset key.
- A box header would also only fit the 13 mm can turned 90°, taking ≈ 15 × 10.5 mm of the 13 × 22 mm can.
- So keying is not achievable within the SAO standard with stock parts. Recommendation: unkeyed SMT plus large
  pin-1 triangles on the badge and on each can, and the can art drawn so the "upright" can = correct orientation.
- Plugged in rotated 180°, our modules get badge 3V3 on their unused pin 6 and their 3V3/GND pins land on GPIO2/GPIO1:
  nothing is shorted, the module just does not work. Third-party SAOs could be back-powered from a GPIO; firmware
  should keep GPIO1/GPIO2 as inputs until a module is detected.

## rev 0.6d — battery connector J3 (2026-10-29, user request)

| Ref | Was | Now | LCSC | Notes |
|---|---|---|---|---|
| J3 | CAX PH2.0-2P-LT, custom footprint (C722761) | **JST B2B-PH-SM4-TB**, genuine JST PH 2.0 mm, 2-pin SMD vertical, with solder tabs | **C160352** | 72,150 in stock; $0.21 (5+), $0.13 (1,000+). Stock KiCad footprint `Connector_JST:JST_PH_B2B-PH-SM4-TB_1x02-1MP_P2.00mm_Vertical`. Pin 1 = BAT_IN (+), pin 2 = GND as before |

- Same PH 2.0 mating plug as before, so the battery-box lead doesn't change. Check the box's plug polarity against pin 1 (some boxes are wired the other way).
- The footprint changed, so the PCB needs Update PCB from Schematic and J3 re-placed. No JLC rotation data for C160352 yet: check J3 in the JLC preview.

## rev 0.6e — audio module → IMU module (2026-10-29, user request)

| Ref | Change | LCSC | Notes |
|---|---|---|---|
| J4, R17, C21, C22 | **removed** (PJ-320D jack, PWM filter) | C431535, C11702, C15195, C19702 | the audio module is gone |
| U7 | **new** ST **LSM6DS3TR-C** 6-axis IMU (accel + gyro), LGA-14 2.5 × 3 mm | **C967633** | 22,645 in stock; $0.99 (100+), $0.91 (1,000+) |
| C30, C31 | **new** 100 nF on VDD / VDDIO | C60474 | datasheet note 1 |

- I2C mode (datasheet Mode 1): CS = VDDIO, SA0 = GND → address **0x6A**, SDx/SCx = GND, pins 10/11 NC. SDA/SCL go to the SAO I2C bus (pull-ups R22/R23 on the badge). INT1 → SAO GPIO1 (GPIO11, net renamed AUDIO_PWM → IMU_INT1), INT2 → SAO GPIO2 (GPIO27).
- Cost at 600: about +$0.95/board for U7 + caps, −$0.25 for the jack and filter.

## rev 0.6f — 0.96" OLED connector (2026-10-29, user request)

| Ref | Change | LCSC | Notes |
|---|---|---|---|
| J8 | **new** 1×4 2.54 mm SMD female socket, HX PM2.54-1x4P TP-YQ, 5 mm tall | **C42379197** | 15,269 in stock. For a 0.96" SSD1306 I2C OLED module: 1 GND, 2 VCC (3V3), 3 SCL, 4 SDA, on the SAO I2C bus. Check your module's pin order (some swap GND/VCC) |
