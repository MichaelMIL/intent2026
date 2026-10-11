"""Final GND pass on an existing routes.json: keep every non-GND net as routed, re-route all GND fan-outs with
hard clearance against them (same as route2's end-of-run pass), add stitching vias, report conflicts.
usage: python3 gnd_final.py geo.json routes.json [out.json]
Use when route2 ends with a few residual conflicts that all involve GND.
KEEP_GND=1: keep the existing GND copper too and only add stitching vias (route2 skips stitching when its final
GND pass leaves pads for the pour stage)."""
import sys, json, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import route2 as R


def main(geop, routesp, outp=None):
    geo = json.load(open(geop)); routes = json.load(open(routesp))
    rt = R.Router(geo)
    keep = os.environ.get('KEEP_GND') == '1'
    ftr = set((round(a[0], 2), round(a[1], 2), round(b[0], 2), round(b[1], 2)) for L, pts, w in rt.fixed.tracks for a, b in zip(pts[:-1], pts[1:]))
    for t in routes['tracks']:
        if t['net'] == 'GND' and not keep:
            continue
        if t['net'] == 'GND' and (round(t['x1'], 2), round(t['y1'], 2), round(t['x2'], 2), round(t['y2'], 2)) in ftr:
            continue          # fixed copper is re-created by Router()
        rt.routes[t['net']].add_track(0 if t['layer'] == 'F' else 1, [(t['x1'], t['y1']), (t['x2'], t['y2'])], t['w'])
    fixed = set((round(x, 2), round(y, 2)) for x, y in rt.fixed.vias)
    for v in routes['vias']:
        if v['net'] == 'GND' and not keep:
            continue
        if v['net'] == 'GND' and (round(v['x'], 2), round(v['y'], 2)) in fixed:
            continue          # EP / fixed vias are re-created by Router(); avoid co-located holes
        rt.routes[v['net']].add_via(v['x'], v['y'])
    before = rt.conflicts()
    print('conflicts among loaded nets:', before)
    rt.gnd_failed = routes.get('gnd_failed', [])
    if not keep:
        rt.gnd_subset = None
        rt.gnd_hard = True
        f = rt.route_gnd(rt.routes['GND'])
        print('GND fan-out failed pads:', f, ','.join(rt.gnd_failed))
    bad = rt.conflicts()
    print('conflicts after GND pass:', bad)
    if os.environ.get('STITCH', '1') == '1':
        print('stitching vias', rt.stitch())
        print('conflicts after stitching', rt.conflicts())
    data = rt.export()
    data['unrouted'] = {}; data['conflicts'] = bad; data['gnd_failed'] = rt.gnd_failed
    json.dump(data, open(outp or routesp, 'w'), indent=0)
    print('tracks', len(data['tracks']), 'vias', len(data['vias']))


if __name__ == '__main__':
    main(*sys.argv[1:4])
