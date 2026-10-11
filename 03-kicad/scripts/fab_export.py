"""(KiCad python) JLCPCB BOM + CPL from the finished board.

usage: fab_export.py <board.kicad_pcb> <outdir>
CPL rotation/offset are corrected per LCSC part using jlc_footprints.json (JLC/EasyEDA pad geometry):
  if JLC footprint E = rot(K, t) + d  (K = KiCad footprint, both in local frames),
  then JLC rotation = R - t and JLC position = P - rot(d, R - t).
"""
import os, sys, json, math, csv
from collections import OrderedDict
import pcbnew

HERE = os.path.dirname(os.path.abspath(__file__))


def rot(p, deg):
    a = math.radians(deg)
    x, y = p
    # KiCad orientation is CCW as seen on screen (y down)
    return (x * math.cos(a) + y * math.sin(a), -x * math.sin(a) + y * math.cos(a))


def local_pads(fp):
    P = fp.GetPosition(); R = fp.GetOrientationDegrees()
    out = {}
    for pad in fp.Pads():
        q = pad.GetPosition()
        v = (pcbnew.ToMM(q.x - P.x), pcbnew.ToMM(q.y - P.y))
        out.setdefault(pad.GetNumber(), []).append(rot(v, -R))
    return out


def correction(fp, jl):
    if jl.get('same'):
        return 0.0, (0.0, 0.0), 0.0
    K = local_pads(fp)
    kmap = jl.get('kicad_map', {})
    best = None
    for t in (0, 90, 180, 270):
        pairs = []
        used = set()
        for num, e in jl['pads'].items():
            kn = kmap.get(num, num)
            cands = [c for c in K.get(kn, []) if (kn, c) not in used]
            if not cands:
                continue
            # choose the KiCad pad (of that number) closest after rotation
            rc = [rot(c, t) for c in cands]
            pairs.append((e, rc))
        if not pairs:
            continue
        # translation from the centroid of matched pads (nearest candidate)
        ex = sum(e[0] for e, _ in pairs) / len(pairs); ey = sum(e[1] for e, _ in pairs) / len(pairs)
        kx = sum(min(rc, key=lambda c: (c[0] - e[0]) ** 2 + (c[1] - e[1]) ** 2)[0] for e, rc in pairs) / len(pairs)
        ky = sum(min(rc, key=lambda c: (c[0] - e[0]) ** 2 + (c[1] - e[1]) ** 2)[1] for e, rc in pairs) / len(pairs)
        d = (ex - kx, ey - ky)
        err = 0.0
        for e, rc in pairs:
            err += min(math.hypot(c[0] + d[0] - e[0], c[1] + d[1] - e[1]) for c in rc)
        err /= len(pairs)
        if best is None or err < best[2]:
            best = (t, d, err)
    return best


def main(pcb, outdir):
    os.makedirs(outdir, exist_ok=True)
    b = pcbnew.LoadBoard(pcb)
    jlc = json.load(open(os.path.join(HERE, 'jlc_footprints.json')))
    bom = OrderedDict()
    cpl = []
    report = []
    for fp in sorted(b.GetFootprints(), key=lambda f: (f.GetReference()[0], int(''.join(c for c in f.GetReference() if c.isdigit()) or 0))):
        ref = fp.GetReference()
        has = fp.HasField('LCSC') if hasattr(fp, 'HasField') else fp.HasFieldByName('LCSC')   # KiCad 10 / 9
        lcsc = fp.GetFieldText('LCSC') if has else ''
        if fp.IsDNP() or fp.IsExcludedFromBOM() or not lcsc:
            continue
        key = (fp.GetFPID().GetLibItemName().wx_str(), lcsc)
        bom.setdefault(key, []).append((ref, fp.GetValue()))
        P = fp.GetPosition(); R = fp.GetOrientationDegrees() % 360
        x, y = pcbnew.ToMM(P.x), pcbnew.ToMM(P.y)
        t, d, err = 0.0, (0.0, 0.0), 0.0
        if lcsc in jlc:
            t, d, err = correction(fp, jlc[lcsc])
        rj = (R - t) % 360
        dd = rot(d, rj)
        xj, yj = x - dd[0], y - dd[1]
        layer = 'Bottom' if fp.IsFlipped() else 'Top'
        cpl.append((ref, '%.4fmm' % xj, '%.4fmm' % (-yj), layer, '%g' % rj))
        if t or abs(d[0]) > 0.01 or abs(d[1]) > 0.01:
            report.append('%-5s %-10s KiCad rot %5.1f -> JLC rot %5.1f, offset (%.3f, %.3f) mm, fit err %.3f mm'
                          % (ref, lcsc, R, rj, -dd[0], dd[1], err))
    with open(os.path.join(outdir, 'bom_jlc.csv'), 'w', newline='', encoding='utf-8') as f:
        w = csv.writer(f)
        w.writerow(['Comment', 'Designator', 'Footprint', 'LCSC Part #'])
        for (fpn, lcsc), items in bom.items():
            vals = list(OrderedDict.fromkeys(v for _, v in items))
            val = vals[0] if len(vals) == 1 else {'C318884': 'TS-1187A-B-A-B tactile 5.1x5.1', 'C541850': 'Female header 1x3 2.54mm (slots)',
                                                   'C49257': 'Pin header 1x3 2.54mm (modules)'}.get(lcsc, '/'.join(vals))
            w.writerow([val, ','.join(r for r, _ in items), fpn, lcsc])
    with open(os.path.join(outdir, 'cpl_jlc.csv'), 'w', newline='', encoding='utf-8') as f:
        w = csv.writer(f)
        w.writerow(['Designator', 'Mid X', 'Mid Y', 'Layer', 'Rotation'])
        for row in cpl:
            w.writerow(row)
    with open(os.path.join(outdir, 'cpl_rotation_report.txt'), 'w', encoding='utf-8') as f:
        f.write('CPL corrections applied (JLC/EasyEDA footprint orientation vs KiCad):\n')
        f.write('\n'.join(report) + '\n')
        f.write('\nNOT verifiable by pad geometry (symmetric pad pattern, 0 and 180 deg fit equally; 0 assumed).\n'
                'Check these in the JLC placement preview before paying:\n'
                '  D6     C7420330   SOD-123 Schottky: cathode (KiCad pad 1) towards U3 / VSYS. Reversed = no USB power.\n'
                '  U5     C91447     IRM-H638T: GND pair (pins 1,2) on the J4 side. 180 deg wrong puts VCC on a GND pad.\n'
                '  LED1-4 C52917434  WS2812B-2020: pin 1 (DOUT) corner as in the KiCad footprint.\n'
                '  Y1     C133334    3225 crystal: 180 deg is harmless, 90 deg shorts the crystal to GND.\n'
                '  D1-D5  C2286      cathode = KiCad pad 1 (CPL already rotated 180 deg for JLC).\n'
                '  D7     C81598     1N4148W SOD-123 on the SPK module: cathode (KiCad pad 1) towards SPM_3V3 / LS1 side.\n'
                '  LS1    C94599     MLT-8530: lead row (+/-) towards the module header P3. The footprint wires the dummy pads\n'
                '                    crosswise, so 180 deg only reverses the coil; 90 deg = silent but harmless.\n'
                '  J5-J7, P1-P3      1x3 headers (THT, hand-soldered by JLC): symmetric, orientation irrelevant.\n')
    print('BOM lines', len(bom), 'placements', len(cpl), 'corrected', len(report))
    print('\n'.join(report))


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
