"""Minimise delta(X) = d_k / min(d_1, min gap) over n-point planar configurations.

WHY A PLAIN OPTIMISER IS SAFE HERE, AND WHERE IT IS NOT.
delta is scale free by construction, so the failure recorded as p831 lesson P2 - an
absolute residual that the optimiser shrinks by rescaling the configuration - cannot
happen.  What CAN happen is the objective being lowered by degeneracies that change the
combinatorics rather than the geometry:

  * two distance values merging, which lowers k and is a DIFFERENT configuration type;
  * points colliding, which is not an n-point set at all.

Both are excluded explicitly, and, following p831 P11 and P15, the margins are
parameters and the run reports WHICH constraint is active at the optimum, so a floor
sitting on a guard is visible instead of being quoted as a result.

THE REDUCTION THAT MAKES n = 9 SPECIAL.  delta(X) >= k always.  Piepmeyer gives
delta(9) <= 4.6639, so any 9-point set with k >= 5 distances already has delta >= 5 and
cannot beat him.  delta(9) is therefore decided entirely by the 9-point 4-distance sets,
and 9 is the maximum size of a 4-distance set.  The same argument caps the search at
every n: only k < delta_best can improve on the incumbent.

Usage: python search.py <n> [restarts] [seed]
"""
import sys
import json
import time
from itertools import combinations

import numpy as np
from scipy.optimize import minimize

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

GMAX = {1: 3, 2: 5, 3: 7, 4: 9, 5: 12, 6: 13}


def k_min(n):
    for k in sorted(GMAX):
        if GMAX[k] >= n:
            return k
    return None


def unpack(v, n):
    P = np.zeros((n, 2))
    P[1, 0] = abs(v[0]) + 1e-9          # p0 at origin, p1 on the +x axis
    P[2:, :] = v[1:].reshape(n - 2, 2)
    return P


def dists(P):
    n = len(P)
    return np.array([np.hypot(*(P[i] - P[j])) for i, j in combinations(range(n), 2)])


def cluster(ds, tol):
    """group distances into classes at relative tolerance tol; returns sorted class means"""
    s = np.sort(ds)
    out = [[s[0]]]
    for x in s[1:]:
        if x - out[-1][-1] <= tol * max(1.0, x):
            out[-1].append(x)
        else:
            out.append([x])
    return np.array([np.mean(c) for c in out])


def delta_of(P, tol):
    """delta and the pieces; None when the configuration is degenerate"""
    ds = dists(P)
    if ds.min() <= 0:
        return None
    vals = cluster(ds, tol)
    k = len(vals)
    if k < 2:
        return dict(delta=1.0, k=1, vals=vals, g=vals[0], which='d_1',
                    spread=0.0, mind=float(ds.min()))
    gaps = np.diff(vals)
    cand = np.concatenate([[vals[0]], gaps])
    i = int(np.argmin(cand))
    g = float(cand[i])
    # how tightly each class is actually clustered: if a class is wide, the "k" is a lie
    spread = 0.0
    for v in vals:
        mem = ds[np.abs(ds - v) <= tol * max(1.0, v)]
        if len(mem):
            spread = max(spread, float(mem.max() - mem.min()))
    return dict(delta=float(vals[-1] / g), k=k, vals=vals, g=g,
                which=('d_1' if i == 0 else 'gap_%d' % i),
                spread=spread, mind=float(ds.min()))


def objective(v, n, tol, kcap, mind_tau):
    P = unpack(v, n)
    r = delta_of(P, tol)
    if r is None:
        return 1e6
    pen = 0.0
    if r['k'] > kcap:                      # more classes than we are searching for
        pen += 50.0 * (r['k'] - kcap)
    if r['mind'] < mind_tau * r['g']:      # points colliding relative to the scale
        pen += 50.0 * (mind_tau * r['g'] - r['mind']) / max(r['g'], 1e-12)
    span = float(np.max(np.abs(P)))
    if span > 50:
        pen += 0.01 * (span - 50)
    return r['delta'] + pen


def run(n, restarts, seed, tol=1e-7, mind_tau=1e-3):
    rng = np.random.default_rng(seed)
    kc = k_min(n)
    best = (np.inf, None, None)
    t0 = time.time()
    hist = []
    for kcap in range(kc, kc + 3):
        for _ in range(restarts):
            v0 = np.concatenate([[rng.uniform(0.5, 2.0)],
                                 rng.uniform(-3, 3, size=2 * (n - 2))])
            try:
                s = minimize(objective, v0, args=(n, tol, kcap, mind_tau),
                             method='Nelder-Mead',
                             options=dict(maxiter=20000, maxfev=20000,
                                          xatol=1e-12, fatol=1e-14))
            except Exception:
                continue
            P = unpack(s.x, n)
            r = delta_of(P, tol)
            if r is None or r['k'] > kcap:
                continue
            if r['delta'] < best[0]:
                best = (r['delta'], P.copy(), r)
        hist.append(dict(kcap=kcap, best=float(best[0])))
        print('  k <= %d : best delta so far %.9f  (%.0fs)'
              % (kcap, best[0], time.time() - t0), flush=True)
    return best, hist


if __name__ == '__main__':
    n = int(sys.argv[1])
    restarts = int(sys.argv[2]) if len(sys.argv) > 2 else 200
    seed = int(sys.argv[3]) if len(sys.argv) > 3 else 1
    print('n = %d, lower bound from k_min = %s' % (n, k_min(n)))
    (d, P, r), hist = run(n, restarts, seed)
    out = dict(n=n, restarts=restarts, seed=seed, lower_bound=k_min(n),
               best_delta=float(d), k=int(r['k']) if r else None,
               binding=r['which'] if r else None,
               class_spread=float(r['spread']) if r else None,
               values=[float(x) for x in r['vals']] if r else None,
               points=P.tolist() if P is not None else None,
               history=hist, completed=True)
    json.dump(out, open('results/search_n%d.json' % n, 'w'), indent=1)
    print()
    print('  delta(%d) <= %.9f   with k = %s distinct distances' % (n, d, r['k'] if r else '?'))
    if r:
        print('  binding constraint: %s' % r['which'])
        print('  widest class spread: %.2e  (must be tiny or k is not what it says)' % r['spread'])
        print('  values: %s' % np.round(r['vals'], 9))
