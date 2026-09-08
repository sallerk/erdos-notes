"""delta(n) by pattern enumeration, which is the right instrument for this objective.

WHY THE FIRST ATTEMPT FAILED, recorded because it is the interesting part.
search.py minimised delta over raw coordinates with a penalty on the number of distance
classes.  That number is an INTEGER read off by clustering, so the penalty is a step
function and gives the optimiser no descent direction toward making two distances
coincide.  A generic 4-point set has six distinct distances; to reach k = 2 the
optimiser must land on a measure-zero set, and Nelder-Mead never will.  It returned
"no configuration with k <= 2" for n = 4, where the square alone is a counterexample.

The fix is to put the combinatorics in the enumeration and leave only continuous
quantities to the optimiser: choose which pairs share a distance, then solve.

  * a PATTERN is a colouring of the C(n,2) pairs by k classes, canonical under S_n;
  * for a pattern, the equalities "same class => equal distance" are smooth, so a
    least-squares solve either realises them or does not;
  * a realised pattern has k exact distance values, and delta = d_k / min(d_1, gaps)
    follows with no clustering tolerance anywhere.

Only k < the incumbent delta can improve on it, since delta >= k always.  That caps the
enumeration hard: with Piepmeyer at 4.664, n = 9 needs only k = 4.

Usage: python patterns.py <n> <k> [restarts] [seed]
"""
import sys
import json
import time
from itertools import combinations, permutations

import numpy as np
from scipy.optimize import least_squares

sys.stdout.reconfigure(encoding='utf-8', errors='replace')


def canonical(labels, pairs, pidx, n):
    best = None
    for perm in permutations(range(n)):
        out = []
        for (a, b) in pairs:
            out.append(labels[pidx[tuple(sorted((perm[a], perm[b])))]])
        m = {}
        rg = []
        for c in out:
            if c not in m:
                m[c] = len(m)
            rg.append(m[c])
        rg = tuple(rg)
        if best is None or rg < best:
            best = rg
    return best


def enumerate_patterns(n, k, cap=200000):
    """all k-colourings of the pairs of K_n, canonical under S_n, restricted-growth"""
    pairs = list(combinations(range(n), 2))
    pidx = {p: i for i, p in enumerate(pairs)}
    m = len(pairs)
    seen = set()
    out = []
    lab = [0] * m

    def rec(i, used):
        if len(out) >= cap:
            return
        if i == m:
            if used != k:
                return
            cf = canonical(lab, pairs, pidx, n)
            if cf in seen:
                return
            seen.add(cf)
            out.append(list(lab))
            return
        for c in range(min(used + 1, k)):
            lab[i] = c
            rec(i + 1, used + (1 if c == used else 0))
        lab[i] = 0
    rec(0, 0)
    return pairs, out


def unpack(v, n):
    P = np.zeros((n, 2))
    P[1, 0] = 1.0                                  # gauge: p0 origin, p1 at (1,0)
    P[2:, :] = v.reshape(n - 2, 2)
    return P


def make_res(n, pairs, labels, k):
    byc = {}
    for i, c in enumerate(labels):
        byc.setdefault(c, []).append(i)

    def f(v):
        P = unpack(v, n)
        d = np.array([np.hypot(*(P[a] - P[b])) for a, b in pairs])
        if d.min() < 1e-9:
            return np.full(len(pairs), 1e3)
        out = []
        for c, idx in byc.items():
            mu = float(np.mean(d[idx]))
            for i in idx:
                out.append((d[i] - mu) / mu)       # relative, per class (p831 P10)
        while len(out) < len(pairs):
            out.append(0.0)
        return np.array(out)
    return f, byc


def realise(n, pairs, labels, k, restarts, rng):
    """ALL distinct realisations, not the first one found.

    A pattern's equations can have several solution shapes with different distance
    ratios, and delta depends on the ratios.  Stopping at the first hit would silently
    report whichever the optimiser happened to reach.  Solutions are separated by their
    sorted distance-ratio vector, which is what delta actually depends on.
    """
    f, byc = make_res(n, pairs, labels, k)
    best = np.inf
    sols = {}
    degenerate = [0]
    for _ in range(restarts):
        v0 = rng.uniform(-2.0, 2.0, size=2 * (n - 2))
        try:
            s = least_squares(f, v0, xtol=1e-15, ftol=1e-15, gtol=1e-15, max_nfev=4000)
        except Exception:
            continue
        c = float(np.max(np.abs(s.fun)))
        best = min(best, c)
        if c > 1e-13:
            continue
        P = unpack(s.x, n)
        d = np.array([np.hypot(*(P[a] - P[b])) for a, b in pairs])
        if d.min() < 1e-6 * d.max():
            # A configuration with two points merged is an exact solution of the
            # equations (both merged pairs' classes take value 0), so the solver can
            # converge toward it with a residual that shrinks quadratically in the
            # separation.  Such a limit is not a point set.  It is excluded here on a
            # relative threshold; pexact.py excludes it exactly by saturation and is
            # the authority on the count of shapes.
            degenerate[0] += 1
            continue
        # scale-free signature: the FULL sorted distance multiset, not the sorted class
        # values.  Two shapes can share the class values with different multiplicities
        # (the two 2-distance kites on 4 points both have values 1 : 1.932) and they are
        # different point sets.
        key = tuple(np.round(np.sort(d) / d.min(), 9))
        if key not in sols:
            sols[key] = s.x.copy()
    realise.last_degenerate = degenerate[0]
    return best, sols, byc


def delta_from(P, pairs, byc):
    d = np.array([np.hypot(*(P[a] - P[b])) for a, b in pairs])
    vals = np.sort(np.array([float(np.mean(d[idx])) for idx in byc.values()]))
    if len(vals) < 2:
        return 1.0, vals, 'd_1', 0.0
    gaps = np.diff(vals)
    if gaps.min() <= 0:
        return np.inf, vals, 'merged', 0.0
    cand = np.concatenate([[vals[0]], gaps])
    i = int(np.argmin(cand))
    spread = max(float(d[idx].max() - d[idx].min()) for idx in byc.values())
    return float(vals[-1] / cand[i]), vals, ('d_1' if i == 0 else 'gap_%d' % i), spread


if __name__ == '__main__':
    n = int(sys.argv[1]); k = int(sys.argv[2])
    restarts = int(sys.argv[3]) if len(sys.argv) > 3 else 40
    seed = int(sys.argv[4]) if len(sys.argv) > 4 else 7
    rng = np.random.default_rng(seed)
    t0 = time.time()
    pairs, pats = enumerate_patterns(n, k)
    print('n=%d k=%d : %d canonical patterns (%.0fs)' % (n, k, len(pats), time.time() - t0),
          flush=True)
    res = []
    best = (np.inf, None, None)
    nsol_total = 0
    ndegen = 0
    for i, lab in enumerate(pats):
        c, sols, byc = realise(n, pairs, lab, k, restarts, rng)
        ndegen += realise.last_degenerate
        if not sols:
            res.append(dict(i=i, realised=False, residual=float(c), n_shapes=0))
            continue
        nsol_total += len(sols)
        rows = []
        for key, v in sols.items():
            P = unpack(v, n)
            dl, vals, which, spread = delta_from(P, pairs, byc)
            ok = bool(np.isfinite(dl) and spread < 1e-9)
            rows.append(dict(delta=float(dl), values=[float(x) for x in vals],
                             binding=which, spread=float(spread), ok=ok))
            if ok and dl < best[0]:
                best = (dl, P.copy(), dict(i=i, **rows[-1]))
                print('  new best delta = %.10f  binding %s  values %s'
                      % (dl, which, np.round(vals, 6)), flush=True)
        res.append(dict(i=i, realised=True, residual=float(c),
                        n_shapes=len(sols), shapes=rows))
    nre = sum(1 for r in res if r.get('realised'))
    print('  distinct realisation shapes found across all patterns: %d' % nsol_total)
    print('  converged-to-degenerate solutions discarded: %d' % ndegen)
    json.dump(dict(n=n, k=k, patterns=len(pats), realised=nre, shapes=nsol_total,
                   degenerate_discarded=ndegen,
                   best_delta=(float(best[0]) if np.isfinite(best[0]) else None),
                   best=best[2], points=(best[1].tolist() if best[1] is not None else None),
                   results=res, seconds=round(time.time() - t0, 1), completed=True),
              open('results/patterns_n%d_k%d.json' % (n, k), 'w'), indent=1)
    print()
    print('%d of %d patterns realised; best delta = %s' %
          (nre, len(pats), ('%.10f' % best[0]) if np.isfinite(best[0]) else 'none'))
