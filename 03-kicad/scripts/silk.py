"""Silkscreen artwork for the INTENT 2026 badge (front + back).  Board coordinates (front view).

Vending-machine theme (rev 0.5): price-tagged shelf items A1-A4 (the RGB LEDs) over a dispensing coil, a keypad
bezel with SELECT, a CREDIT meter with coin values, an ITEM PICKUP door around the three module slots B1-B3, a coin
slot by the UART test pads, a marquee in the header sign box, service-panel texts on the back. The breakaway modules
are soda cans: B1 "IR COLA", B2 "AUDIO POP", B3 "BEEP FIZZ" (rim lines, label band with a wave, pin labels)."""
import math
import pcbnew
from pcb_build import OX, OY, mm, P, MODULES

TEAM = ['Idan Ben Moshe (I.B.M)', 'Matar Maoz', 'Benny Mizels', 'Michael Mark', "Mattar Bernhard ('t'*2)", 'Tomer Zait']
FS, BS = pcbnew.F_SilkS, pcbnew.B_SilkS


def text(board, s, x, y, size=1.0, layer=FS, just='C', angle=0, thick=None, bold=False):
    t = pcbnew.PCB_TEXT(board)
    t.SetText(s)
    t.SetLayer(layer)
    t.SetPosition(P(x, y))
    t.SetTextSize(pcbnew.VECTOR2I(mm(size), mm(size)))
    t.SetTextThickness(mm(thick if thick else max(0.15, size * 0.15)))
    if bold:
        t.SetBold(True)
    t.SetHorizJustify({'L': pcbnew.GR_TEXT_H_ALIGN_LEFT, 'C': pcbnew.GR_TEXT_H_ALIGN_CENTER,
                       'R': pcbnew.GR_TEXT_H_ALIGN_RIGHT}[just])
    if layer == BS:
        t.SetMirrored(True)
    if angle:
        t.SetTextAngleDegrees(angle)
    board.Add(t)
    return t


def line(board, x1, y1, x2, y2, layer=FS, w=0.15):
    s = pcbnew.PCB_SHAPE(board)
    s.SetShape(pcbnew.SHAPE_T_SEGMENT)
    s.SetStart(P(x1, y1)); s.SetEnd(P(x2, y2))
    s.SetLayer(layer); s.SetWidth(mm(w))
    board.Add(s)


def rect(board, x1, y1, x2, y2, layer=FS, w=0.15, dash=None, fill=False):
    if dash:
        for (a, b, c, d) in ((x1, y1, x2, y1), (x2, y1, x2, y2), (x2, y2, x1, y2), (x1, y2, x1, y1)):
            dashed(board, a, b, c, d, layer, w, dash)
        return
    s = pcbnew.PCB_SHAPE(board)
    s.SetShape(pcbnew.SHAPE_T_RECT)
    s.SetStart(P(x1, y1)); s.SetEnd(P(x2, y2))
    s.SetLayer(layer); s.SetWidth(mm(w)); s.SetFilled(fill)
    board.Add(s)


def dashed(board, x1, y1, x2, y2, layer, w, dash):
    import math
    L = math.hypot(x2 - x1, y2 - y1)
    on, off = dash
    t = 0.0
    while t < L:
        e = min(L, t + on)
        line(board, x1 + (x2 - x1) * t / L, y1 + (y2 - y1) * t / L, x1 + (x2 - x1) * e / L, y1 + (y2 - y1) * e / L, layer, w)
        t += on + off


def circle(board, x, y, r, layer=FS, w=0.15):
    s = pcbnew.PCB_SHAPE(board)
    s.SetShape(pcbnew.SHAPE_T_CIRCLE)
    s.SetCenter(P(x, y)); s.SetEnd(P(x + r, y))
    s.SetLayer(layer); s.SetWidth(mm(w)); s.SetFilled(False)
    board.Add(s)




def arc(board, x1, y1, xm, ym, x2, y2, layer=FS, w=0.15):
    s = pcbnew.PCB_SHAPE(board)
    s.SetShape(pcbnew.SHAPE_T_ARC)
    s.SetArcGeometry(P(x1, y1), P(xm, ym), P(x2, y2))
    s.SetLayer(layer); s.SetWidth(mm(w))
    board.Add(s)


def polyline(board, pts, layer=FS, w=0.15, close=True):
    for a, b in zip(pts, pts[1:] + (pts[:1] if close else [])):
        line(board, a[0], a[1], b[0], b[1], layer, w)


def zigzag(board, c0, t1, t2, amp=0.3, period=1.0, layer=FS, w=0.15, vertical=True):
    """Crimped wrapper edge: a zigzag along t1..t2 centred on c0 (x for vertical, y for horizontal), ends on c0."""
    n = max(2, int(round(abs(t2 - t1) / (period / 2))))
    pts = []
    for i in range(n + 1):
        t = t1 + (t2 - t1) * i / n
        off = 0 if i in (0, n) else (amp if i % 2 else -amp)
        pts.append((c0 + off, t) if vertical else (t, c0 + off))
    polyline(board, pts, layer, w, close=False)


def wave(board, xa, xb, y, amp=0.4, period=2.75, layer=FS, w=0.15, n_per=8):
    """Soda-label wave: one sine line from xa to xb."""
    n = max(4, int((xb - xa) / period * n_per))
    pts = [(xa + (xb - xa) * i / n, y + amp * math.sin(2 * math.pi * ((xb - xa) * i / n) / period)) for i in range(n + 1)]
    polyline(board, pts, layer, w, close=False)


def product(board, kind, cx, layer=FS):
    """Vending item drawn around a shelf LED (pads x +-1.3, y 35.1-36.9; its capacitor sits above at y 33.3-33.9)."""
    if kind == 'can':
        polyline(board, [(cx - 1.9, 35.1), (cx - 1.5, 34.7), (cx + 1.5, 34.7), (cx + 1.9, 35.1), (cx + 1.9, 38.6),
                         (cx + 1.5, 39.0), (cx - 1.5, 39.0), (cx - 1.9, 38.6)], layer)
        for sx in (-1, 1):
            line(board, cx + sx * 1.9, 35.4, cx + sx * 1.5, 35.4, layer); line(board, cx + sx * 1.9, 38.3, cx + sx * 1.5, 38.3, layer)
    elif kind == 'cup':
        polyline(board, [(cx - 2.0, 34.7), (cx + 2.0, 34.7), (cx + 1.5, 39.0), (cx - 1.5, 39.0)], layer)
        line(board, cx - 2.2, 34.7, cx + 2.2, 34.7, layer, 0.25)                  # lid
        line(board, cx + 1.1, 34.7, cx + 1.8, 32.9, layer)                          # straw
    elif kind == 'bag':
        line(board, cx - 2.1, 34.6, cx - 2.1, 39.0, layer); line(board, cx + 2.1, 34.6, cx + 2.1, 39.0, layer)
        zigzag(board, 34.6, cx - 2.1, cx + 2.1, amp=0.25, period=0.7, layer=layer, vertical=False)
        zigzag(board, 39.0, cx - 2.1, cx + 2.1, amp=0.25, period=0.7, layer=layer, vertical=False)
    else:  # candy bar with crimped ends
        line(board, cx - 2.3, 34.6, cx + 2.3, 34.6, layer); line(board, cx - 2.3, 39.0, cx + 2.3, 39.0, layer)
        zigzag(board, cx - 2.3, 34.6, 39.0, amp=0.25, period=0.8, layer=layer)
        zigzag(board, cx + 2.3, 34.6, 39.0, amp=0.25, period=0.8, layer=layer)


def coil(board, xa, xb, y, d=1.2, layer=FS, w=0.15):
    """Dispensing spiral seen from the front: a row of half loops hanging under the shelf line."""
    x = xa
    while x + d <= xb + 1e-6:
        arc(board, x, y, x + d / 2, y + d / 2, x + d, y, layer, w)
        x += d

def logo(board, art):
    for pg in art['polys']:
        ps = pcbnew.SHAPE_POLY_SET()
        ps.NewOutline()
        for x, y in pg['ext'][:-1]:
            ps.Append(mm(OX + x), mm(OY + y))
        for h in pg['holes']:
            ps.NewHole()
            for x, y in h[:-1]:
                ps.Append(mm(OX + x), mm(OY + y), -1, 0)
        ps.Fracture()
        for k in range(ps.OutlineCount()):
            s = pcbnew.PCB_SHAPE(board)
            s.SetShape(pcbnew.SHAPE_T_POLY)
            sub = pcbnew.SHAPE_POLY_SET()
            sub.AddOutline(ps.Outline(k))
            s.SetPolyShape(sub)
            s.SetFilled(True)
            s.SetWidth(0)
            s.SetLayer(FS)
            board.Add(s)


def pin1(board, x, y, s=0.7):
    """Filled pin-1 triangle pointing right (+x), tip at (x + s/2, y)."""
    polyline(board, [(x - s / 2, y - s / 2), (x + s / 2, y), (x - s / 2, y + s / 2)], w=0.12)
    poly = pcbnew.PCB_SHAPE(board)
    poly.SetShape(pcbnew.SHAPE_T_POLY)
    poly.SetPolyPoints([P(x - s / 2, y - s / 2), P(x + s / 2, y), P(x - s / 2, y + s / 2)])
    poly.SetFilled(True); poly.SetWidth(0); poly.SetLayer(FS)
    board.Add(poly)


def hide_refs(board):
    for fp in board.GetFootprints():
        r = fp.Reference()
        r.SetLayer(pcbnew.B_Fab if fp.IsFlipped() else pcbnew.F_Fab)
        r.SetVisible(True)


def apply(board, art):
    hide_refs(board)
    # ---------------- FRONT ----------------
    # logo, marquee, key letters and BOOT are exposed copper now (art_copper.py)
    text(board, '2026 · THE SECURITY SUMMIT', 28, 23.3, 1.2, thick=0.2)
    text(board, 'FOR RESEARCHERS / BY RESEARCHERS', 28, 25.1, 1.2, thick=0.2)
    # product window (notched at the bottom right for the keypad bezel), shelf with dispensing coil, snack boxes
    polyline(board, [(9, 26.2), (53, 26.2), (53, 61.0), (38.4, 61.0), (38.4, 64.6), (9, 64.6)], w=0.2)
    line(board, 10.2, 40.0, 51.8, 40.0, w=0.2)
    coil(board, 10.4, 25.0, 40.0)        # gap for C12 / Y1 under the middle of the shelf
    coil(board, 32.0, 51.6, 40.0)
    for i, (x, price, kind) in enumerate(((14, '25¢', 'can'), (24, '50¢', 'cup'), (34, '75¢', 'bag'), (44, '$1', 'bar'))):
        rect(board, x - 3.4, 31.9, x + 3.4, 39.6, w=0.15)
        text(board, 'A%d  %s' % (i + 1, price), x, 29.3, 0.8)      # shelf price tags A1..A4
        product(board, kind, x)                                     # the WS2812 glows inside the product
    line(board, 10.0, 63.5, 13.5, 54.0, w=0.25); line(board, 11.6, 63.5, 14.0, 57.0, w=0.2)   # glass glare, lower-left pane
    text(board, '← PRIZE', 41.5, 50.3, 1.0)                        # the RP2040 is the prize behind the glass
    text(board, 'RESET', 49.5, 48.6, 0.8)                          # SW6 (rev 0.6)
    text(board, 'J2  HACK PORT', 8.1, 36.0, 0.9, angle=90)
    # credit meter: five LEDs = coins inserted
    rect(board, 9, 65.4, 33, 73.0, w=0.2)
    for x, v in ((12, '5¢'), (16, '10¢'), (20, '25¢'), (24, '50¢'), (28, '$1')):
        text(board, v, x, 70.75, 0.8)
    text(board, 'CREDIT', 21, 72.25, 1.0, thick=0.18)
    # keypad bezel with SELECT; key letters stay beside the keys
    text(board, 'SELECT', 43.2, 59.8, 0.8)
    rect(board, 38.4, 61.0, 48.0, 80.4, w=0.2)
    # item pickup door: the three SAO slots B1..B3 (2x3 SMD sockets at rot 90, pin 1 = top-left pad, marked)
    text(board, 'ITEM PICKUP', 13.45, 77.3, 0.8)
    rect(board, 0.6, 78.4, 26.9, 89.5, w=0.2)
    for x, name in ((4.65, 'B1 IR'), (13.45, 'B2 AUDIO'), (22.25, 'B3 SPK')):
        text(board, name, x, 79.3, 0.8, thick=0.15)
        pin1(board, x - 3.75, 81.98)
    text(board, 'USB-C', 53.3, 78.1, 0.8)
    # coin slot: the UART test pads are the coins
    circle(board, 32.9, 92.3, 0.9, w=0.18); text(board, '¢', 32.9, 92.3, 0.8)   # the coin
    text(board, 'INSERT COIN →', 40.3, 92.3, 1.0)
    rect(board, 46.7, 91.1, 47.3, 93.5, w=0, fill=True)
    text(board, 'TX', 37.0, 97.0, 0.9); text(board, 'RX', 40.5, 97.0, 0.9); text(board, 'GND', 44.0, 97.0, 0.9)
    text(board, '3×AAA', 12.2, 94.4, 1.0)
    text(board, '+', 17.6, 97.4, 1.2, thick=0.2); text(board, '−', 22.5, 97.4, 1.2, thick=0.2)
    # ---------------- BREAKAWAY MODULES = soda cans (front: rims, label band; back: name + where it plugs in) --------
    for name, (x1, y1, x2, y2, tx) in MODULES.items():
        X = lambda v: x1 + v
        Y = lambda v: y1 + v
        code, slot = {'IR': ('B1', 'J5'), 'AUDIO': ('B2', 'J6'), 'SPK': ('B3', 'J7')}[name]
        circle(board, tx, 101.1, 0.6)                        # pull tab on the stub that stays on the can
        line(board, X(1.1), Y(0.7), X(11.9), Y(0.7))        # top rim (the bottom of the can is the SAO header now)
        pin1(board, X(1.55), Y(16.06))                      # SAO header pin 1 (top-left pad)
        if name == 'IR':
            line(board, X(0.7), Y(11.3), X(12.3), Y(11.3)); line(board, X(0.7), Y(14.6), X(12.3), Y(14.6))
            text(board, 'B1 · IR COLA', X(6.5), Y(12.35), 0.8, thick=0.15)
            text(board, '38 kHz', X(6.5), Y(13.75), 0.8)
        elif name == 'AUDIO':
            text(board, 'B2', X(0.85), Y(18.6), 0.8, angle=90)
            text(board, 'AUDIO POP', X(12.05), Y(18.6), 0.8, angle=90)
        else:
            text(board, 'B3', X(0.85), Y(18.6), 0.8, angle=90)
            text(board, 'BEEP FIZZ', X(12.05), Y(18.6), 0.8, angle=90)
        cx = (x1 + x2) / 2
        text(board, code + ' ' + name + ' MODULE', cx, Y(11.0), 0.8, layer=BS, thick=0.15)
        text(board, 'snap off,', cx, Y(13.0), 0.8, layer=BS)
        text(board, 'plug into ' + slot, cx, Y(14.6), 0.8, layer=BS)
    # ---------------- BACK: service panel ----------------
    text(board, 'TEAM', 52, 11.5, 1.6, layer=BS, just='L', thick=0.25)
    for i, n in enumerate(TEAM):
        text(board, n, 52, 13.9 + 2.0 * i, 1.3, layer=BS, just='L', thick=0.2)
    rect(board, 5, 9.5, 19, 23.5, layer=BS, w=0.15, dash=(0.8, 0.5))
    text(board, 'QR', 12, 16.0, 1.6, layer=BS, thick=0.25)
    text(board, 'repo link later', 12, 18.4, 0.9, layer=BS)
    rect(board, 10, 26, 46, 76, layer=BS, w=0.15, dash=(1.2, 0.8))
    text(board, 'SERVICE COMPARTMENT', 28, 27.8, 1.0, layer=BS, thick=0.18)
    text(board, 'AUTHORIZED PERSONNEL ONLY', 28, 29.4, 0.8, layer=BS)
    text(board, 'MODEL VM-2026 · 3V3 · 2 LAYERS', 28, 31.0, 0.8, layer=BS)
    text(board, 'NO USER-SERVICEABLE PARTS INSIDE (JK, SEE J2)', 28, 32.6, 0.8, layer=BS)
    text(board, '3×AAA BATTERY BOX · tape here · switch on box', 28, 34.4, 0.85, layer=BS)
    for cx in (18, 28, 38):                                   # the three cells, drawn where they will sit
        rect(board, cx - 4.5, 36.5, cx + 4.5, 73.5, layer=BS, w=0.2)
        rect(board, cx - 1.2, 35.6, cx + 1.2, 36.5, layer=BS, w=0.15)
        text(board, 'AAA', cx, 55.0, 1.8, layer=BS, angle=90, thick=0.3)
        text(board, '+', cx, 38.8, 1.3, layer=BS, thick=0.22); text(board, '−', cx, 71.3, 1.3, layer=BS, thick=0.22)
    # service sticker in the free strip beside the compartment (back-view left): warning triangle + service log
    polyline(board, [(51.2, 33.2), (47.8, 39.2), (54.6, 39.2)], layer=BS, w=0.25)
    polyline(board, [(51.6, 34.8), (50.5, 36.9), (51.3, 36.9), (50.8, 38.5), (52.0, 36.3), (51.2, 36.3), (51.8, 34.8)], layer=BS, w=0.2, close=False)
    text(board, 'DANGER', 51.2, 40.6, 0.9, layer=BS, thick=0.16)
    text(board, '3V3 INSIDE', 51.2, 42.1, 0.8, layer=BS)
    text(board, 'SERVICE LOG', 48.6, 58.0, 0.9, layer=BS, angle=90)
    for x in (50.6, 52.4, 54.2):
        line(board, x, 46.0, x, 70.0, layer=BS, w=0.15)
    rect(board, 22.0, 77.4, 46.5, 84.4, layer=BS, w=0.15)
    text(board, 'J2: 3V3 LOGIC ONLY \u2014 NO 5V', 34.25, 79.4, 1.1, layer=BS, thick=0.2)
    text(board, 'INTENT 2026 badge \u00b7 rev 0.6 \u00b7 2026-10', 34.25, 82.4, 0.9, layer=BS)
    text(board, 'battery lead \u2192 J3 (front, bottom)', 34.25, 86.8, 0.9, layer=BS)
    text(board, 'NO REFUNDS · DO NOT TILT OR ROCK', 34.25, 89.0, 0.9, layer=BS)
    text(board, 'JLCJLCJLCJLC', 4.9, 68.0, 1.0, layer=BS, angle=90)
