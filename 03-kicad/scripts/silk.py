"""Silkscreen artwork for the INTENT 2026 badge (front + back).  Board coordinates (front view)."""
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


def rect(board, x1, y1, x2, y2, layer=FS, w=0.15, dash=None):
    if dash:
        for (a, b, c, d) in ((x1, y1, x2, y1), (x2, y1, x2, y2), (x2, y2, x1, y2), (x1, y2, x1, y1)):
            dashed(board, a, b, c, d, layer, w, dash)
        return
    s = pcbnew.PCB_SHAPE(board)
    s.SetShape(pcbnew.SHAPE_T_RECT)
    s.SetStart(P(x1, y1)); s.SetEnd(P(x2, y2))
    s.SetLayer(layer); s.SetWidth(mm(w)); s.SetFilled(False)
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
    # product window + shelf + snack boxes
    rect(board, 9, 26.2, 53, 64.6, w=0.2)
    line(board, 10.2, 40.0, 51.8, 40.0, w=0.2)
    for x in (14, 24, 34, 44):
        rect(board, x - 3.4, 31.9, x + 3.4, 39.6, w=0.15)
    text(board, 'BOOT', 50.6, 32.9, 1.0)
    text(board, '* PRIZE *', 41.0, 60.4, 1.0)
    text(board, 'J2  HACK PORT', 5.6, 29.4, 0.9, just='L')
    # credit display + keypad
    rect(board, 9, 65.4, 33, 73.0, w=0.2)
    text(board, 'CREDIT', 21, 71.9, 1.1, thick=0.18)
    for y, c in ((65, 'A'), (71, 'B'), (77, 'C')):
        text(board, c, 49.7, y, 1.8, thick=0.3)
    # coin / dispense area: three expansion slots (1x3 sockets), pin 1 = GND at the top
    for x, name in ((4.5, 'IR'), (11.5, 'AUDIO'), (18.5, 'SPK')):
        text(board, name, x, 79.6, 0.9, thick=0.15)
    for y, c in ((82.46, 'G'), (85.0, '+'), (87.54, 'S')):
        text(board, c, 21.3, y, 0.8, just='L')
    text(board, 'USB-C', 53.3, 78.1, 0.8)
    text(board, 'INSERT COIN →', 40.6, 92.3, 1.0)
    text(board, 'TX', 37.0, 97.0, 0.9); text(board, 'RX', 40.5, 97.0, 0.9); text(board, 'GND', 44.0, 97.0, 0.9)
    text(board, '3×AAA', 12.2, 94.4, 1.0)
    text(board, '+', 17.6, 97.4, 1.2, thick=0.2); text(board, '−', 22.5, 97.4, 1.2, thick=0.2)
    # ---------------- BREAKAWAY MODULES (front: labels; back: name + where it plugs in) ----------------
    for name, (x1, y1, x2, y2, tx) in MODULES.items():
        hx = x1 + {'IR': 5.46, 'AUDIO': 5.96, 'SPK': 5.96}[name]
        for i, c in enumerate(('G', '+', 'S')):
            text(board, c, hx + 2.54 * i, y1 + 15.2, 0.8)
        if name == 'IR':
            text(board, 'IR EYE', x1 + 13.0, y1 + 9.0, 0.8)
        elif name == 'AUDIO':
            text(board, 'AUDIO', x1 + 8.5, y1 + 11.15, 0.8)
        else:
            text(board, 'SPK', x1 + 8.0, y1 + 11.15, 0.8)
        slot = {'IR': 'J5', 'AUDIO': 'J6', 'SPK': 'J7'}[name]
        cx = (x1 + x2) / 2
        text(board, name + ' MODULE', cx, y1 + 8.6, 1.0, layer=BS, thick=0.16)
        text(board, 'snap off, plug into ' + slot, cx, y1 + 10.7, 0.8, layer=BS)
    # ---------------- BACK ----------------
    text(board, 'TEAM', 52, 11.5, 1.6, layer=BS, just='L', thick=0.25)
    for i, n in enumerate(TEAM):
        text(board, n, 52, 13.9 + 2.0 * i, 1.3, layer=BS, just='L', thick=0.2)
    rect(board, 5, 9.5, 19, 23.5, layer=BS, w=0.15, dash=(0.8, 0.5))
    text(board, 'QR', 12, 16.0, 1.6, layer=BS, thick=0.25)
    text(board, 'repo link later', 12, 18.4, 0.9, layer=BS)
    rect(board, 10, 26, 46, 76, layer=BS, w=0.15, dash=(1.2, 0.8))
    text(board, '3×AAA BATTERY BOX', 28, 49.6, 1.6, layer=BS, thick=0.25)
    text(board, 'tape here · switch on box', 28, 52.2, 1.1, layer=BS)
    rect(board, 22.0, 77.4, 46.5, 84.4, layer=BS, w=0.15)
    text(board, 'J2: 3V3 LOGIC ONLY \u2014 NO 5V', 34.25, 79.4, 1.1, layer=BS, thick=0.2)
    text(board, 'INTENT 2026 badge \u00b7 rev 0.5 \u00b7 2026-10', 34.25, 82.4, 0.9, layer=BS)
    text(board, 'battery lead \u2192 J3 (front, bottom)', 34.25, 86.8, 0.9, layer=BS)
    text(board, 'SW5: optional (DNP)', 18.6, 92.6, 0.8, layer=BS)
    text(board, 'JP1: cut for SW5', 18.6, 94.4, 0.8, layer=BS)
    text(board, 'JLCJLCJLCJLC', 4.9, 68.0, 1.0, layer=BS, angle=90)
