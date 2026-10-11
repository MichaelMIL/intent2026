"""Stage C (KiCad python): add routes, GND pours, silkscreen art; fill zones; save.

usage: python pcb_finish.py <project_dir> <routes.json> <art.json>
"""
import os, sys, json
sys.path.insert(0, os.path.dirname(__file__))
import pcbnew
from pcb_build import OX, OY, mm, P, outline_points, MODULES
import design
import silk
import art_copper

LAY = {'F': pcbnew.F_Cu, 'B': pcbnew.B_Cu}


def add_routes(board, routes):
    nets = board.GetNetsByName()
    for t in routes['tracks']:
        tr = pcbnew.PCB_TRACK(board)
        tr.SetStart(P(t['x1'], t['y1'])); tr.SetEnd(P(t['x2'], t['y2']))
        tr.SetWidth(mm(t['w'])); tr.SetLayer(LAY[t['layer']])
        tr.SetNet(nets[t['net']])
        board.Add(tr)
    for v in routes['vias']:
        via = pcbnew.PCB_VIA(board)
        via.SetPosition(P(v['x'], v['y']))
        via.SetWidth(mm(v['d'])); via.SetDrill(mm(v['drill']))
        via.SetViaType(pcbnew.VIATYPE_THROUGH)
        via.SetLayerPair(pcbnew.F_Cu, pcbnew.B_Cu)
        via.SetNet(nets[v['net']])
        board.Add(via)


def add_zone(board, layer, net, pts, name, priority=0):
    """Ground pour over pts (board mm). The main pour covers the badge only, never the breakaway tabs; each
    module gets its own pour on its own ground net, so no copper crosses a tab."""
    z = pcbnew.ZONE(board)
    z.SetLayer(layer)
    z.SetNet(board.GetNetsByName()[net])
    z.SetAssignedPriority(priority)
    z.SetLocalClearance(mm(0.25))
    z.SetMinThickness(mm(0.25))
    z.SetThermalReliefGap(mm(0.3))
    z.SetThermalReliefSpokeWidth(mm(0.35))
    z.SetPadConnection(pcbnew.ZONE_CONNECTION_THERMAL)
    z.SetIslandRemovalMode(pcbnew.ISLAND_REMOVAL_MODE_ALWAYS)
    z.SetZoneName(name + '_' + ('TOP' if layer == pcbnew.F_Cu else 'BOT'))
    ol = z.Outline()
    ol.NewOutline()
    for x, y in pts:
        ol.Append(mm(OX + x), mm(OY + y))
    board.Add(z)
    return z


def main(prj, routes_path, art_path):
    pcbpath = os.path.join(prj, 'intent-2026-badge.kicad_pcb')
    stage_a = os.path.join(prj, 'stage_a.kicad_pcb')
    board = pcbnew.LoadBoard(stage_a if os.path.exists(stage_a) else pcbpath)
    routes = json.load(open(routes_path))
    ds = board.GetDesignSettings()
    ds.m_TentViasFront = True
    ds.m_TentViasBack = True
    add_routes(board, routes)
    extra = os.path.join(prj, 'stitch_extra.json')
    if os.path.exists(extra):
        ev = json.load(open(extra))
        add_routes(board, dict(tracks=[], vias=ev))
        print('island-stitch vias added:', len(ev))
    for L in (pcbnew.B_Cu, pcbnew.F_Cu):
        add_zone(board, L, 'GND', outline_points(5, with_modules=False), 'GND')
        for name, (x1, y1, x2, y2, _) in MODULES.items():
            add_zone(board, L, design.MODULES[name]['gnd'], [(x1, y1), (x2, y1), (x2, y2), (x1, y2)], name + '_GND')
    art = json.load(open(art_path)) if art_path and os.path.exists(art_path) else None
    art_copper.apply(board, art)
    silk.apply(board, art)
    filler = pcbnew.ZONE_FILLER(board)
    filler.Fill(board.Zones())
    pcbnew.SaveBoard(pcbpath, board)
    print('finished', pcbpath, 'tracks', len(routes['tracks']), 'vias', len(routes['vias']))


if __name__ == '__main__':
    main(*sys.argv[1:4])
