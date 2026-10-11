# JLCPCB order spec — prototype run (10 boards)

| Field | Value |
|---|---|
| Base material | FR-4, TG 130–140 |
| Layers | 2 |
| Dimensions | **56 × 118 mm** blank: the 56 × 100 badge plus three breakaway modules under the pedestal, joined by 4 mm tabs with mouse bites (0.5 mm NPTH). Irregular outline, tab-routed. Order it as **one board**, not as a panel |
| Quantity | 10 |
| Thickness | 1.6 mm |
| Solder mask | **Purple** |
| Silkscreen | White |
| Surface finish | HASL (lead-free) — switch to ENIG if RP2040 paste/assembly issues appear |
| Outer copper | 1 oz |
| Via covering | Tented |
| Min via hole / diameter | 0.3 / 0.6 mm (all vias on the board) |
| Mark on PCB | **Order number (specify position)** — the back silk carries the `JLCJLCJLCJLC` placeholder next to J2. Do not pick "Remove mark", or the placeholder text may be printed literally |
| Assembly | Standard PCBA, top side, 10 boards, confirm parts placement (yes). Includes **THT hand-soldering of six 1×3 headers** (J5–J7 sockets, P1–P3 pins: 18 joints). To avoid the THT fee, mark them DNP in the BOM and bag loose headers |
| DNP | J2, TP1–TP3, SW5 (back), JP1 is a copper jumper. MB1–MB3 are the mouse-bite holes (board-only, not parts) |

Files to upload (produced in stage 3): `gerbers.zip`, `bom_jlc.csv`, `cpl_jlc.csv`.

**Check in the JLC placement preview before paying** (symmetric pad patterns, the CPL rotation fitter cannot tell 0° from 180°):
- D6 B5819W — cathode band must face U3/VSYS side (pad 1). Reversed = no USB power.
- U5 IRM-H638T — GND pair (pins 1, 2) on the J4 side. 180° wrong puts VCC on a GND pad and cooks R19.
- U5 is now on the IR module: GND pair (pins 1, 2) on the left, toward the module edge; OUT/VCC on the R19/C23 side.
- LS1 MLT-8530 (speaker module) — the two coil leads must sit on the pads nearest the header P3 (+Y row). 180° only reverses the coil (harmless), 90° makes it silent.
- D7 1N4148W (speaker module) — cathode band toward the 3V3 bus / LS1 side (pad 1).
- D1–D5 cathode orientation, LED1–LED4 pin 1 corner, Y1, plus Q1/Q2/U2/U3/U4 as listed in `cpl_rotation_report.txt`.
- Check that JLC's DFM review accepts the 0.5 mm mouse-bite holes on the edge line and the 2 mm routed gaps (their minimum slot is 1.0 mm). If they ask, the holes may be moved 0.25 mm into the tab.

Production run (600): same board. The outline is irregular, so the panel is **tab-routed, not V-scored**; 2-up fits a 120 × 125 panel. Let JLC panelise ("Panel by JLCPCB"), no need to draw the panel ourselves.

## Outside JLC
- Wired 3×AAA battery box **with on/off switch** and JST-PH 2.0 mm plug (e.g. "3xAAA battery holder with switch, PH2.0 connector" — common on AliExpress/LCSC alternatives). Check the plug polarity against J3 silk (+ −) on the first delivery; many boxes ship with pins reversed.
- Lanyards with a clip that passes a Ø4 mm hole.
- Optional: right-angle 1×3 pin headers if the modules should lie flat instead of standing up (not from JLC; attendees could re-solder).
- Double-sided foam tape for the battery box, 36 × 50 mm.
