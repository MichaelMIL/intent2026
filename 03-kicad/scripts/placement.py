"""Component placement, board coordinates in mm (origin = top-left of the 56x100 bounding box,
y down, as in 02-layout/placement-plan.md). rot = KiCad degrees (CCW). side F/B.

rev 0.6 (2026-10-18): RP2040 core re-placed after the hardware design guide (RP-008279-DS): 1 uF on VREG_VIN (C18)
and VREG_VOUT (C26) and 100 nF on DVDD 50 (C10) / USB_VDD (C7) / IOVDD 49 (C5) / ADC_AVDD (C8) in a row right under
pins 43-50; C19 (DVDD 23) stays 3 mm out at the top-left so SWCLK/SWDIO/RUN can fan out; the 27R USB terminations R11/R12 right below pins 46/47; QSPI_SS resistors R3/R14
next to the flash. New parts: U6 RGB buffer + C29, SW6 RESET, C27/C28 VBUS, R22/R23 I2C pull-ups, HRO USB-C, SAO 2x3
SMD sockets J5-J7 and SMD headers P1-P3.

rev 0.5: three breakaway modules hang under the pedestal (y 102-118). MODULES gives each module's rectangle
and the x centre of its 4 mm tab on the pedestal edge (y 100-102). Module part coordinates below are given in
module-local mm (origin = module top-left) via MP and converted to board coordinates at import.
"""

# --- breakaway modules = soda cans (13 x 22 mm, R 2.2 shoulders), name -> (x1, y1, x2, y2, tab_x).
# Tabs must sit on the straight pedestal edge x 9.5-46.5; the cans leave 3 mm routed gaps between them.
TAB_W, TAB_L = 4.0, 2.0          # tab width / length (= routed gap between main board and module)
CAN_W, CAN_H, CAN_R = 13.0, 22.0, 2.2
MODULES = {
    'IR':    (5.5, 102.0, 18.5, 124.0, 12.0),
    'IMU':   (21.5, 102.0, 34.5, 124.0, 28.0),
    'SPK':   (37.5, 102.0, 50.5, 124.0, 44.0),
}
# outline corner style of each module: ('chamfer' | 'round', size mm). Corners must stay clear of the tab
# (tab_x +- 2) and of copper; the router sees the real outline, the pours are clipped to it.
MODULE_CORNERS = {name: ('round', CAN_R) for name in MODULES}

P = {
    # --- MCU block ("PRIZE" window) ---
    # U1 rot 180: pins 43-50 along the bottom edge (y 53.44, x 25.4 ... 28.2), 19-23 along the top (x 29.0 ... 27.4)
    'U1': (28.0, 50.0, 180), 'U2': (30.0, 62.3, 270), 'Y1': (29.2, 43.0, 90),
    'R13': (26.4, 43.6, 90), 'C11': (31.8, 44.4, 90), 'C12': (26.4, 41.0, 90),
    'C19': (24.6, 44.4, 0), 'C2': (33.6, 46.2, 0), 'C3': (35.2, 44.6, 0),
    'C1': (33.6, 55.0, 0), 'C4': (23.2, 54.6, 0), 'C17': (35.7, 55.0, 0),
    # row under pins 43-50: ADC_AVDD, VREG_VIN 1u, VREG_VOUT 1u | USB 27R | DVDD 50, USB_VDD, IOVDD 49
    'C8': (23.75, 56.6, 90), 'C18': (24.8, 55.2, 90), 'C26': (25.85, 55.2, 90),
    'R12': (26.6, 57.3, 90), 'R11': (27.65, 57.3, 90),
    'C10': (29.3, 55.2, 90), 'C7': (30.35, 55.2, 90), 'C5': (31.4, 55.2, 90),
    'C6': (34.0, 65.0, 0), 'R3': (34.4, 62.6, 90), 'R14': (35.5, 62.6, 90), 'R4': (21.0, 45.2, 90),
    # --- RGB data buffer (VSYS-powered) between U1 and LED1 ---
    'U6': (40.5, 41.0, 0), 'C29': (40.5, 44.0, 0),
    # --- RGB shelf (chain runs right -> left) ---
    'LED1': (44.0, 36.0, 0), 'LED2': (34.0, 36.0, 0), 'LED3': (24.0, 36.0, 0), 'LED4': (14.0, 36.0, 0),
    'C13': (44.0, 33.6, 0), 'C14': (34.0, 33.6, 0), 'C15': (24.0, 33.6, 0), 'C16': (14.0, 33.6, 0),
    # --- BOOTSEL service key ---
    'SW1': (49.0, 29.0, 0),
    'SW6': (49.5, 44.6, 0),          # RESET, in the product window under the shelf (BOOT is above it)
    # --- J2 service port (left edge) ---
    'J2': (3.6, 31.0, 0),
    # --- credit display + keypad ---
    'D1': (12.0, 69.4, 0), 'D2': (16.0, 69.4, 0), 'D3': (20.0, 69.4, 0), 'D4': (24.0, 69.4, 0), 'D5': (28.0, 69.4, 0),
    'R5': (12.0, 67.0, 0), 'R6': (16.0, 67.0, 0), 'R7': (20.0, 67.0, 0), 'R8': (24.0, 67.0, 0), 'R9': (28.0, 67.0, 0),
    'SW2': (44.0, 65.0, 0), 'SW3': (44.0, 71.0, 0), 'SW4': (44.0, 77.0, 0),
    # --- coin / dispense area: three SAO slots (2x3 SMD sockets at rot 90, rows horizontal), power path ---
    'J5': (4.65, 84.5, 90), 'J6': (13.45, 84.5, 90), 'J7': (22.25, 84.5, 90),
    'R22': (31.0, 76.6, 0), 'R23': (31.0, 77.8, 0),
    'J8': (14.5, 22.0, 90),          # OLED socket, placed by Benny in KiCad (2026-10-29)
    'C20': (28.2, 86.0, 90), 'U3': (31.4, 86.0, 0), 'C9': (31.4, 89.6, 0),
    'Q1': (35.6, 82.4, 0), 'D6': (37.0, 88.2, 0), 'R10': (38.6, 83.4, 90),
    'R15': (40.0, 87.0, 90), 'R16': (41.2, 87.0, 90),
    'U4': (44.4, 84.0, 0), 'R1': (46.4, 86.6, 0), 'R2': (46.4, 81.4, 0),
    'C28': (44.4, 81.0, 0), 'C27': (44.4, 87.0, 0),
    'J1': (53.15, 84.6, 90),         # HRO TYPE-C-31-M-12: shell front 0.8 mm past the x 56 edge
    # --- pedestal ---
    'J3': (20.0, 95.2, 0),
    'TP1': (37.0, 95.0, 0), 'TP2': (40.5, 95.0, 0), 'TP3': (44.0, 95.0, 0),
    # --- back side ---
    # --- lanyard ---
    'H1': (12.0, 5.5, 0), 'H2': (44.0, 5.5, 0),      # in the header sign box, 3 mm web above the hole
}

# --- module parts, module-local coordinates (origin = can top-left; can = 13 x 22 mm, tab at the top centre x 6.5) ---
# rev 0.6: SAO 2x3 SMD header at the bottom of the can. 2026-10-29: rot 90 (rows horizontal, like the badge sockets
# J5-J7; pin 1 = bottom-left pad), 1.1 mm higher so the pads clear the can bottom.
HDR = (6.5, 17.5, 90)
MP = {
    # IR: receiver dome up top, RC filter below it, label band y 11.3-14.5
    'IR': {'P1': HDR, 'U5': (6.5, 5.0, 0), 'R19': (3.0, 9.6, 90), 'C23': (10.0, 9.6, 90), 'C24': (6.5, 10.3, 0)},
    # IMU (2026-10-29, replaces the audio jack): LSM6DS3TR-C in the middle of the can, its two 100 nF caps beside it
    'IMU': {'P2': HDR, 'U7': (6.5, 7.5, 0), 'C30': (2.6, 7.5, 90), 'C31': (10.4, 7.5, 90)},
    # SPK: transducer up top; since the header turned (2026-10-29) the driver row sits on the BACK of the can
    'SPK': {'P3': HDR, 'LS1': (6.5, 5.5, 0), 'Q2': (2.6, 12.4, 0, 'B'), 'D7': (7.5, 11.8, 0, 'B'),
            'R20': (6.0, 13.6, 0, 'B'), 'R21': (8.5, 13.6, 0, 'B'), 'C25': (11.4, 12.4, 90, 'B')},
}
for _m, _parts in MP.items():
    _x1, _y1 = MODULES[_m][0], MODULES[_m][1]
    for _ref, _v in _parts.items():
        P[_ref] = (round(_x1 + _v[0], 3), round(_y1 + _v[1], 3)) + tuple(_v[2:])


def get(ref):
    v = P[ref]
    side = v[3] if len(v) > 3 else 'F'
    return v[0], v[1], v[2], side

# --- exposed-copper art regions (front): no tracks or vias of any net here. Since rev 0.6 router/route2.py enforces
# these as a hard F.Cu keepout (ART_KEEPOUT=1, default); router/prune_routes.py --art is only needed for old route sets.
ART_KEEPOUTS = [            # (x1, y1, x2, y2, layer)
    (8.0, 9.8, 48.0, 21.5, 'F'),      # INTENT logo in copper
    (15.0, 3.2, 41.0, 6.0, 'F'),      # INTENT-O-MATIC marquee
    (48.9, 63.6, 50.9, 78.4, 'F'),    # key letters A / B / C (a VSYS track runs at x 48.3-48.55)
    (48.3, 32.1, 52.9, 33.7, 'F'),    # BOOT
]
