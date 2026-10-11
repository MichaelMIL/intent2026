"""Quick PNG preview of geometry + routes. usage: viz.py geo.json routes.json out.png [scale] [x0 y0 x1 y1]"""
import sys, json
from PIL import Image, ImageDraw

geo = json.load(open(sys.argv[1])); rt = json.load(open(sys.argv[2]))
S = float(sys.argv[4]) if len(sys.argv) > 4 else 12
win = list(map(float, sys.argv[5:9])) if len(sys.argv) > 8 else [-2, -2, 58, 102]
W, H = int((win[2] - win[0]) * S), int((win[3] - win[1]) * S)
im = Image.new('RGB', (W, H), (20, 20, 28))
d = ImageDraw.Draw(im, 'RGBA')
T = lambda x, y: ((x - win[0]) * S, (y - win[1]) * S)
d.polygon([T(*p) for p in geo['outline']], outline=(200, 200, 60), fill=(40, 30, 60))
failed = set()
for k, v in rt.get('failed', {}).items():
    failed.add(k)
for p in geo['pads']:
    col = (170, 140, 60, 255) if 'F' in p['layers'] else (60, 90, 170, 255)
    if p['net'] in failed:
        col = (255, 60, 255, 255)
    d.polygon([T(*q) for q in p['poly']], fill=col)
for t in rt['tracks']:
    col = (220, 50, 50, 200) if t['layer'] == 'F' else (60, 140, 255, 170)
    d.line([T(t['x1'], t['y1']), T(t['x2'], t['y2'])], fill=col, width=max(1, int(t['w'] * S)))
for v in rt['vias']:
    x, y = T(v['x'], v['y']); r = v['d'] / 2 * S
    d.ellipse([x - r, y - r, x + r, y + r], fill=(230, 230, 230, 255))
for f in geo['footprints']:
    x, y = T(f['x'], f['y'])
    d.text((x + 2, y + 2), f['ref'], fill=(255, 255, 255, 160))
im.save(sys.argv[3])
