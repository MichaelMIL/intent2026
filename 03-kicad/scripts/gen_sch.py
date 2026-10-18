"""Generate intent-2026-badge.kicad_sch from design.py as a readable, wired schematic.

Layout (A2, one sheet):
    row 1: USB-C | power path | expansion ports (J5-J7) | IR module
    row 2: RP2040 core (decoupling, crystal, flash, BOOTSEL) | UI (keys, LEDs, RGB) | header / TP / flags
    row 3: audio module | speaker module      (the three modules are breakaway boards with their own nets)
Power rails use power symbols; every other net carries a local label with the design.py net
name, so the PCB netlist (names included) is unchanged. Verify with scripts/check_sch.py.
"""
import os, sys
sys.path.insert(0, os.path.dirname(__file__))
import design
from schlib import Sheet, uid, PROJECT

OUT = os.path.join(os.path.dirname(__file__), '..', PROJECT + '.kicad_sch')
D = {p['ref']: p for p in design.parts}
sh = Sheet('A2')


def put(ref, x, y, rot=0, mir=None, **kw):
    p = D[ref]
    fields = {'LCSC': p['lcsc']} if p['lcsc'] else {}
    if p['desc']:
        fields['Description'] = p['desc']
    kw.setdefault('fields', fields)
    return sh.place(ref, p['lib'], p['value'], x, y, rot=rot, mir=mir, fp=p['fp'], in_bom=p['in_bom'], dnp=p['dnp'], **kw)


# label offsets for passives: horizontal (rot 90/270) -> ref above, value below; vertical -> right side
H = dict(ref_at=(0, -2.54), val_at=(0, 2.54))
V = dict(ref_at=(2.54, -1.27), val_at=(2.54, 1.27), just=['left'])
P = sh.pin
W = sh.wire


def note(x, y, *lines, size=1.5):
    """Multi-line note, first line at y, 3.81 mm line pitch."""
    for i, ln in enumerate(lines):
        sh.text(ln, x, y + 3.81 * i, size)


def stub_labels(ref, pins, x_to, ang, names=None):
    """Horizontal stubs from pins to x_to with labels (names: pin -> net, default from design)."""
    for pn in pins:
        net = (names or D[ref]['pins'])[str(pn)]
        p = P(ref, pn)
        W(p, (x_to, p[1]))
        sh.label(net, x_to, p[1], ang)


# =============================================================================================
# Block A - USB-C
# =============================================================================================
sh.box(25.4, 25.4, 152.4, 121.92, 'USB-C  (USB 2.0 full speed, device)')
put('J1', 55.88, 68.58, ref_at=(-10.16, -27.94), val_at=(-10.16, -25.4), just=['left'])
W(P('J1', 'A4'), (78.74, 53.34), (78.74, 45.72)); sh.power('VBUS', 78.74, 45.72)
put('R1', 83.82, 58.42, 90, ref_at=(0, -5.08), val_at=(0, -2.54)); put('R2', 83.82, 60.96, 90, ref_at=(0, 2.54), val_at=(0, 5.08))
W(P('J1', 'A5'), P('R1', 1)); sh.label('CC1', 73.66, 58.42)
W(P('J1', 'B5'), P('R2', 1)); sh.label('CC2', 73.66, 60.96)
W(P('R1', 2), (92.71, 58.42), (92.71, 66.04)); W(P('R2', 2), (92.71, 60.96)); sh.power('GND', 92.71, 66.04)
# D- (upper pins) and D+ (lower pins) to the ESD array; one deliberate crossing at (78.74, 101.6)
W(P('J1', 'A7'), (73.66, 66.04), (73.66, 68.58)); W(P('J1', 'B7'), (78.74, 68.58), (78.74, 104.14), (93.98, 104.14))
W(P('J1', 'A6'), (76.2, 71.12), (76.2, 73.66)); W(P('J1', 'B6'), (76.2, 73.66), (76.2, 101.6), (93.98, 101.6))
sh.label('USB_DP_CONN', 80.01, 101.6); sh.label('USB_DM_CONN', 78.74, 91.44, 90)
sh.nc(P('J1', 'A8')); sh.nc(P('J1', 'B8'))
W(P('J1', 'A1'), (55.88, 96.52)); W(P('J1', 'SH'), (48.26, 96.52), (55.88, 96.52)); sh.power('GND', 55.88, 96.52)
# VBUS decoupling (rev 0.6): 1 uF bulk + 100 nF at the connector / USBLC6 pin 5
sh.power('VBUS', 127.0, 40.64); W((127.0, 40.64), (142.24, 40.64))
put('C27', 132.08, 44.45, **V); put('C28', 142.24, 44.45, **V)
W(P('C27', 2), (132.08, 53.34), (142.24, 53.34)); W(P('C28', 2), (142.24, 53.34)); sh.power('GND', 137.16, 53.34)
put('U4', 99.06, 101.6, ref_at=(-6.35, -7.62), val_at=(2.54, -7.62), just=['left'])
W(P('U4', 5), (99.06, 91.44)); sh.power('VBUS', 99.06, 91.44)
W(P('U4', 2), (99.06, 111.76)); sh.power('GND', 99.06, 111.76)
# pins 1/6 and 3/4 of the USBLC6 are the same line each; the labels on both sides make that explicit
put('R11', 121.92, 101.6, 90, **H); put('R12', 124.46, 106.68, 90, ref_at=(0, 2.54), val_at=(0, 5.08))
W(P('U4', 6), P('R11', 1)); sh.label('USB_DP_CONN', 105.41, 101.6)
W(P('R11', 2), (130.81, 101.6)); sh.label('USB_DP', 130.81, 101.6)
W(P('U4', 4), (106.68, 104.14), (106.68, 106.68), P('R12', 1)); sh.label('USB_DM_CONN', 107.95, 106.68)
W(P('R12', 2), (130.81, 106.68)); sh.label('USB_DM', 130.81, 106.68)
note(27.94, 110.49, 'HRO TYPE-C-31-M-12 (C165948). 5.1k on CC1/CC2 = UFP.',
     'USBLC6-2 ESD array, 27R series (RP2040 guide).',
     'C27/C28 VBUS decoupling. SBU pins unused.')

# =============================================================================================
# Block B - power path
# =============================================================================================
sh.box(157.48, 25.4, 330.2, 121.92, 'POWER   USB or 3xAAA -> VSYS -> 3V3 LDO')
sh.power('VBUS', 170.18, 43.18); W((170.18, 43.18), (170.18, 53.34), (179.07, 53.34))
put('D6', 182.88, 53.34, 180, **H)                      # anode left (VBUS), cathode right (VSYS)
W(P('D6', 1), (226.06, 53.34), (226.06, 43.18)); sh.power('VSYS', 226.06, 43.18)
# battery: J3 -> JP1 (or SW5) -> Q1 drain; VBUS on the gate holds Q1 off when USB is present
put('J3', 170.18, 71.12, mir='y', ref_at=(-2.54, -5.08), val_at=(-2.54, 7.62))
W(P('J3', 1), (185.42, 71.12)); sh.label('BAT_IN', 177.8, 71.12)
W(P('J3', 2), (177.8, 73.66), (177.8, 78.74)); sh.power('GND', 177.8, 78.74)
put('JP1', 190.5, 71.12, ref_at=(0, -3.81), val_at=(0, 3.81))
put('SW5', 190.5, 60.96, ref_at=(0, -5.08), val_at=(8.89, 0.64), just=['left'])
W((185.42, 71.12), P('SW5', 2)); W(P('SW5', 1), (198.12, 58.42), (198.12, 71.12)); sh.nc(P('SW5', 3))
put('Q1', 215.9, 73.66, 90, ref_at=(6.35, 2.54), val_at=(6.35, 5.08), just=['left'])
W(P('JP1', 2), P('Q1', 3)); sh.label('BAT_SW', 200.66, 71.12)
W(P('Q1', 2), (226.06, 71.12), (226.06, 53.34))
put('R10', 215.9, 87.63, **V)
W(P('Q1', 1), P('R10', 1)); W(P('R10', 2), (215.9, 93.98)); sh.power('GND', 215.9, 93.98)
W((215.9, 83.82), (236.22, 83.82)); sh.power('VBUS', 236.22, 83.82)
# VBUS sense divider
sh.power('VBUS', 248.92, 43.18); put('R15', 248.92, 50.8, **V); put('R16', 248.92, 64.77, **V)
W((248.92, 43.18), P('R15', 1)); W(P('R15', 2), P('R16', 1)); W(P('R16', 2), (248.92, 71.12)); sh.power('GND', 248.92, 71.12)
W((248.92, 57.15), (259.08, 57.15)); sh.label('VBUS_SENSE', 259.08, 57.15)
# LDO
sh.power('VSYS', 279.4, 43.18); W((279.4, 43.18), (279.4, 53.34))
put('C9', 279.4, 57.15, **V); put('U3', 297.18, 55.88, ref_at=(0, -7.62), val_at=(0, -10.16)); put('C20', 309.88, 57.15, **V)
W((279.4, 53.34), P('U3', 1)); W((284.48, 53.34), (284.48, 55.88), P('U3', 3)); sh.nc(P('U3', 4))
W(P('U3', 5), (317.5, 53.34), (317.5, 43.18)); sh.power('+3V3', 317.5, 43.18)
W(P('C9', 2), (279.4, 66.04), (309.88, 66.04), P('C20', 2)); W(P('U3', 2), (297.18, 66.04)); sh.power('GND', 297.18, 66.04)
note(160.02, 102.87, 'VSYS = 4.65 V on USB (after D6), 3.0-4.8 V on battery. With both present VBUS holds Q1 off, D6 blocks back-feed.',
     'SW5 is DNP (the switch is on the battery box); JP1 bridges it. Cut JP1 only if SW5 is fitted.',
     'RGB LEDs run from VSYS, everything else from 3V3 (AP2112K-3.3, 600 mA, EN tied to VIN).',
     'R15/R16: VBUS_SENSE = 2.5 V on USB, 0 V on battery (GPIO29 / ADC3) so firmware can dim and sleep.')

# =============================================================================================
# Block C - expansion ports (main board side)
# =============================================================================================
sh.box(335.28, 25.4, 424.18, 121.92, 'SAO PORTS  3 x 2x3 socket')
for ref, y in (('J5', 40.64), ('J6', 60.96), ('J7', 81.28)):
    put(ref, 381.0, y, ref_at=(-1.27, -6.35), val_at=(-1.27, 6.35), just=['left'])
    pins = D[ref]['pins']
    p = P(ref, 1); W(p, (368.3, p[1])); sh.power('+3V3', 368.3, p[1])
    for pn in (3, 5):
        p = P(ref, pn); W(p, (368.3, p[1])); sh.label(pins[str(pn)], 368.3, p[1], 180)
    p = P(ref, 2); W(p, (393.7, p[1])); sh.power('GND', 393.7, p[1], rot=90)
    for pn in (4, 6):
        p = P(ref, pn); W(p, (396.24, p[1])); sh.label(pins[str(pn)], 396.24, p[1])
for ref, y in (('R22', 96.52), ('R23', 104.14)):
    put(ref, 360.68, y, 90, ref_at=(0, -1.91), val_at=(0, 1.91))
    W(P(ref, 1), (350.52, y)); sh.label(D[ref]['pins']['1'], 350.52, y, 180)
    W(P(ref, 2), (370.84, y))
W((370.84, 93.98), (370.84, 104.14)); sh.power('+3V3', 370.84, 93.98)
sh.text('SAO (badge.team): 1 3V3, 2 GND, 3 SDA, 4 SCL, 5 GPIO1, 6 GPIO2.', 337.82, 110.49, 1.27)
sh.text('I2C0 on GPIO12/13, 4.7k pull-ups. GPIO1: IR 22 / AUDIO 11 / SPK 25.', 337.82, 113.79, 1.27)
sh.text('GPIO2: GPIO26/27/28 (ADC). Socket on badge, 2x3 pin header on the add-on.', 337.82, 117.09, 1.27)

# =============================================================================================
# Block D - IR module (breakaway board; nets IRM_*)
# =============================================================================================
sh.box(429.26, 25.4, 568.96, 121.92, 'IR MODULE  breakaway board, plugs into J5')
sh.power('IRM_3V3', 447.04, 43.18); put('R19', 447.04, 54.61, **V)
W((447.04, 43.18), P('R19', 1)); W(P('R19', 2), (447.04, 63.5), (482.6, 63.5))
put('C23', 452.12, 67.31, **V); put('C24', 462.28, 67.31, **V)
put('U5', 492.76, 68.58, mir='y', ref_at=(0, -10.16), val_at=(0, 10.16))
sh.label('IRM_VCC', 469.9, 63.5)
W(P('C23', 2), (452.12, 73.66), P('U5', 1)); W(P('C24', 2), (462.28, 73.66)); sh.power('IRM_GND', 457.2, 73.66, lib='power:GND')
sh.label('IRM_OUT', P('U5', 3)[0], P('U5', 3)[1], 180)
put('P1', 444.5, 88.9, mir='y', ref_at=(-1.27, -6.35), val_at=(-1.27, 6.35), just=['left'])
p = P('P1', 1); W(p, (457.2, p[1])); sh.label('IRM_3V3', 457.2, p[1])
p = P('P1', 5); W(p, (457.2, p[1])); sh.label('IRM_OUT', 457.2, p[1])
p = P('P1', 2); W(p, (434.34, p[1]), (434.34, 96.52)); sh.power('IRM_GND', 434.34, 96.52, lib='power:GND')
for pn in (3, 4, 6):
    sh.nc(P('P1', pn))
note(434.34, 106.68, 'Everlight IRM-H638T, 38 kHz. Open-collector out, active low, internal pull-up.',
     'R19 + C24 = datasheet RC filter. Pinout 1,2 = GND, 3 = OUT, 4 = VCC (verified).',
     'P1: SAO 2x3 header, 1 = 3V3, 2 = GND, 5 = GPIO1 = OUT; plugs into J5. IRM_* nets live only on this board;',
     'no copper crosses the tab. Snap off at the mouse bites, plug in standing up (lens looks sideways).')

# =============================================================================================
# Block E - RP2040 core
# =============================================================================================
sh.box(25.4, 127.0, 330.2, 342.9, 'RP2040  dual Cortex-M0+, 2 MB QSPI flash, 12 MHz crystal')
UX, UY = 203.2, 254.0
put('U1', UX, UY, ref_at=(-21.59, -50.8), val_at=(-21.59, -48.26), just=['left'])
# supplies
for pn in (43, 48, 1, 44):
    W(P('U1', pn), (P('U1', pn)[0], 200.66))
W((190.5, 200.66), (205.74, 200.66)); sh.power('+3V3', 196.85, 200.66)
for pn in (45, 23):
    W(P('U1', pn), (P('U1', pn)[0], 203.2))
W((210.82, 203.2), (215.9, 203.2)); sh.power('+1V1', 213.36, 203.2)
W(P('U1', 57), (UX, 304.8)); sh.power('GND', UX, 304.8)
# TESTEN, RUN
W(P('U1', 19), (170.18, 223.52), (170.18, 226.06)); sh.power('GND', 170.18, 226.06)
put('R4', 162.56, 227.33, 180, **V)
W(P('U1', 26), (154.94, 231.14)); sh.label('RUN', 154.94, 231.14, 180)
W(P('R4', 2), (162.56, 220.98)); sh.power('+3V3', 162.56, 220.98)
put('SW6', 124.46, 233.68, ref_at=(0, -5.08), val_at=(0, -7.62))
W(P('SW6', 1), (114.3, 233.68)); sh.label('RUN', 114.3, 233.68, 180)
W(P('SW6', 2), (132.08, 233.68), (132.08, 236.22)); sh.power('GND', 132.08, 236.22)
# USB, QSPI, SWD stubs with labels
stub_labels('U1', (46, 47, 56, 52, 53, 55, 54, 51, 24, 25), 172.72, 180)
# crystal
put('Y1', 144.78, 294.64, ref_at=(0, -3.81), val_at=(6.35, 0.64), just=['left'])
W(P('U1', 20), (140.97, 269.24), P('Y1', 1)); sh.label('XIN', 160.02, 269.24)
put('R13', 163.83, 279.4, 270, **H)
W(P('U1', 21), P('R13', 1)); sh.label('XOUT', 170.18, 279.4)
W(P('R13', 2), (148.59, 279.4), P('Y1', 3)); sh.label('XOUT_R', 151.13, 279.4)
put('C11', 137.16, 287.02, 270, **H); put('C12', 152.4, 287.02, 90, **H)
W(P('C11', 2), (130.81, 287.02), (130.81, 302.26), (158.75, 302.26), (158.75, 287.02), P('C12', 2))
W(P('Y1', 2), (144.78, 302.26)); sh.power('GND', 144.78, 302.26)
# decoupling bank
sh.text('Decoupling (RP2040 guide 2.1.2/2.1.3): 100 nF per IOVDD (6x), USB_VDD, ADC_AVDD, DVDD (C19 pin 23, C10 pin 50); 1 uF on VREG_VIN (C18) and VREG_VOUT (C26).', 33.02, 143.51, 1.5)
caps = ['C1', 'C2', 'C3', 'C4', 'C5', 'C17', 'C7', 'C8', 'C18']
for i, c in enumerate(caps):
    put(c, 38.1 + 10.16 * i, 156.21, **V)
    W(P(c, 2), (38.1 + 10.16 * i, 165.1))
W((33.02, 152.4), (119.38, 152.4)); W((33.02, 165.1), (119.38, 165.1))
sh.power('+3V3', 33.02, 152.4); sh.power('GND', 33.02, 165.1)
put('C19', 142.24, 156.21, **V); put('C10', 152.4, 156.21, **V); put('C26', 162.56, 156.21, **V)
W((137.16, 152.4), (162.56, 152.4)); W(P('C19', 2), (142.24, 165.1), (162.56, 165.1)); W(P('C10', 2), (152.4, 165.1))
W(P('C26', 2), (162.56, 165.1))
sh.power('+1V1', 137.16, 152.4); sh.power('GND', 157.48, 165.1)
# flash + BOOTSEL
put('U2', 88.9, 254.0, ref_at=(-7.62, -15.24), val_at=(-7.62, 15.24), just=['left'])
stub_labels('U2', (1, 6, 5, 2, 3, 7), 73.66, 180)
put('C6', 92.71, 236.22, 90, **H)
W(P('U2', 8), (88.9, 233.68)); W(P('C6', 2), (99.06, 236.22), (99.06, 241.3)); sh.power('+3V3', 88.9, 233.68); sh.power('GND', 99.06, 241.3)
W(P('U2', 4), (88.9, 269.24)); sh.power('GND', 88.9, 269.24)
put('R3', 88.9, 288.29, 180, **V); put('R14', 99.06, 292.1, 90, **H); put('SW1', 116.84, 292.1, ref_at=(0, -5.08), val_at=(0, -7.62))
sh.label('QSPI_SS', 73.66, 292.1, 180); W((73.66, 292.1), P('R3', 1)); W(P('R3', 2), (88.9, 281.94)); sh.power('+3V3', 88.9, 281.94)
W(P('R3', 1), P('R14', 1)); W(P('R14', 2), P('SW1', 1)); sh.label('BOOT_SW', 104.14, 292.1)
W(P('SW1', 2), (124.46, 292.1), (124.46, 294.64)); sh.power('GND', 124.46, 294.64)
note(33.02, 320.04, 'BOOTSEL: hold SW1 while plugging USB in -> UF2 bootloader. R14 protects the QSPI_SS driver.',
     'Crystal: Abracon ABM8-272-T3 (CL 10 pF, ESR 50 ohm) with 15 pF loads + 1k, exactly the RP2040 guide 2.3 circuit.',
     'TESTEN tied to GND. RUN: 10k pull-up, SW6 RESET to GND, also on J2. BOOTSEL + tap RESET = UF2 mode.')
# GPIO stubs
stub_labels('U1', tuple(design.gpio_pin[g] for g in range(30)), 236.22, 0)
note(243.84, 320.04, 'GPIO: 0/1 UART0 -> TP1/TP2;  4/3/2 = keys A/B/C;', '5-9 red LEDs;  10 WS2812 data (via U6);  11/22/25 SAO GPIO1;',
     '12/13 SAO I2C0;  26-28 SAO GPIO2 (ADC0-2);  29 VBUS sense;', '14-21, 23/24 free on J2 (SPI1, UART1).')

# =============================================================================================
# Block F - UI
# =============================================================================================
sh.box(335.28, 127.0, 568.96, 242.57, 'USER INTERFACE  keys, credit LEDs, RGB shelf')
for i, (ref, y) in enumerate(zip(('SW2', 'SW3', 'SW4'), (147.32, 160.02, 172.72))):
    put(ref, 355.6, y, ref_at=(0, -5.08), val_at=(0, 3.81))
    sh.label(D[ref]['pins']['1'], 345.44, y, 180); W((345.44, y), P(ref, 1))
    W(P(ref, 2), (363.22, y), (363.22, y + 2.54)); sh.power('GND', 363.22, y + 2.54)
note(340.36, 189.23, 'Keys A/B/C: active low, internal pull-ups, debounce in firmware.',
     'Credit display: 5 red LEDs, 1k series -> ~1.5 mA each (dim by design).')
for i in range(5):
    y = 147.32 + 7.62 * i
    r, d = 'R%d' % (5 + i), 'D%d' % (i + 1)
    put(r, 388.62, y, 90, **H); put(d, 406.4, y, 180, **H)
    sh.label(D[r]['pins']['1'], 381.0, y, 180); W((381.0, y), P(r, 1))
    W(P(r, 2), P(d, 2)); sh.label(D[d]['pins']['2'], 393.7, y)
    W(P(d, 1), (414.02, y))
W((414.02, 147.32), (414.02, 180.34)); sh.power('GND', 414.02, 180.34)
# RGB chain
sh.power('VSYS', 434.34, 203.2); W((434.34, 203.2), (556.26, 203.2))
put('U6', 398.78, 215.9, ref_at=(5.08, -7.62), val_at=(5.08, 7.62), just=['left'])
W(P('U6', 2), (383.54, 215.9)); sh.label('RGB_CTRL', 383.54, 215.9, 180)
W(P('U6', 4), (424.18, 215.9)); sh.label('RGB_DIN', 414.02, 215.9)
sh.nc(P('U6', 1))
W(P('U6', 5), (398.78, 203.2)); sh.power('VSYS', 398.78, 203.2)
put('C29', 383.54, 207.01, **V); W((383.54, 203.2), (398.78, 203.2)); sh.power('GND', 383.54, 210.82)
W(P('U6', 3), (398.78, 226.06)); sh.power('GND', 398.78, 226.06)
leds = ['LED1', 'LED2', 'LED3', 'LED4']
chain = ['RGB_DIN', 'RGB_D2', 'RGB_D3', 'RGB_D4', 'RGB_DOUT']
for i, ref in enumerate(leds):
    lx = 439.42 + 22.86 * i
    put(ref, lx, 215.9, ref_at=(1.27, -10.16), val_at=(1.27, 11.43), just=['left'])
    W(P(ref, 4), (lx, 203.2)); W(P(ref, 2), (lx, 228.6))
    if i:
        sh.label(chain[i], lx - 15.24, 215.9)
    W((lx - 15.24, 215.9), P(ref, 3))
W(P('LED4', 1), (523.24, 215.9)); sh.label('RGB_DOUT', 523.24, 215.9)
W((439.42, 228.6), (513.08, 228.6)); sh.power('GND', 513.08, 228.6)
for i, c in enumerate(('C13', 'C14', 'C15', 'C16')):
    x = 533.4 + 7.62 * i
    put(c, x, 207.01, **V); W(P(c, 2), (x, 213.36))
W((533.4, 213.36), (556.26, 213.36)); sh.power('GND', 541.02, 213.36)
note(376.92, 236.22, 'WS2812B-2020-V6 x4 on VSYS, 100 nF each. GPIO10 -> U6 SN74LV1T34 (VCC = VSYS) -> DIN, so DIN swings to VSYS.',
     'LED VDD spec is 3.7-5.3 V: firmware dims/stops the LEDs on low battery (VSYS < ~3.7 V). Chain out to J2 pin 19.')

# =============================================================================================
# Block G - header, test points, holes, power flags
# =============================================================================================
sh.box(335.28, 245.11, 568.96, 342.9, 'HACK HEADER  J2 (DNP), test points, lanyard holes')
put('J2', 375.92, 284.48, ref_at=(0, -22.86), val_at=(0, -20.32))
odd = [1, 3, 5, 7, 9, 11, 13, 15, 17, 19, 21, 23, 25]
even = [2, 4, 6, 8, 10, 12, 14, 16, 18, 20, 22, 24, 26]
j2 = D['J2']['pins']
for pn in odd:
    p = P('J2', pn); net = j2[str(pn)]
    if net == '+3V3':
        W(p, (363.22, p[1]), (363.22, p[1] - 5.08)); sh.power('+3V3', 363.22, p[1] - 5.08)
    elif net == 'GND':
        W(p, (363.22, p[1])); sh.power('GND', 363.22, p[1], rot=270)
    else:
        W(p, (363.22, p[1])); sh.label(net, 363.22, p[1], 180)
for pn in even:
    p = P('J2', pn); net = j2[str(pn)]
    if net == 'GND':
        W(p, (391.16, p[1])); sh.power('GND', 391.16, p[1], rot=90)
    else:
        W(p, (391.16, p[1])); sh.label(net, 391.16, p[1], 0)
note(340.36, 313.69, '2x13, 2.54 mm, not fitted - players solder their own pins. 3V3 logic only, no 5 V on the header.',
     'Pin 1 = top-left square pad. GND on both end rows: a reversed ribbon shorts 3V3 to GND at worst (LDO limits).',
     '10 free GPIO + SAO I2C/GPIO2 + SPK_PWM + SWD + RUN + RGB out.   TP1-TP3: UART0 115200 8N1.   H1/H2: 4.0 mm lanyard holes.')
# test points
for ref, y in (('TP1', 271.78), ('TP2', 284.48), ('TP3', 297.18)):
    put(ref, 436.88, y, ref_at=(-2.54, -3.81), val_at=(2.54, -3.81), just=['left'])
W(P('TP1', 1), (436.88, 274.32), (444.5, 274.32)); sh.label('UART0_TX', 444.5, 274.32)
W(P('TP2', 1), (436.88, 287.02), (444.5, 287.02)); sh.label('UART0_RX', 444.5, 287.02)
W(P('TP3', 1), (436.88, 302.26)); sh.power('GND', 436.88, 302.26)
# lanyard holes
put('H1', 482.6, 274.32, ref_at=(0, -5.08), val_at=(0, 5.08)); put('H2', 482.6, 287.02, ref_at=(0, -5.08), val_at=(0, 5.08))
# power flags
for x, net in ((515.62, 'VBUS'), (530.86, 'VSYS'), (546.1, None)):
    if net:
        sh.power(net, x, 274.32); W((x, 274.32), (x, 279.4)); sh.flag(x, 279.4, rot=180)
    else:
        W((x, 274.32), (x, 279.4)); sh.flag(x, 274.32); sh.power('GND', x, 279.4)
W((561.34, 274.32), (561.34, 279.4)); sh.label('IRM_VCC', 561.34, 274.32); sh.flag(561.34, 279.4, rot=180)
# module rails and grounds: fed only through header pins / passives, so each needs a flag
for i, net in enumerate(('IRM_3V3', 'IRM_GND', 'AUM_GND', 'SPM_3V3', 'SPM_GND')):
    x = 505.46 + 12.7 * i
    W((x, 297.18), (x, 302.26)); sh.label(net, x, 297.18); sh.flag(x, 302.26, rot=180)
sh.text('PWR_FLAGs: nets fed only through passive pins', 505.46, 318.77, 1.5)
sh.text('(row 2: breakaway-module rails and grounds).', 505.46, 322.58, 1.5)

# =============================================================================================
# Block H - audio module (breakaway board; nets AUM_*)
# =============================================================================================
sh.box(17.78, 347.98, 203.2, 407.67, 'AUDIO MODULE  breakaway board, plugs into J6')
put('P2', 30.48, 378.46, mir='y', ref_at=(-1.27, -8.89), val_at=(-1.27, -6.35), just=['left'])
put('R17', 45.72, 381.0, 90, **H)
W(P('P2', 5), P('R17', 1)); sh.label('AUM_PWM', 38.1, 381.0, 270)
p = P('P2', 2); W(p, (20.32, p[1]), (20.32, 388.62)); sh.power('AUM_GND', 20.32, 388.62, lib='power:GND')
for pn in (1, 3, 4, 6):
    sh.nc(P('P2', pn))
W(P('R17', 2), (63.5, 381.0))
put('C21', 55.88, 384.81, **V); sh.power('AUM_GND', 55.88, 388.62, lib='power:GND')
sh.label('AUM_FILT', 52.07, 381.0)
put('C22', 67.31, 381.0, 90, ref_at=(0, -5.08), val_at=(0, -2.54))
put('J4', 99.06, 375.92, mir='y', ref_at=(0, -10.16), val_at=(0, 10.16))
W(P('C22', 2), P('J4', 'T')); sh.label('AUM_OUT', 72.39, 381.0)
W(P('J4', 'R1'), (83.82, 378.46), (83.82, 381.0))
W(P('J4', 'R2'), (88.9, 375.92), (88.9, 368.3)); W(P('J4', 'S'), (88.9, 373.38)); sh.power('AUM_GND', 88.9, 368.3, rot=180, lib='power:GND')
note(20.32, 397.51, 'GPIO11 PWM (>= 100 kHz carrier) -> 1k / 10n low-pass (fc ~ 16 kHz) -> 10 uF DC block -> tip + ring 1 (mono). Sleeve + ring 2 = GND.',
     'Level into 32 ohm ~ 0.1 Vpp. PJ-320D (C431535) SMD pads: 1 = S, 2 = R2, 3 = R1, 4 = T. Detect-switch pads unused.',
     'P2: SAO 2x3 header, 2 = GND, 5 = GPIO1 = PWM (3V3 unused); plugs into J6. Snap off; the jack then points sideways.')

# =============================================================================================
# Block I - speaker module (breakaway board; nets SPM_*; BOM-B2 add-on 7)
# =============================================================================================
sh.box(208.28, 347.98, 406.4, 407.67, 'SPEAKER MODULE  breakaway board, plugs into J7')
put('P3', 223.52, 378.46, mir='y', ref_at=(-1.27, -8.89), val_at=(-1.27, -6.35), just=['left'])
put('R20', 241.3, 381.0, 90, **H)
W(P('P3', 5), P('R20', 1)); sh.label('SPM_SIG', 231.14, 381.0, 270)
p = P('P3', 1); W(p, (233.68, p[1])); sh.label('SPM_3V3', 233.68, p[1])
p = P('P3', 2); W(p, (213.36, p[1]), (213.36, 388.62)); sh.power('SPM_GND', 213.36, 388.62, lib='power:GND')
for pn in (3, 4, 6):
    sh.nc(P('P3', pn))
put('Q2', 264.16, 381.0, ref_at=(5.08, -2.54), val_at=(5.08, 0), just=['left'])
W(P('R20', 2), P('Q2', 1)); sh.label('SPM_BASE', 247.65, 381.0)
put('R21', 251.46, 388.62, **V)
W(P('R21', 1), (251.46, 381.0)); W(P('R21', 2), (251.46, 393.7)); sh.power('SPM_GND', 251.46, 393.7, lib='power:GND')
W(P('Q2', 2), (266.7, 393.7)); sh.power('SPM_GND', 266.7, 393.7, lib='power:GND')
# 3V3 bus, transducer, flyback, bulk cap
sh.power('SPM_3V3', 231.14, 360.68); W((231.14, 360.68), (304.8, 360.68))
put('D7', 274.32, 365.76, ref_at=(0, -2.54), val_at=(0, 2.54))          # K left -> 3V3 bus, A right -> collector line
W(P('D7', 1), (270.51, 360.68)); W(P('D7', 2), (278.13, 373.38))
put('LS1', 284.48, 370.84, ref_at=(5.08, -2.54), val_at=(5.08, 0), just=['left'])
W(P('LS1', 1), (281.94, 360.68))
W(P('Q2', 3), (266.7, 373.38), P('LS1', 2)); sh.label('SPM_COL', 267.97, 373.38)
put('C25', 304.8, 364.49, **V); W(P('C25', 2), (304.8, 373.38)); sh.power('SPM_GND', 304.8, 373.38, lib='power:GND')
note(317.5, 362.0, 'MLT-8530 magnetic transducer: 2.7 kHz resonance, 16 ohm,', '<= 95 mA at 2.5-4.5 V, so it runs from the 3V3 LDO.',
     'S8050 low-side switch, 1k base; 10k keeps it off while the', 'GPIO floats at reset. 1N4148W flyback, 10 uF local bulk.',
     'Drive: 2.7 kHz square wave (50 % PWM) on GPIO25.', 'GPIO25 is also J2 pin 15 (shared).',
     'P3: SAO 2x3, 1 = 3V3, 2 = GND, 5 = GPIO1 = SIG (J7).', 'Footprint wires the two dummy pads crosswise,',
     'so a 180 deg placement only reverses the coil.', '(BOM-B2 add-on 7.)')

# =============================================================================================
sh.text('INTENT 2026 hardware badge - generated by 03-kicad/scripts/gen_sch.py from design.py (edit design.py, not this file).', 25.4, 22.86, 1.8)

if __name__ == '__main__':
    dang = sh.check()
    if dang:
        print('DANGLING wire ends:', sorted(dang)[:20])
    missing = [r for r in D if r not in sh.placed]
    if missing:
        raise SystemExit('parts not placed: %s' % missing)
    nw, nj = sh.write(OUT, 'INTENT 2026 Hardware Badge', '2026-10-17', '0.6', 'INTENT 2026 - by Palo Alto Networks',
                      ['RP2040 badge, 56x100 mm vending-machine outline + 3 breakaway SAO modules (IR, audio, speaker)',
                       'Generated by scripts/gen_sch.py - edit design.py, not this file'])
    print('wrote', os.path.abspath(OUT), len(sh.placed), 'symbols', nw, 'wires', nj, 'junctions')
