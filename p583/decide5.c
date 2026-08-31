/* Erdos #583: FASTER exhaustive decider.
 *
 * Decides, per graph, whether E(G) partitions into at most k = ceil(n/2) simple paths.
 *
 * Four changes over decide.c, in rough order of how much they matter:
 *
 * 1. LONGEST PATHS FIRST.  decide.c offered "stop the path here" before "extend it",
 *    so it explored short paths first.  We are trying to cover m edges with few paths,
 *    so short paths are nearly always wrong.  Extending first flips the whole search
 *    order.
 *
 * 2. CAPACITY BOUND.  A simple path on n vertices has at most n-1 edges, so budget
 *    paths cover at most budget*(n-1) edges.  If m exceeds that, fail immediately.
 *
 * 3. LENGTH FLOOR ON THE CURRENT PATH.  Once this path is closed, the remaining m-L
 *    edges must fit in budget-1 paths, so L >= m - (budget-1)*(n-1).  Paths shorter
 *    than that floor are never even offered as candidates.
 *
 * 4. FAILURE MEMOISATION.  Different peel orders reach the same remaining edge set.
 *    A Zobrist fingerprint of (edge set, budget) is stored for states already proved
 *    undecomposable; caching failures only is sound and never changes an answer.
 *
 * The two bounds from decide.c are kept: components carrying edges, and
 * P >= ceil(odd/2) from deg(v) = 2*(through) + ends(v).
 *
 * Usage: decide2 [node_cap] < graphs.g6
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>

#define MAXN 16
static int n, K;
static unsigned adj[MAXN];
static long long calls, node_cap;
static int cap_hit;

/* ---------------------------------------------------------------- memoisation */
#define HB 20
#define HSZ (1u << HB)
static unsigned long long *htab;
static unsigned long long zob[MAXN][MAXN];
static unsigned long long zbud[MAXN + 2];
static unsigned long long salt;   /* per-graph, so stale table entries cannot match */

static unsigned long long splitmix(unsigned long long x)
{
    x += 0x9E3779B97F4A7C15ULL;
    x = (x ^ (x >> 30)) * 0xBF58476D1CE4E5B9ULL;
    x = (x ^ (x >> 27)) * 0x94D049BB133111EBULL;
    return x ^ (x >> 31);
}

static unsigned long long fingerprint(int budget)
{
    unsigned long long h = zbud[budget] ^ salt;
    for (int i = 0; i < n; i++) {
        unsigned a = adj[i] & ~((1u << (i + 1)) - 1);   /* each edge once, i<j */
        while (a) { int j = __builtin_ctz(a); a &= a - 1; h ^= zob[i][j]; }
    }
    return h ? h : 1;
}

static inline int memo_seen(unsigned long long h)
{
    unsigned idx = (unsigned)(h >> (64 - HB));
    for (int p = 0; p < 8; p++) {
        unsigned long long v = htab[(idx + p) & (HSZ - 1)];
        if (v == 0) return 0;
        if (v == h) return 1;
    }
    return 0;
}
static inline void memo_add(unsigned long long h)
{
    unsigned idx = (unsigned)(h >> (64 - HB));
    for (int p = 0; p < 8; p++) {
        unsigned long long *slot = &htab[(idx + p) & (HSZ - 1)];
        if (*slot == 0 || *slot == h) { *slot = h; return; }
    }
    htab[idx & (HSZ - 1)] = h;      /* evict */
}

/* ---------------------------------------------------------------- bounds */
static int edge_count(void)
{
    int m = 0;
    for (int i = 0; i < n; i++) m += __builtin_popcount(adj[i]);
    return m / 2;
}

static int lower_bound_paths(void)
{
    int odd = 0;
    for (int i = 0; i < n; i++) if (__builtin_popcount(adj[i]) & 1) odd++;
    int lb = (odd + 1) / 2;
    unsigned seen = 0; int comps = 0;
    for (int i = 0; i < n; i++) {
        if (!adj[i] || ((seen >> i) & 1)) continue;
        comps++;
        unsigned st = 1u << i;
        while (st) {
            int v = __builtin_ctz(st); st &= ~(1u << v);
            if ((seen >> v) & 1) continue;
            seen |= 1u << v;
            st |= adj[v] & ~seen;
        }
    }
    if (comps > lb) lb = comps;
    int m = 0;
    for (int i = 0; i < n; i++) m += __builtin_popcount(adj[i]);
    m /= 2;
    int capb = (m + (n - 2)) / (n - 1);
    if (capb > lb) lb = capb;
    return lb;
}

static int solve(int budget);

static int grow_v(int uend, int vend, unsigned used, int budget, int len, int minlen)
{
    unsigned cand = adj[vend] & ~used;
    while (cand) {                                    /* EXTEND FIRST */
        int w = __builtin_ctz(cand); cand &= cand - 1;
        adj[vend] &= ~(1u << w); adj[w] &= ~(1u << vend);
        int r = grow_v(uend, w, used | (1u << w), budget, len + 1, minlen);
        adj[vend] |= 1u << w; adj[w] |= 1u << vend;
        if (r) return 1;
        if (cap_hit) return 0;
    }
    if (len >= minlen && solve(budget - 1)) return 1; /* then close the path */
    return 0;
}

static int grow_u(int uend, int vend, unsigned used, int budget, int len, int minlen)
{
    unsigned cand = adj[uend] & ~used;
    while (cand) {
        int w = __builtin_ctz(cand); cand &= cand - 1;
        adj[uend] &= ~(1u << w); adj[w] &= ~(1u << uend);
        int r = grow_u(w, vend, used | (1u << w), budget, len + 1, minlen);
        adj[uend] |= 1u << w; adj[w] |= 1u << uend;
        if (r) return 1;
        if (cap_hit) return 0;
    }
    return grow_v(uend, vend, used, budget, len, minlen);
}

static int solve(int budget)
{
    if (++calls > node_cap) { cap_hit = 1; return 0; }
    int m = edge_count();
    if (m == 0) return 1;
    if (budget <= 0) return 0;
    if (m > budget * (n - 1)) return 0;                  /* capacity */
    if (lower_bound_paths() > budget) return 0;
    unsigned long long h = fingerprint(budget);
    if (memo_seen(h)) return 0;
    int minlen = m - (budget - 1) * (n - 1);
    if (minlen < 1) minlen = 1;
    int u = -1, bestd = 99;
    for (int i = 0; i < n; i++) {
        int d = __builtin_popcount(adj[i]);
        if (d && d < bestd) { bestd = d; u = i; }
    }
    int v = __builtin_ctz(adj[u]);
    adj[u] &= ~(1u << v); adj[v] &= ~(1u << u);
    int r;
    if (bestd == 1)                       /* u is forced to be a path endpoint */
        r = grow_v(u, v, (1u << u) | (1u << v), budget, 1, minlen);
    else
        r = grow_u(u, v, (1u << u) | (1u << v), budget, 1, minlen);
    adj[u] |= 1u << v; adj[v] |= 1u << u;
    if (!r && !cap_hit) memo_add(h);
    return r;
}

static int decode_g6(const char *s, int *pn, unsigned *A)
{
    const unsigned char *p = (const unsigned char *)s;
    int nn = *p++ - 63;
    if (nn > MAXN) return 0;
    for (int i = 0; i < nn; i++) A[i] = 0;
    int bit = 0, cur = 0;
    for (int j = 1; j < nn; j++)
        for (int i = 0; i < j; i++) {
            if (bit == 0) { cur = *p++ - 63; bit = 6; }
            bit--;
            if ((cur >> bit) & 1) { A[i] |= 1u << j; A[j] |= 1u << i; }
        }
    *pn = nn;
    return 1;
}

int main(int argc, char **argv)
{
    node_cap = (argc > 1) ? atoll(argv[1]) : 50000000LL;
    htab = calloc(HSZ, sizeof(unsigned long long));
    unsigned long long sd = 0x243F6A8885A308D3ULL;
    for (int i = 0; i < MAXN; i++)
        for (int j = 0; j < MAXN; j++) { sd = splitmix(sd); zob[i][j] = sd; }
    for (int i = 0; i < MAXN + 2; i++) { sd = splitmix(sd); zbud[i] = sd; }

    char line[256];
    long long tot = 0, yes = 0, no = 0, und = 0;
    double worst = 0;
    clock_t t_all = clock();
    while (fgets(line, sizeof line, stdin)) {
        char *nl = strchr(line, '\n'); if (nl) *nl = 0;
        if (!line[0]) continue;
        if (!decode_g6(line, &n, adj)) continue;
        K = (n + 1) / 2;
        calls = 0; cap_hit = 0;
        sd = splitmix(sd); salt = sd;
        clock_t t0 = clock();
        int r = solve(K);
        double dt = (double)(clock() - t0) / CLOCKS_PER_SEC;
        if (dt > worst) worst = dt;
        tot++;
        if (cap_hit) und++;
        else if (r) yes++;
        else { no++; printf("COUNTEREXAMPLE %s\n", line); fflush(stdout); }
    }
    double secs = (double)(clock() - t_all) / CLOCKS_PER_SEC;
    fprintf(stderr, "decided %lld: decomposable=%lld NOT=%lld undecided(cap)=%lld\n"
                    "total %.3fs  mean %.1f us/graph  worst %.1f us\n",
            tot, yes, no, und, secs, tot ? secs * 1e6 / tot : 0.0, worst * 1e6);
    return 0;
}
