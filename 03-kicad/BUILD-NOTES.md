# 03-kicad — build notes (rev 0.5, 2026-10-11)

KiCad project, regenerated with **KiCad 10.0.3** on the Mac on 2026-10-11 (the board file is now in the v10 format; the schematic is still written in the 2025 format and opens in 9 and 10). Open `intent-2026-badge.kicad_pro`. The project folder holds custom footprints in `intent.pretty` (they are registered in `fp-lib-table`).

**rev 0.5:** the IR receiver, the audio jack and a new speaker are **breakaway modules** under the pedestal. Blank 56 × 118 mm: badge 56 × 100 + a 2 mm routed gap + three 16–17 × 16 mm modules on 4 mm tabs with 4 × 0.5 mm mouse bites each (MB1–MB3, board-only footprints on the pedestal edge line). Sockets J5/J6/J7 (IR/AUDIO/SPK) on the main board, pin headers P1/P2/P3 on the modules, pin 1 = GND, 2 = 3V3, 3 = signal. Module nets are prefixed IRM_/AUM_/SPM_; no copper crosses a tab; each module has its own ground pour. Details and cost in `../00-bom/bom-deltas.md` (rev 0.5) and `../01-spec/design-spec.md` §3.11.

## Status
| Check | Result |
|---|---|
| ERC | 0 errors, 1 warning (`lib_symbol_mismatch` on J1, deliberate: KiCad 10 renamed the USB-C shield pin, see below) |
| DRC (with schematic parity) | **rev 0.5: 0 violations, 0 unconnected** (KiCad 10.0.3). The 86 `footprint_symbol_field_mismatch` items are the cosmetic KiCad 10 Description-field notes. |
| Routing | rev 0.5: 2 layers, 1313 track segments, 412 vias (0.3/0.6), 194 of them GND (9 under the RP2040 pad, 134 stitching). Pours: GND on both layers over the badge; IRM_GND / AUM_GND / SPM_GND on the three modules. Netlist: 86 parts, 78 nets. |
| Fab outputs | `../04-fab/` (rev 0.5, 2026-10-11; the rev 0.4 set is in `../04-fab/archive-rev0.4/`, the rev 0.4 board in `build/rev0.4/`) |

## How the files are generated (all scripted, reproducible)
`scripts/design.py` is the netlist source of truth, and `scripts/placement.py` holds the coordinates.
1. `gen_fp.py` → `intent.pretty` (USB-C C393939, PJ-320D C431535, IRM-H638T C91447, JST-PH C722761, MLT-8530 C94599, lanyard hole, mouse bites). Pad geometry is copied from the JLC/EasyEDA footprints of those exact LCSC parts. The MLT-8530 footprint numbers its two dummy pads crosswise (1/2), so a 180° placement only reverses the coil.
2. `gen_sch.py` → `.kicad_sch`, a **wired schematic** (2026-10-11 rework): nine blocks on one A2 sheet (USB-C, power path, expansion ports, IR module, RP2040 core, UI, header, audio module, speaker module). Rails use power symbols, every other net carries a global label with the design.py net name, so the PCB netlist is unchanged. Drawing primitives are in `schlib.py`; `check_sch.py --erc` exports the netlist and proves every (ref, pin) → net matches design.py, then runs ERC. `render_sch.py` makes a PNG for a visual check. The previous labels-only schematic is kept as `build/intent-2026-badge.kicad_sch.v1-labels.bak`.
3. `pcb_build.py` (KiCad Python) → unrouted board + `build/geo.json`. Draws the badge outline, splits the pedestal edge at the tabs, adds the tab sides and module rectangles as one closed Edge.Cuts contour, and places the mouse-bite footprints (`SetBoardOnly`, excluded from BOM/CPL and from schematic parity). `geo.json` carries the full polygon (router) and the badge-only polygon (pours, silk).
4. `router/route2.py` routes the board with a negotiated-congestion grid router: exact clearances, A* in C (`astar.c`), and a final GND fan-out pass into the main B.Cu plane.
5. `pcb_finish.py` → tracks, pours, silkscreen (`silk.py`, logo from `art_logo.py`). Pours: GND over the badge polygon only (it stops at the pedestal edge), plus IRM_GND / AUM_GND / SPM_GND over the three module rectangles. The 0.5 mm clearance on the mouse-bite holes keeps copper off the break line. `router/gnd_repair.py` + `island_stitch.py` check the main ground; module grounds are routed as ordinary nets.
6. `fab_export.py` → JLC BOM/CPL with rotation correction taken from `jlc_footprints.json`. `kicad-cli` produces the Gerbers and drill files.
`build_prep.sh` / `build_finish.sh` run the chain. 2026-10-11: run on the Mac with KiCad 10.0.3 (`scripts/env.mac.sh`, see CLAUDE.md); two KiCad 10 API renames are handled with fallbacks (`HasField`/`GetField`). The router grid was extended to y 120 for the modules (`NY = 1210`).
Router settings used for the rev 0.5 board (run from a scratch copy `$W`):
```
ROUTE_ITERS=60 FIXED_ROUTES=$W/scripts/router/fixed_routes.json GND_SKIP=U1.19 GND_LAST=1 \
GND_SUBSET=U2.4,Y1.4,C17.2,R10.2,C8.2,C7.2,C5.2,C4.2,C19.2,C18.2,C10.2,C1.2 CORR_R=6.5 HIST_INC=30 PRES_CAP=150000 \
ROUTE_STATE=$W/route_state.pkl python3 scripts/router/route2.py $W/geo.json $W/routes.json
```
`fixed_routes.json` pre-places the TESTEN (U1.19) ground fan-out to the crystal GND pad Y1.4 (the corridor between XIN and GPIO15, taken from the rev 0.4 board); the negotiation alone ended with XIN and that fan-out 0.05 mm apart. Every other net routes around fixed copper. If a run ends with a few residual conflicts that all involve GND, `router/gnd_final.py geo.json routes.json` keeps the signal nets and re-does only the GND fan-outs with hard clearance (plus stitching). `ROUTE_STATE` lets a run resume with more `ROUTE_ITERS`.
rev 0.4 settings for reference: `GND_LAST=1 GND_SUBSET=U2.4,U1.19,R10.2,C8.2,C7.2,C5.2,C4.2,C19.2,C18.2,C10.2,C1.2 CORR_R=6.5 HIST_INC=30 PRES_CAP=150000`.

## Changes against design-spec rev 0.3 (all reflected in the files)
10. **rev 0.5 breakaway modules** (user decision 2026-10-11): U5/R19/C23/C24 → IR module, J4/R17/C21/C22 → audio module, new speaker module LS1/Q2/D7/R20/R21/C25 (BOM-B2 add-on 7). GPIO25 drives the speaker and stays on J2 pin 15. Sockets J5–J7 sit where U5 and J4 were (x 4.5 / 11.5 / 18.5, y 82.5–87.5, pins along y, pin 1 = GND at the top). Headers are THT: either JLC hand-solders them or they ship DNP. Modules stand upright when plugged in; right-angle headers (same pads) would make them lie flat.
1. **R11/R12 27 Ω = C25100.** The C25105 in bom-deltas is 33 Ω.
2. **U5 IR pinout corrected:** 1, 2 = GND, 3 = OUT, 4 = VCC. The spec text had OUT on pin 1.
3. **J4 PJ-320D (C431535) is an SMD part.** Pads: 1 = S, 2 = R2, 3 = R1, 4 = T (same geometry as KiCad's PJ320D). Tip + R1 = audio, S + R2 = GND.
4. **Keypad GPIOs swapped for routing:** A = GPIO4 (SW2, top), B = GPIO3, C = GPIO2 (SW4, bottom). Firmware only. The gpio-map is updated.
5. **J3 battery connector is on the front pedestal** (20, 95), so assembly stays top-side only (user decision). SW5 (DNP) and JP1 (bridged jumper) are on the back pedestal.
6. U1 rotated 180° and flash U2 rotated 270° under U1. Several decaps sit 2–5 mm from their pins (corners of the QFN) instead of ≤ 1 mm. That is acceptable for RP2040.
7. U1 exposed pad: 9 × 0.3 mm vias in the pad. These are not tented on the pad side, which is usual for QFN thermal vias.
8. USB D+/D− are routed as 0.2 mm tracks. A 90 Ω pair is not achievable on 1.6 mm 2-layer FR-4 at a reasonable width. Full-speed USB (12 Mbit/s) does not need it.
9. Silkscreen reference designators are moved to the Fab layer (not printed). The art follows `02-layout`. Glyphs that the KiCad font lacks (★ ♪) are replaced with plain text.

## Schematic rework notes (2026-10-11)
- Verified with `scripts/check_sch.py --erc`: 259 pins, 68 nets, 0 mismatches against design.py; ERC 0 errors.
- The one ERC warning (`lib_symbol_mismatch` on J1) is deliberate: the KiCad 10 library renamed the USB-C shield pin from `S1` to `SH`; `schlib.PIN_RENAMES` maps it back so the symbol still matches the custom footprint pad `S1` and the PCB.
- PCB DRC with schematic parity after the rework: 0 errors, 0 unconnected. Under KiCad 10 it also lists 74 `footprint_symbol_field_mismatch` warnings (Description field empty on the PCB footprints); cosmetic, not present under KiCad 9.
- One intentional wire crossing in the USB block (D− drops past the D+ run at (78.74, 101.6)); crossings without a junction dot are not connections.

## Still to verify (cannot be done from here)
- **JLC preview after upload:** rotation of D1–D5 (assumes LCSC pad 1 = cathode, CPL uses 180°), Q1/Q2/U3 (180°), U2 (180°), U4 (270°). **Also D6, D7, U5, LS1**: symmetric pad patterns, the fitter cannot detect a 180° error (D6 reversed = no USB power; U5 reversed puts VCC on a GND pad; D7 reversed shorts the collector drive through the diode; LS1 is tolerant by footprint design). See `../04-fab/cpl_rotation_report.txt`.
- **JLC DFM on the breakaway features:** 0.5 mm NPTH mouse bites centred on the edge line, 2 mm routed gap, 4 mm tabs. If JLC objects to the half-holes on the edge, move the MB footprints 0.25 mm into the tab (`pcb_build.add_mousebites`).
- 1N4148W C81598 showed 300 pieces in LCSC stock on 2026-10-11; check JLC's own stock or substitute.
- The 12 MHz crystal C133334 is specified for CL = 20 pF, but C11/C12 are 15 pF (Pico values). Expect about +50 ppm, which is fine for USB. If you want it exact, use 27–33 pF caps.
- The 3D view has no models for the 4 custom footprints. This is cosmetic only.
