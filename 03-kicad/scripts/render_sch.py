"""Render the schematic to PNG for a visual check: render_sch.py <out.png> [dpi] [x0 y0 x1 y1 crop in mm]"""
import os, sys, subprocess, tempfile, glob
HERE = os.path.dirname(os.path.abspath(__file__))
KCLI = os.environ.get('KCLI', '/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli')
SCH = os.path.join(HERE, '..', 'intent-2026-badge.kicad_sch')

out = sys.argv[1]
dpi = int(float(sys.argv[2])) if len(sys.argv) > 2 else 60
tmp = tempfile.mkdtemp()
subprocess.run([KCLI, 'sch', 'export', 'pdf', '-o', os.path.join(tmp, 's.pdf'), '--no-background-color', SCH],
               capture_output=True, text=True)
import fitz
doc = fitz.open(os.path.join(tmp, 's.pdf'))
page = doc[0]
clip = None
if len(sys.argv) > 6:
    x0, y0, x1, y1 = map(float, sys.argv[3:7])
    k = 72 / 25.4
    clip = fitz.Rect(x0 * k, y0 * k, x1 * k, y1 * k)
pix = page.get_pixmap(dpi=dpi, clip=clip)
pix.save(out)
print(out, pix.width, pix.height)
