"""Silkscreen artwork for the INTENT 2026 badge (front + back).  Board coordinates (front view).

Vending-machine theme (rev 0.5): price-tagged shelf items A1-A4 (the RGB LEDs) over a dispensing coil, a keypad
bezel with SELECT, a CREDIT meter with coin values, an ITEM PICKUP door around the three module slots B1-B3, a coin
slot by the UART test pads, service-panel texts on the back. The breakaway modules are the vended items: B1 IR
"EYE CANDY" (candy bar wrapper), B2 "AUDIO POP" (soda can), B3 "BEEP CHIPS" (chips bag)."""
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


def hide_refs(board):
    for fp in board.GetFootprints():
        r = fp.Reference()
        r.SetLayer(pcbnew.B_Fab if fp.IsFlipped() else pcbnew.F_Fab)
        r.SetVisible(True)


def apply(board, art):
    hide_refs(board)
    # ---------------- FRONT ----------------
    if art:
        logo(board, art)
    text(board, '2026 · THE SECURITY SUMMIT', 28, 22.5, 1.2, thick=0.2)
    text(board, 'FOR RESEARCHERS / BY RESEARCHERS', 28, 24.5, 1.2, thick=0.2)
    # product window (notched at the bottom right for the keypad bezel), shelf with dispensing coil, snack boxes
    polyline(board, [(9, 26.2), (53, 26.2), (53, 61.0), (38.4, 61.0), (38.4, 64.6), (9, 64.6)], w=0.2)
    line(board, 10.2, 40.0, 51.8, 40.0, w=0.2)
    coil(board, 10.4, 25.0, 40.0)        # gap for C12 / Y1 under the middle of the shelf
    coil(board, 32.0, 51.6, 40.0)
    for i, (x, price) in enumerate(((14, '25¢'), (24, '50¢'), (34, '75¢'), (44, '$1'))):
        rect(board, x - 3.4, 31.9, x + 3.4, 39.6, w=0.15)
        text(board, 'A%d  %s' % (i + 1, price), x, 29.3, 0.8)      # shelf price tags A1..A4
    text(board, 'BOOT', 50.6, 32.9, 1.0)
    text(board, '← PRIZE', 41.5, 50.3, 1.0)                        # the RP2040 is the prize behind the glass
    text(board, 'J2  HACK PORT', 8.1, 36.0, 0.9, angle=90)
    # credit meter: five LEDs = coins inserted
    rect(board, 9, 65.4, 33, 73.0, w=0.2)
    for x, v in ((12, '5¢'), (16, '10¢'), (20, '25¢'), (24, '50¢'), (28, '$1')):
        text(board, v, x, 70.75, 0.8)
    text(board, 'CREDIT', 21, 72.25, 1.0, thick=0.18)
    # keypad bezel with SELECT; key letters stay beside the keys
    text(board, 'SELECT', 43.2, 59.8, 0.8)
    rect(board, 38.4, 61.0, 48.0, 80.4, w=0.2)
    for y, c in ((65, 'A'), (71, 'B'), (77, 'C')):
        text(board, c, 49.7, y, 1.8, thick=0.3)
    # item pickup door: the three module slots B1..B3 (1x3 sockets, pin 1 = GND at the top)
    text(board, 'ITEM PICKUP', 12.5, 77.4, 0.8)
    rect(board, 1.2, 78.4, 23.8, 89.2, w=0.2)
    for x, name in ((4.5, 'B1 IR'), (11.5, 'B2 AUDIO'), (18.5, 'B3 SPK')):
        text(board, name, x, 79.6, 0.8, thick=0.15)
    for y, c in ((82.46, 'G'), (85.0, '+'), (87.54, 'S')):
        text(board, c, 21.3, y, 0.8, just='L')
    text(board, 'USB-C', 53.3, 78.1, 0.8)
    # coin slot: the UART test pads are the coins
    text(board, 'INSERT COIN →', 40.3, 92.3, 1.0)
    rect(board, 46.7, 91.1, 47.3, 93.5, w=0, fill=True)
    text(board, 'TX', 37.0, 97.0, 0.9); text(board, 'RX', 40.5, 97.0, 0.9); text(board, 'GND', 44.0, 97.0, 0.9)
    text(board, '3×AAA', 12.2, 94.4, 1.0)
    text(board, '+', 17.6, 97.4, 1.2, thick=0.2); text(board, '−', 22.5, 97.4, 1.2, thick=0.2)
    # ---------------- BREAKAWAY MODULES = vended items (front art, back: name + where it plugs in) ----------------
    for name, (x1, y1, x2, y2, tx) in MODULES.items():
        hx = x1 + {'IR': 5.46, 'AUDIO': 5.96, 'SPK': 5.96}[name]
        for i, c in enumerate(('G', '+', 'S')):
            text(board, c, hx + 2.54 * i, y1 + 15.2, 0.8)
        X = lambda v: x1 + v
        Y = lambda v: y1 + v
        if name == 'IR':
            # candy bar: wrapper with crimped ends, item code B1
            zigzag(board, X(0.95), Y(0.8), Y(11.2))
            zigzag(board, X(15.05), Y(0.8), Y(11.2))
            line(board, X(0.95), Y(0.8), X(15.05), Y(0.8)); line(board, X(0.95), Y(11.2), X(15.05), Y(11.2))
            text(board, 'B1', X(2.3), Y(1.75), 0.8)
            text(board, 'EYE CANDY', X(8.0), Y(7.8), 0.8)
            text(board, 'IR', X(3.4), Y(9.6), 0.8); text(board, '38kHz', X(12.3), Y(9.6), 0.8)
        elif name == 'AUDIO':
            # soda can lying on its side: the jack barrel is the opening, fizz bubbles, item code B2
            text(board, 'B2', X(13.3), Y(1.0), 0.8)
            circle(board, X(14.9), Y(9.6), 0.45); circle(board, X(13.8), Y(10.6), 0.3); circle(board, X(15.9), Y(8.4), 0.25)
            text(board, 'AUDIO POP · 3.5mm', X(8.5), Y(11.3), 0.8)
        else:
            # chips bag: crimped sides, item code B3
            zigzag(board, X(0.95), Y(2.4), Y(9.4))            # starts below the 2 mm corner chamfer
            zigzag(board, X(16.5), Y(5.0), Y(13.4), amp=0.25)
            text(board, 'B3', X(1.6), Y(10.0), 0.8)
            text(board, 'BEEP CHIPS', X(8.0), Y(11.2), 0.8)
        slot, code = {'IR': ('J5', 'B1'), 'AUDIO': ('J6', 'B2'), 'SPK': ('J7', 'B3')}[name]
        cx = (x1 + x2) / 2
        text(board, code + ' · ' + name + ' MODULE', cx, y1 + 8.6, 0.9, layer=BS, thick=0.15)
        text(board, 'snap off, plug into ' + slot, cx, y1 + 10.7, 0.8, layer=BS)
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
    text(board, '3×AAA BATTERY BOX', 28, 49.6, 1.6, layer=BS, thick=0.25)
    text(board, 'tape here · switch on box', 28, 52.2, 1.1, layer=BS)
    rect(board, 22.0, 77.4, 46.5, 84.4, layer=BS, w=0.15)
    text(board, 'J2: 3V3 LOGIC ONLY \u2014 NO 5V', 34.25, 79.4, 1.1, layer=BS, thick=0.2)
    text(board, 'INTENT 2026 badge \u00b7 rev 0.5 \u00b7 2026-10', 34.25, 82.4, 0.9, layer=BS)
    text(board, 'battery lead \u2192 J3 (front, bottom)', 34.25, 86.8, 0.9, layer=BS)
    text(board, 'NO REFUNDS · DO NOT TILT OR ROCK', 34.25, 89.0, 0.9, layer=BS)
    text(board, 'SW5: optional (DNP)', 18.6, 92.6, 0.8, layer=BS)
    text(board, 'JP1: cut for SW5', 18.6, 94.4, 0.8, layer=BS)
    text(board, 'JLCJLCJLCJLC', 4.9, 68.0, 1.0, layer=BS, angle=90)
