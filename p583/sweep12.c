/* Erdos #583 sweep stage: read graph6 on stdin, apply the sound cited-theorem
 * filters, try randomised greedy path decomposition, and emit on stdout every
 * graph the greedy cannot decompose (those go to the exhaustive decider).
 *
 * Filters, each discarding graphs the conjecture is already proved for:
 *   Delta <= 5                     Bonamy-Perrett [BoPe19]
 *   <= 1 vertex of even degree     Lovasz [Lo68]
 *   even-degree vertices a forest  Pyber [Py96]
 *
 * Writes a heartbeat JSON periodically so the supervisor can measure progress as
 * a DELTA between reads rather than as state.
 *
 * Usage: sweep12 heartbeat.json [restarts] < graphs.g6 > hard.g6
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>

#define MAXN 16
static int n;
static unsigned adj[MAXN];
static int RESTARTS = 40;
static unsigned long long rng_s = 88172645463325252ULL;
static inline unsigned long long xs(void)
{ rng_s ^= rng_s << 13; rng_s ^= rng_s >> 7; rng_s ^= rng_s << 17; return rng_s; }

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

static int greedy(int randomize)
{
    unsigned R[MAXN];
    memcpy(R, adj, sizeof(unsigned) * n);
    int edges = 0;
    for (int i = 0; i < n; i++) edges += __builtin_popcount(R[i]);
    edges /= 2;
    int paths = 0;
    while (edges > 0) {
        int s = -1;
        int off = randomize ? (int)(xs() % (unsigned)n) : 0;
        for (int t = 0; t < n; t++) {
            int i = (t + off) % n;
            if (R[i] && (__builtin_popcount(R[i]) & 1)) { s = i; break; }
        }
        if (s < 0) for (int i = 0; i < n; i++) if (R[i]) { s = i; break; }
        unsigned visited = 1u << s;
        int cur = s;
        for (;;) {
            unsigned cand = R[cur] & ~visited;
            if (!cand) break;
            int best = -1, bestd = 1 << 30;
            unsigned c = cand;
            while (c) {
                int v = __builtin_ctz(c); c &= c - 1;
                int d = __builtin_popcount(R[v]);
                if (randomize) d = d * 8 + (int)(xs() & 7);
                if (d < bestd) { bestd = d; best = v; }
            }
            R[cur] &= ~(1u << best); R[best] &= ~(1u << cur);
            edges--; visited |= 1u << best; cur = best;
        }
        paths++;
        if (paths > n) break;
    }
    return paths;
}

int main(int argc, char **argv)
{
    const char *hb = (argc > 1) ? argv[1] : NULL;
    if (argc > 2) RESTARTS = atoi(argv[2]);
    char line[256];
    long long total = 0, hard = 0;
    long long f_delta = 0, f_even = 0, f_forest = 0, survived = 0;
    clock_t t0 = clock();

    while (fgets(line, sizeof line, stdin)) {
        char *nl = strchr(line, '\n'); if (nl) *nl = 0;
        if (!line[0]) continue;
        if (!decode_g6(line, &n, adj)) continue;
        total++;
        if (hb && (total & 0xFFFFFF) == 0) {
            FILE *f = fopen(hb, "w");
            if (f) {
                fprintf(f, "{\"graphs\":%lld,\"hard\":%lld,\"filtered\":%lld,"
                           "\"seconds\":%.1f,\"status\":\"RUNNING\"}",
                        total, hard, f_delta + f_even + f_forest,
                        (double)(clock() - t0) / CLOCKS_PER_SEC);
                fputc('\n', f);
                fclose(f);
            }
        }
        int maxdeg = 0, neven = 0;
        int deg[MAXN];
        for (int i = 0; i < n; i++) {
            deg[i] = __builtin_popcount(adj[i]);
            if (deg[i] > maxdeg) maxdeg = deg[i];
            if (!(deg[i] & 1)) neven++;
        }
        if (maxdeg <= 5) { f_delta++; continue; }
        if (neven <= 1) { f_even++; continue; }
        unsigned evenmask = 0;
        for (int i = 0; i < n; i++) if (!(deg[i] & 1)) evenmask |= 1u << i;
        int cyc = 0;
        unsigned seen = 0;
        for (int i = 0; i < n && !cyc; i++) {
            if (!((evenmask >> i) & 1) || ((seen >> i) & 1)) continue;
            unsigned st = 1u << i, comp = 0;
            int ce = 0, cv = 0;
            while (st) {
                int v = __builtin_ctz(st); st &= ~(1u << v);
                if ((comp >> v) & 1) continue;
                comp |= 1u << v; cv++;
                unsigned nb = adj[v] & evenmask;
                ce += __builtin_popcount(nb);
                st |= nb & ~comp;
            }
            ce /= 2; seen |= comp;
            if (ce >= cv) cyc = 1;
        }
        if (!cyc) { f_forest++; continue; }
        survived++;

        int k = (n + 1) / 2;
        int p = greedy(0);
        for (int t = 0; t < RESTARTS && p > k; t++) {
            int q = greedy(1);
            if (q < p) p = q;
        }
        if (p > k) { hard++; puts(line); }
    }
    double secs = (double)(clock() - t0) / CLOCKS_PER_SEC;
    if (hb) {
        FILE *f = fopen(hb, "w");
        if (f) {
            fprintf(f, "{\"graphs\":%lld,\"hard\":%lld,\"filtered\":%lld,"
                       "\"seconds\":%.1f,\"status\":\"COMPLETED\"}",
                    total, hard, f_delta + f_even + f_forest, secs);
            fputc('\n', f);
            fclose(f);
        }
    }
    fprintf(stderr, "graphs=%lld filtered=%lld survived=%lld HARD=%lld  %.1fs (%.3f us/graph)\n",
            total, f_delta + f_even + f_forest, survived, hard, secs,
            total ? secs * 1e6 / total : 0.0);
    return 0;
}
