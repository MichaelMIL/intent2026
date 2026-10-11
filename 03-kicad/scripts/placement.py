"""Component placement, board coordinates in mm (origin = top-left of the 56x100 bounding box,
y down, as in 02-layout/placement-plan.md). rot = KiCad degrees (CCW). side F/B.

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
    'AUDIO': (21.5, 102.0, 34.5, 124.0, 28.0),
    'SPK':   (37.5, 102.0, 50.5, 124.0, 44.0),
}
# outline corner style of each module: ('chamfer' | 'round', size mm). Corners must stay clear of the tab
# (tab_x +- 2) and of copper; the router sees the real outline, the pours are clipped to it.
MODULE_CORNERS = {name: ('round', CAN_R) for name in MODULES}

P = {
    # --- MCU block ("PRIZE" window) ---
    'U1': (28.0, 50.0, 180), 'U2': (30.0, 60.8, 270), 'Y1': (29.2, 43.0, 90),
    'R13': (26.4, 43.6, 90), 'C11': (31.8, 44.4, 90), 'C12': (26.4, 41.0, 90),
    'C19': (24.6, 44.4, 0), 'C2': (33.6, 46.2, 0), 'C3': (35.2, 44.6, 0),
    'C1': (33.6, 55.0, 0), 'C4': (23.4, 54.6, 0), 'C17': (35.7, 55.0, 0),
    'C8': (21.9, 57.2, 90), 'C18': (22.9, 57.2, 90), 'C10': (23.9, 57.2, 90), 'C7': (24.9, 57.2, 90),
    'C5': (25.9, 55.2, 0), 'C6': (34.0, 64.0, 0),
    'R3': (34.4, 61.6, 90), 'R4': (21.0, 45.2, 90),
    'R11': (24.6, 63.2, 90), 'R12': (23.4, 63.2, 90),
    # --- RGB shelf (chain runs right -> left) ---
    'LED1': (44.0, 36.0, 0), 'LED2': (34.0, 36.0, 0), 'LED3': (24.0, 36.0, 0), 'LED4': (14.0, 36.0, 0),
    'C13': (44.0, 33.6, 0), 'C14': (34.0, 33.6, 0), 'C15': (24.0, 33.6, 0), 'C16': (14.0, 33.6, 0),
    # --- BOOTSEL service key ---
    'SW1': (49.0, 29.0, 0), 'R14': (44.6, 27.4, 90),
    # --- J2 service port (left edge) ---
    'J2': (3.6, 31.0, 0),
    # --- credit display + keypad ---
    'D1': (12.0, 69.4, 0), 'D2': (16.0, 69.4, 0), 'D3': (20.0, 69.4, 0), 'D4': (24.0, 69.4, 0), 'D5': (28.0, 69.4, 0),
    'R5': (12.0, 67.0, 0), 'R6': (16.0, 67.0, 0), 'R7': (20.0, 67.0, 0), 'R8': (24.0, 67.0, 0), 'R9': (28.0, 67.0, 0),
    'SW2': (44.0, 65.0, 0), 'SW3': (44.0, 71.0, 0), 'SW4': (44.0, 77.0, 0),
    # --- coin / dispense area: three expansion "slots" (1x3 sockets, pin 1 = GND at the top), power path ---
    'J5': (4.5, 82.46, 0), 'J6': (11.5, 82.46, 0), 'J7': (18.5, 82.46, 0),
    'U3': (29.6, 85.6, 0), 'C9': (33.0, 85.6, 90), 'C20': (27.0, 85.6, 90),
    'Q1': (35.6, 82.4, 0), 'D6': (36.6, 87.8, 0), 'R10': (38.6, 83.4, 90),
    'R15': (40.0, 87.0, 90), 'R16': (41.2, 87.0, 90),
    'U4': (44.4, 84.0, 0), 'R1': (46.4, 86.6, 0), 'R2': (46.4, 81.4, 0),
    'J1': (51.34, 84.0, 90),
    # --- pedestal ---
    'J3': (20.0, 95.2, 0),
    'TP1': (37.0, 95.0, 0), 'TP2': (40.5, 95.0, 0), 'TP3': (44.0, 95.0, 0),
    # --- back side ---
    'SW5': (30.5, 95.6, 0, 'B'), 'JP1': (30.5, 91.0, 0, 'B'),
    # --- lanyard ---
    'H1': (12.0, 5.5, 0), 'H2': (44.0, 5.5, 0),      # in the header sign box, 3 mm web above the hole
}

# --- module parts, module-local coordinates (origin = can top-left; can = 13 x 22 mm, tab at the top centre x 6.5) ---
# Headers lie along the bottom (pins extend +x at rot 90, pin 1 = GND on the left, pin 2 on the can centre line).
HDR = (3.96, 19.0, 90)
MP = {
    # IR: receiver dome up top, RC filter below it, label band y 12-17.5
    'IR': {'P1': HDR, 'U5': (6.5, 5.0, 0), 'R19': (3.0, 9.6, 90), 'C23': (10.0, 9.6, 90), 'C24': (6.5, 10.3, 0)},
    # AUDIO: jack lying across the can, body 0.2 mm inside the left edge, barrel 1.8 mm into the 3 mm gap (mouth -x);
    # PWM filter in a row below it
    'AUDIO': {'P2': HDR, 'J4': (7.5, 7.0, 0), 'R17': (3.5, 14.2, 0), 'C21': (6.5, 14.2, 0), 'C22': (10.2, 14.3, 0)},
    # SPK: transducer up top (leads toward the driver row), driver row below, label line above the header
    'SPK': {'P3': HDR, 'LS1': (6.5, 6.0, 0), 'Q2': (3.2, 12.95, 0), 'D7': (9.6, 12.3, 0), 'R20': (9.6, 14.0, 0),
            'R21': (6.5, 14.0, 0), 'C25': (3.4, 15.75, 0)},
}
for _m, _parts in MP.items():
    _x1, _y1 = MODULES[_m][0], MODULES[_m][1]
    for _ref, (_x, _y, _rot) in _parts.items():
        P[_ref] = (round(_x1 + _x, 3), round(_y1 + _y, 3), _rot)


def get(ref):
    v = P[ref]
    side = v[3] if len(v) > 3 else 'F'
    return v[0], v[1], v[2], side

# --- exposed-copper art regions (front): no signal tracks may run here, GND stitching vias are pruned here
# (router/prune_routes.py --art). Checked against routes.json on 2026-10-11; re-check after any re-route.
ART_KEEPOUTS = [            # (x1, y1, x2, y2, layer)
    (8.0, 9.8, 48.0, 21.5, 'F'),      # INTENT logo in copper
    (15.0, 3.2, 41.0, 6.0, 'F'),      # INTENT-O-MATIC marquee
    (48.9, 63.6, 50.9, 78.4, 'F'),    # key letters A / B / C (a VSYS track runs at x 48.3-48.55)
    (48.3, 32.1, 52.9, 33.7, 'F'),    # BOOT
]
