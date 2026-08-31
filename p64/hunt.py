"""
NON-EXHAUSTIVE heuristic hunt for an actual cubic counterexample.

WHY THIS WINDOW.  For n <= 63 the power-of-2 lengths that fit in an n-vertex simple
graph are exactly 4, 8, 16, 32.  So for 54 <= n <= 62 (even), a cubic graph with no
C4, C8, C16 and C32 IS a counterexample to Erdos-Gyarfas -- nothing further to check.
And by Markstrom's f(4) >= 54 (unpublished, cited in Exoo arXiv:1403.5636) nothing
smaller than 54 can work.  So {54,56,58,60,62} is exactly the window in which a
"small" cubic counterexample could still hide.

METHOD.  Two-phase simulated annealing over connected cubic graphs under 2-opt edge
swaps.  Phase 1 drives #C4 + #C8 to 0 (cheap objective).  Phase 2 minimises #C16
while REJECTING any move that re-creates a C4 or C8.  Any graph reaching #C16 = 0 is
then tested exactly for C32.

THIS CANNOT CERTIFY ANYTHING.  Failure is not evidence of non-existence.  Note also
that Exoo's smallest known (4,8,16)-free cubic graph has 78 vertices and is a highly
structured vertex-replacement construction, so random search in 54..62 is a long shot.

usage: python hunt.py N [restarts] [iters] [seed] [workers]
"""

import sys
import time
from multiprocessing import Pool

import numpy as np
from numba import njit

from anneal import _has, _replace, count_cycles_len, random_cubic


@njit(cache=True)
def _c48(nbr, n, seen, sv, si):
    return (count_cycles_len(nbr, n, 4, seen, sv, si)
            + count_cycles_len(nbr, n, 8, seen, sv, si))


@njit(cache=True)
def _run(nbr, n, iters1, iters2, T0, T1, seed):
    np.random.seed(seed)
    seen = np.zeros(n, np.bool_)
    sv = np.zeros(70, np.int32)
    si = np.zeros(70, np.int32)
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

    # ---- phase 1: kill all C4 and C8 ----
    cur = _c48(nbr, n, seen, sv, si)
    for it in range(iters1):
        if cur == 0:
            break
        T = 2.0 * (0.02 / 2.0) ** (it / iters1)
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
        if np.random.random() < 0.5:
            p, q = c, d
        else:
            p, q = d, c
        if _has(nbr, a, p) or _has(nbr, b, q):
            continue
        _replace(nbr, a, b, p)
        _replace(nbr, b, a, q)
        _replace(nbr, p, q, a)
        _replace(nbr, q, p, b)
        new = _c48(nbr, n, seen, sv, si)
        if new <= cur or np.random.random() < np.exp(-(new - cur) / T):
            cur = new
            ea[i] = a
            eb[i] = p
            ea[j] = b
            eb[j] = q
        else:
            _replace(nbr, a, p, b)
            _replace(nbr, b, q, a)
            _replace(nbr, p, a, q)
            _replace(nbr, q, b, p)
    if cur != 0:
        return 10 ** 9, 10 ** 9

    # ---- phase 2: minimise #C16 while staying C4/C8-free ----
    c16 = count_cycles_len(nbr, n, 16, seen, sv, si)
    best = c16
    for it in range(iters2):
        if c16 == 0:
            break
        T = 8.0 * (0.05 / 8.0) ** (it / iters2)
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
        if np.random.random() < 0.5:
            p, q = c, d
        else:
            p, q = d, c
        if _has(nbr, a, p) or _has(nbr, b, q):
            continue
        _replace(nbr, a, b, p)
        _replace(nbr, b, a, q)
        _replace(nbr, p, q, a)
        _replace(nbr, q, p, b)
        # cheap feasibility gate first
        if _c48(nbr, n, seen, sv, si) != 0:
            _replace(nbr, a, p, b)
            _replace(nbr, b, q, a)
            _replace(nbr, p, a, q)
            _replace(nbr, q, b, p)
            continue
        new = count_cycles_len(nbr, n, 16, seen, sv, si)
        if new <= c16 or np.random.random() < np.exp(-(new - c16) / T):
            c16 = new
            ea[i] = a
            eb[i] = p
            ea[j] = b
            eb[j] = q
            if c16 < best:
                best = c16
        else:
            _replace(nbr, a, p, b)
            _replace(nbr, b, q, a)
            _replace(nbr, p, a, q)
            _replace(nbr, q, b, p)
    return c16, best


def _job(args):
    n, seed, restarts, it1, it2 = args
    rng = np.random.default_rng(seed)
    bl = 10 ** 9
    hit = None
    for r in range(restarts):
        nbr = random_cubic(n, rng)
        cur, best = _run(nbr, n, it1, it2, 2.0, 0.05, (seed * 7919 + r) % (2 ** 31))
        if best < bl:
            bl = best
        if cur == 0:
            hit = [int(x) for x in nbr]
            break
    return bl, hit


def main():
    n = int(sys.argv[1])
    restarts = int(sys.argv[2]) if len(sys.argv) > 2 else 20
    it1 = 200000
    it2 = int(sys.argv[3]) if len(sys.argv) > 3 else 40000
    seed0 = int(sys.argv[4]) if len(sys.argv) > 4 else 1
    workers = int(sys.argv[5]) if len(sys.argv) > 5 else 5
    assert workers <= 5

    t = time.time()
    with Pool(workers) as p:
        res = p.map(_job, [(n, seed0 + 1000 * w, restarts, it1, it2)
                           for w in range(workers)])
    bl = min(r[0] for r in res)
    hits = [r[1] for r in res if r[1] is not None]
    print(f"n={n}: {workers*restarts} annealing restarts, best #C16 reached = {bl} "
          f"(with #C4=#C8=0)   {time.time()-t:.0f}s", flush=True)
    if hits:
        nbr = np.array(hits[0], np.int32)
        seen = np.zeros(n, np.bool_)
        sv = np.zeros(70, np.int32)
        si = np.zeros(70, np.int32)
        c32 = count_cycles_len(nbr, n, 32, seen, sv, si)
        E = sorted({(min(v, int(nbr[3 * v + t])), max(v, int(nbr[3 * v + t])))
                    for v in range(n) for t in range(3)})
        print(f"*** (4,8,16)-FREE CUBIC GRAPH ON {n} VERTICES FOUND *** #C32 = {c32}")
        print(E)
        if c32 == 0 and n <= 63:
            print("*** THIS IS A COUNTEREXAMPLE TO ERDOS-GYARFAS ***")
    else:
        print("  no (4,8,16)-free graph found (expected: none is known below 78)")


if __name__ == "__main__":
    main()
