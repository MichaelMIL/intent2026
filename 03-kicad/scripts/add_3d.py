"""(KiCad python) Attach the gen_3d.py models to an existing finished board without regenerating it.
usage: add_3d.py <board.kicad_pcb>   (custom intent.pretty footprints + the FALLBACK_3D stock footprints)"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pcbnew
from pcb_build import FALLBACK_3D

CUSTOM = ('USB_C_TYPE-C16PIN_C393939', 'Jack_3.5mm_PJ-320D_SMD_C431535', 'IRM-H638T_C91447',
          'JST_PH_2P_SMD_Vertical_C722761', 'Buzzer_MLT-8530_C94599')
b = pcbnew.LoadBoard(sys.argv[1])
n = 0
for fp in b.GetFootprints():
    name = fp.GetFPID().GetLibItemName().wx_str()
    if name in CUSTOM or name in FALLBACK_3D:
        fp.Models().clear()
        m = pcbnew.FP_3DMODEL()
        m.m_Filename = '${KIPRJMOD}/intent.3dshapes/%s.wrl' % name
        fp.Models().push_back(m)
        n += 1
pcbnew.SaveBoard(sys.argv[1], b)
print('models attached to', n, 'footprints')
