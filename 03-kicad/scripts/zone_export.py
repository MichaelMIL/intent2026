"""(KiCad python) dump filled GND zone islands, drills and GND connection points for island_stitch.py.
usage: zone_export.py <board.kicad_pcb> <out.json>"""
import sys, json
import pcbnew
from pcb_build import OX, OY


def pts(chain):
    return [(pcbnew.ToMM(chain.CPoint(i).x) - OX, pcbnew.ToMM(chain.CPoint(i).y) - OY) for i in range(chain.PointCount())]


def main(path, out):
    b = pcbnew.LoadBoard(path)
    zones = {}
    for z in b.Zones():
        if z.GetNetname() != 'GND':
            continue
        for L, name in ((pcbnew.F_Cu, 'F'), (pcbnew.B_Cu, 'B')):
            if not z.IsOnLayer(L):
                continue
            ps = z.GetFilledPolysList(L)
            isl = []
            for k in range(ps.OutlineCount()):
                isl.append(dict(ext=pts(ps.Outline(k)), holes=[pts(ps.Hole(k, h)) for h in range(ps.HoleCount(k))]))
            zones.setdefault(name, []).extend(isl)
    drills, gnd_links = [], []
    for t in b.GetTracks():
        if t.Type() == pcbnew.PCB_VIA_T:
            p = t.GetPosition()
            x, y = pcbnew.ToMM(p.x) - OX, pcbnew.ToMM(p.y) - OY
            drills.append((x, y, pcbnew.ToMM(t.GetDrillValue())))
            if t.GetNetname() == 'GND':
                gnd_links.append((x, y))
    gnd_pads = []
    for fp in b.GetFootprints():
        for pad in fp.Pads():
            p = pad.GetPosition()
            x, y = pcbnew.ToMM(p.x) - OX, pcbnew.ToMM(p.y) - OY
            if pad.HasHole():
                drills.append((x, y, max(pcbnew.ToMM(pad.GetDrillSize().x), pcbnew.ToMM(pad.GetDrillSize().y))))
                if pad.GetNetname() == 'GND':
                    gnd_links.append((x, y))
    gtracks, gpads = [], []
    for t in b.GetTracks():
        if t.GetNetname() == 'GND' and t.Type() == pcbnew.PCB_TRACE_T:
            s, e = t.GetStart(), t.GetEnd()
            gtracks.append(dict(L='F' if t.GetLayer() == pcbnew.F_Cu else 'B', w=pcbnew.ToMM(t.GetWidth()),
                                p=[(pcbnew.ToMM(s.x) - OX, pcbnew.ToMM(s.y) - OY), (pcbnew.ToMM(e.x) - OX, pcbnew.ToMM(e.y) - OY)]))
    for fp in b.GetFootprints():
        for pad in fp.Pads():
            if pad.GetNetname() != 'GND':
                continue
            for L, name in ((pcbnew.F_Cu, 'F'), (pcbnew.B_Cu, 'B')):
                if pad.IsOnLayer(L):
                    poly = pad.GetEffectivePolygon(L, pcbnew.ERROR_INSIDE)
                    gpads.append(dict(L=name, ref=fp.GetReference() + '.' + pad.GetNumber(), poly=pts(poly.Outline(0)),
                                      tht=pad.HasHole()))
    json.dump(dict(zones=zones, drills=drills, gnd_links=gnd_links, gtracks=gtracks, gpads=gpads), open(out, 'w'))


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
