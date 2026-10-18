# Git Bash on Windows (KiCad 10 at C:\Program Files\KiCad\10.0). Source before the build steps.
#   W   = scratch copy of 03-kicad to build in (default: the 03-kicad folder itself; prefer a copy while KiCad is open)
#   KPY = KiCad's bundled Python (pcbnew); plain-Python steps that need scipy/shapely/gcc run in the
#         intent-router container (podman build -t intent-router -f scripts/win/Containerfile scripts/win)
export W="${W:-$(cd "$(dirname "${BASH_SOURCE[0]:-$0}")/../.." && pwd)}"
export KCLI="/c/Program Files/KiCad/10.0/bin/kicad-cli.exe"
export KPY="/c/Program Files/KiCad/10.0/bin/python.exe"
export KICAD9_FOOTPRINT_DIR="C:/Program Files/KiCad/10.0/share/kicad/footprints"
export KICAD9_SYMBOL_DIR="C:/Program Files/KiCad/10.0/share/kicad/symbols"
export PYTHONIOENCODING=utf-8
