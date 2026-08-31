"""Exhaustive DFS over k=3 witness patterns for a strictly convex n-gon,
with the OBTUSE-MIDDLE prune.  numba-jitted (no C compiler in this environment).

PATTERN: assign each vertex i a 3-subset T_i of the other vertices, meaning
"these three are equidistant from v_i".

LEMMA (proved and checked in control.py, verified on Danzer's 9-gon and on
random convex polygons).  Write T_i = {j,k,l} in ccw order starting after i.
Then v_i is the circumcentre of triangle jkl.  The four points v_i,v_j,v_k,v_l
are in convex position in that ccw order, so the diagonals v_i v_k and v_j v_l
cross: v_i and v_k are strictly on opposite sides of line v_j v_l.  A
circumcentre lies on the far side of a chord from the third vertex exactly when
the inscribed angle there is obtuse.  Hence angle(j,k,l) > 90 degrees, i.e.

        D_jl > D_jk + D_kl          (D = squared distance)

and in particular D_jl > D_jk and D_jl > D_kl.

PRUNE (sound): maintain a union-find on the C(n,2) squared distances for the
equalities D_ij = D_ik = D_il, and a strict-order digraph on the resulting
classes for the two inequalities.  A strict edge inside a class (D > D), or a
directed cycle (D_1 > D_2 > ... > D_1), refutes the partial pattern.  Both only
ever discard patterns that NO convex polygon realises, so completeness is kept.
"""
import numpy as np, sys, time
from numba import njit
from itertools import combinations

def tables(n):
    pid = np.zeros((n, n), np.int32)
    p = 0
    for a in range(n):
        for b in range(a+1, n):
            pid[a, b] = pid[b, a] = p; p += 1
    NP = p
    others0 = [[(i+a) % n for a in range(1, n)] for i in range(n)]   # ccw after i
    NT = len(list(combinations(range(n-1), 3)))
    TJ = np.zeros((n, NT), np.int32); TK = np.zeros((n, NT), np.int32)
    TL = np.zeros((n, NT), np.int32)
    for i in range(n):
        for t, (a, b, c) in enumerate(combinations(range(n-1), 3)):
            TJ[i, t] = others0[i][a]; TK[i, t] = others0[i][b]; TL[i, t] = others0[i][c]
    return pid, NP, NT, TJ, TK, TL

@njit(cache=True)
def _find(uf, x):
    while uf[x] != x:
        uf[x] = uf[uf[x]]
        x = uf[x]
    return x

@njit(cache=True)
def _consistent(choice, d, pid, NP, TJ, TK, TL, uf, hi, lo, indeg, present, stack):
    for i in range(NP):
        uf[i] = i
    for i in range(d+1):
        t = choice[i]
        a = pid[i, TJ[i, t]]; b = pid[i, TK[i, t]]; c = pid[i, TL[i, t]]
        ra = _find(uf, a); rb = _find(uf, b)
        if ra != rb: uf[ra] = rb
        rb = _find(uf, b); rc = _find(uf, c)
        if rb != rc: uf[rb] = rc
    ne = 0
    for i in range(d+1):
        t = choice[i]
        j = TJ[i, t]; k = TK[i, t]; l = TL[i, t]
        big = _find(uf, pid[j, l])
        s1 = _find(uf, pid[j, k]); s2 = _find(uf, pid[k, l])
        if big == s1 or big == s2:
            return 0
        hi[ne] = big; lo[ne] = s1; ne += 1
        hi[ne] = big; lo[ne] = s2; ne += 1
    for i in range(NP):
        indeg[i] = 0; present[i] = 0
    for e in range(ne):
        present[hi[e]] = 1; present[lo[e]] = 1
        indeg[lo[e]] += 1
    total = 0
    for i in range(NP):
        if present[i]: total += 1
    sp = 0
    for i in range(NP):
        if present[i] and indeg[i] == 0:
            stack[sp] = i; sp += 1
    cnt = 0
    while sp > 0:
        sp -= 1
        v = stack[sp]
        cnt += 1
        for e in range(ne):
            if hi[e] == v:
                indeg[lo[e]] -= 1
                if indeg[lo[e]] == 0:
                    stack[sp] = lo[e]; sp += 1
    if cnt < total:
        return 0
    return 1

@njit(cache=True)
def dfs(n, NP, NT, pid, TJ, TK, TL, t0_lo, t0_hi, out, out_cap):
    """explore only first-vertex triple indices in [t0_lo, t0_hi) -> parallel shards"""
    choice = np.zeros(16, np.int32)
    idx    = np.full(16, -1, np.int32)
    uf = np.zeros(64, np.int32); hi = np.zeros(64, np.int32); lo = np.zeros(64, np.int32)
    indeg = np.zeros(64, np.int32); present = np.zeros(64, np.int32); stack = np.zeros(64, np.int32)
    nodes = 0; survivors = 0; nout = 0
    d = 0
    idx[0] = t0_lo - 1
    while d >= 0:
        idx[d] += 1
        hi_d = t0_hi if d == 0 else NT
        if idx[d] >= hi_d:
            idx[d] = -1
            d -= 1
            continue
        choice[d] = idx[d]
        nodes += 1
        if _consistent(choice, d, pid, NP, TJ, TK, TL, uf, hi, lo, indeg, present, stack):
            if d == n-1:
                survivors += 1
                if nout < out_cap:
                    for q in range(n):
                        out[nout, q] = choice[q]
                    nout += 1
            else:
                d += 1
                idx[d] = -1
    return nodes, survivors, nout

def run(n, shards=None, cap=2_000_000, verbose=True):
    pid, NP, NT, TJ, TK, TL = tables(n)
    out = np.zeros((cap, n), np.int32)
    t0 = time.time()
    nodes, surv, nout = dfs(n, NP, NT, pid, TJ, TK, TL, 0, NT, out, cap)
    dt = time.time()-t0
    if verbose:
        print(f"n={n} triples/vertex={NT} raw={NT**n:,} nodes={nodes:,} "
              f"survivors={surv:,} ({dt:.1f}s)", flush=True)
    return dict(n=n, NT=NT, raw=NT**n, nodes=int(nodes), survivors=int(surv),
                stored=int(nout), seconds=round(dt,2)), out[:nout], (TJ,TK,TL)

if __name__ == '__main__':
    for n in [int(x) for x in (sys.argv[1:] or ['4','5','6'])]:
        run(n)
