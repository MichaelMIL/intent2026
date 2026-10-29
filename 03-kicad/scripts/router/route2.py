"""Negotiated-congestion (PathFinder-style) grid router, 2 layers.

usage: python3 route2.py geo.json routes.json
 * pads / board edge / NPTH holes: hard obstacles with exact clearance
 * other nets' tracks and vias: soft obstacles (present-congestion + history cost),
   evaluated with exact distances; iterate until no clearance conflicts remain.
"""
import os, sys, json, ctypes, time
import numpy as np
import shapely
from shapely.geometry import Polygon, Point, LineString

HERE = os.path.dirname(os.path.abspath(__file__))
G = 0.1
X0, Y0 = -1.0, -1.0
NX, NY = 590, 1270        # x -1..57.9, y -1..125.9 (main board 0..100 + breakaway cans to y 124)
NC = NX * NY
CLR = 0.15
MARGIN = 0.045
EDGE_CLR = 0.3
VIA_D, VIA_DRILL = 0.6, 0.3
WIN = 1.3
# IMM_INT2 0.15 mm: LGA-14 pad 9 of U7 sits 0.5 mm between two foreign pads
WIDTH = {'VBUS': 0.5, 'VSYS': 0.5, 'BAT_IN': 0.5, 'BAT_SW': 0.5, '+3V3': 0.3, '+1V1': 0.3, 'GND': 0.3,
         'IRM_GND': 0.3, 'IRM_3V3': 0.3, 'IMM_GND': 0.3, 'IMM_3V3': 0.3, 'IMM_INT2': 0.15, 'SPM_GND': 0.3, 'SPM_3V3': 0.3, 'SPM_COL': 0.3}
LAYER_COST = (100, 230)
VIA_COST = 55


def width_of(net):
    return WIDTH.get(net, 0.2)


def load_core():
    so = '/tmp/libastar2.so'
    src = os.path.join(HERE, 'astar.c')
    if not os.path.exists(so) or os.path.getmtime(so) < os.path.getmtime(src):
        assert os.system('gcc -O2 -shared -fPIC -o %s "%s"' % (so, src)) == 0
    lib = ctypes.CDLL(so)
    P8 = np.ctypeslib.ndpointer(np.uint8, flags='C')
    P32 = np.ctypeslib.ndpointer(np.int32, flags='C')
    lib.astar.argtypes = [ctypes.c_int, ctypes.c_int, P8, P8, P8, P32, P32, P32, P8, P8, P32, ctypes.c_int, P32,
                          ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int,
                          ctypes.c_int, ctypes.c_int, P32, ctypes.c_int]
    lib.astar.restype = ctypes.c_int
    return lib


CORE = load_core()
XS = X0 + G * np.arange(NX)
YS = Y0 + G * np.arange(NY)


def window(geom, win):
    x1, y1, x2, y2 = geom.bounds
    i1 = max(0, int((x1 - win - X0) / G)); i2 = min(NX, int((x2 + win - X0) / G) + 2)
    j1 = max(0, int((y1 - win - Y0) / G)); j2 = min(NY, int((y2 + win - Y0) / G) + 2)
    return i1, i2, j1, j2


def dist_window(geom, win):
    i1, i2, j1, j2 = window(geom, win)
    xx, yy = np.meshgrid(XS[i1:i2], YS[j1:j2])
    d = shapely.distance(geom, shapely.points(xx.ravel(), yy.ravel())).reshape(j2 - j1, i2 - i1)
    return (i1, i2, j1, j2), d.astype(np.float32)

def via_block(vias, rr=9):
    m = np.zeros((NY, NX), bool)
    jj, ii = np.ogrid[-rr:rr + 1, -rr:rr + 1]
    disk = (ii * ii + jj * jj) <= rr * rr
    for x, y in vias:
        i, j = int(round((x - X0) / G)), int(round((y - Y0) / G))
        j1, j2, i1, i2 = max(0, j - rr), min(NY, j + rr + 1), max(0, i - rr), min(NX, i + rr + 1)
        m[j1:j2, i1:i2] |= disk[(j1 - j + rr):(j2 - j + rr), (i1 - i + rr):(i2 - i + rr)]
    return m


class Static:
    """pads, holes, edge"""

    def __init__(self, geo):
        self.d1 = [np.full((NY, NX), 99.0, np.float32) for _ in range(2)]
        self.n1 = [np.zeros((NY, NX), np.int32) for _ in range(2)]
        self.d2 = [np.full((NY, NX), 99.0, np.float32) for _ in range(2)]
        self.paddist = np.full((NY, NX), 99.0, np.float32)
        self.netid = {}
        outline = Polygon(geo['outline'])
        xx, yy = np.meshgrid(XS, YS)
        pts = shapely.points(xx.ravel(), yy.ravel())
        ed = shapely.distance(outline.exterior, pts).reshape(NY, NX)
        inside = shapely.contains_xy(outline, xx.ravel(), yy.ravel()).reshape(NY, NX)
        self.edist = np.where(inside, ed, -ed).astype(np.float32)
        self.pads = geo['pads']
        uniq = 100000
        for p in self.pads:
            if p['npth']:
                p['nid'] = -2
            elif not p['net']:
                uniq += 1; p['nid'] = uniq
            else:
                p['nid'] = self.nid(p['net'])
        for p in self.pads:
            poly = Polygon(p['poly'])
            extra = 0.0
            if p['npth']:
                poly = Point(p['x'], p['y']).buffer(p['drill'] / 2, 32); extra = 0.1
            if p['clearance'] and p['clearance'] > CLR:
                extra = p['clearance'] - CLR
            geom = poly.buffer(extra) if extra else poly
            layers = [0, 1] if (p['npth'] or p['drill'] > 0) else [0 if 'F' in p['layers'] else 1]
            p['cells'] = {}
            for L in layers:
                (i1, i2, j1, j2), d = dist_window(geom, WIN + extra)
                self._merge(L, p['nid'], (i1, i2, j1, j2), d)
                jj, ii = np.nonzero(d <= 1e-6)
                p['cells'][L] = ((jj + j1) * NX + (ii + i1)).astype(np.int64)
            if not p['npth']:
                (i1, i2, j1, j2), d = dist_window(poly, 1.0)
                sl = (slice(j1, j2), slice(i1, i2))
                self.paddist[sl] = np.minimum(self.paddist[sl], d)

    def nid(self, name):
        if name not in self.netid:
            self.netid[name] = len(self.netid) + 1
        return self.netid[name]

    def _merge(self, L, nid, w, d):
        i1, i2, j1, j2 = w
        sl = (slice(j1, j2), slice(i1, i2))
        d1, n1, d2 = self.d1[L][sl], self.n1[L][sl], self.d2[L][sl]
        same = n1 == nid
        closer = (~same) & (d < d1)
        farther = (~same) & (d >= d1)
        nd1 = np.where(same, np.minimum(d1, d), np.where(closer, d, d1))
        nd2 = np.where(closer, d1, np.where(farther, np.minimum(d2, d), d2))
        nn1 = np.where(closer, nid, n1)
        self.d1[L][sl], self.d2[L][sl], self.n1[L][sl] = nd1, nd2, nn1

    def foreign(self, L, nid):
        return np.where(self.n1[L] == nid, self.d2[L], self.d1[L])


class NetRoute:
    def __init__(self, name):
        self.name = name
        self.tracks = []        # (L, pts, w)
        self.vias = []          # (x, y)
        self.fields = []        # (L, window, dist)  copper distance (edge distance, i.e. minus half width)
        self.path_cells = []    # (L, flat cells) of centerlines for conflict detection

    def clear(self):
        self.__init__(self.name)

    def add_track(self, L, pts, w):
        self.tracks.append((L, pts, w))
        geom = LineString(pts) if len(pts) > 1 else Point(pts[0])
        wnd, d = dist_window(geom, WIN)
        self.fields.append((L, wnd, d - w / 2))

    def add_via(self, x, y):
        self.vias.append((x, y))
        wnd, d = dist_window(Point(x, y), WIN)
        for L in (0, 1):
            self.fields.append((L, wnd, d - VIA_D / 2))


class Router:
    def __init__(self, geo):
        t0 = time.time()
        self.geo = geo
        self.st = Static(geo)
        print('static ready %.1fs' % (time.time() - t0))
        self.nets = {}
        for p in self.st.pads:
            if p['net'] and not p['npth']:
                self.nets.setdefault(p['net'], []).append(p)
        self.routes = {n: NetRoute(n) for n in self.nets}
        self.fixed = NetRoute('GND')   # EP vias
        ep = [p for p in self.st.pads if p['ref'] == 'U1' and p['num'] == '57'][0]
        for dx in (-1.0, 0, 1.0):
            for dy in (-1.0, 0, 1.0):
                self.fixed.add_via(ep['x'] + dx, ep['y'] + dy)
        # FIXED_ROUTES=<json with tracks/vias>: pre-placed GND copper (hand-chosen fan-outs the negotiation
        # cannot find on its own); every other net routes around it. Pads listed in GND_SKIP are not fanned out.
        fx = os.environ.get('FIXED_ROUTES')
        if fx and os.path.exists(fx):
            d = json.load(open(fx))
            for t in d.get('tracks', []):
                self.fixed.add_track(0 if t['layer'] == 'F' else 1, [(t['x1'], t['y1']), (t['x2'], t['y2'])], t['w'])
            for v in d.get('vias', []):
                self.fixed.add_via(v['x'], v['y'])
            print('fixed routes loaded:', len(d.get('tracks', [])), 'tracks', len(d.get('vias', [])), 'vias')
        # keep the B.Cu ground plane under U1 tied to the rest of the plane: no B.Cu signal tracks
        # under the chip body or along the four diagonal corridors leaving it
        u1 = [f for f in geo['footprints'] if f['ref'] == 'U1'][0]
        xx, yy = np.meshgrid(XS - u1['x'], YS - u1['y'])
        quad = (np.sign(xx) * np.sign(yy)) < 0 if os.environ.get('CORR_Q', 'TR_BL') == 'TR_BL' else np.ones_like(xx, bool)
        diag = quad & (np.abs(np.abs(xx) - np.abs(yy)) < float(os.environ.get("CORR_W", "0.5")) * 1.4142) & (np.hypot(xx, yy) < float(os.environ.get("CORR_R", "7")))
        body = (np.abs(xx) < 1.9) & (np.abs(yy) < 1.9)
        self.b_forbid = diag | body
        # exposed-copper art (placement.ART_KEEPOUTS, F.Cu only): no tracks or vias of any net there, plus the
        # clearance ring (rev 0.6; before, the art regions were only checked after routing)
        self.art_forbid = np.zeros((NY, NX), bool)
        if os.environ.get('ART_KEEPOUT', '1') == '1':
            sys.path.insert(0, os.path.join(HERE, '..'))
            import placement
            gx, gy = np.meshgrid(XS, YS)
            m = CLR + 0.15 + MARGIN
            for x1, y1, x2, y2, lay in placement.ART_KEEPOUTS:
                if lay == 'F':
                    self.art_forbid |= (gx > x1 - m) & (gx < x2 + m) & (gy > y1 - m) & (gy < y2 + m)
        self.hist = [np.zeros((NY, NX), np.int32), np.zeros((NY, NX), np.int32)]
        self.vhist = np.zeros((NY, NX), np.int32)
        self.pres = 30

    # ----------------------------------------------------------------------------
    def foreign_tracks(self, net):
        f = [np.full((NY, NX), 99.0, np.float32), np.full((NY, NX), 99.0, np.float32)]
        cnt = [np.zeros((NY, NX), np.int16), np.zeros((NY, NX), np.int16)]
        allr = list(self.routes.values()) + [self.fixed]
        for r in allr:
            if r.name == net:
                continue
            for L, (i1, i2, j1, j2), d in r.fields:
                sl = (slice(j1, j2), slice(i1, i2))
                np.minimum(f[L][sl], d, out=f[L][sl])
        return f

    def masks(self, net, w):
        nid = self.st.nid(net)
        r = CLR + w / 2 + MARGIN
        er = EDGE_CLR + w / 2 + 0.02
        free = [((self.st.foreign(L, nid) >= r) & (self.st.edist >= er)).astype(np.uint8) for L in (0, 1)]
        if net != 'GND':
            free[1] = (free[1] & ~self.b_forbid).astype(np.uint8)
        free[0] = (free[0] & ~self.art_forbid).astype(np.uint8)
        vr = CLR + VIA_D / 2 + MARGIN
        via = ((self.st.foreign(0, nid) >= vr) & (self.st.foreign(1, nid) >= vr) & (self.st.paddist >= VIA_D / 2 + 0.08)
               & (self.st.edist >= EDGE_CLR + VIA_D / 2 + 0.05) & ~self.art_forbid).astype(np.uint8)
        ft = self.foreign_tracks(net)
        pen = []
        for L in (0, 1):
            pd1, pn1, pd2 = self.st.d1[L], self.st.n1[L], self.st.d2[L]
            near_pad = np.where(pn1 == nid, pd2, pd1) < 0.75
            p = self.hist[L] + (ft[L] < r).astype(np.int32) * self.pres + near_pad.astype(np.int32) * 12
            pen.append(np.ascontiguousarray(p.astype(np.int32)))
        vconf = (ft[0] < vr) | (ft[1] < vr)
        vpen = np.ascontiguousarray((self.vhist + vconf.astype(np.int32) * self.pres * 2).astype(np.int32))
        return free, via, pen, vpen, ft

    def astar(self, free, via, pen, vpen, src, tgt, bbox=None, maxexp=12_000_000, layer_cost=LAYER_COST):
        t0 = np.ascontiguousarray(tgt[0].ravel().astype(np.uint8)); t1 = np.ascontiguousarray(tgt[1].ravel().astype(np.uint8))
        if bbox is None:
            allt = np.nonzero(t0 | t1)[0]
            if len(allt) == 0:
                return None
            jj, ii = allt // NX, allt % NX
            bbox = (int(ii.min()), int(jj.min()), int(ii.max()), int(jj.max()))
        out = np.zeros(300000, np.int32)
        n = CORE.astar(NX, NY, np.ascontiguousarray(free[0].ravel()), np.ascontiguousarray(free[1].ravel()),
                       np.ascontiguousarray(via.ravel()), pen[0].ravel(), pen[1].ravel(), vpen.ravel(), t0, t1,
                       np.ascontiguousarray(src.astype(np.int32)), len(src), np.array(layer_cost, np.int32), VIA_COST,
                       3, 8, bbox[0], bbox[1], bbox[2], bbox[3], maxexp, out, len(out))
        if n <= 0:
            return None
        return out[:n][::-1]

    @staticmethod
    def geometry(path):
        runs, vias = [], []
        cur, curL = [], None
        for c in path:
            L, cell = int(c // NC), int(c % NC)
            p = (round(X0 + G * (cell % NX), 4), round(Y0 + G * (cell // NX), 4))
            if curL is None:
                curL = L
            if L != curL:
                runs.append((curL, cur)); vias.append(cur[-1]); cur = [cur[-1]]; curL = L
                continue
            cur.append(p)
        runs.append((curL, cur))
        out = []
        for L, pts in runs:
            if len(pts) < 2:
                continue
            simp = [pts[0]]
            for k in range(1, len(pts) - 1):
                ax, ay = pts[k][0] - simp[-1][0], pts[k][1] - simp[-1][1]
                bx, by = pts[k + 1][0] - pts[k][0], pts[k + 1][1] - pts[k][1]
                if abs(ax * by - ay * bx) > 1e-9:
                    simp.append(pts[k])
            simp.append(pts[-1])
            out.append((L, simp))
        return out, vias

    # ----------------------------------------------------------------------------
    def route_net(self, net):
        r = self.routes[net]
        r.clear()
        if net == 'GND':
            return self.route_gnd(r)
        pads = self.nets[net]
        w0 = width_of(net)
        groups = [[(L, c) for L, c in p['cells'].items()] for p in pads]
        fails = 0
        w = w0
        cache = {}
        while len(groups) > 1:
            if w not in cache:
                cache[w] = self.masks(net, w)
            free, via, pen, vpen, _ = cache[w]
            src = np.concatenate([c + L * NC for L, c in groups[0]])
            fl = np.concatenate([free[0].ravel(), free[1].ravel()])
            src = src[fl[src] > 0]
            tm = [np.zeros(NC, np.uint8), np.zeros(NC, np.uint8)]
            for gi in groups[1:]:
                for L, c in gi:
                    tm[L][c] = 1
            tgt = [tm[0].reshape(NY, NX) & free[0], tm[1].reshape(NY, NX) & free[1]]
            path = None
            via_eff = via
            if r.vias:
                via_eff = (via & ~via_block(r.vias)).astype(np.uint8)
            if len(src) and (tgt[0].any() or tgt[1].any()):
                path = self.astar(free, via_eff, pen, vpen, src, tgt)
            if path is None and w > 0.2:
                w = 0.2
                continue
            if path is None:
                fails += 1
                groups.pop(1)
                w = w0
                continue
            runs, vs = self.geometry(path)
            new = []
            for L, pts in runs:
                r.add_track(L, pts, w)
            for x, y in vs:
                r.add_via(x, y)
            cells = path.astype(np.int64)
            for c in cells:
                new.append((int(c // NC), np.array([c % NC], np.int64)))
            r.path_cells.append(cells)
            # update free-mask cache: own new copper does not change hard masks; penalties stay (same net)
            endc = int(path[-1]); Le, cell = endc // NC, endc % NC
            hit = 1
            for gi in range(1, len(groups)):
                if any(L2 == Le and np.any(c == cell) for L2, c in groups[gi]):
                    hit = gi; break
            groups[0] = groups[0] + new + groups[hit]
            groups.pop(hit)
            w = w0
        return fails

    def route_gnd(self, r):
        """Every F.Cu SMD GND pad gets a path (F track + via, optionally a short B track) that ends inside the
        main connected region of the B.Cu ground plane, computed from the current routing."""
        from scipy import ndimage
        fails = 0
        Z = np.zeros((NY, NX), np.uint8)
        gid = self.st.nid('GND')
        u1 = [f for f in self.geo['footprints'] if f['ref'] == 'U1'][0]
        xx, yy = np.meshgrid(XS - u1['x'], YS - u1['y'])
        ring = (np.abs(xx) < 4.0) & (np.abs(yy) < 4.0)
        placed = list(self.fixed.vias)
        pre = {}
        for ww in (0.25, 0.2):
            free, via, pen, vpen, ft = self.masks('GND', ww)
            if getattr(self, 'gnd_hard', False):
                rr = CLR + ww / 2 + 0.01
                free = [(free[L] & (ft[L] >= rr)).astype(np.uint8) for L in (0, 1)]
            plane = (ft[1] >= 0.45) & (self.st.foreign(1, gid) >= 0.45) & (self.st.edist >= 0.6)
            plane = ndimage.binary_erosion(plane, iterations=1)
            lab, nl = ndimage.label(plane)
            cnt = np.bincount(lab.ravel()); cnt[0] = 0
            main = lab == int(np.argmax(cnt))
            tgtB = (main & (free[1] > 0)).astype(np.uint8)
            pre[ww] = (free, (via & (vpen == 0) & ~ring), pen, tgtB)
        self.gnd_failed = []
        subset = getattr(self, 'gnd_subset', None)
        prio = set((os.environ.get('GND_SUBSET') or '').split(','))
        skip = set((os.environ.get('GND_SKIP') or '').split(','))
        for p in sorted(self.nets['GND'], key=lambda q: ('%s.%s' % (q['ref'], q['num'])) not in prio):
            if not (p['smd'] and p['layers'] == ['F']) or (p['ref'] == 'U1' and p['num'] == '57'):
                continue
            if '%s.%s' % (p['ref'], p['num']) in skip:
                continue
            if subset is not None and '%s.%s' % (p['ref'], p['num']) not in subset:
                continue
            cells = p['cells'][0]
            done = False
            for ww in (0.25, 0.2):
                free, via0, pen, tgtB = pre[ww]
                v2 = (via0 & ~via_block(placed + r.vias)).astype(np.uint8)
                src = cells[free[0].ravel()[cells] > 0]
                if len(src) == 0:
                    continue
                path = None
                for attempt in range(4):
                    path = self.astar(free, v2, pen, np.zeros((NY, NX), np.int32), src, [Z, tgtB],
                                      bbox=(0, 0, NX - 1, NY - 1), maxexp=1500000, layer_cost=(100, 500))
                    if path is None:
                        break
                    runs, vs = self.geometry(path)
                    close = [(a, b) for k, a in enumerate(vs) for b in vs[k + 1:]
                             if (a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2 < 0.8 ** 2]
                    if not close:
                        break
                    v2 = (v2 & ~via_block([c[1] for c in close], rr=3)).astype(np.uint8)
                    path = None
                if path is None:
                    continue
                for L, pts in runs:
                    r.add_track(L, pts, ww)
                for x, y in vs:
                    r.add_via(x, y)
                r.path_cells.append(path.astype(np.int64))
                done = True
                break
            if not done:
                fails += 1
                self.gnd_failed.append('%s.%s' % (p['ref'], p['num']))
        return fails

    def stitch(self, pitch=6.0):
        """GND stitching vias on a grid, only where both layers' pours are part of the main ground body."""
        from scipy import ndimage
        free, via, pen, vpen, ft = self.masks('GND', 0.3)
        gid = self.st.nid('GND')
        vr = CLR + VIA_D / 2 + 0.1
        mains = []
        for L in (0, 1):
            plane = (ft[L] >= 0.45) & (self.st.foreign(L, gid) >= 0.45) & (self.st.edist >= 0.6)
            plane = ndimage.binary_erosion(plane, iterations=2)
            lab, nl = ndimage.label(plane)
            cnt = np.bincount(lab.ravel()); cnt[0] = 0
            mains.append(lab == int(np.argmax(cnt)))
        ok = (via > 0) & (ft[0] >= vr) & (ft[1] >= vr) & (self.st.foreign(0, gid) >= 0.6) \
            & (self.st.foreign(1, gid) >= 0.6) & mains[0] & mains[1]
        placed = []
        allv = [v for r in self.routes.values() for v in r.vias] + self.fixed.vias
        for gy in np.arange(2.0, 100.0, pitch / 2):
            for gx in np.arange(2.0, 56.0, pitch / 2):
                best = None
                for dx in np.arange(-0.8, 0.81, 0.2):
                    for dy in np.arange(-0.8, 0.81, 0.2):
                        x, y = round(gx + dx, 1), round(gy + dy, 1)
                        i, j = int(round((x - X0) / G)), int(round((y - Y0) / G))
                        if 0 <= i < NX and 0 <= j < NY and ok[j, i]:
                            best = (x, y); break
                    if best:
                        break
                if not best:
                    continue
                x, y = best
                if any((x - a) ** 2 + (y - b) ** 2 < (pitch * 0.7) ** 2 for a, b in placed):
                    continue
                if any((x - a) ** 2 + (y - b) ** 2 < 1.2 ** 2 for a, b in allv):
                    continue
                placed.append((x, y))
        for x, y in placed:
            self.fixed.add_via(x, y)
        return len(placed)

    # ----------------------------------------------------------------------------
    def conflicts(self):
        """exact clearance check between routed copper of different nets; returns dict net->count and hist update"""
        bad = {}
        for net, r in self.routes.items():
            if not r.tracks and not r.vias:
                continue
            ft = self.foreign_tracks(net)
            n = 0
            for L, pts, w in r.tracks:
                rr = CLR + w / 2 + 0.001
                geom = LineString(pts)
                (i1, i2, j1, j2), d = dist_window(geom, 0.05)
                on = d <= 0.051
                sl = (slice(j1, j2), slice(i1, i2))
                viol = on & (ft[L][sl] < rr)
                if viol.any():
                    n += int(viol.sum())
                    self.hist[L][sl] += viol.astype(np.int32) * int(os.environ.get('HIST_INC', '12'))
            for x, y in r.vias:
                (i1, i2, j1, j2), d = dist_window(Point(x, y), 0.05)
                sl = (slice(j1, j2), slice(i1, i2))
                rr = CLR + VIA_D / 2 + 0.001
                viol = (d <= 0.051) & ((ft[0][sl] < rr) | (ft[1][sl] < rr))
                if viol.any():
                    n += int(viol.sum())
                    self.vhist[sl] += viol.astype(np.int32) * 25
            if n:
                bad[net] = n
        return bad

    def run(self, iters=30):
        t0 = time.time()

        def span(n):
            xs = [p['x'] for p in self.nets[n]]; ys = [p['y'] for p in self.nets[n]]
            return (max(xs) - min(xs)) + (max(ys) - min(ys))
        order = sorted([n for n in self.nets if n != 'GND'], key=span) + ([] if os.environ.get('GND_LAST') else ['GND'])
        # NET_ONLY=IRM_,IMM_,SPM_: route just these net prefixes (e.g. the breakaway modules after a re-placement);
        # everything else comes in as FIXED_ROUTES and is exported separately by main()
        only = os.environ.get('NET_ONLY')
        if only:
            pre = tuple(only.split(','))
            order = [n for n in order if n.startswith(pre)]
        gs = os.environ.get('GND_SUBSET')
        if gs:
            self.gnd_subset = set(gs.split(','))
            order.append('GND')
        best = None
        it0 = 0
        sp = os.environ.get('ROUTE_STATE')
        if sp and os.path.exists(sp):
            import pickle
            stt = pickle.load(open(sp, 'rb'))
            self.hist, self.vhist, self.pres, order, it0, best = stt['hist'], stt['vhist'], stt['pres'], stt['order'], stt['it'], stt['best']
            for n, (tr, vi, fi, pc) in stt['routes'].items():
                r = self.routes[n]; r.tracks, r.vias, r.fields, r.path_cells = tr, vi, fi, pc
            print('resumed at iter', it0, 'best score', best[0] if best else None)
        tstart = time.time()
        budget = float(os.environ.get('ROUTE_BUDGET', '1e9'))
        for it in range(it0, it0 + iters):
            if time.time() - tstart > budget:
                break
            unrouted = {}
            for n in order:
                f = self.route_net(n)
                if f:
                    unrouted[n] = f
            bad = self.conflicts()
            score = sum(unrouted.values()) * 1000 + sum(bad.values())
            print('iter %2d pres=%4d  unrouted=%s  conflicts=%d in %d nets %s (%.0fs)' % (
                it, self.pres, unrouted, sum(bad.values()), len(bad), sorted(bad)[:8], time.time() - t0), flush=True)
            if best is None or score <= best[0]:
                best = (score, self.export(), dict(unrouted), dict(bad))
                if getattr(self, 'outpath', None):
                    d = dict(best[1]); d['unrouted'] = unrouted; d['conflicts'] = bad
                    json.dump(d, open(self.outpath, 'w'))
            if score == 0:
                break
            self.pres = min(int(os.environ.get("PRES_CAP", "4000")), int(self.pres * 1.35) + 10)
            # nets in conflict go first next round
            order = [n for n in order if n in bad or n in unrouted] + [n for n in order if n not in bad and n not in unrouted]
            if 'GND' in order:
                order.remove('GND'); order.append('GND')
            if os.environ.get('GND_LAST') and 'GND' in order and not gs:
                order.remove('GND')
            if sp:
                import pickle
                pickle.dump(dict(hist=self.hist, vhist=self.vhist, pres=self.pres, order=order, it=it + 1, best=best,
                                 routes={n: (r.tracks, r.vias, r.fields, r.path_cells) for n, r in self.routes.items()}),
                            open(sp, 'wb'))
        return best

    def export(self, prefixes=None):
        tracks, vias = [], []
        for r in list(self.routes.values()) + [self.fixed]:
            if prefixes and not r.name.startswith(prefixes):
                continue
            for L, pts, w in r.tracks:
                for a, b in zip(pts[:-1], pts[1:]):
                    tracks.append(dict(net=r.name, layer='F' if L == 0 else 'B', x1=a[0], y1=a[1], x2=b[0], y2=b[1], w=w))
            for x, y in r.vias:
                vias.append(dict(net=r.name, x=x, y=y, d=VIA_D, drill=VIA_DRILL))
        return dict(tracks=tracks, vias=vias)


def main(geopath, outpath):
    geo = json.load(open(geopath))
    rt = Router(geo)
    rt.outpath = outpath
    score, data, unrouted, bad = rt.run(int(os.environ.get('ROUTE_ITERS', '30')))
    if score == 0 and os.environ.get('GND_LAST'):
        rt.routes['GND'].clear()
        rt.gnd_subset = None
        rt.gnd_hard = True
        f = rt.route_gnd(rt.routes['GND'])
        print('final GND fanout pass, failed pads:', f, ','.join(rt.gnd_failed))
        data = rt.export(); score = f
        bad = rt.conflicts()
        print('conflicts after GND pass', bad)
    if score == 0 and os.environ.get('STITCH', '1') == '1':
        # restore best routing into the router, add stitching vias, export again
        n = rt.stitch()
        print('stitching vias', n)
        bad2 = rt.conflicts()
        print('conflicts after stitching', bad2)
        data = rt.export()
    if os.environ.get('NET_ONLY'):
        data = rt.export(tuple(os.environ['NET_ONLY'].split(',')))
    data['unrouted'] = unrouted
    data['conflicts'] = bad
    json.dump(data, open(outpath, 'w'), indent=0)
    print('final: score', score, 'unrouted', unrouted, 'conflicts', bad, 'tracks', len(data['tracks']), 'vias', len(data['vias']))


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
