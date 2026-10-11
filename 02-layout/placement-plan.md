# Placement plan — rev 0.5, 56 × 100 mm vending-machine silhouette + 3 breakaway soda cans (blank 56 × 124)

Origin top-left of bounding box, mm. Front: `board-mockup.svg`. Back: `board-mockup-back.svg`.

## Front

| Zone (y) | Machine element | Parts / art | Position |
|---|---|---|---|
| 0–9 | Header sign box x 7–49 (R 2.5 corners; cabinet shoulders at y 9 with R 1 fillets, R 2 outer corners) | H1, H2 lanyard Ø4.0 inside the box, "INTENT-O-MATIC" marquee between them | (12, 5.5), (44, 5.5) |
| 8–25 | Marquee | **INTENT by Palo Alto Networks** logo, white silk, 40 mm wide (`artwork/intent-logo-white.png`, aspect 3.55:1 → 11.3 mm tall) at x 8–48, y 9–20.5. Below it two lines of 1.2 mm text: "2026 · THE SECURITY SUMMIT" / "FOR RESEARCHERS / BY RESEARCHERS" | centred, x 28 |
| 26–60 | Product window (silk frame x 9–53) | Shelf 1 y 36: LED1–4 WS2812 at x 14/24/34/44 inside "product" boxes. Shelf 2 y 50: U1 RP2040 (28, 50), U2 (36, 48), Y1 (21, 48), decaps around U1, "★ PRIZE ★" box. SW1 BOOTSEL "service key" at (49, 29) + "BOOT" | |
| 30–64 | Service port (left edge) | J2 2×13 THT at x 3.6 / 6.14, y 31 → 61.5 (pin 1 top) | |
| 62–79 | Credit display + keypad | D1–D5 in display box x 9–33, y 65–73 (LEDs at x 12..28 step 4, y 69). SW2/3/4 column at x 44, y 65/71/77; "A B C" at x 50 | |
| 80–90 | Coin / dispense area | **rev 0.5:** three expansion slots J5 IR / J6 AUDIO / J7 SPK, 1×3 THT sockets at x 4.5 / 11.5 / 18.5, pins along y (82.46 / 85.0 / 87.54, pin 1 = GND at the top), labels above, "G + S" legend at x 21.3. J1 USB-C on the **right edge** (52, 85). Power path U3/U4/D6/Q1/R10–R16/C9/C20 in x 27–47, y 81–89. R11/R12 27 Ω next to U1 (USB pair end). (rev 0.3 had U5 and J4 here.) | |
| 90–100 | Pedestal x 8–48 | J3 battery plug (20, 95.2), TP1–TP3 (TX RX GND) at x 37/40.5/44, y 95. "INSERT COIN →" silk pointing at J1. Mouse bites (MB1–MB3) on the bottom edge at x 12.5 / 27.5 / 43.5 | |
| 102–124 | **Breakaway cans** 13 × 22 mm, R 2.2 corners (2 mm gap to the pedestal, 4 mm tabs at x 12 / 28 / 44, 3 mm gaps between cans) | Can-local coordinates in `placement.MP`: header P1–P3 at (3.96, 19.0) rot 90 (pin 2 on the centre line). IR x 5.5–18.5: U5 (6.5, 5.0), R19 (3.0, 9.6), C23 (10.0, 9.6), C24 (6.5, 10.3). AUDIO x 21.5–34.5: J4 (7.5, 7.0) mouth −x, R17 (3.5, 14.2), C21 (6.5, 14.2), C22 (10.2, 14.3). SPK x 37.5–50.5: LS1 (6.5, 6.0), Q2 (3.2, 12.95), D7 (9.6, 12.3), R20 (9.6, 14.0), R21 (6.5, 14.0), C25 (3.4, 15.75) | |

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
Front (vending-machine theme): outline, "INTENT-O-MATIC" marquee in the header box, logo + tagline, product window (notched around the keypad) with shelf, dispensing coil and 4 product boxes with price tags A1 25¢ … A4 $1, "← PRIZE" at the RP2040, "J2 HACK PORT" (vertical), CREDIT meter with coin values 5¢…$1, keypad bezel + SELECT + A/B/C, BOOT, ITEM PICKUP door with slot labels "B1 IR / B2 AUDIO / B3 SPK" + "G + S", "INSERT COIN →" + coin slot, 3×AAA + −, TX/RX/GND.
Modules (soda cans): rim lines top and bottom, label band: "B1 · IR COLA" + wave + "38 kHz", "3.5mm" + wave + "B2 · AUDIO POP", "B3 · BEEP FIZZ"; "G + S" under each header; back: "Bn <name> MODULE / snap off, / plug into Jx".
Back: team list, QR box, battery outline = SERVICE COMPARTMENT (AUTHORIZED PERSONNEL ONLY, model plate), J2 warning + rev, battery lead note, NO REFUNDS · DO NOT TILT OR ROCK, SW5/JP1 notes.
