"""Minimise delta over k-distance sets directly, by treating the k values as unknowns.

The exhaustive pattern enumeration is exact but dies at n = 6: there are S(15,3) = 2.4
million three-block partitions of the pairs of K_6 and canonicalising each against 720
permutations is out of reach in Python.  This scales instead.

THE FORMULATION.  Carry the coordinates AND the k distance values v_1 < ... < v_k as
unknowns.  Every pair must sit on one of the values, which is the soft constraint

        sum over pairs of ( d_pair - v_{nearest} )^2  ->  0,

and among configurations that achieve it we want the smallest

        delta = v_k / min(v_1, min_i (v_{i+1} - v_i)).

Assignment to the nearest value is recomputed each outer iteration, so this is Lloyd's
algorithm with a geometric inner solve: the combinatorics is discovered rather than
enumerated, and nothing depends on a clustering tolerance at the end because the values
are variables in their own right.

WHY THIS AVOIDS THE EARLIER TRAP (lesson Q1).  The first attempt penalised the INTEGER
number of distance classes, a step function with no descent direction.  Here the class
count is fixed at k by construction and what moves continuously is how far each distance
is from its assigned value, so there is always a direction to descend.

Controls, fixed before running (L74): at n = 5, k = 2 it must find the regular pentagon
at delta = 2.6180339887, and at n = 9, k = 4 it must reach Piepmeyer's 4.6639024601.
A run that misses either is not allowed to report an absence.

Usage: python fewdist.py <n> <k> [restarts] [seed]
"""
import sys
import json
import time
from itertools import combinations

import numpy as np
from scipy.optimize import least_squares, minimize

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

PAIRS = {}


def pairs_of(n):
    if n not in PAIRS:
        PAIRS[n] = list(combinations(range(n), 2))
    return PAIRS[n]


def unpack(v, n):
    P = np.zeros((n, 2))
    P[1, 0] = 1.0
    P[2:, :] = v[:2 * (n - 2)].reshape(n - 2, 2)
    return P


def dists(P, n):
    return np.array([np.hypot(*(P[a] - P[b])) for a, b in pairs_of(n)])


def delta_of_values(vals):
    v = np.sort(vals)
    if v[0] <= 0:
        return np.inf, None
    gaps = np.diff(v)
    if len(gaps) and gaps.min() <= 0:
        return np.inf, None
    cand = np.concatenate([[v[0]], gaps]) if len(gaps) else np.array([v[0]])
    i = int(np.argmin(cand))
    return float(v[-1] / cand[i]), ('d_1' if i == 0 else 'gap_%d' % i)


def fit_values(P, n, k):
    """Lloyd: assign each distance to the nearest of k centres, then recentre"""
    d = np.sort(dists(P, n))
    # k-means++ style init on a 1-D array: quantiles are enough and deterministic
    v = np.quantile(d, np.linspace(0, 1, k))
    for _ in range(200):
        idx = np.argmin(np.abs(d[:, None] - v[None, :]), axis=1)
        nv = v.copy()
        for j in range(k):
            m = d[idx == j]
            if len(m):
                nv[j] = m.mean()
        if np.allclose(nv, v, rtol=0, atol=1e-15):
            break
        v = nv
    return np.sort(v)


def residual(x, n, k, lam):
    P = unpack(x, n)
    v = np.sort(np.abs(x[2 * (n - 2):]))
    d = dists(P, n)
    if d.min() < 1e-9 or v[0] < 1e-9:
        return np.full(len(d) + 2, 1e3)
    assign = np.argmin(np.abs(d[:, None] - v[None, :]), axis=1)
    fit = (d - v[assign]) / v[assign]                 # relative, per value (p831 P10)
    dl, _ = delta_of_values(v)
    if not np.isfinite(dl):
        return np.full(len(d) + 2, 1e3)
    # every value must actually be used, or this is really a (k-1)-distance set
    unused = k - len(set(assign.tolist()))
    return np.concatenate([lam * fit, [dl * 1e-3, unused * 1.0]])


def polish(x, n, k):
    """drive the fit to machine precision with delta out of the objective"""
    def f(y):
        P = unpack(y, n)
        v = np.sort(np.abs(y[2 * (n - 2):]))
        d = dists(P, n)
        if d.min() < 1e-9 or v[0] < 1e-9:
            return np.full(len(d), 1e3)
        a = np.argmin(np.abs(d[:, None] - v[None, :]), axis=1)
        return (d - v[a]) / v[a]
    s = least_squares(f, x, xtol=1e-15, ftol=1e-15, gtol=1e-15, max_nfev=8000)
    return s.x, float(np.max(np.abs(s.fun)))


def evaluate(x, n, k):
    P = unpack(x, n)
    v = np.sort(np.abs(x[2 * (n - 2):]))
    d = dists(P, n)
    a = np.argmin(np.abs(d[:, None] - v[None, :]), axis=1)
    err = float(np.max(np.abs((d - v[a]) / v[a])))
    used = len(set(a.tolist()))
    dl, which = delta_of_values(v)
    return dict(delta=dl, binding=which, values=v.tolist(), fit_error=err,
                classes_used=used, min_dist=float(d.min()))


def run(n, k, restarts, seed):
    rng = np.random.default_rng(seed)
    best = (np.inf, None, None)
    t0 = time.time()
    for r in range(restarts):
        P0 = rng.uniform(-2, 2, size=(n, 2))
        P0[0] = 0.0
        P0[1] = [1.0, 0.0]
        v0 = fit_values(P0, n, k)
        x = np.concatenate([P0[2:].ravel(), v0])
        for lam in (1.0, 10.0, 100.0):
            try:
                s = least_squares(residual, x, args=(n, k, lam), xtol=1e-14,
                                  ftol=1e-14, gtol=1e-14, max_nfev=4000)
                x = s.x
            except Exception:
                break
        try:
            x, ferr = polish(x, n, k)
        except Exception:
            continue
        e = evaluate(x, n, k)
        if e['fit_error'] > 1e-11 or e['classes_used'] != k:
            continue
        if not np.isfinite(e['delta']):
            continue
        if e['delta'] < best[0] - 1e-12:
            best = (e['delta'], x.copy(), e)
            print('  [%4d] delta = %.10f  binding %s  values %s'
                  % (r, e['delta'], e['binding'],
                     np.round(np.array(e['values']) / e['values'][0], 6)), flush=True)
    return best, time.time() - t0


if __name__ == '__main__':
    n = int(sys.argv[1]); k = int(sys.argv[2])
    restarts = int(sys.argv[3]) if len(sys.argv) > 3 else 400
    seed = int(sys.argv[4]) if len(sys.argv) > 4 else 11
    print('n = %d, k = %d, lower bound delta >= %d' % (n, k, k), flush=True)
    (d, x, e), el = run(n, k, restarts, seed)
    P = unpack(x, n).tolist() if x is not None else None
    json.dump(dict(n=n, k=k, restarts=restarts, seed=seed,
                   best_delta=(float(d) if np.isfinite(d) else None),
                   detail=e, points=P, seconds=round(el, 1), completed=True),
              open('results/fewdist_n%d_k%d.json' % (n, k), 'w'), indent=1)
    print()
    if np.isfinite(d):
        print('  delta(%d) <= %.10f   with k = %d   (%.0fs, %d restarts)'
              % (n, d, k, el, restarts))
        print('  fit error %.2e, min distance %.6f, binding %s'
              % (e['fit_error'], e['min_dist'], e['binding']))
    else:
        print('  no %d-distance set found for n = %d in %d restarts' % (k, n, restarts))
