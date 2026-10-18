#!/bin/bash
# Windows port of scripts/build_finish.sh: KiCad steps on the host, shapely steps in the intent-router container.
set -e
source "$(dirname "${BASH_SOURCE[0]}")/env.win.sh"
cd $W
WW="$(cygpath -w $W)"
CPY() { MSYS_NO_PATHCONV=1 podman run --rm -v "$WW:/w" -w /w "$@"; }
kfinish() { "$KPY" scripts/pcb_finish.py "$WW" "$WW\\routes.json" "$WW\\build\\logo.json" | tail -1; }
kzones() { "$KPY" scripts/zone_export.py intent-2026-badge.kicad_pcb zones.json; }
[ -f stage_a.kicad_pcb ] || { echo "no stage_a"; exit 1; }
rm -f stitch_extra.json
python scripts/gen_pro.py >/dev/null
for pass in 1 2; do
  kfinish; kzones
  RW=$([ $pass = 1 ] && echo 0.2 || echo 0.15)
  CPY -e REPAIR_W=$RW intent-router python scripts/router/gnd_repair.py geo.json routes.json zones.json | tail -1
done
for pass in 1 2; do
  kfinish; kzones
  CPY intent-router python scripts/island_stitch.py zones.json stitch_extra.json | tail -1
done
kfinish
python scripts/gen_pro.py >/dev/null
"$KCLI" pcb drc --schematic-parity --severity-all -o drc.rpt intent-2026-badge.kicad_pcb >/dev/null
grep "^\[" drc.rpt | sed 's/:.*//' | sort | uniq -c | sort -rn
grep "^\*\*" drc.rpt | sed -n 4,6p
