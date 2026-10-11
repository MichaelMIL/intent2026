"""Stage A (run with KiCad's python): netlist + placement -> unrouted board + geometry JSON.

usage: python pcb_build.py <project_dir> <netlist.net> <geometry.json>
"""
import os, sys, json, math
sys.path.insert(0, os.path.dirname(__file__))
import pcbnew
from sexpr import parse, find, findall
import placement
from placement import MODULES, TAB_W, TAB_L

OX, OY = 100.0, 50.0          # board origin on the KiCad page
BOTTOM = ('L', (46.5, 100), (9.5, 100))   # pedestal bottom edge: the breakaway tabs hang from it
FPDIR = os.environ.get('KICAD9_FOOTPRINT_DIR', '/tmp/kroot/usr/share/kicad/footprints')


def mm(v):
    return pcbnew.FromMM(v)


def P(x, y):
    return pcbnew.VECTOR2I(mm(OX + x), mm(OY + y))


# board outline: vending-machine silhouette (02-layout/board-mockup.svg path)
def s45(r):
    return r * math.sqrt(0.5)


OUTLINE = [
    ('L', (6, 0), (50, 0)),
    ('A', (50, 0), (50 + s45(6), 6 - s45(6)), (56, 6)),
    ('L', (56, 6), (56, 88)),
    ('A', (56, 88), (54 + s45(2), 88 + s45(2)), (54, 90)),
    ('L', (54, 90), (49.5, 90)),
    ('A', (49.5, 90), (49.5 - s45(1.5), 91.5 - s45(1.5)), (48, 91.5)),
    ('L', (48, 91.5), (48, 98.5)),
    ('A', (48, 98.5), (46.5 + s45(1.5), 98.5 + s45(1.5)), (46.5, 100)),
    ('L', (46.5, 100), (9.5, 100)),
    ('A', (9.5, 100), (9.5 - s45(1.5), 98.5 + s45(1.5)), (8, 98.5)),
    ('L', (8, 98.5), (8, 91.5)),
    ('A', (8, 91.5), (6.5 + s45(1.5), 91.5 - s45(1.5)), (6.5, 90)),
    ('L', (6.5, 90), (2, 90)),
    ('A', (2, 90), (2 - s45(2), 88 + s45(2)), (0, 88)),
    ('L', (0, 88), (0, 6)),
    ('A', (0, 6), (6 - s45(6), 6 - s45(6)), (6, 0)),
]


def tab_x(name):
    tx = MODULES[name][4]
    return tx - TAB_W / 2, tx + TAB_W / 2


def modules_desc():
    """modules sorted by tab x descending = the order met when walking the pedestal edge right to left"""
    return sorted(MODULES, key=lambda n: -MODULES[n][4])


def bottom_detour():
    """Points replacing the straight pedestal bottom edge: down each tab, around its module, back up."""
    pts = [BOTTOM[1]]
    for name in modules_desc():
        mx1, my1, mx2, my2, _ = MODULES[name]
        tx1, tx2 = tab_x(name)
        pts += [(tx2, 100.0), (tx2, my1), (mx2, my1), (mx2, my2), (mx1, my2), (mx1, my1), (tx1, my1), (tx1, 100.0)]
    return pts


def outline_points(step_deg=5, with_modules=True):
    """Board outline as one polygon. with_modules=True includes the tabs and the breakaway modules (router,
    DRC); False gives the main badge only (ground pour, silkscreen)."""
    pts = []
    for seg in OUTLINE:
        if seg == BOTTOM and with_modules:
            pts += bottom_detour()
        elif seg[0] == 'L':
            pts.append(seg[1])
        else:
            (x1, y1), (xm, ym), (x2, y2) = seg[1], seg[2], seg[3]
            # circle through 3 points
            d = 2 * (x1 * (ym - y2) + xm * (y2 - y1) + x2 * (y1 - ym))
            ux = ((x1 ** 2 + y1 ** 2) * (ym - y2) + (xm ** 2 + ym ** 2) * (y2 - y1) + (x2 ** 2 + y2 ** 2) * (y1 - ym)) / d
            uy = ((x1 ** 2 + y1 ** 2) * (x2 - xm) + (xm ** 2 + ym ** 2) * (x1 - x2) + (x2 ** 2 + y2 ** 2) * (xm - x1)) / d
            r = math.hypot(x1 - ux, y1 - uy)
            a1 = math.atan2(y1 - uy, x1 - ux)
            am = math.atan2(ym - uy, xm - ux)
            a2 = math.atan2(y2 - uy, x2 - ux)

            def norm(a):
                while a < 0:
                    a += 2 * math.pi
                return a
            # direction: go from a1 through am to a2
            ccw = norm(am - a1) < norm(a2 - a1)
            span = norm(a2 - a1) if ccw else -norm(a1 - a2)
            n = max(2, int(abs(math.degrees(span)) / step_deg))
            for i in range(n):
                a = a1 + span * i / n
                pts.append((ux + r * math.cos(a), uy + r * math.sin(a)))
    return pts


def edge_line(board, a, b):
    s = pcbnew.PCB_SHAPE(board)
    s.SetLayer(pcbnew.Edge_Cuts)
    s.SetWidth(mm(0.1))
    s.SetShape(pcbnew.SHAPE_T_SEGMENT)
    s.SetStart(P(*a)); s.SetEnd(P(*b))
    board.Add(s)


def add_outline(board):
    for seg in OUTLINE:
        if seg == BOTTOM:
            continue
        s = pcbnew.PCB_SHAPE(board)
        s.SetLayer(pcbnew.Edge_Cuts)
        s.SetWidth(mm(0.1))
        if seg[0] == 'L':
            s.SetShape(pcbnew.SHAPE_T_SEGMENT)
            s.SetStart(P(*seg[1]))
            s.SetEnd(P(*seg[2]))
        else:
            s.SetShape(pcbnew.SHAPE_T_ARC)
            s.SetArcGeometry(P(*seg[1]), P(*seg[2]), P(*seg[3]))
        board.Add(s)
    # pedestal bottom edge in pieces between the tabs, then the tabs and the module rectangles
    x = BOTTOM[1][0]
    for name in modules_desc():
        mx1, my1, mx2, my2, _ = MODULES[name]
        tx1, tx2 = tab_x(name)
        edge_line(board, (x, 100.0), (tx2, 100.0))
        edge_line(board, (tx2, 100.0), (tx2, my1)); edge_line(board, (tx1, 100.0), (tx1, my1))
        edge_line(board, (mx1, my1), (tx1, my1)); edge_line(board, (tx2, my1), (mx2, my1))
        edge_line(board, (mx2, my1), (mx2, my2)); edge_line(board, (mx2, my2), (mx1, my2)); edge_line(board, (mx1, my2), (mx1, my1))
        x = tx1
    edge_line(board, (x, 100.0), BOTTOM[2])


def add_mousebites(board):
    """One board-only footprint per tab: 4 x 0.5 mm NPTH on the main-board edge line, so the badge keeps a clean
    pedestal and the stub stays on the module."""
    lib = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'intent.pretty')
    for i, name in enumerate(sorted(MODULES, key=lambda n: MODULES[n][4])):
        fp = pcbnew.FootprintLoad(lib, 'MouseBites_1x4_D0.5_P1.0')
        fp.SetFPID(pcbnew.LIB_ID('intent', 'MouseBites_1x4_D0.5_P1.0'))
        fp.SetReference('MB%d' % (i + 1))
        fp.SetValue('tab ' + name)
        board.Add(fp)
        fp.SetPosition(P(MODULES[name][4], 100.0))
        fp.SetBoardOnly(True)
        fp.SetExcludedFromBOM(True)
        fp.SetExcludedFromPosFiles(True)
        fp.Reference().SetVisible(False)
        fp.Value().SetVisible(False)


# stock footprints whose STEP model is not shipped with this KiCad install -> simplified VRML from gen_3d.py
FALLBACK_3D = ('SW_Push_1P1T_XKB_TS-1187A', 'LED_WS2812B-2020_PLCC4_2.0x2.0mm', 'SW_SPDT_Shouhan_MSK12C02')


def set_fallback_model(fp, name):
    if name not in FALLBACK_3D:
        return
    fp.Models().clear()
    m = pcbnew.FP_3DMODEL()
    m.m_Filename = '${KIPRJMOD}/intent.3dshapes/%s.wrl' % name
    fp.Models().push_back(m)


def load_netlist(path):
    tree = parse(open(path, encoding='utf-8').read())[0]
    comps = {}
    for c in findall(find(tree, 'components'), 'comp'):
        ref = find(c, 'ref')[1]
        fields = {}
        fl = find(c, 'fields')
        if fl:
            for fd in findall(fl, 'field'):
                nm = find(fd, 'name')[1]
                fields[nm] = fd[2] if len(fd) > 2 and not isinstance(fd[2], list) else ''
        props = {find(p, 'name')[1]: (find(p, 'value')[1] if find(p, 'value') else '') for p in findall(c, 'property')}
        sp = find(c, 'sheetpath')
        comps[ref] = dict(ref=ref, value=find(c, 'value')[1], fp=find(c, 'footprint')[1],
                          uuid=find(c, 'tstamps')[1], sheet=find(sp, 'tstamps')[1], fields=fields, props=props)
    nets = {}
    for n in findall(find(tree, 'nets'), 'net'):
        name = find(n, 'name')[1]
        nets[name] = [(find(nd, 'ref')[1], find(nd, 'pin')[1]) for nd in findall(n, 'node')]
    return comps, nets


def main(prj, netpath, geopath):
    comps, nets = load_netlist(netpath)
    pcbpath = os.path.join(prj, 'intent-2026-badge.kicad_pcb')
    board = pcbnew.NewBoard(pcbpath)
    board.SetCopperLayerCount(2)
    ds = board.GetDesignSettings()
    ds.SetBoardThickness(mm(1.6))
    tb = board.GetTitleBlock()
    tb.SetTitle('INTENT 2026 Hardware Badge')
    tb.SetRevision('0.5')
    tb.SetDate('2026-10-11')
    tb.SetCompany('INTENT 2026 - by Palo Alto Networks')
    add_outline(board)
    add_mousebites(board)

    netinfo = {}
    for name in sorted(nets):
        ni = pcbnew.NETINFO_ITEM(board, name)
        board.Add(ni)
        netinfo[name] = ni
    padnet = {}
    for name, nodes in nets.items():
        for ref, pin in nodes:
            padnet[(ref, pin)] = name

    for ref, c in sorted(comps.items()):
        lib, name = c['fp'].split(':')
        libpath = os.path.join(prj, 'intent.pretty') if lib == 'intent' else os.path.join(FPDIR, lib + '.pretty')
        fp = pcbnew.FootprintLoad(libpath, name)
        if fp is None:
            raise SystemExit('footprint not found: ' + c['fp'])
        fp.SetFPID(pcbnew.LIB_ID(lib, name))
        fp.SetReference(ref)
        fp.SetValue(c['value'])
        fp.SetPath(pcbnew.KIID_PATH(c['sheet'] + c['uuid']))
        for k in ('LCSC',):
            if c['fields'].get(k):
                fp.SetField(k, c['fields'][k])
                f = fp.GetFieldByName(k) if hasattr(fp, 'GetFieldByName') else fp.GetField(k)   # KiCad 9 / 10
                f.SetVisible(False)
                f.SetLayer(pcbnew.F_Fab)
        if c['fields'].get('Description'):
            pass
        dnp = 'dnp' in c['props']
        exbom = 'exclude_from_bom' in c['props']
        fp.SetDNP(dnp)
        fp.SetExcludedFromBOM(exbom or dnp)
        if dnp or exbom:
            fp.SetExcludedFromPosFiles(True)
        set_fallback_model(fp, name)
        x, y, rot, side = placement.get(ref)
        board.Add(fp)
        if side == 'B':
            fp.Flip(fp.GetPosition(), pcbnew.FLIP_DIRECTION_LEFT_RIGHT)
        fp.SetPosition(P(x, y))
        fp.SetOrientationDegrees(rot)
        for pad in fp.Pads():
            nn = padnet.get((ref, pad.GetNumber()))
            if nn:
                pad.SetNet(netinfo[nn])
        fp.Reference().SetTextSize(pcbnew.VECTOR2I(mm(0.8), mm(0.8)))
        fp.Reference().SetTextThickness(mm(0.12))

    pcbnew.SaveBoard(pcbpath, board)
    export_geometry(board, geopath)
    print('board saved', pcbpath)


def export_geometry(board, geopath):
    pads = []
    for fp in board.GetFootprints():
        for pad in fp.Pads():
            layers = []
            if pad.IsOnLayer(pcbnew.F_Cu):
                layers.append('F')
            if pad.IsOnLayer(pcbnew.B_Cu):
                layers.append('B')
            if not layers and pad.GetAttribute() != pcbnew.PAD_ATTRIB_NPTH:
                continue
            lay = pcbnew.F_Cu if 'F' in layers or not layers else pcbnew.B_Cu
            poly = pad.GetEffectivePolygon(lay, pcbnew.ERROR_INSIDE)
            outl = poly.Outline(0)
            pts = [(pcbnew.ToMM(outl.CPoint(i).x) - OX, pcbnew.ToMM(outl.CPoint(i).y) - OY) for i in range(outl.PointCount())]
            drill = 0.0
            if pad.HasHole():
                drill = max(pcbnew.ToMM(pad.GetDrillSize().x), pcbnew.ToMM(pad.GetDrillSize().y))
            npth = pad.GetAttribute() == pcbnew.PAD_ATTRIB_NPTH
            pos = pad.GetPosition()
            clr = pad.GetLocalClearance()
            pads.append(dict(ref=fp.GetReference(), num=pad.GetNumber(), net=pad.GetNetname(), layers=layers,
                             poly=pts, drill=drill, npth=npth,
                             x=pcbnew.ToMM(pos.x) - OX, y=pcbnew.ToMM(pos.y) - OY,
                             clearance=(pcbnew.ToMM(clr) if clr is not None and clr != 0 else 0.0),
                             smd=pad.GetAttribute() == pcbnew.PAD_ATTRIB_SMD))
    fps = []
    for fp in board.GetFootprints():
        bb = fp.GetBoundingBox(False)
        cy = fp.GetCourtyard(pcbnew.F_CrtYd if not fp.IsFlipped() else pcbnew.B_CrtYd)
        fps.append(dict(ref=fp.GetReference(), side='B' if fp.IsFlipped() else 'F',
                        x=pcbnew.ToMM(fp.GetPosition().x) - OX, y=pcbnew.ToMM(fp.GetPosition().y) - OY,
                        bbox=[pcbnew.ToMM(bb.GetLeft()) - OX, pcbnew.ToMM(bb.GetTop()) - OY,
                              pcbnew.ToMM(bb.GetRight()) - OX, pcbnew.ToMM(bb.GetBottom()) - OY]))
    json.dump(dict(pads=pads, footprints=fps, outline=outline_points(), main_outline=outline_points(5, False),
                   modules={n: list(v) for n, v in MODULES.items()}), open(geopath, 'w'), indent=0)


if __name__ == '__main__':
    main(*sys.argv[1:4])
