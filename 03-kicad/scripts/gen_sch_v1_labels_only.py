"""Generate intent-2026-badge.kicad_sch from design.py.

Every pin gets a net label at its tip (or a no-connect flag), so the schematic
is complete and ERC-checkable without hand-drawn wires.
"""
import os, sys, uuid, datetime
sys.path.insert(0, os.path.dirname(__file__))
from sexpr import Sym as S, dump, find, findall
import symlib
import design

PROJECT = 'intent-2026-badge'
OUT = os.path.join(os.path.dirname(__file__), '..', PROJECT + '.kicad_sch')
NS = uuid.UUID('6b1e7a52-1d0a-4c1f-9a51-2026bade0001')


def uid(*k):
    return str(uuid.uuid5(NS, '/'.join(map(str, k))))


ROOT = uid('root')
G = 2.54


def snap(v):
    return round(round(v / 1.27) * 1.27, 4)


def font(size=1.27, hide=False, justify=None):
    e = [S('effects'), [S('font'), [S('size'), size, size]]]
    if justify:
        e.append([S('justify')] + [S(j) for j in justify])
    if hide:
        e.append([S('hide'), S('yes')])
    return e


def prop(name, value, x, y, hide=False, ang=0, justify=None):
    return [S('property'), name, value, [S('at'), x, y, ang], font(hide=hide, justify=justify)]


# --------------------------------------------------------------------------
lib_cache = {}


def libsym(lib_id):
    if lib_id not in lib_cache:
        lib_cache[lib_id] = symlib.load(lib_id)
    return lib_cache[lib_id]


def bbox(lib_id):
    ps = symlib.pins(libsym(lib_id))
    xs = [p['x'] for p in ps] + [0]
    ys = [p['y'] for p in ps] + [0]
    return min(xs), max(xs), min(ys), max(ys)


def label_for(pin, net, sx, sy, items):
    x, y = symlib.pin_tip(pin, sx, sy)
    ang = (pin['ang'] + 180) % 360
    items.append(glabel(net, x, y, ang, uid('lbl', net, x, y)))


def glabel(net, x, y, ang, u):
    just = {0: ['left'], 90: ['left'], 180: ['right'], 270: ['right']}[int(ang)]
    return [S('global_label'), net, [S('shape'), S('passive')], [S('at'), x, y, ang],
            [S('fields_autoplaced'), S('yes')], font(size=1.0, justify=just), [S('uuid'), u],
            [S('property'), 'Intersheetrefs', '${INTERSHEET_REFS}', [S('at'), x, y, 0], font(size=1.0, hide=True)]]


def nc_for(pin, sx, sy, items):
    x, y = symlib.pin_tip(pin, sx, sy)
    items.append([S('no_connect'), [S('at'), x, y], [S('uuid'), uid('nc', x, y)]])


def sym_instance(ref, lib_id, value, fp, x, y, fields, pins_used, in_bom=True, dnp=False, on_board=True):
    lib = libsym(lib_id)
    props = {p[1]: p for p in findall(lib, 'property')}
    x0, x1, y0, y1 = bbox(lib_id)
    node = [S('symbol'), [S('lib_id'), lib_id], [S('at'), x, y, 0], [S('unit'), 1],
            [S('exclude_from_sim'), S('no')], [S('in_bom'), S('yes' if in_bom else 'no')],
            [S('on_board'), S('yes' if on_board else 'no')], [S('dnp'), S('yes' if dnp else 'no')],
            [S('fields_autoplaced'), S('yes')], [S('uuid'), uid('sym', ref)]]
    ty = snap(y - y1 - 2.0)
    node.append(prop('Reference', ref, x, ty - 1.6, justify=None))
    node.append(prop('Value', value, x, ty))
    node.append(prop('Footprint', fp, x, y, hide=True))
    ds = props.get('Datasheet')
    node.append(prop('Datasheet', ds[2] if ds else '', x, y, hide=True))
    dsc = props.get('Description')
    node.append(prop('Description', fields.pop('Description', None) or (dsc[2] if dsc else ''), x, y, hide=True))
    for k, v in fields.items():
        node.append(prop(k, v, x, y, hide=True))
    for pn in pins_used:
        node.append([S('pin'), pn, [S('uuid'), uid('pin', ref, pn)]])
    node.append([S('instances'), [S('project'), PROJECT,
                                  [S('path'), '/' + ROOT, [S('reference'), ref], [S('unit'), 1]]]])
    return node


def main():
    items = []
    used_libs = []
    # ---- placement: shelf packing, A2 sheet (594 x 420) ----
    X0, Y0, XMAX = 25.4, 30.48, 560.0
    cx, cy, row_h = X0, Y0, 0
    order = design.parts
    flags = []
    for p in order:
        x0, x1, y0, y1 = bbox(p['lib'])
        lab_l = 22 if x0 < -0.1 else 6
        lab_r = 22 if x1 > 0.1 else 6
        w = (x1 - x0) + lab_l + lab_r
        h = (y1 - y0) + 14
        if cx + w > XMAX:
            cx = X0
            cy += row_h
            row_h = 0
        sx = snap(cx + lab_l - x0)
        sy = snap(cy + 6 + y1)
        sx = round(round(sx / G) * G, 4)
        sy = round(round(sy / G) * G, 4)
        p['_sch'] = (sx, sy)
        cx += w
        row_h = max(row_h, h)
    # ---- emit symbols ----
    for p in order:
        sx, sy = p['_sch']
        if p['lib'] not in used_libs:
            used_libs.append(p['lib'])
        fields = {'LCSC': p['lcsc']} if p['lcsc'] else {}
        if p['desc']:
            fields['Description'] = p['desc']
        lib_pins = symlib.pins(libsym(p['lib']))
        items.append(sym_instance(p['ref'], p['lib'], p['value'], p['fp'], sx, sy, fields,
                                  [lp['num'] for lp in lib_pins], in_bom=p['in_bom'], dnp=p['dnp']))
        done = {}
        for lp in lib_pins:
            if lp['num'] not in p['pins']:
                raise SystemExit('%s pin %s (%s) not assigned' % (p['ref'], lp['num'], lp['name']))
            net = p['pins'][lp['num']]
            tip = symlib.pin_tip(lp, sx, sy)
            if tip in done:
                assert done[tip] == net, (p['ref'], lp['num'], net, done[tip])
                continue
            done[tip] = net
            if net is None:
                nc_for(lp, sx, sy, items)
            else:
                label_for(lp, net, sx, sy, items)
        extra = set(p['pins']) - {lp['num'] for lp in lib_pins}
        if extra:
            raise SystemExit('%s has unknown pins %s' % (p['ref'], extra))
    # ---- PWR_FLAGs ----
    fx, fy = 40.64, snap(cy + row_h + 20)
    fy = round(round(fy / G) * G, 4)
    used_libs.append('power:PWR_FLAG')
    for i, net in enumerate(design.PWR_FLAGS):
        x = fx + i * 30.48
        ref = '#FLG%02d' % (i + 1)
        node = sym_instance(ref, 'power:PWR_FLAG', 'PWR_FLAG', '', x, fy, {}, ['1'], in_bom=False, on_board=False)
        items.append(node)
        items.append(glabel(net, x, fy, 270, uid('flaglbl', net)))
    # ---- notes ----
    notes = ('INTENT 2026 hardware badge - rev 0.3 - generated from 03-kicad/scripts/design.py. '
             'Every connection is made by net labels at pin ends. Source of truth: 01-spec/design-spec.md.')
    items.append([S('text'), notes, [S('exclude_from_sim'), S('no')], [S('at'), 25.4, 20.32, 0],
                  font(size=2.0, justify=['left', 'bottom']), [S('uuid'), uid('note')]])

    libsyms = [S('lib_symbols')] + [libsym(l) for l in used_libs]
    sch = [S('kicad_sch'), [S('version'), 20250114], [S('generator'), 'eeschema'], [S('generator_version'), '9.0'],
           [S('uuid'), ROOT], [S('paper'), 'A2'],
           [S('title_block'), [S('title'), 'INTENT 2026 Hardware Badge'], [S('date'), '2026-10-08'],
            [S('rev'), '0.3'], [S('company'), 'INTENT 2026 - by Palo Alto Networks'],
            [S('comment'), 1, 'RP2040 badge, 56x100 mm vending-machine outline'],
            [S('comment'), 2, 'Generated by scripts/gen_sch.py - edit design.py, not this file']],
           libsyms] + items + [[S('sheet_instances'), [S('path'), '/', [S('page'), '1']]],
                               [S('embedded_fonts'), S('no')]]
    with open(OUT, 'w', encoding='utf-8', newline='\n') as f:
        f.write(dump(sch) + '\n')
    print('wrote', os.path.abspath(OUT), len(design.parts), 'symbols')


if __name__ == '__main__':
    main()
