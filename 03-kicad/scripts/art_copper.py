"""Exposed-copper art for the INTENT 2026 badge: gold with ENIG, silver with lead-free HASL.

INTENT logo, the INTENT-O-MATIC marquee, the key letters A/B/C, BOOT, and the rims of the soda cans. Logo and
texts are isolated copper graphics on F.Cu (no net, the GND pour keeps its clearance) with the same shape on F.Mask
to open the mask; the can rims are mask openings over the module ground pours. Only regions without signal tracks
on F.Cu are used: placement.ART_KEEPOUTS lists them and router/prune_routes.py --art drops the GND stitching vias
there. Called by pcb_finish.py before the zone fill."""
import pcbnew
from pcb_build import OX, OY, mm, P, MODULES

FCU, FMASK = pcbnew.F_Cu, pcbnew.F_Mask


def polys(board, art, layer):
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
            s.SetLayer(layer)
            board.Add(s)


def ctext(board, s, x, y, size, thick, bold=False):
    """Copper text + matching mask opening."""
    for layer in (FCU, FMASK):
        t = pcbnew.PCB_TEXT(board)
        t.SetText(s)
        t.SetLayer(layer)
        t.SetPosition(P(x, y))
        t.SetTextSize(pcbnew.VECTOR2I(mm(size), mm(size)))
        t.SetTextThickness(mm(thick))
        if bold:
            t.SetBold(True)
        t.SetHorizJustify(pcbnew.GR_TEXT_H_ALIGN_CENTER)
        board.Add(t)


def mask_rect(board, x1, y1, x2, y2):
    s = pcbnew.PCB_SHAPE(board)
    s.SetShape(pcbnew.SHAPE_T_RECT)
    s.SetStart(P(x1, y1)); s.SetEnd(P(x2, y2))
    s.SetLayer(FMASK); s.SetWidth(0); s.SetFilled(True)
    board.Add(s)


def apply(board, art):
    if art:
        polys(board, art, FCU)
        polys(board, art, FMASK)
    ctext(board, 'INTENT-O-MATIC', 28, 4.6, 1.8, 0.3, bold=True)        # header sign marquee
    for y, c in ((65, 'A'), (71, 'B'), (77, 'C')):                       # keypad letters
        ctext(board, c, 49.7, y, 1.8, 0.32)
    ctext(board, 'BOOT', 50.6, 32.9, 1.0, 0.18)
    for name, (x1, y1, x2, y2, tx) in MODULES.items():                   # can rims over the module ground pours
        rx1, rx2 = (4.2, 8.8) if name == 'SPK' else (2.4, 10.6)          # SPK: stay clear of the LS1 corner pads
        mask_rect(board, x1 + rx1, y1 + 0.45, x1 + rx2, y1 + 0.95)      # top rim only: the SAO header pads reach y1 + 21.6
