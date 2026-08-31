/* Erdos #217 crescent configurations -- sharded, incremental-mask version.
 *
 * Improvement over crescent.c: instead of re-testing every candidate point against
 * every chosen pair (collinear) and chosen triple (concyclic), maintain a FORBIDDEN
 * BITMASK.  When a point is accepted at depth d we mark, once, every point that is
 * collinear with it and one earlier chosen point, or concyclic with it and two
 * earlier chosen points.  Testing a candidate then costs one bit lookup.  The work
 * moves from (candidates x depth^3) to (accepted nodes x depth^2 x NP).
 *
 * All arithmetic is exact integer -- see crescent.c for why the triangular lattice
 * makes collinearity and concyclicity integer determinants.
 *
 * Sharding: point 0 is pinned at the origin; shard s takes the second point from
 * indices congruent to s mod NSHARDS.  Shards are independent and their union is
 * the whole search, so the sweep is exhaustive iff every shard completes.
 *
 * Usage: crescent2 n R2 out.txt shard nshards [heartbeat.json]
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>

#define MAXP 2048
#define MAXW (MAXP/64)
#define MAXN 12

static int NP, n, SHARD, NSH;
static long long R2;
static int PA[MAXP], PB[MAXP];
static long long PX[MAXP], PY[MAXP], PN[MAXP];

typedef unsigned long long u64;
static int NW;

static inline long long d2i(int i, int j)
{
    long long p = PA[i] - PA[j], q = PB[i] - PB[j];
    return p * p + p * q + q * q;
}
static inline long long cross3(int i, int j, int k)
{
    return (PX[j]-PX[i])*(PY[k]-PY[i]) - (PY[j]-PY[i])*(PX[k]-PX[i]);
}
static long long circ4(int a, int b, int c, int d)
{
    int id[4] = { a, b, c, d };
    long long M[4][3];
    for (int r = 0; r < 4; r++) { M[r][0]=PN[id[r]]; M[r][1]=PX[id[r]]; M[r][2]=PY[id[r]]; }
    long long det = 0;
    for (int r = 0; r < 4; r++) {
        long long m[3][3]; int rr = 0;
        for (int s = 0; s < 4; s++) { if (s==r) continue;
            m[rr][0]=M[s][0]; m[rr][1]=M[s][1]; m[rr][2]=M[s][2]; rr++; }
        long long sub = m[0][0]*(m[1][1]*m[2][2]-m[1][2]*m[2][1])
                      - m[0][1]*(m[1][0]*m[2][2]-m[1][2]*m[2][0])
                      + m[0][2]*(m[1][0]*m[2][1]-m[1][1]*m[2][0]);
        det += ((r & 1) ? 1 : -1) * sub;
    }
    return det;
}

static u64 forb[MAXN][MAXW];
static int chosen[MAXN];
#define MAXD 64
static long long dval[MAXD];
static int dcnt[MAXD], ndist;
static long long nodes, solutions;
static FILE *out;
static char hbfile[512];
static clock_t T0;
static int cur_p1;

static int mult_ok(void)
{
    if (ndist > n - 1) return 0;
    int m[MAXD];
    memcpy(m, dcnt, sizeof(int)*ndist);
    for (int i = 1; i < ndist; i++) { int v=m[i], j=i-1;
        while (j>=0 && m[j]<v) { m[j+1]=m[j]; j--; } m[j+1]=v; }
    for (int j = 0; j < ndist; j++) if (m[j] > n-1-j) return 0;
    return 1;
}

static void heartbeat(void)
{
    if (!hbfile[0]) return;
    FILE *f = fopen(hbfile, "w");
    if (!f) return;
    fprintf(f, "{\"n\":%d,\"R2\":%lld,\"shard\":%d,\"nshards\":%d,"
               "\"points\":%d,\"p1_index\":%d,\"nodes\":%lld,\"solutions\":%lld,"
               "\"seconds\":%.1f,\"status\":\"RUNNING\"}\n",
            n, R2, SHARD, NSH, NP, cur_p1, nodes, solutions,
            (double)(clock()-T0)/CLOCKS_PER_SEC);
    fclose(f);
}

static void rec(int depth, int start)
{
    if (depth == n) {
        if (ndist != n-1) return;
        int seen[MAXN]; memset(seen, 0, sizeof seen);
        for (int i = 0; i < ndist; i++) {
            int c = dcnt[i];
            if (c < 1 || c > n-1 || seen[c]) return;
            seen[c] = 1;
        }
        solutions++;
        fprintf(out, "SOLUTION");
        for (int i = 0; i < n; i++) fprintf(out, " (%d,%d)", PA[chosen[i]], PB[chosen[i]]);
        fprintf(out, "\n"); fflush(out);
        fprintf(stderr, "*** SOLUTION n=%d shard %d\n", n, SHARD);
        return;
    }
    for (int p = start; p < NP; p++) {
        if (NP - p < n - depth) break;
        if (forb[depth][p >> 6] >> (p & 63) & 1ULL) continue;
        nodes++;
        if ((nodes & 0xFFFFFF) == 0) heartbeat();

        int added[MAXN], nadded = 0, newclasses = 0, bad = 0;
        for (int i = 0; i < depth; i++) {
            long long v = d2i(chosen[i], p);
            int f = -1;
            for (int t = 0; t < ndist; t++) if (dval[t] == v) { f = t; break; }
            if (f < 0) {
                if (ndist >= MAXD) { bad = 1; break; }
                dval[ndist]=v; dcnt[ndist]=1; f=ndist; ndist++; newclasses++;
            } else dcnt[f]++;
            added[nadded++] = f;
        }
        if (!bad && mult_ok()) {
            chosen[depth] = p;
            /* build the forbidden mask for the next level */
            memcpy(forb[depth+1], forb[depth], sizeof(u64)*NW);
            forb[depth+1][p>>6] |= 1ULL << (p & 63);
            for (int i = 0; i < depth; i++)
                for (int q = p+1; q < NP; q++)
                    if (cross3(chosen[i], p, q) == 0)
                        forb[depth+1][q>>6] |= 1ULL << (q & 63);
            for (int i = 0; i < depth; i++)
                for (int j = i+1; j < depth; j++)
                    for (int q = p+1; q < NP; q++)
                        if (!(forb[depth+1][q>>6] >> (q&63) & 1ULL))
                            if (circ4(chosen[i], chosen[j], p, q) == 0)
                                forb[depth+1][q>>6] |= 1ULL << (q & 63);
            rec(depth+1, p+1);
        }
        for (int t = nadded-1; t >= 0; t--) dcnt[added[t]]--;
        ndist -= newclasses;
    }
}

int main(int argc, char **argv)
{
    n = atoi(argv[1]); R2 = atoll(argv[2]);
    const char *fn = argv[3];
    SHARD = (argc>4) ? atoi(argv[4]) : 0;
    NSH   = (argc>5) ? atoi(argv[5]) : 1;
    if (argc>6) snprintf(hbfile, sizeof hbfile, "%s", argv[6]);
    out = fopen(fn, "w");

    int lim = 1; while ((long long)lim*lim <= R2) lim++;
    lim += 2;
    NP = 0; PA[0]=0; PB[0]=0; NP=1;
    for (int a = -lim; a <= lim; a++)
        for (int b = -lim; b <= lim; b++) {
            if (!a && !b) continue;
            long long N = (long long)a*a + (long long)a*b + (long long)b*b;
            if (N <= R2 && NP < MAXP) { PA[NP]=a; PB[NP]=b; NP++; }
        }
    for (int i = 0; i < NP; i++) {
        PX[i]=2LL*PA[i]+PB[i]; PY[i]=PB[i];
        PN[i]=(long long)PA[i]*PA[i]+(long long)PA[i]*PB[i]+(long long)PB[i]*PB[i];
    }
    NW = (NP + 63) / 64;
    fprintf(stderr, "n=%d R2=%lld points=%d shard %d/%d\n", n, R2, NP, SHARD, NSH);

    T0 = clock();
    chosen[0] = 0; ndist = 0;
    memset(forb[1], 0, sizeof(u64)*NW);
    forb[1][0] |= 1ULL;                       /* origin used */
    /* depth 1 -> choose the second point, sharded */
    for (int p = 1; p < NP; p++) {
        if (p % NSH != SHARD) continue;
        cur_p1 = p; heartbeat();
        nodes++;
        long long v = d2i(0, p);
        dval[0]=v; dcnt[0]=1; ndist=1;
        chosen[1] = p;
        memcpy(forb[2], forb[1], sizeof(u64)*NW);
        forb[2][p>>6] |= 1ULL << (p & 63);
        for (int q = p+1; q < NP; q++)
            if (cross3(0, p, q) == 0) forb[2][q>>6] |= 1ULL << (q & 63);
        rec(2, p+1);
        ndist = 0;
    }
    double secs = (double)(clock()-T0)/CLOCKS_PER_SEC;
    if (hbfile[0]) {
        FILE *f = fopen(hbfile, "w");
        fprintf(f, "{\"n\":%d,\"R2\":%lld,\"shard\":%d,\"nshards\":%d,\"points\":%d,"
                   "\"nodes\":%lld,\"solutions\":%lld,\"seconds\":%.1f,"
                   "\"status\":\"COMPLETED\"}\n",
                n, R2, SHARD, NSH, NP, nodes, solutions, secs);
        fclose(f);
    }
    fprintf(stderr, "n=%d R2=%lld shard %d: nodes=%lld solutions=%lld %.2fs\n",
            n, R2, SHARD, nodes, solutions, secs);
    fclose(out);
    return 0;
}
