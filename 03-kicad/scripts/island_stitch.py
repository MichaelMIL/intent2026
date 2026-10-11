"""Union-find connectivity of all GND copper (pour islands, tracks, vias, pads) on both layers;
propose stitching vias for every component that is not part of the main ground.
usage: island_stitch.py <zones.json> <stitch_extra.json>   (appends)"""
import sys, json, os
from shapely.geometry import Polygon, Point, LineString
from shapely.ops import unary_union
from shapely.strtree import STRtree

VIA_R = 0.3


def main(zpath, out):
    z = json.load(open(zpath))
    items = []   # (layers set, geometry, label)
    for L in ('F', 'B'):
        for isl in z['zones'].get(L, []):
            pg = Polygon(isl['ext'], isl['holes']).buffer(0)
            if pg.area > 0:
                items.append(({L}, pg, 'island'))
    for t in z['gtracks']:
        items.append(({t['L']}, LineString(t['p']).buffer(t['w'] / 2), 'track'))
    for x, y in z['gnd_links']:
        items.append(({'F', 'B'}, Point(x, y).buffer(0.25), 'via/tht'))
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
                jj = idx[j]
                if jj != i and geoms[k].distance(items[jj][1]) < 0.02:
                    parent[find(jj)] = find(i)
    comps = {}
    for i in range(n):
        comps.setdefault(find(i), []).append(i)
    area = lambda c: sum(items[i][1].area for i in c if items[i][2] == 'island')
    main_c = max(comps.values(), key=area)
    main_by_layer = {L: unary_union([items[i][1] for i in main_c if items[i][2] == 'island' and L in items[i][0]]) for L in ('F', 'B')}
    drills = z['drills']
    new = json.load(open(out)) if os.path.exists(out) else []
    added, bad = 0, []
    for c in comps.values():
        if c is main_c:
            continue
        labels = sorted(set(items[i][2] for i in c))
        done = False
        for i in c:
            if items[i][2] != 'island':
                continue
            (L,) = tuple(items[i][0])
            other = 'B' if L == 'F' else 'F'
            cand = items[i][1].buffer(-(VIA_R + 0.02)).intersection(main_by_layer[other].buffer(-(VIA_R + 0.02)))
            if cand.is_empty:
                continue
            x1, y1, x2, y2 = cand.bounds
            best = None
            for a in range(41):
                for b in range(41):
                    px = x1 + (x2 - x1) * a / 40; py = y1 + (y2 - y1) * b / 40
                    if not cand.contains(Point(px, py)):
                        continue
                    dmin = min([((px - dx) ** 2 + (py - dy) ** 2) ** 0.5 - dd / 2 for dx, dy, dd in drills] +
                               [((px - v['x']) ** 2 + (py - v['y']) ** 2) ** 0.5 - 0.15 for v in new] + [9])
                    if dmin < 0.65:
                        continue
                    sc = cand.boundary.distance(Point(px, py))
                    if best is None or sc > best[0]:
                        best = (sc, px, py)
            if best:
                new.append(dict(net='GND', x=round(best[1], 3), y=round(best[2], 3), d=0.6, drill=0.3))
                added += 1; done = True
                break
        if not done:
            bad.append([l for l in labels if l.startswith('pad')] or [(round(items[i][1].bounds[0], 1), round(items[i][1].bounds[1], 1)) for i in c[:2]])
    json.dump(new, open(out, 'w'))
    print('components', len(comps), 'stitch vias added', added, 'total', len(new), 'unresolved', bad)


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
