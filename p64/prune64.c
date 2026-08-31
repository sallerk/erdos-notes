/* PRUNE / PREPRUNE hooks for nauty's geng, for Erdos #64.
 *
 * Reject any (intermediate or final) graph containing a cycle of length 4, 8 or 16.
 * Sound for geng's incremental construction: geng only ever adds vertices and edges,
 * so a forbidden cycle present at an intermediate stage is present in every
 * descendant.  This is the same monotonicity the original search relied on, but here
 * it sits on top of geng's isomorph-free generation, so each graph is built once
 * instead of many times.
 *
 * PREPRUNE gets the cheap C4 test (two vertices with two common neighbours), which
 * kills the overwhelming majority.  PRUNE gets the C8 and C16 searches.
 *
 * Build (from the nauty directory):
 *   gcc -o geng64.exe -O3 -march=native -DMAXN=WORDSIZE -DWORDSIZE=64 \
 *       -DPRUNE=prune64 -DPREPRUNE=preprune64 geng.c prune64.c \
 *       gtoolsW.o nautyW1.o nautilW1.o naugraphW1.o schreierW.o naurng.o
 */
#include "gtools.h"

/* cheap: any two vertices with >= 2 common neighbours give a C4 */
int preprune64(graph *g, int n, int maxn)
{
    for (int i = 0; i < n; i++) {
        setword gi = g[i];
        for (int j = i + 1; j < n; j++) {
            setword common = gi & g[j];
            if (POPCOUNT(common) >= 2) return 1;   /* C4 present, reject */
        }
    }
    return 0;
}

/* depth-first search for a simple cycle of length exactly L through the
 * lowest-indexed vertex of the cycle, so each cycle is considered once */
static int seek(graph *g, int n, int start, int cur, setword used, int len, int L)
{
    if (len == L) return (g[cur] & bit[start]) != 0;
    setword cand = g[cur] & ~used;
    /* only vertices above start */
    for (int w = start + 1; w < n; w++) {
        if (!(cand & bit[w])) continue;
        if (seek(g, n, start, w, used | bit[w], len + 1, L)) return 1;
    }
    return 0;
}

static int has_cycle(graph *g, int n, int L)
{
    if (n < L) return 0;
    for (int s = 0; s + L <= n + 0; s++)
        if (seek(g, n, s, s, bit[s], 1, L)) return 1;
    return 0;
}

int prune64(graph *g, int n, int maxn)
{
    if (preprune64(g, n, maxn)) return 1;
    if (has_cycle(g, n, 8)) return 1;
    if (n >= 16 && has_cycle(g, n, 16)) return 1;
    return 0;
}
