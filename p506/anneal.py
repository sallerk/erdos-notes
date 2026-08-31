"""Simulated annealing for FEW distinct circles (Erdos #506), upper-bound side.

Exhaustive branch-and-bound reaches n=6 comfortably and stalls well before n=9,
so for the larger n this searches an integer grid heuristically.  A heuristic
search that finds a configuration PROVES an upper bound (the configuration is
then re-verified exactly); a heuristic search that finds nothing proves nothing,
and is reported as such.

Objective: the exact number of distinct circles.  Points are grid indices and all
triple->circle assignments are precomputed exactly over the integers, so the
objective is exact at every step -- annealing never sees a floating point number.

Invalid configurations (all collinear, all concyclic, or repeated points) are
rejected outright rather than penalised.
"""
import numpy as np, sys, json, time
from numba import njit
from gridsearch import build_grid, precompute


@njit(cache=True)
def _count(cid, sel, n, mark, stamp):
    """distinct circle ids among the C(n,3) triples of sel; lines (-1) ignored"""
    c = 0
    for a in range(n):
        for b in range(a + 1, n):
            for d in range(b + 1, n):
                q = cid[sel[a], sel[b], sel[d]]
                if q >= 0 and mark[q] != stamp:
                    mark[q] = stamp
                    c += 1
    return c


@njit(cache=True)
def _anneal(cid, N, n, iters, seed, mark, best_sel):
    np.random.seed(seed)
    sel = np.empty(n, np.int32)
    inset = np.zeros(N, np.uint8)
    k = 0
    while k < n:
        p = np.random.randint(0, N)
        if inset[p] == 0:
            inset[p] = 1
            sel[k] = p
            k += 1
    stamp = 1
    cur = _count(cid, sel, n, mark, stamp); stamp += 1
    best = cur
    for t in range(n):
        best_sel[t] = sel[t]
    T0, T1 = 4.0, 0.02
    for it in range(iters):
        T = T0 * (T1 / T0) ** (it / iters)
        i = np.random.randint(0, n)
        old = sel[i]
        p = np.random.randint(0, N)
        if inset[p] == 1:
            continue
        sel[i] = p
        cand = _count(cid, sel, n, mark, stamp); stamp += 1
        if cand < 2:                       # all collinear or all concyclic
            sel[i] = old
            continue
        d = cand - cur
        if d <= 0 or np.random.random() < np.exp(-d / T):
            inset[old] = 0
            inset[p] = 1
            cur = cand
            if cur < best:
                best = cur
                for t in range(n):
                    best_sel[t] = sel[t]
        else:
            sel[i] = old
    return best


def run(n, w, h, restarts, iters, seed0, tag=''):
    P = build_grid(w, h)
    cid, ncirc = precompute(P)
    N = len(P)
    mark = np.zeros(ncirc, np.int64)
    best_sel = np.zeros(n, np.int32)
    overall = 10 ** 9
    overall_pts = None
    t0 = time.time()
    for r in range(restarts):
        b = _anneal(cid, N, n, iters, seed0 + r, mark, best_sel)
        if b < overall:
            overall = b
            overall_pts = [P[i] for i in best_sel]
            print('  restart %d: %d circles  %s' % (r, b, overall_pts), flush=True)
    dt = time.time() - t0
    print('n=%d grid %dx%d: best found = %d circles (%d restarts x %d iters, %.0fs)'
          % (n, w, h, overall, restarts, iters, dt), flush=True)
    rec = {'n': n, 'grid': [w, h], 'best_circles': int(overall), 'points': overall_pts,
           'restarts': restarts, 'iters': iters, 'seed0': seed0,
           'seconds': round(dt, 1), 'method': 'simulated annealing, exact objective',
           'note': 'HEURISTIC: a found configuration is a proven upper bound; finding '
                   'nothing better proves nothing',
           'status': 'COMPLETED'}
    if overall_pts:
        from circles import count_circles, valid
        rec['recheck_circles'] = count_circles(overall_pts)
        rec['recheck_valid'] = valid(overall_pts)
        print('   independent recheck: circles=%d valid=%s'
              % (rec['recheck_circles'], rec['recheck_valid']), flush=True)
    json.dump(rec, open('anneal_n%d_%dx%d%s.json' % (n, w, h, tag), 'w'), indent=1)
    return overall, overall_pts


if __name__ == '__main__':
    n = int(sys.argv[1]); w = int(sys.argv[2]); h = int(sys.argv[3])
    restarts = int(sys.argv[4]); iters = int(sys.argv[5])
    seed0 = int(sys.argv[6]) if len(sys.argv) > 6 else 1
    tag = sys.argv[7] if len(sys.argv) > 7 else ''
    run(n, w, h, restarts, iters, seed0, tag)
