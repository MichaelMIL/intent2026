#!/bin/bash
# Full re-route in the intent-router container (rev 0.6 settings: run "j" of 2026-10-18).
# usage: W=<build dir> bash scripts/win/route.win.sh [HIST_INC] [CORR_R]
source "$(dirname "${BASH_SOURCE[0]}")/env.win.sh"
MSYS_NO_PATHCONV=1 podman run --rm -v "$(cygpath -w $W):/w" -w /w -e ROUTE_ITERS=80 \
  -e FIXED_ROUTES=/w/scripts/router/fixed_routes.json -e GND_SKIP=U1.19 -e GND_LAST=1 \
  -e GND_SUBSET=U2.4,Y1.4,C17.2,R10.2,C8.2,C7.2,C5.2,C4.2,C19.2,C18.2,C26.2,C10.2,C1.2,C2.2,C6.2,C12.2,C11.2 \
  -e CORR_R=${2:-7} -e HIST_INC=${1:-30} -e PRES_CAP=150000 -e ROUTE_STATE=/w/route_state.pkl \
  intent-router python scripts/router/route2.py /w/geo.json /w/routes.json
