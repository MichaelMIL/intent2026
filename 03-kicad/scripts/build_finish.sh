#!/bin/bash
# sandbox helper: routes.json -> finished board (pours, silk, GND repair, island stitching) + DRC
set -e
W=${W:-/tmp/work}; KCLI=${KCLI:-/tmp/kcli}; KPY=${KPY:-/tmp/kpy}
cd $W
rm -f stitch_extra.json
python3 scripts/gen_pro.py >/dev/null
for pass in 1 2; do
  $KPY scripts/pcb_finish.py $W routes.json logo.json | tail -1
  $KPY scripts/zone_export.py intent-2026-badge.kicad_pcb zones.json
  REPAIR_W=$([ $pass = 1 ] && echo 0.2 || echo 0.15) python3 scripts/router/gnd_repair.py geo.json routes.json zones.json | tail -1
done
for pass in 1 2; do
  $KPY scripts/pcb_finish.py $W routes.json logo.json | tail -1
  $KPY scripts/zone_export.py intent-2026-badge.kicad_pcb zones.json
  python3 scripts/island_stitch.py zones.json stitch_extra.json | tail -1
done
$KPY scripts/pcb_finish.py $W routes.json logo.json | tail -1
python3 scripts/gen_pro.py >/dev/null
$KCLI pcb drc --schematic-parity --severity-all -o drc.rpt intent-2026-badge.kicad_pcb >/dev/null
grep "^\[" drc.rpt | sed 's/:.*//' | sort | uniq -c | sort -rn
grep "^\*\*" drc.rpt | sed -n 4,6p
