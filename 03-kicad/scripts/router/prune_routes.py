"""Prepare routes.json for a partial re-route.

usage: python3 prune_routes.py <geo.json> <routes.json> <out_main.json> [net_prefixes=IRM_,AUM_,SPM_]
       python3 prune_routes.py --merge <main.json> <modules.json> <out_routes.json>

Pass 1 drops the copper of the given net prefixes (to be re-routed) and every GND track/via that no longer fits the
board outline in geo.json (stitching vias at edges that moved) or sits inside the clearance ring of an unconnected
pad (lanyard holes).  Copper of any other net that conflicts with the new
outline is reported and kept, so the problem is visible.  --merge concatenates the kept copper with the new routes.
"""
import sys, json
from shapely.geometry import Polygon, Point, LineString

EDGE_CLR = 0.3


def main():
    a = sys.argv[1:]
    if a and a[0] == '--merge':
        m = json.load(open(a[1])); n = json.load(open(a[2]))
        out = dict(tracks=m['tracks'] + n['tracks'], vias=m['vias'] + n['vias'],
                   unrouted=n.get('unrouted', {}), conflicts=n.get('conflicts', {}))
        json.dump(out, open(a[3], 'w'), indent=0)
        print('merged: tracks', len(out['tracks']), 'vias', len(out['vias']), 'unrouted', out['unrouted'], 'conflicts', out['conflicts'])
        return
    geo = json.load(open(a[0])); routes = json.load(open(a[1]))
    pre = tuple((a[3] if len(a) > 3 else 'IRM_,AUM_,SPM_').split(','))
    board = Polygon(geo['outline'])
    # unconnected pads with their own clearance (lanyard holes): GND copper inside that ring is dropped as well
    keepouts = [(Polygon(p['poly']), p['clearance']) for p in geo['pads'] if not p['net'] and p.get('clearance', 0) > 0]
    keep_t, keep_v, drop_mod, drop_gnd, bad = [], [], 0, 0, []

    def fits(g, r):
        if not (board.contains(g) and board.exterior.distance(g) >= r + EDGE_CLR - 1e-6):
            return False
        return all(kp.distance(g) >= clr + r - 1e-6 for kp, clr in keepouts)
    for t in routes['tracks']:
        if t['net'].startswith(pre):
            drop_mod += 1; continue
        g = LineString([(t['x1'], t['y1']), (t['x2'], t['y2'])])
        if not fits(g, t['w'] / 2):
            if t['net'] == 'GND':
                drop_gnd += 1; continue
            bad.append(('track', t['net'], round(t['x1'], 2), round(t['y1'], 2)))
        keep_t.append(t)
    for v in routes['vias']:
        if v['net'].startswith(pre):
            drop_mod += 1; continue
        if not fits(Point(v['x'], v['y']), v['d'] / 2):
            if v['net'] == 'GND':
                drop_gnd += 1; continue
            bad.append(('via', v['net'], round(v['x'], 2), round(v['y'], 2)))
        keep_v.append(v)
    json.dump(dict(tracks=keep_t, vias=keep_v), open(a[2], 'w'), indent=0)
    print('kept tracks', len(keep_t), 'vias', len(keep_v), '| dropped module copper', drop_mod, '| dropped GND at edge', drop_gnd)
    if bad:
        print('WARNING: non-GND copper conflicts with the new outline:', bad[:20])


if __name__ == '__main__':
    main()
