#!/bin/bash
# sandbox helper: regenerate schematic, netlist, footprints and the unrouted board in $W
set -e
W=${W:-/tmp/work}; KCLI=${KCLI:-/tmp/kcli}; KPY=${KPY:-/tmp/kpy}
cd $W
python3 scripts/gen_3d.py >/dev/null
python3 scripts/gen_fp.py >/dev/null
python3 scripts/gen_pro.py >/dev/null
python3 scripts/gen_sch.py >/dev/null
python3 scripts/check_sch.py --erc | tail -2   # netlist == design.py, ERC clean
$KCLI sch erc -o erc.rpt intent-2026-badge.kicad_sch >/dev/null; tail -1 erc.rpt
$KCLI sch export netlist -o net.net intent-2026-badge.kicad_sch >/dev/null
rm -f intent-2026-badge.kicad_pcb
$KPY scripts/pcb_build.py $W $W/net.net $W/geo.json | tail -1
cp intent-2026-badge.kicad_pcb stage_a.kicad_pcb
rm -f stitch_extra.json
