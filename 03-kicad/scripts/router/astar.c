/* Two-layer grid A* with 8-way moves, turn penalties and vias.
 * Build: gcc -O2 -shared -fPIC -o libastar.so astar.c
 * State = ((layer * ny + j) * nx + i) * 8 + dir   (dir 0..7, the direction of arrival)
 */
#include <stdlib.h>
#include <string.h>
#include <stdint.h>

typedef struct { int32_t f; int32_t s; } node;
static node *heap; static int hn, hcap;
static void hpush(int32_t f, int32_t s) {
    if (hn >= hcap) { hcap = hcap ? hcap * 2 : 1 << 16; heap = realloc(heap, hcap * sizeof(node)); }
    int k = hn++;
    while (k > 0) { int p = (k - 1) >> 1; if (heap[p].f <= f) break; heap[k] = heap[p]; k = p; }
    heap[k].f = f; heap[k].s = s;
}
static node hpop(void) {
    node top = heap[0], last = heap[--hn];
    int k = 0;
    for (;;) { int c = 2 * k + 1; if (c >= hn) break; if (c + 1 < hn && heap[c + 1].f < heap[c].f) c++;
        if (heap[c].f >= last.f) break; heap[k] = heap[c]; k = c; }
    heap[k] = last; return top;
}

static const int DX[8] = {1, 1, 0, -1, -1, -1, 0, 1};
static const int DY[8] = {0, 1, 1, 1, 0, -1, -1, -1};
static const int DC[8] = {10, 14, 10, 14, 10, 14, 10, 14};

/* free0/free1: per-layer traversable masks; viaok: via allowed; tgt0/tgt1: target masks;
 * src: list of source cells (layer*nx*ny + j*nx + i), nsrc;
 * layer_cost[2] in percent (100 = normal); via_cost; turn45, turn90 penalties;
 * bbox of targets (ti0,tj0,ti1,tj1) for the heuristic; maxexp limit.
 * out: path as cell indices (layer*nx*ny + j*nx + i), returns length or -1. */
int astar(int nx, int ny, const uint8_t *free0, const uint8_t *free1, const uint8_t *viaok,
          const int32_t *pen0, const int32_t *pen1, const int32_t *vpen,
          const uint8_t *tgt0, const uint8_t *tgt1, const int32_t *src, int nsrc,
          const int32_t *layer_cost, int via_cost, int turn45, int turn90,
          int ti0, int tj0, int ti1, int tj1, int maxexp, int32_t *out, int outmax)
{
    long ncell = (long)nx * ny;
    long nstate = ncell * 2 * 8;
    int32_t *g = malloc(nstate * sizeof(int32_t));
    int32_t *par = malloc(nstate * sizeof(int32_t));
    if (!g || !par) return -2;
    for (long k = 0; k < nstate; k++) g[k] = 0x7fffffff;
    hn = 0;
    const uint8_t *fr[2] = {free0, free1};
    const uint8_t *tg[2] = {tgt0, tgt1};
    const int32_t *pn[2] = {pen0, pen1};
#define H(i, j) ({ int ddx = (i) < ti0 ? ti0 - (i) : ((i) > ti1 ? (i) - ti1 : 0); \
                   int ddy = (j) < tj0 ? tj0 - (j) : ((j) > tj1 ? (j) - tj1 : 0); \
                   int mn = ddx < ddy ? ddx : ddy, mx = ddx < ddy ? ddy : ddx; 10 * (mx - mn) + 14 * mn; })
    for (int k = 0; k < nsrc; k++) {
        int c = src[k]; int L = c / ncell; int cell = c % ncell; int i = cell % nx, j = cell / nx;
        if (!fr[L][cell]) continue;
        for (int d = 0; d < 8; d++) { long s = ((long)L * ncell + cell) * 8 + d; g[s] = 0; par[s] = -1; }
        long s = ((long)L * ncell + cell) * 8;
        hpush(H(i, j), (int32_t)s);
    }
    int found = -1; int exp = 0;
    while (hn > 0) {
        node nd = hpop();
        long s = nd.s; int d = s % 8; long sc = s / 8; int L = sc / ncell; int cell = sc % ncell;
        int i = cell % nx, j = cell / nx;
        int gs = g[s];
        if (nd.f - H(i, j) > gs) continue;
        if (tg[L][cell] && gs >= 0) { found = (int)s; break; }
        if (++exp > maxexp) break;
        /* planar moves */
        for (int nd2 = 0; nd2 < 8; nd2++) {
            int ni = i + DX[nd2], nj = j + DY[nd2];
            if (ni < 0 || nj < 0 || ni >= nx || nj >= ny) continue;
            int nc = nj * nx + ni;
            if (!fr[L][nc]) continue;
            if (nd2 & 1) { /* diagonal: both orthogonal neighbours must be free (no corner cutting) */
                if (!fr[L][j * nx + ni] || !fr[L][nj * nx + i]) continue;
            }
            int dd = (nd2 - d + 8) % 8; if (dd > 4) dd = 8 - dd;
            int tp = 0;
            if (par[s] != -1 || gs > 0) { if (dd == 1) tp = turn45; else if (dd == 2) tp = turn90; else if (dd >= 3) continue; }
            int cost = DC[nd2] * layer_cost[L] / 100 + tp + pn[L][nc];
            long ns = ((long)L * ncell + nc) * 8 + nd2;
            if (gs + cost < g[ns]) { g[ns] = gs + cost; par[ns] = (int32_t)s; hpush(g[ns] + H(ni, nj), (int32_t)ns); }
        }
        /* via */
        if (viaok[cell]) {
            int L2 = 1 - L;
            if (fr[L2][cell]) {
                long ns = ((long)L2 * ncell + cell) * 8 + d;
                int vc = via_cost + vpen[cell];
                if (gs + vc < g[ns]) { g[ns] = gs + vc; par[ns] = (int32_t)s; hpush(g[ns] + H(i, j), (int32_t)ns); }
            }
        }
    }
    int n = -1;
    if (found >= 0) {
        n = 0; long s = found;
        while (s != -1 && n < outmax) { long sc = s / 8; out[n++] = (int32_t)sc; s = par[s]; }
    }
    free(g); free(par);
    return n;
}
