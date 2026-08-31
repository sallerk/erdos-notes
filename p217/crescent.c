/* Erdos #217 -- crescent configurations, exhaustive search in the triangular lattice.
 *
 * STATEMENT (erdosproblems.com/217): for which n are there n points in R^2, no three
 * on a line and no four on a circle, determining n-1 distinct distances such that
 * (IN SOME ORDERING of the distances) the i-th distance occurs i times?
 * Note "in some ordering": the multiplicities need only form the multiset
 * {1,2,...,n-1}; they need NOT increase with the distance.  Sum = C(n,2), so every
 * pair is accounted for exactly.
 * Known: n = 4,5,6,7,8 exist (Pomerance n=5; Palasti n=6,7,8).  n = 9 OPEN.
 *
 * WHY THE TRIANGULAR LATTICE IS EXACT.  Embed (a,b) as a*(1,0) + b*(1/2, sqrt3/2).
 * Then for p = a1-a2, q = b1-b2 the squared distance is exactly the integer
 *      N(p,q) = p^2 + p q + q^2.
 * Writing X = 2a+b and Y = b (both integers), the point is ((X)/2, (Y)sqrt3/2), so
 *   three points are COLLINEAR iff det[[X,Y,1]] = 0, and
 *   four points are CONCYCLIC iff det[[N, X, Y, 1]] = 0,
 * because scaling the X column by 2 and the Y column by 2/sqrt3 does not change
 * whether a determinant vanishes.  Both determinants are integers.  No floating
 * point is used anywhere.
 *
 * COMPLETENESS.  Point 0 of the configuration is pinned at the origin and the other
 * n-1 points range over every lattice point of squared norm <= R2.  Since the pinned
 * point may be taken to be any point of the configuration, this enumerates every
 * crescent configuration all of whose points lie within distance R of one of them --
 * in particular every configuration of diameter <= R -- up to translation.
 *
 * Prior computation to beat: Burt, Goldstein, Manski, Miller, Palsson, Suh,
 * arXiv:1509.07220 Remark 3.1 -- exhaustive over a 91-point hexagonal region, none
 * found, "over 900 hours of computation", and they ask for better techniques.
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>

#define MAXP 4096
#define MAXN 12

static int NP;                 /* number of lattice points in the region */
static int PX[MAXP], PY[MAXP]; /* X = 2a+b, Y = b   (integers) */
static long long PN[MAXP];     /* N = a^2+ab+b^2 = squared distance from origin */
static int PA[MAXP], PB[MAXP];

static int n;                  /* configuration size sought */
static long long R2;

/* squared distance between lattice points i,j */
static inline long long d2(int i, int j)
{
    long long p = PA[i] - PA[j], q = PB[i] - PB[j];
    return p * p + p * q + q * q;
}

static inline long long cross3(int i, int j, int k)   /* collinearity */
{
    long long x1 = PX[j] - PX[i], y1 = PY[j] - PY[i];
    long long x2 = PX[k] - PX[i], y2 = PY[k] - PY[i];
    return x1 * y2 - y1 * x2;
}

/* concyclicity: det of rows [N, X, Y, 1] for four points */
static long long circ4(int a, int b, int c, int d)
{
    long long M[4][4];
    int id[4] = { a, b, c, d };
    for (int r = 0; r < 4; r++) {
        M[r][0] = PN[id[r]]; M[r][1] = PX[id[r]]; M[r][2] = PY[id[r]]; M[r][3] = 1;
    }
    /* 4x4 determinant by cofactor expansion along the last column (entries all 1) */
    long long det = 0;
    for (int r = 0; r < 4; r++) {
        long long m[3][3];
        int rr = 0;
        for (int s = 0; s < 4; s++) {
            if (s == r) continue;
            m[rr][0] = M[s][0]; m[rr][1] = M[s][1]; m[rr][2] = M[s][2];
            rr++;
        }
        long long sub = m[0][0] * (m[1][1] * m[2][2] - m[1][2] * m[2][1])
                      - m[0][1] * (m[1][0] * m[2][2] - m[1][2] * m[2][0])
                      + m[0][2] * (m[1][0] * m[2][1] - m[1][1] * m[2][0]);
        det += ((r & 1) ? 1 : -1) * sub;
    }
    return det;
}

/* distance multiset state */
#define MAXD 64
static long long dval[MAXD];
static int dcnt[MAXD];
static int ndist;

static int chosen[MAXN];
static long long nodes, solutions;
static FILE *out;

/* the multiplicities must be extendable to exactly {1,2,...,n-1}.
 * Sorting current multiplicities descending as m_1 >= m_2 >= ... >= m_t, and the
 * targets descending as n-1, n-2, ..., 1, a necessary condition is m_j <= n-j for
 * every j, together with t <= n-1.  (Hall's condition for the obvious bipartite
 * matching between distance classes and target multiplicities.) */
static int mult_ok(void)
{
    if (ndist > n - 1) return 0;
    int m[MAXD];
    memcpy(m, dcnt, sizeof(int) * ndist);
    /* insertion sort descending; ndist is tiny */
    for (int i = 1; i < ndist; i++) {
        int v = m[i], j = i - 1;
        while (j >= 0 && m[j] < v) { m[j + 1] = m[j]; j--; }
        m[j + 1] = v;
    }
    for (int j = 0; j < ndist; j++)
        if (m[j] > n - 1 - j) return 0;
    return 1;
}

static void rec(int depth, int start)
{
    if (depth == n) {
        /* multiplicities must be exactly {1,...,n-1} */
        if (ndist != n - 1) return;
        int seen[MAXN];
        memset(seen, 0, sizeof seen);
        for (int i = 0; i < ndist; i++) {
            int c = dcnt[i];
            if (c < 1 || c > n - 1 || seen[c]) return;
            seen[c] = 1;
        }
        solutions++;
        fprintf(out, "SOLUTION");
        for (int i = 0; i < n; i++) fprintf(out, " (%d,%d)", PA[chosen[i]], PB[chosen[i]]);
        fprintf(out, "\n");
        fflush(out);
        fprintf(stderr, "*** SOLUTION FOUND (n=%d)\n", n);
        return;
    }
    for (int p = start; p < NP; p++) {
        if (NP - p < n - depth) break;
        nodes++;
        /* no three collinear */
        int bad = 0;
        for (int i = 0; i < depth && !bad; i++)
            for (int j = i + 1; j < depth; j++)
                if (cross3(chosen[i], chosen[j], p) == 0) { bad = 1; break; }
        if (bad) continue;
        /* no four concyclic */
        for (int i = 0; i < depth && !bad; i++)
            for (int j = i + 1; j < depth && !bad; j++)
                for (int k = j + 1; k < depth; k++)
                    if (circ4(chosen[i], chosen[j], chosen[k], p) == 0) { bad = 1; break; }
        if (bad) continue;
        /* add the new distances */
        int added[MAXN], nadded = 0, newclasses = 0;
        for (int i = 0; i < depth; i++) {
            long long v = d2(chosen[i], p);
            int f = -1;
            for (int t = 0; t < ndist; t++) if (dval[t] == v) { f = t; break; }
            if (f < 0) {
                if (ndist >= MAXD) { bad = 1; break; }
                dval[ndist] = v; dcnt[ndist] = 1; f = ndist; ndist++; newclasses++;
            } else dcnt[f]++;
            added[nadded++] = f;
        }
        if (!bad && mult_ok()) {
            chosen[depth] = p;
            rec(depth + 1, p + 1);
        }
        /* undo */
        for (int t = nadded - 1; t >= 0; t--) dcnt[added[t]]--;
        ndist -= newclasses;
    }
}

int main(int argc, char **argv)
{
    n = atoi(argv[1]);
    R2 = atoll(argv[2]);
    const char *fn = (argc > 3) ? argv[3] : "solutions.txt";
    out = fopen(fn, "w");

    /* lattice points of squared norm <= R2, origin first */
    int lim = 1; while (lim * lim <= R2) lim++;
    lim += 2;
    NP = 0;
    PA[NP] = 0; PB[NP] = 0; NP++;
    for (int a = -lim; a <= lim; a++)
        for (int b = -lim; b <= lim; b++) {
            if (a == 0 && b == 0) continue;
            long long N = (long long)a * a + (long long)a * b + (long long)b * b;
            if (N <= R2 && NP < MAXP) { PA[NP] = a; PB[NP] = b; NP++; }
        }
    for (int i = 0; i < NP; i++) {
        PX[i] = 2 * PA[i] + PB[i];
        PY[i] = PB[i];
        PN[i] = (long long)PA[i] * PA[i] + (long long)PA[i] * PB[i] + (long long)PB[i] * PB[i];
    }
    fprintf(stderr, "n=%d  R2=%lld  region has %d lattice points (origin pinned)\n",
            n, R2, NP);

    clock_t t0 = clock();
    chosen[0] = 0;           /* pin the origin */
    ndist = 0;
    rec(1, 1);
    double secs = (double)(clock() - t0) / CLOCKS_PER_SEC;
    fprintf(stderr, "n=%d R2=%lld: nodes=%lld solutions=%lld  %.2fs\n",
            n, R2, nodes, solutions, secs);
    printf("%d %lld %d %lld %lld %.2f\n", n, R2, NP, nodes, solutions, secs);
    fclose(out);
    return 0;
}
