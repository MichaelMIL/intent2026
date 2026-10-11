"""Single source of truth for the INTENT 2026 badge netlist (rev 0.5).

rev 0.5 (2026-10-11): the IR receiver, the audio jack and a new speaker are **breakaway modules** on the same
PCB (under the pedestal, tab-routed with mouse bites). Each module has a 1x3 2.54 mm pin header (P1-P3) and
plugs into a matching socket on the main board (J5-J7). Module nets carry a module prefix (IRM_, AUM_, SPM_)
because no copper crosses the breakaway tabs; the sockets are the only link.
Port pinout (all three identical): 1 = GND (square pad), 2 = 3V3, 3 = signal. Power sits in the middle, so a
module plugged in backwards swaps GND and signal and never puts 3V3 on a GPIO.

Derived from 01-spec/design-spec.md §2–§3 with the corrections found while
building the KiCad project (see 03-kicad/BUILD-NOTES.md):
  * R11/R12 27 Ω = C25100 (C25105 is 33 Ω)
  * U5 IRM-H638T pinout: 1,2 = GND, 3 = OUT, 4 = VCC
  * J4 PJ-320D (C431535) pads: 1 = S, 2 = R2, 3 = R1, 4 = T
"""

GND = 'GND'

# footprints ---------------------------------------------------------------
FP_R = 'Resistor_SMD:R_0402_1005Metric'
FP_C = 'Capacitor_SMD:C_0402_1005Metric'
FP_C0805 = 'Capacitor_SMD:C_0805_2012Metric'
FP_LED = 'LED_SMD:LED_0603_1608Metric'

# LCSC numbers -------------------------------------------------------------
L_100N = 'C60474'
L_1U = 'C6119792'
L_10U = 'C7503495'
L_15P = 'C1548'
L_10N = 'C15195'
L_10K = 'C25744'
L_1K = 'C11702'
L_5K1 = 'C25905'
L_27R = 'C25100'
L_100R = 'C25076'
L_SOCKET3 = 'C541850'   # XFCN PM254V-11-03-H85, 1x3 2.54 mm socket, THT (JLC extended)
L_PINS3 = 'C49257'      # BOOMELE 2.54-1*3P, 1x3 2.54 mm pin header, THT (JLC extended)
FP_SOCKET3 = 'Connector_PinSocket_2.54mm:PinSocket_1x03_P2.54mm_Vertical'
FP_PINS3 = 'Connector_PinHeader_2.54mm:PinHeader_1x03_P2.54mm_Vertical'

parts = []


def part(ref, lib, value, fp, lcsc, pins, dnp=False, in_bom=True, desc='', side='F', module=''):
    """module: '' = main board, else the breakaway module the part sits on ('IR', 'AUDIO', 'SPK')."""
    parts.append(dict(ref=ref, lib=lib, value=value, fp=fp, lcsc=lcsc, pins=pins,
                      dnp=dnp, in_bom=in_bom, desc=desc, side=side, module=module))


def R(ref, val, lcsc, a, b, desc='', module=''):
    part(ref, 'Device:R', val, FP_R, lcsc, {'1': a, '2': b}, desc=desc, module=module)


def C(ref, val, lcsc, a, b, fp=FP_C, desc='', module=''):
    part(ref, 'Device:C', val, fp, lcsc, {'1': a, '2': b}, desc=desc, module=module)


# ---- MCU --------------------------------------------------------------------
gpio = {i: None for i in range(30)}
gpio.update({0: 'UART0_TX', 1: 'UART0_RX', 2: 'BTN_C', 3: 'BTN_B', 4: 'BTN_A',   # A=GPIO4 (layout order)
             5: 'LED_R1', 6: 'LED_R2', 7: 'LED_R3', 8: 'LED_R4', 9: 'LED_R5',
             10: 'RGB_DIN', 11: 'AUDIO_PWM', 22: 'IR_OUT', 25: 'SPK_PWM', 29: 'VBUS_SENSE'})
for i in list(range(12, 22)) + [23, 24, 26, 27, 28]:
    gpio[i] = 'GPIO%d' % i
gpio_pin = {0: 2, 1: 3, 2: 4, 3: 5, 4: 6, 5: 7, 6: 8, 7: 9, 8: 11, 9: 12, 10: 13, 11: 14, 12: 15, 13: 16,
            14: 17, 15: 18, 16: 27, 17: 28, 18: 29, 19: 30, 20: 31, 21: 32, 22: 34, 23: 35, 24: 36,
            25: 37, 26: 38, 27: 39, 28: 40, 29: 41}
u1 = {str(p): '+3V3' for p in (1, 10, 22, 33, 42, 49, 43, 44, 48)}
u1.update({'23': '+1V1', '50': '+1V1', '45': '+1V1', '57': GND, '19': GND,
           '20': 'XIN', '21': 'XOUT', '24': 'SWCLK', '25': 'SWDIO', '26': 'RUN',
           '46': 'USB_DM', '47': 'USB_DP', '51': 'QSPI_SD3', '52': 'QSPI_SCLK', '53': 'QSPI_SD0',
           '54': 'QSPI_SD2', '55': 'QSPI_SD1', '56': 'QSPI_SS'})
for g, p in gpio_pin.items():
    u1[str(p)] = gpio[g]
part('U1', 'MCU_RaspberryPi:RP2040', 'RP2040', 'Package_DFN_QFN:QFN-56-1EP_7x7mm_P0.4mm_EP3.2x3.2mm',
     'C2040', u1, desc='Dual Cortex-M0+ MCU')

part('U2', 'Memory_Flash:W25Q32JVSS', 'W25Q16JVSNIQ', 'Package_SO:SOIC-8_3.9x4.9mm_P1.27mm', 'C2456211',
     {'1': 'QSPI_SS', '2': 'QSPI_SD1', '3': 'QSPI_SD2', '4': GND, '5': 'QSPI_SD0', '6': 'QSPI_SCLK',
      '7': 'QSPI_SD3', '8': '+3V3'}, desc='16 Mbit QSPI flash')

part('Y1', 'Device:Crystal_GND24', '12MHz', 'Crystal:Crystal_SMD_3225-4Pin_3.2x2.5mm', 'C133334',
     {'1': 'XIN', '2': GND, '3': 'XOUT_R', '4': GND})
C('C11', '15pF', L_15P, 'XIN', GND)
C('C12', '15pF', L_15P, 'XOUT_R', GND)
R('R13', '1k', L_1K, 'XOUT', 'XOUT_R')

# decoupling
for ref in ('C1', 'C2', 'C3', 'C4', 'C5', 'C17'):
    C(ref, '100nF', L_100N, '+3V3', GND, desc='IOVDD')
C('C6', '100nF', L_100N, '+3V3', GND, desc='flash VCC')
C('C7', '100nF', L_100N, '+3V3', GND, desc='USB_VDD')
C('C8', '100nF', L_100N, '+3V3', GND, desc='ADC_AVDD')
C('C18', '100nF', L_100N, '+3V3', GND, desc='VREG_VIN')
C('C19', '100nF', L_100N, '+1V1', GND, desc='DVDD pin 23')
C('C10', '1uF', L_1U, '+1V1', GND, desc='VREG_VOUT / DVDD pin 50')

R('R3', '10k', L_10K, 'QSPI_SS', '+3V3')
R('R4', '10k', L_10K, 'RUN', '+3V3')
R('R14', '1k', L_1K, 'QSPI_SS', 'BOOT_SW')
part('SW1', 'Switch:SW_Push', 'BOOTSEL', 'Button_Switch_SMD:SW_Push_1P1T_XKB_TS-1187A', 'C318884',
     {'1': 'BOOT_SW', '2': GND})

# ---- USB --------------------------------------------------------------------
part('J1', 'Connector:USB_C_Receptacle_USB2.0_16P', 'TYPE-C-16PIN', 'intent:USB_C_TYPE-C16PIN_C393939', 'C393939',
     {'A1': GND, 'A12': GND, 'B1': GND, 'B12': GND, 'S1': GND,
      'A4': 'VBUS', 'A9': 'VBUS', 'B4': 'VBUS', 'B9': 'VBUS',
      'A5': 'CC1', 'B5': 'CC2', 'A6': 'USB_DP_CONN', 'B6': 'USB_DP_CONN', 'A7': 'USB_DM_CONN',
      'B7': 'USB_DM_CONN', 'A8': None, 'B8': None})
R('R1', '5.1k', L_5K1, 'CC1', GND)
R('R2', '5.1k', L_5K1, 'CC2', GND)
part('U4', 'Power_Protection:USBLC6-2SC6', 'USBLC6-2SC6', 'Package_TO_SOT_SMD:SOT-23-6', 'C2827654',
     {'1': 'USB_DP_CONN', '6': 'USB_DP_CONN', '3': 'USB_DM_CONN', '4': 'USB_DM_CONN', '2': GND, '5': 'VBUS'})
R('R11', '27', L_27R, 'USB_DP_CONN', 'USB_DP')
R('R12', '27', L_27R, 'USB_DM_CONN', 'USB_DM')

# ---- power path -------------------------------------------------------------
part('D6', 'Device:D_Schottky', 'B5819W', 'Diode_SMD:D_SOD-123', 'C7420330', {'1': 'VSYS', '2': 'VBUS'})
part('Q1', 'Transistor_FET:AO3401A', 'HL3401', 'Package_TO_SOT_SMD:SOT-23', 'C22469449',
     {'1': 'VBUS', '2': 'VSYS', '3': 'BAT_SW'})
R('R10', '10k', L_10K, 'VBUS', GND)
R('R15', '10k', L_10K, 'VBUS', 'VBUS_SENSE')
R('R16', '10k', L_10K, 'VBUS_SENSE', GND)
part('J3', 'Connector_Generic:Conn_01x02', 'BATT 3xAAA', 'intent:JST_PH_2P_SMD_Vertical_C722761', 'C722761',
     {'1': 'BAT_IN', '2': GND}, desc='Battery box plug, pin1 = +')
part('SW5', 'Switch:SW_SPDT', 'MSK12C02', 'Button_Switch_SMD:SW_SPDT_Shouhan_MSK12C02', 'C431540',
     {'1': 'BAT_SW', '2': 'BAT_IN', '3': None}, dnp=True, in_bom=False, side='B',
     desc='Optional on-board power switch (DNP, cut JP1 if fitted)')
part('JP1', 'Jumper:SolderJumper_2_Bridged', 'SW5 bypass', 'Jumper:SolderJumper-2_P1.3mm_Bridged_Pad1.0x1.5mm', '',
     {'1': 'BAT_IN', '2': 'BAT_SW'}, in_bom=False, side='B')
C('C9', '10uF', L_10U, 'VSYS', GND, fp=FP_C0805, desc='LDO input')
part('U3', 'Regulator_Linear:XC6206PxxxMR', 'ME6206A33M3G', 'Package_TO_SOT_SMD:SOT-23-3', 'C35259',
     {'1': GND, '2': '+3V3', '3': 'VSYS'})
C('C20', '1uF', L_1U, '+3V3', GND, desc='LDO output')

# ---- UI -----------------------------------------------------------------------
for i, ref in enumerate(('SW2', 'SW3', 'SW4')):
    part(ref, 'Switch:SW_Push', 'ABC'[i], 'Button_Switch_SMD:SW_Push_1P1T_XKB_TS-1187A', 'C318884',
         {'1': 'BTN_' + 'ABC'[i], '2': GND})
for i in range(5):
    R('R%d' % (5 + i), '1k', L_1K, 'LED_R%d' % (i + 1), 'LED_A%d' % (i + 1))
    part('D%d' % (i + 1), 'Device:LED', 'Red', FP_LED, 'C2286', {'1': GND, '2': 'LED_A%d' % (i + 1)})

rgb_chain = ['RGB_DIN', 'RGB_D2', 'RGB_D3', 'RGB_D4', 'RGB_DOUT']
for i in range(4):
    part('LED%d' % (i + 1), 'LED:WS2812B-2020', 'WS2812B-2020-V6', 'LED_SMD:LED_WS2812B-2020_PLCC4_2.0x2.0mm',
         'C52917434', {'3': rgb_chain[i], '1': rgb_chain[i + 1], '4': 'VSYS', '2': GND})
    C('C%d' % (13 + i), '100nF', L_100N, 'VSYS', GND, desc='LED%d VDD' % (i + 1))

# ---- expansion ports (main board) ---------------------------------------------
# 1x3 sockets in the coin area. 1 = GND, 2 = 3V3, 3 = signal. The module side is P1-P3 below.
for ref, name, sig in (('J5', 'IR', 'IR_OUT'), ('J6', 'AUDIO', 'AUDIO_PWM'), ('J7', 'SPK', 'SPK_PWM')):
    part(ref, 'Connector:Conn_01x03_Socket', name, FP_SOCKET3, L_SOCKET3, {'1': GND, '2': '+3V3', '3': sig},
         desc='Expansion port %s: 1 = GND, 2 = 3V3, 3 = %s' % (name, sig))

# ---- IR module (breakaway, nets IRM_*) ------------------------------------------
M = 'IR'
part('P1', 'Connector:Conn_01x03_Pin', 'IR MODULE', FP_PINS3, L_PINS3, {'1': 'IRM_GND', '2': 'IRM_3V3', '3': 'IRM_OUT'},
     desc='Module pins, mate with J5', module=M)
part('U5', 'Interface_Optical:IRM-H6xxT', 'IRM-H638T/TR2', 'intent:IRM-H638T_C91447', 'C91447',
     {'1': 'IRM_GND', '2': 'IRM_GND', '3': 'IRM_OUT', '4': 'IRM_VCC'}, module=M)
R('R19', '100', L_100R, 'IRM_3V3', 'IRM_VCC', module=M)
C('C23', '100nF', L_100N, 'IRM_VCC', 'IRM_GND', module=M)
C('C24', '10uF', L_10U, 'IRM_VCC', 'IRM_GND', fp=FP_C0805, module=M)

# ---- audio module (breakaway, nets AUM_*) ---------------------------------------
M = 'AUDIO'
part('P2', 'Connector:Conn_01x03_Pin', 'AUDIO MODULE', FP_PINS3, L_PINS3, {'1': 'AUM_GND', '2': None, '3': 'AUM_PWM'},
     desc='Module pins, mate with J6 (3V3 pin unused)', module=M)
R('R17', '1k', L_1K, 'AUM_PWM', 'AUM_FILT', module=M)
C('C21', '10nF', L_10N, 'AUM_FILT', 'AUM_GND', module=M)
C('C22', '10uF', L_10U, 'AUM_FILT', 'AUM_OUT', fp=FP_C0805, desc='DC block', module=M)
part('J4', 'Connector_Audio:AudioJack4', 'PJ-320D', 'intent:Jack_3.5mm_PJ-320D_SMD_C431535', 'C431535',
     {'T': 'AUM_OUT', 'R1': 'AUM_OUT', 'R2': 'AUM_GND', 'S': 'AUM_GND'}, module=M)

# ---- speaker module (breakaway, nets SPM_*) — BOM-B2 add-on 7 ---------------------
M = 'SPK'
part('P3', 'Connector:Conn_01x03_Pin', 'SPK MODULE', FP_PINS3, L_PINS3, {'1': 'SPM_GND', '2': 'SPM_3V3', '3': 'SPM_SIG'},
     desc='Module pins, mate with J7', module=M)
R('R20', '1k', L_1K, 'SPM_SIG', 'SPM_BASE', desc='base resistor', module=M)
R('R21', '10k', L_10K, 'SPM_BASE', 'SPM_GND', desc='keeps Q2 off while the GPIO floats', module=M)
part('Q2', 'Transistor_BJT:Q_NPN_BEC', 'S8050', 'Package_TO_SOT_SMD:SOT-23', 'C2146',
     {'1': 'SPM_BASE', '2': 'SPM_GND', '3': 'SPM_COL'}, desc='NPN low-side driver', module=M)
part('LS1', 'Device:Buzzer', 'MLT-8530', 'intent:Buzzer_MLT-8530_C94599', 'C94599',
     {'1': 'SPM_3V3', '2': 'SPM_COL'}, desc='Magnetic transducer 2.7 kHz, 16 ohm, 95 mA max', module=M)
part('D7', 'Diode:1N4148W', '1N4148W', 'Diode_SMD:D_SOD-123', 'C81598',
     {'1': 'SPM_3V3', '2': 'SPM_COL'}, desc='flyback', module=M)
C('C25', '10uF', L_10U, 'SPM_3V3', 'SPM_GND', fp=FP_C0805, desc='module bulk', module=M)

# ---- header / test --------------------------------------------------------------
j2 = {1: '+3V3', 2: GND, 3: 'GPIO12', 4: 'GPIO13', 5: 'GPIO14', 6: 'GPIO15', 7: 'GPIO16', 8: 'GPIO17',
      9: 'GPIO18', 10: 'GPIO19', 11: 'GPIO20', 12: 'GPIO21', 13: 'GPIO23', 14: 'GPIO24', 15: 'SPK_PWM',
      16: 'GPIO26', 17: 'GPIO27', 18: 'GPIO28', 19: 'RGB_DOUT', 20: GND, 21: 'SWCLK', 22: 'SWDIO',
      23: 'RUN', 24: GND, 25: GND, 26: GND}
part('J2', 'Connector_Generic:Conn_02x13_Odd_Even', 'HACK HEADER', 'Connector_PinHeader_2.54mm:PinHeader_2x13_P2.54mm_Vertical',
     '', {str(k): v for k, v in j2.items()}, dnp=True, in_bom=False, desc='2x13 expansion / SWD, DNP')
part('TP1', 'Connector:TestPoint', 'TX', 'TestPoint:TestPoint_THTPad_D1.5mm_Drill0.7mm', '', {'1': 'UART0_TX'}, in_bom=False)
part('TP2', 'Connector:TestPoint', 'RX', 'TestPoint:TestPoint_THTPad_D1.5mm_Drill0.7mm', '', {'1': 'UART0_RX'}, in_bom=False)
part('TP3', 'Connector:TestPoint', 'GND', 'TestPoint:TestPoint_THTPad_D1.5mm_Drill0.7mm', '', {'1': GND}, in_bom=False)
part('H1', 'Mechanical:MountingHole', 'Lanyard', 'intent:LanyardHole_4.0mm_Plated', '', {}, in_bom=False)
part('H2', 'Mechanical:MountingHole', 'Lanyard', 'intent:LanyardHole_4.0mm_Plated', '', {}, in_bom=False)

PWR_FLAGS = ['GND', 'VBUS', 'VSYS', 'IRM_VCC', 'IRM_3V3', 'IRM_GND', 'AUM_GND', 'SPM_3V3', 'SPM_GND']

# breakaway modules: name -> ground net (zones) and the socket it mates with
MODULES = {'IR': dict(gnd='IRM_GND', socket='J5', pins='P1'),
           'AUDIO': dict(gnd='AUM_GND', socket='J6', pins='P2'),
           'SPK': dict(gnd='SPM_GND', socket='J7', pins='P3')}

if __name__ == '__main__':
    from collections import defaultdict
    nets = defaultdict(list)
    for p in parts:
        for pin, n in p['pins'].items():
            if n:
                nets[n].append(p['ref'] + '.' + pin)
    for n in sorted(nets):
        print('%-14s %3d  %s' % (n, len(nets[n]), ' '.join(nets[n][:12])))
    print(len(parts), 'parts', len(nets), 'nets')
