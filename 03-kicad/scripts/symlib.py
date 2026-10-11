"""Load KiCad symbols from the stock libraries, flatten 'extends', list pins."""
import os, copy, math
from sexpr import parse, find, findall, Sym

SYMDIR = os.environ.get('KICAD9_SYMBOL_DIR', '/tmp/kroot/usr/share/kicad/symbols')
_cache = {}


def _lib(name):
    if name not in _cache:
        with open(os.path.join(SYMDIR, name + '.kicad_sym'), encoding='utf-8') as f:
            tree = parse(f.read())[0]
        _cache[name] = {s[1]: s for s in findall(tree, 'symbol')}
    return _cache[name]


def load(lib_id):
    """Return a flattened symbol S-expr named 'Lib:Name' suitable for lib_symbols."""
    lib, name = lib_id.split(':')
    syms = _lib(lib)
    s = copy.deepcopy(syms[name])
    ext = find(s, 'extends')
    if ext:
        parent = copy.deepcopy(syms[ext[1]])
        pname = ext[1]
        # child properties override parent's
        props = {p[1]: p for p in findall(s, 'property')}
        new = [Sym('symbol'), name]
        for item in parent[2:]:
            if isinstance(item, list) and item[0] == 'property' and item[1] in props:
                new.append(props.pop(item[1]))
            elif isinstance(item, list) and item[0] == 'symbol':
                item[1] = item[1].replace(pname, name, 1)
                new.append(item)
            else:
                new.append(item)
        for p in props.values():
            new.append(p)
        s = new
    s[1] = lib_id
    return s


def pins(sym):
    """List of (number, name, type, x, y, angle, length) for unit 1/common (unit 0) and all units."""
    out = []
    for sub in findall(sym, 'symbol'):
        # name like Name_U_S ; unit U (0 = common), style S (1 = normal)
        parts = sub[1].rsplit('_', 2)
        unit, style = int(parts[1]), int(parts[2])
        if style not in (0, 1):
            continue
        for p in findall(sub, 'pin'):
            at = find(p, 'at')
            ln = find(p, 'length')
            nm = find(p, 'name')[1]
            nu = find(p, 'number')[1]
            out.append(dict(num=nu, name=nm, type=str(p[1]), x=float(at[1]), y=float(at[2]),
                            ang=float(at[3]) if len(at) > 3 else 0.0, length=float(ln[1]), unit=unit))
    return out


def pin_tip(pin, sx, sy):
    """Schematic coordinate of the connectable end of a pin for an unrotated symbol at sx,sy."""
    return (round(sx + pin['x'], 4), round(sy - pin['y'], 4))


if __name__ == '__main__':
    import sys
    for lid in sys.argv[1:]:
        s = load(lid)
        print('==', lid, [ (p[1], p[2]) for p in findall(s, 'property') if p[1] in ('Footprint',)])
        for p in sorted(pins(s), key=lambda p: (p['unit'], p['num'])):
            print('  %s %-14s %-14s u%d (%g,%g) a%g' % (p['num'], p['name'], p['type'], p['unit'], p['x'], p['y'], p['ang']))
