# Placement plan — rev 0.5, 56 × 100 mm vending-machine silhouette + 3 breakaway modules (blank 56 × 118)

Origin top-left of bounding box, mm. Front: `board-mockup.svg`. Back: `board-mockup-back.svg`.

## Front

| Zone (y) | Machine element | Parts / art | Position |
|---|---|---|---|
| 0–8 | Rounded top | H1, H2 lanyard Ø4.0 | (10, 6), (46, 6) |
| 8–25 | Marquee | **INTENT by Palo Alto Networks** logo, white silk, 40 mm wide (`artwork/intent-logo-white.png`, aspect 3.55:1 → 11.3 mm tall) at x 8–48, y 9–20.5. Below it two lines of 1.2 mm text: "2026 · THE SECURITY SUMMIT" / "FOR RESEARCHERS / BY RESEARCHERS" | centred, x 28 |
| 26–60 | Product window (silk frame x 9–53) | Shelf 1 y 36: LED1–4 WS2812 at x 14/24/34/44 inside "product" boxes. Shelf 2 y 50: U1 RP2040 (28, 50), U2 (36, 48), Y1 (21, 48), decaps around U1, "★ PRIZE ★" box. SW1 BOOTSEL "service key" at (49, 29) + "BOOT" | |
| 30–64 | Service port (left edge) | J2 2×13 THT at x 3.6 / 6.14, y 31 → 61.5 (pin 1 top) | |
| 62–79 | Credit display + keypad | D1–D5 in display box x 9–33, y 65–73 (LEDs at x 12..28 step 4, y 69). SW2/3/4 column at x 44, y 65/71/77; "A B C" at x 50 | |
| 80–90 | Coin / dispense area | **rev 0.5:** three expansion slots J5 IR / J6 AUDIO / J7 SPK, 1×3 THT sockets at x 4.5 / 11.5 / 18.5, pins along y (82.46 / 85.0 / 87.54, pin 1 = GND at the top), labels above, "G + S" legend at x 21.3. J1 USB-C on the **right edge** (52, 85). Power path U3/U4/D6/Q1/R10–R16/C9/C20 in x 27–47, y 81–89. R11/R12 27 Ω next to U1 (USB pair end). (rev 0.3 had U5 and J4 here.) | |
| 90–100 | Pedestal x 8–48 | J3 battery plug (20, 95.2), TP1–TP3 (TX RX GND) at x 37/40.5/44, y 95. "INSERT COIN →" silk pointing at J1. Mouse bites (MB1–MB3) on the bottom edge at x 12.5 / 27.5 / 43.5 | |
| 102–118 | **Breakaway modules** (2 mm gap, 4 mm tabs) | IR module x 0–16: U5 (8, 4.6), R19/C23 at x 13.5, C24 (8, 9.4), P1 pins at y 13 (x 5.46/8/10.54). AUDIO module x 19–36: J4 (7.7, 5.6) mouth −x (barrel in the gap), R17/C21/C22 at x 15, P2 pins at y 13. SPK module x 39–56: LS1 (8, 5.3) leads toward the header, Q2/D7/R20/R21 column at x 14.8, C25 (2.3, 12.3), P3 pins at y 13. Coordinates module-local (see `placement.py` MP) | |

## Back (mirrored: J1 on the left when viewed from the back)

| Zone (y) | Content |
|---|---|
| 8–25 | Left: **TEAM** list (1.4 mm text): Idan Ben Moshe (I.B.M), Matar Maoz, Benny Mizels, Michael Mark, Mattar Bernhard ('t'*2), Tomer Zait. Right: **QR reserve** 14 × 14 mm silk box with "QR" placeholder — replaced by the repo QR later (silk only, no re-layout needed) |
| 26–76 | Battery box area, x 10–46 — dashed silk outline, "3×AAA  ←  box here", **no THT pins, no tall parts** inside it |
| 78–90 | **rev 0.4: J3 moved to the FRONT pedestal (20, 95) — top-side-only assembly.** Old: J3 JST-PH 2-pin (28, 80) with "+ −" silk; SW5 slide-switch footprint (40, 80) DNP + solder-jumper bridge; rev / date text |
| 90–100 | Pedestal: "J2: 3V3 LOGIC ONLY — NO 5V", board rev, JLC order-number spot |

## Routing (2 layers)
- B.Cu ground pour; keep the back under the battery box free of THT only (SMD J3 and SW5 are below the box area).
- USB D± ≈ 35 mm J1 → U4 → R11/R12 → U1: 90 Ω pair on F.Cu, ground under, no vias.
- VSYS 0.6 mm, 3V3 / 5V_RGB 0.4 mm. Crystal ≤ 3 mm from U1. 100 nF ≤ 1 mm from pins.
- Lanyard holes: 1.5 mm copper keepout, no parts within 3 mm; the logo starts at y 9, below the holes.
- IR receiver ≥ 10 mm from the WS2812B: on the module, plugged into J5, it stands ≈ 45 mm below the shelf — fine.
- Modules: each has its own ground net and pour (IRM_GND / AUM_GND / SPM_GND); the main GND pour stops at the pedestal edge, nothing is routed across a tab. The mouse-bite holes carry a 0.5 mm clearance so copper stays off the break line.

## Silkscreen checklist (JLC: min 0.15 mm line, ≥ 1 mm text; logo fine detail ≥ 0.2 mm)
Front: outline, logo + tagline, window + shelves + 4 product boxes + prize box, display box + "CREDIT", A/B/C, BOOT, slot labels "IR / AUDIO / SPK" + "G + S", "INSERT COIN →". Modules: name, "G + S" under the header; back: "<name> MODULE — snap off, plug into slot Jx".
Back: team list, QR box, battery outline, J3 polarity, SW5 note, warning, rev.
