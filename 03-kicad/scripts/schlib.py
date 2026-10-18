"""Drawing primitives for generating a wired KiCad schematic (.kicad_sch, format 20250114).

Coordinates are schematic mm, y down. Symbol transform verified against KiCad 10
(rotate in library space, then mirror on screen):
    rot 0   : (px, -py)      rot 90  : (-py, -px)
    rot 180 : (-px,  py)     rot 270 : ( py,  px)
    mirror x: negate screen y   mirror y: negate screen x
"""
import uuid
from sexpr import Sym as S, dump, find, findall
import symlib

PROJECT = 'intent-2026-badge'
NS = uuid.UUID('6b1e7a52-1d0a-4c1f-9a51-2026bade0001')
ROOT = str(uuid.uuid5(NS, 'root'))


def uid(*k):
    return str(uuid.uuid5(NS, '/'.join(map(str, k))))


def r4(v):
    return round(v + 0.0, 4) + 0.0


def xf(px, py, rot, mir):
    x, y = {0: (px, -py), 90: (-py, -px), 180: (-px, py), 270: (py, px)}[rot % 360]
    if mir == 'x':
        y = -y
    elif mir == 'y':
        x = -x
    return x, y


def font(size=1.27, hide=False, justify=None, bold=False):
    f = [S('font'), [S('size'), size, size]]
    if bold:
        f.append([S('bold'), S('yes')])
    e = [S('effects'), f]
    if justify:
        e.append([S('justify')] + [S(j) for j in justify])
    if hide:
        e.append([S('hide'), S('yes')])
    return e


def prop(name, value, x, y, hide=False, ang=0, justify=None, size=1.27):
    return [S('property'), name, value, [S('at'), r4(x), r4(y), ang], font(size=size, hide=hide, justify=justify)]


class Sheet:
    def __init__(self, paper='A2'):
        self.paper = paper
        self.items = []
        self.wires = []        # (x1,y1,x2,y2)
        self.pinpts = set()    # connection points of placed pins
        self.anchors = set()   # label / no-connect anchors
        self.libs = []         # lib ids in order
        self.placed = {}       # ref -> dict(lib, x, y, rot, mir, pins{num:(x,y)})
        self.lib_cache = {}
        self.pwr_n = 0
        self.seq = 0

    # ---- symbols --------------------------------------------------------
    # pin numbers that newer KiCad libraries renamed; the footprints / design.py keep the old names
    PIN_RENAMES = {}   # rev 0.6: J1 uses the stock HRO footprint (shield pad SH), no rename needed

    def libsym(self, lib_id):
        if lib_id not in self.lib_cache:
            sym = symlib.load(lib_id)
            ren = self.PIN_RENAMES.get(lib_id)
            if ren:
                for sub in findall(sym, 'symbol'):
                    for p in findall(sub, 'pin'):
                        num = find(p, 'number')
                        if num[1] in ren:
                            num[1] = ren[num[1]]
            self.lib_cache[lib_id] = sym
            self.libs.append(lib_id)
        return self.lib_cache[lib_id]

    def place(self, ref, lib_id, value, x, y, rot=0, mir=None, fp='', fields=None, in_bom=True, dnp=False,
              on_board=True, ref_at=None, val_at=None, hide_ref=False, hide_val=False, just=None, unit=1):
        """Place a symbol. Returns dict with pin positions. ref_at/val_at are offsets from (x, y)."""
        lib = self.libsym(lib_id)
        props = {p[1]: p for p in findall(lib, 'property')}
        pins = {}
        for p in symlib.pins(lib):
            dx, dy = xf(p['x'], p['y'], rot, mir)
            pins[p['num']] = (r4(x + dx), r4(y + dy))
            self.pinpts.add((r4(x + dx), r4(y + dy)))
        node = [S('symbol'), [S('lib_id'), lib_id], [S('at'), r4(x), r4(y), rot]]
        if mir:
            node.append([S('mirror'), S(mir)])
        node += [[S('unit'), unit], [S('exclude_from_sim'), S('no')], [S('in_bom'), S('yes' if in_bom else 'no')],
                 [S('on_board'), S('yes' if on_board else 'no')], [S('dnp'), S('yes' if dnp else 'no')],
                 [S('uuid'), uid('sym', ref)]]
        rx, ry = ref_at or (0, -5.08)
        vx, vy = val_at or (0, 5.08)
        # field angle is added to the symbol rotation; keep the text horizontal, and swap the
        # anchor side when KiCad will flip the (effectively 180-degree or mirrored) text to read it
        fang = 90 if rot % 180 == 90 else 0
        flip = ((rot + fang) % 360 == 180) != (mir == 'y')
        fj = just
        if flip and just:
            fj = [{'left': 'right', 'right': 'left'}.get(j, j) for j in just]
        node.append(prop('Reference', ref, x + rx, y + ry, hide=hide_ref, justify=fj, ang=fang))
        node.append(prop('Value', value, x + vx, y + vy, hide=hide_val, justify=fj, ang=fang))
        node.append(prop('Footprint', fp, x, y, hide=True))
        ds = props.get('Datasheet')
        node.append(prop('Datasheet', ds[2] if ds else '', x, y, hide=True))
        fields = dict(fields or {})
        dsc = props.get('Description')
        node.append(prop('Description', fields.pop('Description', None) or (dsc[2] if dsc else ''), x, y, hide=True))
        for k, v in fields.items():
            node.append(prop(k, v, x, y, hide=True))
        for pn in pins:
            node.append([S('pin'), pn, [S('uuid'), uid('pin', ref, pn)]])
        node.append([S('instances'), [S('project'), PROJECT,
                                      [S('path'), '/' + ROOT, [S('reference'), ref], [S('unit'), unit]]]])
        self.items.append(node)
        self.placed[ref] = dict(lib=lib_id, x=x, y=y, rot=rot, mir=mir, pins=pins)
        return pins

    def pin(self, ref, num):
        return self.placed[ref]['pins'][str(num)]

    def power(self, net, x, y, rot=0, lib=None, hide_val=False):
        """Power symbol with its pin at (x, y). GND points down (rot 0); rails point up (rot 0)."""
        lib = lib or {'GND': 'power:GND', '+3V3': 'power:+3V3', '+1V1': 'power:+1V1', 'VBUS': 'power:VBUS'}.get(net, 'power:VCC')
        self.pwr_n += 1
        ref = '#PWR%03d' % self.pwr_n
        down = (lib == 'power:GND')
        # GND body hangs below at rot 0 (right at 90, left at 270); rails stand above (left at 90, right at 270)
        if down:
            val_at = {0: (0, 3.81), 90: (3.81, 0), 180: (0, -3.81), 270: (-3.81, 0)}[rot % 360]
        else:
            val_at = {0: (0, -5.33), 90: (-5.33, 0), 180: (0, 5.33), 270: (5.33, 0)}[rot % 360]
        just = None
        if rot % 180 == 90:
            just = ['left'] if val_at[0] > 0 else ['right']
        self.place(ref, lib, net, x, y, rot=rot, in_bom=False, on_board=False, hide_ref=True, hide_val=hide_val,
                   ref_at=(0, 0), val_at=val_at, just=just)
        self.anchors.add((r4(x), r4(y)))
        return ref

    def flag(self, x, y, rot=0):
        self.pwr_n += 1
        ref = '#FLG%03d' % self.pwr_n
        self.place(ref, 'power:PWR_FLAG', 'PWR_FLAG', x, y, rot=rot, in_bom=False, on_board=False, hide_ref=True,
                   ref_at=(0, 0), val_at=(0, -7.0))
        return ref

    # ---- wires ----------------------------------------------------------
    def wire(self, *pts):
        """Polyline through points (x, y)."""
        for (x1, y1), (x2, y2) in zip(pts, pts[1:]):
            if (r4(x1), r4(y1)) != (r4(x2), r4(y2)):
                assert r4(x1) == r4(x2) or r4(y1) == r4(y2), ('diagonal wire', pts)
                self.wires.append((r4(x1), r4(y1), r4(x2), r4(y2)))

    def hwire(self, p, x):
        self.wire(p, (x, p[1]))
        return (r4(x), p[1])

    def vwire(self, p, y):
        self.wire(p, (p[0], y))
        return (p[0], r4(y))

    def L(self, a, b, via='h'):
        """L-shaped wire from a to b; via='h' goes horizontal first."""
        if via == 'h':
            self.wire(a, (b[0], a[1]), b)
        else:
            self.wire(a, (a[0], b[1]), b)
        return b

    # ---- annotations ----------------------------------------------------
    def label(self, net, x, y, ang=0, size=1.27):
        """Net label. Global labels are used on purpose: a local label on the root sheet would be
        exported as '/NAME' and break parity with the PCB's net names."""
        self.glabel(net, x, y, ang, size=size)

    def local_label(self, net, x, y, ang=0, size=1.27):
        just = {0: ['left', 'bottom'], 90: ['left', 'bottom'], 180: ['right', 'bottom'], 270: ['right', 'bottom']}[ang % 360]
        self.seq += 1
        self.items.append([S('label'), net, [S('at'), r4(x), r4(y), ang % 360], [S('fields_autoplaced'), S('yes')],
                           font(size=size, justify=just), [S('uuid'), uid('lbl', net, x, y, self.seq)]])
        self.anchors.add((r4(x), r4(y)))

    def glabel(self, net, x, y, ang=0, shape='passive', size=1.27):
        just = {0: ['left'], 90: ['left'], 180: ['right'], 270: ['right']}[ang % 360]
        self.seq += 1
        self.items.append([S('global_label'), net, [S('shape'), S(shape)], [S('at'), r4(x), r4(y), ang % 360],
                           [S('fields_autoplaced'), S('yes')], font(size=size, justify=just),
                           [S('uuid'), uid('glbl', net, x, y, self.seq)],
                           [S('property'), 'Intersheetrefs', '${INTERSHEET_REFS}', [S('at'), r4(x), r4(y), 0],
                            font(size=size, hide=True)]])
        self.anchors.add((r4(x), r4(y)))

    def nc(self, p):
        self.items.append([S('no_connect'), [S('at'), r4(p[0]), r4(p[1])], [S('uuid'), uid('nc', p[0], p[1])]])
        self.anchors.add((r4(p[0]), r4(p[1])))

    def text(self, s, x, y, size=1.5, bold=False, just=('left', 'bottom'), ang=0):
        self.seq += 1
        self.items.append([S('text'), s, [S('exclude_from_sim'), S('no')], [S('at'), r4(x), r4(y), ang],
                           font(size=size, justify=list(just), bold=bold), [S('uuid'), uid('txt', x, y, self.seq)]])

    def box(self, x1, y1, x2, y2, title=None):
        self.seq += 1
        self.items.append([S('rectangle'), [S('start'), r4(x1), r4(y1)], [S('end'), r4(x2), r4(y2)],
                           [S('stroke'), [S('width'), 0.25], [S('type'), S('solid')], [S('color'), 120, 120, 120, 1]],
                           [S('fill'), [S('type'), S('none')]], [S('uuid'), uid('box', x1, y1, self.seq)]])
        if title:
            self.text(title, x1 + 2.54, y1 + 5.5, size=3.0, bold=True)

    # ---- finishing ------------------------------------------------------
    def _split_wires(self):
        """Split wires at every pin / anchor / wire endpoint lying in their interior."""
        pts = set(self.pinpts) | set(self.anchors)
        for (x1, y1, x2, y2) in self.wires:
            pts.add((x1, y1)); pts.add((x2, y2))
        out = []
        for (x1, y1, x2, y2) in self.wires:
            if x1 == x2:
                lo, hi = sorted((y1, y2))
                cuts = sorted(p[1] for p in pts if p[0] == x1 and lo < p[1] < hi)
                ys = [y1] + (cuts if y1 < y2 else cuts[::-1]) + [y2]
                out += [(x1, a, x1, b) for a, b in zip(ys, ys[1:])]
            else:
                lo, hi = sorted((x1, x2))
                cuts = sorted(p[0] for p in pts if p[1] == y1 and lo < p[0] < hi)
                xs = [x1] + (cuts if x1 < x2 else cuts[::-1]) + [x2]
                out += [(a, y1, b, y1) for a, b in zip(xs, xs[1:])]
        self.wires = out

    def _junctions(self):
        from collections import Counter
        c = Counter()
        for (x1, y1, x2, y2) in self.wires:
            c[(x1, y1)] += 1
            c[(x2, y2)] += 1
        for p in self.pinpts:
            if p in c:
                c[p] += 1
        return [p for p, n in c.items() if n >= 3]

    def check(self):
        """Dangling wire ends (not on a pin, anchor or another wire end)."""
        from collections import Counter
        self._split_wires()
        c = Counter()
        for (x1, y1, x2, y2) in self.wires:
            c[(x1, y1)] += 1
            c[(x2, y2)] += 1
        dangling = [p for p, n in c.items() if n == 1 and p not in self.pinpts and p not in self.anchors]
        return dangling

    def write(self, path, title, date, rev, company, comments=()):
        self._split_wires()
        wires = [[S('wire'), [S('pts'), [S('xy'), x1, y1], [S('xy'), x2, y2]],
                  [S('stroke'), [S('width'), 0], [S('type'), S('default')]], [S('uuid'), uid('w', x1, y1, x2, y2)]]
                 for (x1, y1, x2, y2) in self.wires]
        juncs = [[S('junction'), [S('at'), x, y], [S('diameter'), 0], [S('color'), 0, 0, 0, 0], [S('uuid'), uid('j', x, y)]]
                 for (x, y) in self._junctions()]
        tb = [S('title_block'), [S('title'), title], [S('date'), date], [S('rev'), rev], [S('company'), company]]
        for i, cm in enumerate(comments):
            tb.append([S('comment'), i + 1, cm])
        libsyms = [S('lib_symbols')] + [self.lib_cache[l] for l in self.libs]
        sch = [S('kicad_sch'), [S('version'), 20250114], [S('generator'), 'eeschema'], [S('generator_version'), '9.0'],
               [S('uuid'), ROOT], [S('paper'), self.paper], tb, libsyms] + juncs + wires + self.items + \
              [[S('sheet_instances'), [S('path'), '/', [S('page'), '1']]], [S('embedded_fonts'), S('no')]]
        with open(path, 'w', encoding='utf-8', newline='\n') as f:
            f.write(dump(sch) + '\n')
        return len(wires), len(juncs)
