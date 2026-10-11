"""Verify the generated schematic against design.py.

usage: check_sch.py [--erc]   (run from anywhere; uses KCLI env or the macOS KiCad app path)

Exports the netlist with kicad-cli and checks that every (ref, pin) carries exactly the
net name design.py assigns, that no extra nets exist, and optionally that ERC is clean.
Exit status 1 on any mismatch.
"""
import os, sys, subprocess, tempfile
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from sexpr import parse, find, findall
import design

KCLI = os.environ.get('KCLI', '/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli')
SCH = os.path.join(HERE, '..', 'intent-2026-badge.kicad_sch')


def main():
    tmp = tempfile.mkdtemp()
    net = os.path.join(tmp, 'n.net')
    r = subprocess.run([KCLI, 'sch', 'export', 'netlist', '-o', net, SCH], capture_output=True, text=True)
    if r.returncode or not os.path.exists(net):
        print(r.stdout, r.stderr); sys.exit(1)
    t = parse(open(net, encoding='utf-8').read())[0]
    have = {}
    for n in findall(find(t, 'nets'), 'net'):
        name = find(n, 'name')[1]
        for nd in findall(n, 'node'):
            ref = find(nd, 'ref')[1]
            if ref.startswith('#'):
                continue
            have[(ref, find(nd, 'pin')[1])] = name
    want = {}
    for p in design.parts:
        for pin, nn in p['pins'].items():
            if nn:
                want[(p['ref'], pin)] = nn
    bad = 0
    for k in sorted(set(want) | set(have)):
        w, h = want.get(k), have.get(k)
        if w != h:
            if h is not None and h.startswith('unconnected-') and w is None:
                continue
            print('MISMATCH %-5s pin %-4s design=%-14s schematic=%s' % (k[0], k[1], w, h)); bad += 1
    wn, hn = set(want.values()), {v for v in have.values() if not v.startswith('unconnected-')}
    for n in sorted(wn - hn):
        print('net missing in schematic:', n); bad += 1
    for n in sorted(hn - wn):
        print('extra net in schematic:', n); bad += 1
    comps = {find(c, 'ref')[1] for c in findall(find(t, 'components'), 'comp')}
    refs = {p['ref'] for p in design.parts}
    for r_ in sorted(refs - comps):
        print('part missing in schematic:', r_); bad += 1
    for r_ in sorted(comps - refs):
        print('extra part in schematic:', r_); bad += 1
    print('netlist: %d pins checked, %d nets, %d problems' % (len(want), len(wn), bad))
    if '--erc' in sys.argv:
        rpt = os.path.join(tmp, 'erc.rpt')
        subprocess.run([KCLI, 'sch', 'erc', '--severity-all', '-o', rpt, SCH], capture_output=True, text=True)
        txt = open(rpt, encoding='utf-8').read()
        import re
        m = re.search(r'ERC messages:\s*(\d+)\s+Errors\s+(\d+)\s+Warnings\s+(\d+)', txt)
        print('ERC:', m.group(0) if m else txt[-400:])
        for line in txt.splitlines():
            if line.startswith('['):
                print('  ', line[:140])
        if m and int(m.group(2)):
            bad += int(m.group(2))
    sys.exit(1 if bad else 0)


if __name__ == '__main__':
    main()
