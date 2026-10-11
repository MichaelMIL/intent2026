"""Connect isolated GND groups (found by island_stitch analysis) to the main ground with extra GND tracks/vias.

usage: python3 gnd_repair.py geo.json routes.json zones.json   (routes.json is updated in place)
All copper of other nets is a hard obstacle; the target is the interior of the main-ground pour.
"""
import sys, json, os
import numpy as np
import shapely
from shapely.geometry import Polygon, Point, LineString
from shapely.ops import unary_union
from shapely.strtree import STRtree
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import route2 as R


def components(z):
    items = []
    for L in ('F', 'B'):
        for isl in z['zones'].get(L, []):
            pg = Polygon(isl['ext'], isl['holes']).buffer(0)
            if pg.area > 0:
                items.append(({L}, pg, 'island'))
    for t in z['gtracks']:
        items.append(({t['L']}, LineString(t['p']).buffer(t['w'] / 2), 'track'))
    for x, y in z['gnd_links']:
        items.append(({'F', 'B'}, Point(x, y).buffer(0.25), 'via'))
    for p in z['gpads']:
        items.append(({p['L']}, Polygon(p['poly']).buffer(0), 'pad ' + p['ref']))
    n = len(items)
    parent = list(range(n))

    def find(a):
        while parent[a] != a:
            parent[a] = parent[parent[a]]; a = parent[a]
        return a
    for L in ('F', 'B'):
        idx = [i for i in range(n) if L in items[i][0]]
        geoms = [items[i][1] for i in idx]
        tree = STRtree(geoms)
        for k, i in enumerate(idx):
            for j in tree.query(geoms[k].buffer(0.02)):
                if idx[j] != i and geoms[k].distance(items[idx[j]][1]) < 0.02:
                    parent[find(idx[j])] = find(i)
    comps = {}
    for i in range(n):
        comps.setdefault(find(i), []).append(i)
    area = lambda c: sum(items[i][1].area for i in c if items[i][2] == 'island')
    main_c = max(comps.values(), key=area)
    return items, comps, main_c


def main(geop, routesp, zonesp):
    geo = json.load(open(geop)); routes = json.load(open(routesp)); z = json.load(open(zonesp))
    items, comps, main_c = components(z)
    iso = [c for c in comps.values() if c is not main_c]
    print('isolated GND groups:', len(iso))
    if not iso:
        return
    rt = R.Router(geo)
    # load existing copper
    for t in routes['tracks']:
        r = rt.routes.get(t['net']) or rt.fixed
        r.add_track(0 if t['layer'] == 'F' else 1, [(t['x1'], t['y1']), (t['x2'], t['y2'])], t['w'])
    for v in routes['vias']:
        r = rt.routes.get(v['net']) or rt.fixed
        r.add_via(v['x'], v['y'])
    rt.fixed.name = 'GND'
    w = float(os.environ.get('REPAIR_W', '0.25'))
    free, via, pen, vpen, ft = rt.masks('GND', w)
    rr = R.CLR + w / 2 + R.MARGIN
    vr = R.CLR + R.VIA_D / 2 + R.MARGIN
    free = [(free[L] & (ft[L] >= rr)).astype(np.uint8) for L in (0, 1)]
    via = (via & (ft[0] >= vr) & (ft[1] >= vr)).astype(np.uint8)
    xx, yy = np.meshgrid(R.XS, R.YS)
    tgt = []
    for L, name in ((0, 'F'), (1, 'B')):
        mainL = unary_union([items[i][1] for i in main_c if items[i][2] == 'island' and name in items[i][0]]).buffer(-0.25)
        m = shapely.contains_xy(mainL, xx.ravel(), yy.ravel()).reshape(R.NY, R.NX)
        tgt.append((m & (free[L] > 0)).astype(np.uint8))
    zero = np.zeros((R.NY, R.NX), np.int32)
    added = 0
    for c in iso:
        src = []
        for i in c:
            Ls, g, lab = items[i]
            if lab == 'island':
                continue
            for L, name in ((0, 'F'), (1, 'B')):
                if name not in Ls:
                    continue
                gg = g.buffer(-0.05) if g.area > 0.05 else g
                x1, y1, x2, y2 = gg.bounds
                i1, i2 = int((x1 - R.X0) / R.G), int((x2 - R.X0) / R.G) + 2
                j1, j2 = int((y1 - R.Y0) / R.G), int((y2 - R.Y0) / R.G) + 2
                sx, sy = np.meshgrid(R.XS[i1:i2], R.YS[j1:j2])
                inside = shapely.contains_xy(gg, sx.ravel(), sy.ravel()).reshape(j2 - j1, i2 - i1)
                jj, ii = np.nonzero(inside)
                cells = (jj + j1) * R.NX + (ii + i1)
                cells = cells[free[L].ravel()[cells] > 0]
                src.extend(list(cells + L * R.NC))
        if not src:
            print('  group without usable source', [items[i][2] for i in c][:4]); continue
        path = rt.astar(free, via, [zero, zero], zero, np.array(src, np.int64), tgt, bbox=(0, 0, R.NX - 1, R.NY - 1),
                        maxexp=6_000_000, layer_cost=(100, 150))
        if path is None:
            print('  no path for', [items[i][2] for i in c if items[i][2] != 'island'][:4]); continue
        runs, vs = rt.geometry(path)
        for L, pts in runs:
            for a, b in zip(pts[:-1], pts[1:]):
                routes['tracks'].append(dict(net='GND', layer='F' if L == 0 else 'B', x1=a[0], y1=a[1], x2=b[0], y2=b[1], w=w))
            rt.fixed.add_track(L, pts, w)
        for x, y in vs:
            routes['vias'].append(dict(net='GND', x=x, y=y, d=R.VIA_D, drill=R.VIA_DRILL))
            rt.fixed.add_via(x, y)
        # refresh obstacles for later groups (own GND copper is not an obstacle, so masks stay valid)
        added += 1
        print('  connected', [items[i][2] for i in c if items[i][2] != 'island'][:4], 'len', len(path))
    json.dump(routes, open(routesp, 'w'))
    print('repaired', added, 'of', len(iso))


if __name__ == '__main__':
    main(*sys.argv[1:4])
