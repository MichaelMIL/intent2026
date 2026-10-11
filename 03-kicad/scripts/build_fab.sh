#!/bin/bash
# Stage D: fab outputs from the finished board in $W -> $OUT (default ../04-fab next to $W).
#   BOM/CPL (JLC format, rotation-corrected), Gerbers + drills (JLC naming, same options as the 2026-10-09 set),
#   schematic PDF, ERC/DRC reports, schematic preview PNG.
set -e
W=${W:-/tmp/work}; KCLI=${KCLI:-/tmp/kcli}; KPY=${KPY:-/tmp/kpy}
OUT=${OUT:-$W/../04-fab}
mkdir -p "$OUT"
cd "$W"
$KPY scripts/fab_export.py intent-2026-badge.kicad_pcb "$OUT" | head -1
G=$(mktemp -d)
$KCLI pcb export gerbers --layers F.Cu,B.Cu,F.Paste,B.Paste,F.SilkS,B.SilkS,F.Mask,B.Mask,Edge.Cuts \
      --subtract-soldermask -o "$G" intent-2026-badge.kicad_pcb >/dev/null
$KCLI pcb export drill --format excellon --excellon-separate-th --excellon-units mm --excellon-zeros-format decimal \
      --drill-origin absolute --excellon-oval-format alternate -o "$G/" intent-2026-badge.kicad_pcb >/dev/null
rm -f "$G"/*.gbrjob
(cd "$G" && rm -f "$OUT/gerbers.zip" && zip -q "$OUT/gerbers.zip" *)
echo "gerbers: $(unzip -l "$OUT/gerbers.zip" | tail -1)"
$KCLI sch export pdf -o "$OUT/intent-2026-badge-schematic.pdf" intent-2026-badge.kicad_sch >/dev/null
$KCLI sch erc --severity-all -o "$OUT/erc-report.txt" intent-2026-badge.kicad_sch >/dev/null || true
$KCLI pcb drc --schematic-parity --severity-all -o "$OUT/drc-report.txt" intent-2026-badge.kicad_pcb >/dev/null || true
grep "^\*\*" "$OUT/drc-report.txt" | sed -n 4,6p
python3 scripts/render_sch.py "$OUT/schematic-preview.png" 40 >/dev/null
echo "fab outputs -> $OUT"
