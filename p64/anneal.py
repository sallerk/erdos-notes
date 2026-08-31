"""
Simulated annealing over cubic graphs.  TWO uses:

  1. AS A TEST OF THE EXHAUSTIVE SEARCH.  The literature (MathWorld / Wikipedia,
     via Markstrom) states there are cubic graphs on 24 vertices whose only
     power-of-2 cycle length is 16 -- i.e. cubic, 24 vertices, no C4, no C8.
     If annealing finds one, the exhaustive generator is buggy.  If nothing turns
     up after a long run that is weak evidence only.

  2. AS A NON-EXHAUSTIVE HUNT for an actual counterexample at larger n
     (objective = number of cycles of every forbidden power-of-2 length).

THIS IS A HEURISTIC.  It can never certify that nothing exists.

usage: python anneal.py N L1,L2,... [restarts] [iters] [seed]
"""

import sys
import time

import numpy as np
from numba import njit


@njit(cache=True)
def count_cycles_len(nbr, n, L, seen, sv, si):
    """Exact number of cycles of length exactly L.  Each cycle is counted from its
    minimum-labelled vertex, traversed in both directions -> divide by 2."""
    tot = 0
    for s in range(n):
        for x in range(n):
            seen[x] = False
        seen[s] = True
        top = 0
        sv[0] = s
        si[0] = 0
        while top >= 0:
            x = sv[top]
            if si[top] >= 3:
                seen[x] = False
                top -= 1
                continue
            y = nbr[3 * x + si[top]]
            si[top] += 1
            # edges used after stepping to y == top+1; need L edges total
            if top + 1 == L:
                if y == s:
                    tot += 1
                continue
            if y <= s or seen[y]:
                continue
            seen[y] = True
            top += 1
            sv[top] = y
            si[top] = 0
    return tot // 2


@njit(cache=True)
def cost(nbr, n, Ls, seen, sv, si):
    c = 0
    for t in range(Ls.shape[0]):
        c += count_cycles_len(nbr, n, Ls[t], seen, sv, si)
    return c


@njit(cache=True)
def _has(nbr, u, v):
    for t in range(3):
        if nbr[3 * u + t] == v:
            return True
    return False


@njit(cache=True)
def _replace(nbr, u, old, new):
    for t in range(3):
        if nbr[3 * u + t] == old:
            nbr[3 * u + t] = new
            return


@njit(cache=True)
def anneal(nbr, n, Ls, iters, T0, T1, seed):
    np.random.seed(seed)
    seen = np.zeros(n, np.bool_)
    sv = np.zeros(64, np.int32)
    si = np.zeros(64, np.int32)
    # edge list
    m = 3 * n // 2
    ea = np.zeros(m, np.int32)
    eb = np.zeros(m, np.int32)
    k = 0
    for u in range(n):
        for t in range(3):
            v = nbr[3 * u + t]
            if u < v:
                ea[k] = u
                eb[k] = v
                k += 1
    cur = cost(nbr, n, Ls, seen, sv, si)
    best = cur
    for it in range(iters):
        if cur == 0:
            break
        T = T0 * (T1 / T0) ** (it / iters)
        i = np.random.randint(m)
        j = np.random.randint(m)
        if i == j:
            continue
        a = ea[i]
        b = eb[i]
        c = ea[j]
        d = eb[j]
        if a == c or a == d or b == c or b == d:
            continue
        # Remove edges (a,b) and (c,d); insert either {(a,c),(b,d)} or {(a,d),(b,c)}.
        if np.random.random() < 0.5:
            p, q = c, d     # new edges (a,c) and (b,d)
        else:
            p, q = d, c     # new edges (a,d) and (b,c)
        if _has(nbr, a, p) or _has(nbr, b, q):
            continue
        # apply: a: b->p ; b: a->q ; p: (its old partner) -> a ; q: (old partner) -> b
        _replace(nbr, a, b, p)
        _replace(nbr, b, a, q)
        _replace(nbr, p, q, a)      # p's old partner in edge (c,d) is q
        _replace(nbr, q, p, b)
        new = cost(nbr, n, Ls, seen, sv, si)
        dcost = new - cur
        if dcost <= 0 or np.random.random() < np.exp(-dcost / T):
            cur = new
            ea[i] = a if a < p else p
            eb[i] = p if a < p else a
            ea[j] = b if b < q else q
            eb[j] = q if b < q else b
            if cur < best:
                best = cur
        else:
            # undo
            _replace(nbr, a, p, b)
            _replace(nbr, b, q, a)
            _replace(nbr, p, a, q)
            _replace(nbr, q, b, p)
    return cur, best


def random_cubic(n, rng):
    import networkx as nx
    while True:
        try:
            G = nx.random_regular_graph(3, n, seed=int(rng.integers(1 << 30)))
        except Exception:
            continue
        if nx.is_connected(G):
            nbr = np.full(3 * n, -1, np.int32)
            deg = np.zeros(n, np.int32)
            for u, v in G.edges():
                nbr[3 * u + deg[u]] = v
                deg[u] += 1
                nbr[3 * v + deg[v]] = u
                deg[v] += 1
            return nbr


def main():
    n = int(sys.argv[1])
    Ls = np.array([int(x) for x in sys.argv[2].split(",")], dtype=np.int64)
    restarts = int(sys.argv[3]) if len(sys.argv) > 3 else 200
    iters = int(sys.argv[4]) if len(sys.argv) > 4 else 200000
    seed0 = int(sys.argv[5]) if len(sys.argv) > 5 else 1

    rng = np.random.default_rng(seed0)
    bestall = 10 ** 9
    t0 = time.time()
    for r in range(restarts):
        nbr = random_cubic(n, rng)
        cur, best = anneal(nbr, n, Ls, iters, 3.0, 0.02, (seed0 * 7919 + r) % (2 ** 31))
        if cur < bestall:
            bestall = cur
            print(f"  restart {r}: best cost so far = {bestall}  "
                  f"({time.time()-t0:.0f}s)", flush=True)
        if cur == 0:
            edges = []
            for u in range(n):
                for t in range(3):
                    v = int(nbr[3 * u + t])
                    if u < v:
                        edges.append((u, v))
            print(f"\n*** FOUND cubic n={n} with NO cycle of lengths "
                  f"{list(Ls)} ***")
            print(sorted(edges))
            return sorted(edges)
    print(f"\nno graph found in {restarts} restarts; best cost = {bestall} "
          f"({time.time()-t0:.0f}s)")
    return None


if __name__ == "__main__":
    main()
