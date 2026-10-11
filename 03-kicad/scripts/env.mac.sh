# Source this before running the build chain on this Mac (KiCad 10.0.3 app bundle).
#   source scripts/env.mac.sh
# W   = working dir the build_*.sh scripts cd into (the 03-kicad folder itself)
# KPY = KiCad's bundled Python (has pcbnew; used by pcb_build/pcb_finish/zone_export/fab_export/silk)
# PY  = plain Python with numpy/scipy/shapely/svgelements/pillow (router, island_stitch, art_logo, gen_*)
KAPP=/Applications/KiCad/KiCad.app/Contents
export W="$(cd "$(dirname "${BASH_SOURCE[0]:-$0}")/.." && pwd)"
export KCLI="$KAPP/MacOS/kicad-cli"
export KPY="$KAPP/Frameworks/Python.framework/Versions/Current/bin/python3"
export PY=/Users/michael/miniconda3/bin/python3
export KICAD9_FOOTPRINT_DIR="$KAPP/SharedSupport/footprints"
export KICAD9_SYMBOL_DIR="$KAPP/SharedSupport/symbols"
