"""Convert the INTENT vector logo (02-layout/artwork/intent-logo-page1.svg) to silkscreen polygons.

usage: python3 art_logo.py <svg> <out.json> [width_mm=40] [x_left=8] [y_top=9]
Output: {"polys": [{"ext": [[x,y]...], "holes": [[[x,y]...], ...]}, ...], "bbox": [...]} in board mm.
"""
import sys, json
from svgelements import SVG, Path, Move, Close
from shapely.geometry import Polygon
from shapely.ops import unary_union


def subpaths(path, step=0.6):
    polys, cur = [], []
    for seg in path:
        if isinstance(seg, Move):
            if len(cur) > 2:
                polys.append(cur)
            cur = [(seg.end.x, seg.end.y)]
        elif isinstance(seg, Close):
            if len(cur) > 2:
                polys.append(cur)
            cur = []
        else:
            n = max(1, int(seg.length() / step)) if hasattr(seg, 'length') else 1
            if type(seg).__name__ == 'Line':
                n = 1
            for k in range(1, n + 1):
                p = seg.point(k / n)
                cur.append((p.x, p.y))
    if len(cur) > 2:
        polys.append(cur)
    return polys


def main(svgpath, out, width=40.0, xl=8.0, yt=9.0):
    svg = SVG.parse(svgpath)
    shapes = []
    for e in svg.elements():
        if isinstance(e, Path):
            sp = subpaths(e)
            geom = None
            for pts in sp:   # letters: outer ring + holes -> even-odd
                pg = Polygon(pts).buffer(0)
                geom = pg if geom is None else geom.symmetric_difference(pg)
            if geom is not None and not geom.is_empty:
                shapes.append(geom)
    logo = unary_union(shapes)
    x1, y1, x2, y2 = logo.bounds
    s = width / (x2 - x1)
    polys = []
    geoms = list(logo.geoms) if hasattr(logo, 'geoms') else [logo]
    for g in geoms:
        g = g.simplify(0.25, preserve_topology=True)
        tr = lambda c: [[round(xl + (x - x1) * s, 4), round(yt + (y - y1) * s, 4)] for x, y in c]
        polys.append(dict(ext=tr(g.exterior.coords), holes=[tr(h.coords) for h in g.interiors]))
    bb = [xl, yt, xl + width, yt + (y2 - y1) * s]
    json.dump(dict(polys=polys, bbox=bb), open(out, 'w'))
    print('logo polys', len(polys), 'bbox', [round(v, 2) for v in bb])


if __name__ == '__main__':
    a = sys.argv
    main(a[1], a[2], *(float(v) for v in a[3:6]))
