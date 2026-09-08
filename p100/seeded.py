"""delta(n) from STRUCTURED starts, because random ones almost never land.

Measured first, then fixed (L74 done properly).  With uniform random starts the search
lands a valid k-distance set on well under 1% of restarts: at n = 5, k = 2 it took about
150 restarts to find the regular pentagon once, and the pentagon is the only 2-distance
set on 5 points.  A search with that hit rate cannot report an absence, and at n = 9 it
would not find Piepmeyer at all.

The reason is not a bad solver.  Seeded at Piepmeyer's own coordinates the solver holds
delta = 4.6639024601 to 3e-16 and recovers it from 30 of 30 starts perturbed by sigma =
0.05.  The problem is purely that few-distance sets are thin and highly symmetric, and a
uniform random cloud is nowhere near one.

So seed from structure: regular polygons, polygons with a centre, two concentric
polygons at every rotation offset, triangular- and square-lattice patches, and Piepmeyer's
own shape.  Each seed is then polished by the same solver, so what changes is coverage,
not correctness.

Usage: python seeded.py <n> <k> [perturbations per seed] [seed]
"""
import sys
import json
import time
from itertools import combinations

import numpy as np

sys.stdout.reconfigure(encoding='utf-8', errors='replace')
from fewdist import (unpack, dists, fit_values, polish, evaluate, delta_of_values,
                     pairs_of)


def regular(n, r=1.0, phase=0.0):
    a = 2 * np.pi * np.arange(n) / n + phase
    return np.stack([r * np.cos(a), r * np.sin(a)], axis=1)


def seeds_for(n, rng, extra):
    """structured configurations of exactly n points"""
    out = []
    names = []

    if n >= 3:
        out.append(regular(n)); names.append('regular %d-gon' % n)
    if n >= 4:
        P = np.vstack([regular(n - 1), [[0.0, 0.0]]])
        out.append(P); names.append('regular %d-gon + centre' % (n - 1))
    # two concentric polygons, all splits and a range of radius ratios and offsets
    for a in range(3, n - 2):
        b = n - a
        if b < 3:
            continue
        for ratio in (0.4, 0.55, 0.7, 0.85, 1.0, 1.3, 1.7, 2.2):
            for off in (0.0, np.pi / max(a, 1), np.pi / max(b, 1), 0.5):
                out.append(np.vstack([regular(a), regular(b, ratio, off)]))
                names.append('%d-gon + %d-gon r=%.2f off=%.2f' % (a, b, ratio, off))
    for a in range(3, n - 3):
        b = n - a - 1
        if b < 3:
            continue
        for ratio in (0.5, 0.75, 1.0, 1.5):
            out.append(np.vstack([regular(a), regular(b, ratio, 0.5), [[0.0, 0.0]]]))
            names.append('%d-gon + %d-gon + centre' % (a, b))
    # lattice patches
    tri = [(i + 0.5 * j, (np.sqrt(3) / 2) * j) for i in range(-3, 4) for j in range(-3, 4)]
    sq = [(i, j) for i in range(-3, 4) for j in range(-3, 4)]
    for lat, nm in ((tri, 'triangular'), (sq, 'square')):
        L = np.array(lat)
        L = L[np.argsort(np.hypot(L[:, 0], L[:, 1]))]
        if len(L) >= n:
            out.append(L[:n].astype(float)); names.append('%s lattice, %d nearest' % (nm, n))
    # Piepmeyer's shape, truncated or padded, when it is relevant
    try:
        d = json.load(open('results/piepmeyer.json'))
        P = np.array([[float(c) for c in p] for p in d['points']])
        if n <= 9:
            out.append(P[:n]); names.append('Piepmeyer first %d' % n)
        else:
            pad = rng.uniform(-2, 2, size=(n - 9, 2))
            out.append(np.vstack([P, pad])); names.append('Piepmeyer + %d random' % (n - 9))
    except Exception:
        pass

    # perturbations of every seed
    base = list(zip(out, names))
    for P, nm in base:
        for s in (0.02, 0.08, 0.2):
            for _ in range(extra):
                out.append(P + rng.normal(0, s, P.shape))
                names.append('%s + noise %.2f' % (nm, s))
    return out, names


def gauge(P):
    """put p0 at the origin and p1 at (1,0), which is the solver's frame"""
    P = np.asarray(P, dtype=float) - P[0]
    r = np.hypot(*P[1])
    if r < 1e-12:
        return None
    a = np.arctan2(P[1, 1], P[1, 0])
    R = np.array([[np.cos(-a), -np.sin(-a)], [np.sin(-a), np.cos(-a)]])
    return (P @ R.T) / r


def run(n, k, extra, seed):
    rng = np.random.default_rng(seed)
    S, names = seeds_for(n, rng, extra)
    print('%d structured starts for n = %d' % (len(S), n), flush=True)
    best = (np.inf, None, None, None)
    hits = 0
    t0 = time.time()
    for P0, nm in zip(S, names):
        G = gauge(P0)
        if G is None:
            continue
        try:
            x = np.concatenate([G[2:].ravel(), fit_values(G, n, k)])
            x, _ = polish(x, n, k)
        except Exception:
            continue
        e = evaluate(x, n, k)
        if e['fit_error'] > 1e-11 or e['classes_used'] != k or not np.isfinite(e['delta']):
            continue
        hits += 1
        if e['delta'] < best[0] - 1e-12:
            best = (e['delta'], x.copy(), e, nm)
            print('  delta = %.10f  from %-38s binding %s  ratios %s'
                  % (e['delta'], nm[:38], e['binding'],
                     np.round(np.array(e['values']) / e['values'][0], 6)), flush=True)
    return best, hits, len(S), time.time() - t0


if __name__ == '__main__':
    n = int(sys.argv[1]); k = int(sys.argv[2])
    extra = int(sys.argv[3]) if len(sys.argv) > 3 else 3
    seed = int(sys.argv[4]) if len(sys.argv) > 4 else 17
    print('n = %d, k = %d, delta >= %d' % (n, k, k), flush=True)
    (d, x, e, nm), hits, tot, el = run(n, k, extra, seed)
    P = unpack(x, n).tolist() if x is not None else None
    json.dump(dict(n=n, k=k, seeds=tot, hits=hits, hit_rate=hits / max(tot, 1),
                   best_delta=(float(d) if np.isfinite(d) else None), detail=e,
                   from_seed=nm, points=P, seconds=round(el, 1), completed=True),
              open('results/seeded_n%d_k%d.json' % (n, k), 'w'), indent=1)
    print()
    print('  %d of %d structured starts landed a valid %d-distance set (%.1f%%)'
          % (hits, tot, k, 100.0 * hits / max(tot, 1)))
    if np.isfinite(d):
        print('  delta(%d) <= %.10f  with k = %d, from: %s' % (n, d, k, nm))
    else:
        print('  no %d-distance set found for n = %d' % (k, n))
