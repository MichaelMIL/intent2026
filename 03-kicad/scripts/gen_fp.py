"""Custom footprints (intent.pretty).

Pad geometry copied from the JLCPCB/EasyEDA footprints of the exact LCSC
parts, in the same orientation and origin, so JLC's CPL needs no rotation or
offset correction for these parts:
  C393939 TYPE-C-16PIN, C431535 PJ-320D (SMD), C91447 IRM-H638T/TR2,
  C722761 PH2.0-2P-LT (SMD vertical), C94599 MLT-8530 transducer.
Plus the mouse-bite footprint for the breakaway module tabs (board-only, no copper).
"""
import os

OUT = os.path.join(os.path.dirname(__file__), '..', 'intent.pretty')
os.makedirs(OUT, exist_ok=True)


def f(v):
    s = ('%.4f' % v).rstrip('0').rstrip('.')
    return '0' if s in ('-0', '') else s


def smd(name, x, y, w, h, layers='"F.Cu" "F.Paste" "F.Mask"', shape='rect', extra=''):
    return '\t(pad "%s" smd %s (at %s %s) (size %s %s) (layers %s)%s)\n' % (name, shape, f(x), f(y), f(w), f(h), layers, extra)


def line(x1, y1, x2, y2, layer, w=0.12):
    return '\t(fp_line (start %s %s) (end %s %s) (stroke (width %s) (type solid)) (layer "%s"))\n' % (
        f(x1), f(y1), f(x2), f(y2), f(w), layer)


def rect(x1, y1, x2, y2, layer, w=0.1):
    return '\t(fp_rect (start %s %s) (end %s %s) (stroke (width %s) (type solid)) (fill no) (layer "%s"))\n' % (
        f(x1), f(y1), f(x2), f(y2), f(w), layer)


def circle(cx, cy, r, layer, w=0.12):
    return '\t(fp_circle (center %s %s) (end %s %s) (stroke (width %s) (type solid)) (fill no) (layer "%s"))\n' % (
        f(cx), f(cy), f(cx + r), f(cy), f(w), layer)


def header(name, descr, tags, attr='smd', ref_y=-5, val_y=5):
    return ('(footprint "%s"\n\t(version 20241229)\n\t(generator "intent_gen_fp")\n\t(generator_version "9.0")\n'
            '\t(layer "F.Cu")\n\t(descr "%s")\n\t(tags "%s")\n'
            '\t(property "Reference" "REF**" (at 0 %s 0) (layer "F.SilkS") (effects (font (size 1 1) (thickness 0.15))))\n'
            '\t(property "Value" "%s" (at 0 %s 0) (layer "F.Fab") (effects (font (size 1 1) (thickness 0.15))))\n'
            '\t(attr %s)\n') % (name, descr, tags, f(ref_y), name, f(val_y), attr)


def write(name, body):
    with open(os.path.join(OUT, name + '.kicad_mod'), 'w', newline='\n') as fh:
        fh.write(body + ')\n')


# ---------------------------------------------------------------- USB-C C393939
def usb_c():
    n = 'USB_C_TYPE-C16PIN_C393939'
    b = header(n, 'USB-C 16-pin receptacle, LCSC C393939 (SHOU HAN TYPE-C 16PIN). Pads per JLC/EasyEDA footprint. Mouth toward +Y.',
               'USB C Type-C receptacle USB2.0', ref_y=-4.4, val_y=6.2)
    y = -2.362
    sig = [('A1', -3.2, .6), ('B12', -3.2, .6), ('A4', -2.4, .6), ('B9', -2.4, .6), ('B8', -1.75, .3), ('A5', -1.25, .3),
           ('B7', -0.75, .3), ('A6', -0.25, .3), ('A7', 0.25, .3), ('B6', 0.75, .3), ('A8', 1.25, .3), ('B5', 1.75, .3),
           ('A9', 2.4, .6), ('B4', 2.4, .6), ('A12', 3.2, .6), ('B1', 3.2, .6)]
    for nm, x, w in sig:
        b += smd(nm, x, y, w, 1.15)
    for x in (-2.89, 2.89):
        b += '\t(pad "" np_thru_hole circle (at %s -1.288) (size 0.65 0.65) (drill 0.65) (layers "*.Cu" "*.Mask"))\n' % f(x)
    for x in (-4.32, 4.32):
        b += '\t(pad "S1" thru_hole oval (at %s -1.787) (size 1 2.1) (drill oval 0.6 1.7) (layers "*.Cu" "*.Mask"))\n' % f(x)
        b += '\t(pad "S1" thru_hole oval (at %s 2.362) (size 1 1.8) (drill oval 0.6 1.4) (layers "*.Cu" "*.Mask"))\n' % f(x)
    b += rect(-4.47, -2.34, 4.47, 4.96, 'F.Fab')
    b += line(-4.47, 4.96, 4.47, 4.96, 'Dwgs.User', 0.1)
    b += line(-4.7, -0.5, -4.7, 1.0, 'F.SilkS') + line(4.7, -0.5, 4.7, 1.0, 'F.SilkS')
    b += line(-4.7, 3.4, -4.7, 4.3, 'F.SilkS') + line(4.7, 3.4, 4.7, 4.3, 'F.SilkS')
    b += rect(-5.2, -3.3, 5.2, 5.2, 'F.CrtYd', 0.05)
    write(n, b)


# ---------------------------------------------------------------- PJ-320D C431535
def pj320d():
    n = 'Jack_3.5mm_PJ-320D_SMD_C431535'
    b = header(n, '3.5 mm TRRS jack, SMD, LCSC C431535 (SHOU HAN PJ-320D). Pads per JLC/EasyEDA. 1=S 2=R2 3=R1 4=T. Mouth toward -X.',
               'audio jack 3.5mm TRRS SMD', ref_y=-5.6, val_y=5.6)
    for nm, x, y in (('R2', -4.2, -3.5), ('R1', -1.2, -3.5), ('T', 2.8, -3.5), ('S', 4.2, 3.5)):
        b += smd(nm, x, y, 1.5, 3.0)
    for x in (-5.7, 1.3):
        b += '\t(pad "" np_thru_hole circle (at %s 0) (size 1 1) (drill 1) (layers "*.Cu" "*.Mask"))\n' % f(x)
    b += rect(-7.3, -3.0, 4.7, 3.0, 'F.Fab') + rect(-9.3, -2.5, -7.3, 2.5, 'F.Fab')
    b += line(-7.3, -3.0, -5.1, -3.0, 'F.SilkS') + line(-7.3, -3.0, -7.3, 3.0, 'F.SilkS')
    b += line(-7.3, 3.0, 3.2, 3.0, 'F.SilkS') + line(4.7, -1.8, 4.7, 1.6, 'F.SilkS')
    b += rect(-9.6, -5.3, 5.2, 5.3, 'F.CrtYd', 0.05)
    write(n, b)


# ---------------------------------------------------------------- IRM-H638T C91447
def irm():
    n = 'IRM-H638T_C91447'
    b = header(n, 'Everlight IRM-H638T/TR2 38 kHz IR receiver, top-looking SMD, LCSC C91447. 1,2=GND 3=OUT 4=VCC.',
               'IR receiver 38kHz', ref_y=-3.6, val_y=3.6)
    for nm, x, y in (('1', -2.95, -1.27), ('2', -2.95, 1.27), ('3', 2.95, 1.27), ('4', 2.95, -1.27)):
        b += smd(nm, x, y, 1.5, 0.9)
    b += rect(-2.0, -2.5, 2.0, 2.5, 'F.Fab')
    b += circle(0, -0.76, 1.5, 'F.Fab', 0.1)
    b += line(-2.0, -2.6, 2.0, -2.6, 'F.SilkS') + line(-2.0, 2.6, 2.0, 2.6, 'F.SilkS')
    b += circle(-3.9, -2.2, 0.15, 'F.SilkS', 0.3)
    b += rect(-3.95, -2.85, 3.95, 2.85, 'F.CrtYd', 0.05)
    write(n, b)


# ---------------------------------------------------------------- JST PH SMD C722761
def jst():
    n = 'JST_PH_2P_SMD_Vertical_C722761'
    b = header(n, 'PH2.0 2-pin SMD vertical (CAX PH2.0-2P-LT), LCSC C722761. Pads per JLC/EasyEDA. 1=BAT+ 2=GND.',
               'JST PH 2.0 battery', ref_y=-6.0, val_y=4.4)
    b += smd('1', -1, 1.756, 1, 3) + smd('2', 1, 1.756, 1, 3)
    b += smd('MP', 4.064, -1.756, 2, 3.5) + smd('MP', -4.064, -1.756, 2, 3.5)
    b += rect(-4.0, -4.73, 4.0, 0.67, 'F.Fab')
    b += line(-4.0, -4.85, 4.0, -4.85, 'F.SilkS') + line(-2.0, 0.8, -1.7, 0.8, 'F.SilkS')
    b += line(-0.3, 0.8, 0.3, 0.8, 'F.SilkS') + line(1.7, 0.8, 2.6, 0.8, 'F.SilkS')
    b += circle(-2.2, 2.6, 0.15, 'F.SilkS', 0.3)
    b += rect(-5.3, -5.1, 5.3, 3.55, 'F.CrtYd', 0.05)
    write(n, b)


# ---------------------------------------------------------------- lanyard hole
def hole():
    n = 'LanyardHole_4.0mm_Plated'
    b = header(n, 'Lanyard hole, 4.0 mm plated, 0.5 mm annular ring, 1.5 mm pour clearance', 'lanyard hole',
               attr='through_hole exclude_from_pos_files exclude_from_bom', ref_y=-3.4, val_y=3.4)
    b += ('\t(pad "1" thru_hole circle (at 0 0) (size 5 5) (drill 4) (layers "*.Cu" "*.Mask") '
          '(clearance 1.5) (zone_connect 0))\n')
    b += circle(0, 0, 2.5, 'F.Fab', 0.1)
    b += circle(0, 0, 4.0, 'F.CrtYd', 0.05)
    write(n, b)


# ---------------------------------------------------------------- MLT-8530 C94599
def mlt8530():
    """Jiangsu Huaneng MLT-8530 SMD magnetic transducer, 8.5 x 8.5 x 3 mm.
    JLC/EasyEDA geometry: four 2.4 mm square pads at (+-3.6, +-3.6). Per the datasheet only the two pads on one
    side are the coil leads ('+' and '-'); the other two are dummy pads. In the EasyEDA orientation the leads are
    the +Y (bottom) row = JLC pads 1 (+) and 2 (-); the sound port is on the -Y (top) edge.
    The dummy pads are numbered 1/2 crosswise, so a 180 deg placement error only reverses the coil (harmless) and
    a 90 deg error shorts nothing (both leads on one net = silent, no damage)."""
    n = 'Buzzer_MLT-8530_C94599'
    b = header(n, 'MLT-8530 SMD magnetic transducer 8.5x8.5x3 mm, LCSC C94599. Pads per JLC/EasyEDA; leads = +Y row '
               '(pad 1 = +, pad 2 = -), -Y pads are dummies wired crosswise (1/2). Sound port on the -Y edge.',
               'buzzer transducer MLT-8530 SMD', ref_y=-5.8, val_y=5.8)
    for nm, x, y in (('1', -3.6, 3.6), ('2', 3.6, 3.6), ('2', 3.6, -3.6), ('1', -3.6, -3.6)):
        b += smd(nm, x, y, 2.4, 2.4)
    b += rect(-4.25, -4.25, 4.25, 4.25, 'F.Fab')
    b += circle(0, 0, 2.0, 'F.Fab', 0.1)
    b += line(-1.0, -3.0, 1.0, -3.0, 'F.Fab', 0.1) + line(-1.0, -3.0, 0, -4.0, 'F.Fab', 0.1) + line(1.0, -3.0, 0, -4.0, 'F.Fab', 0.1)
    b += line(-4.4, -2.0, -4.4, 2.0, 'F.SilkS') + line(4.4, -2.0, 4.4, 2.0, 'F.SilkS')
    b += line(-2.0, -4.4, 2.0, -4.4, 'F.SilkS') + line(-2.0, 4.4, 2.0, 4.4, 'F.SilkS')
    b += circle(-5.3, 4.4, 0.15, 'F.SilkS', 0.3)
    b += rect(-5.0, -5.0, 5.0, 5.0, 'F.CrtYd', 0.05)
    write(n, b)


# ---------------------------------------------------------------- mouse bites (breakaway tabs)
def mousebites():
    """4 x 0.5 mm non-plated holes on a 1.0 mm pitch (0.5 mm webs, within the JLC 0.5 mm hole-to-hole rule),
    centred on a 4 mm breakaway tab. Board-only: not in the schematic, BOM or CPL. The 0.5 mm pad clearance keeps
    tracks and pours half a millimetre away from the break line."""
    n = 'MouseBites_1x4_D0.5_P1.0'
    b = header(n, 'Mouse bites for a 4 mm breakaway tab: 4 x 0.5 mm NPTH, 1.0 mm pitch. Board-only (not in schematic/BOM/CPL).',
               'mouse bites breakaway tab panel', attr='board_only exclude_from_pos_files exclude_from_bom', ref_y=-1.6, val_y=1.6)
    for x in (-1.5, -0.5, 0.5, 1.5):
        b += ('\t(pad "" np_thru_hole circle (at %s 0) (size 0.5 0.5) (drill 0.5) (layers "*.Cu" "*.Mask") '
              '(clearance 0.5))\n' % f(x))
    b += line(-2.0, 0, 2.0, 0, 'Dwgs.User', 0.05)
    write(n, b)


if __name__ == '__main__':
    usb_c(); pj320d(); irm(); jst(); hole(); mlt8530(); mousebites()
    print('footprints ->', os.path.abspath(OUT))
