"""Does a pattern's residual floor measure GEOMETRY, or pscreen's own constant?

The code audit found that the two smallest residuals in the n=5 screen sit exactly on
the hard-coded concyclicity margin tau = 1e-6 inside pscreen's objective.  A residual
that tracks tau is not evidence of unrealisability: it says the pattern is realisable
arbitrarily close to a four-concyclic configuration, and that pscreen stopped where its
own penalty told it to.

This sweeps tau over four decades and classifies every surviving pattern:

  TRACKS-TAU     : floor falls with tau (slope near 1 in log-log).  Approaching four
                   concyclic points is what buys the equalities.
  FLAT-IN-TAU    : floor does not move with tau.  This does NOT mean the equalities
                   are obstructed.  An earlier version of this file drew that
                   conclusion and it was wrong: a second audit showed the
                   class-separation guard, which this sweep holds FIXED, is active at
                   14 of the 15 optima, so a floor that is flat in tau is simply
                   measuring a different constant.

  READ NEITHER LABEL AS AN OBSTRUCTION.  The decisive test is r2check.py, which drops
  every guard and finds the exact roots directly: all of them, for all fifteen
  patterns, are four-concyclic.  That is the real result; this sweep is retained only
  as a record of how the floor moves with one particular margin.
"""
import sys
import json
from itertools import combinations

import numpy as np
from scipy.optimize import least_squares

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

TRI = list(combinations(range(5), 3))
QUADS = list(combinations(range(5), 4))


def unpack(v, n=5):
    P = np.zeros((n, 2))
    P[1, 0] = 1.0
    P[2:, :] = v.reshape(n - 2, 2)
    return P


def quantities(P):
    r2 = np.empty(len(TRI))
    S = np.empty(len(TRI))
    for i, (a, b, c) in enumerate(TRI):
        A, B, C = P[a], P[b], P[c]
        a2 = np.sum((B - C) ** 2)
        b2 = np.sum((C - A) ** 2)
        c2 = np.sum((A - B) ** 2)
        s = 2 * (a2 * b2 + b2 * c2 + c2 * a2) - (a2 * a2 + b2 * b2 + c2 * c2)
        S[i] = s
        r2[i] = a2 * b2 * c2 / s if s > 1e-300 else np.nan
    return r2, S


def det4(P, q):
    return np.linalg.det(np.array(
        [[P[v, 0] ** 2 + P[v, 1] ** 2, P[v, 0], P[v, 1], 1.0] for v in q]))


def make_res(labels, k, tau):
    def f(v):
        P = unpack(v)
        r2, S = quantities(P)
        if np.any(~np.isfinite(r2)) or np.any(r2 <= 0):
            return np.full(len(TRI) + 3 + len(QUADS), 1e3)
        scale = float(np.mean(r2))
        means = {c: float(np.mean([r2[i] for i in range(10) if labels[i] == c]))
                 for c in range(k)}
        out = [(r2[i] - means[labels[i]]) / scale for i in range(10)]
        span = float(np.max(np.abs(P)))
        out.append(0.0 if span < 60 else (span - 60) * 1e-2)
        flat = float(np.min(S)) / (scale ** 2 + 1e-30)
        out.append(0.0 if flat > tau else (tau - flat) * 1e3)
        sep = min(abs(means[a] - means[b]) for a in range(k)
                  for b in range(a + 1, k)) / scale
        out.append(0.0 if sep > 1e-3 else (1e-3 - sep) * 1e2)
        for q in QUADS:
            d = abs(det4(P, q)) / (scale ** 1.5 + 1e-30)
            out.append(0.0 if d > tau else (tau - d) * 1e3)
        return np.array(out)
    return f


def eq_only(v, labels, k):
    """the EQUALITY residual alone, with no penalties, and the degeneracy margin"""
    P = unpack(v)
    r2, S = quantities(P)
    if np.any(~np.isfinite(r2)) or np.any(r2 <= 0):
        return np.inf, 0.0
    scale = float(np.mean(r2))
    means = {c: float(np.mean([r2[i] for i in range(10) if labels[i] == c]))
             for c in range(k)}
    eq = max(abs(r2[i] - means[labels[i]]) / scale for i in range(10))
    dd = min(abs(det4(P, q)) / (scale ** 1.5) for q in QUADS)
    return eq, dd


def floor_at(labels, k, tau, restarts, rng):
    f = make_res(labels, k, tau)
    best = (np.inf, None)
    for _ in range(restarts):
        v0 = rng.uniform(-2.0, 2.5, size=6)
        try:
            s = least_squares(f, v0, xtol=1e-15, ftol=1e-15, gtol=1e-15, max_nfev=3000)
        except Exception:
            continue
        c = float(np.max(np.abs(s.fun)))
        if c < best[0]:
            best = (c, s.x.copy())
    return best


if __name__ == '__main__':
    restarts = int(sys.argv[1]) if len(sys.argv) > 1 else 60
    pats = json.load(open('results/penum_n5_k3.json'))['patterns']
    taus = [1e-4, 1e-5, 1e-6, 1e-7, 1e-8]
    rng = np.random.default_rng(31337)
    out = []
    print('tau sweep, %d restarts per (pattern, tau)' % restarts)
    print('pattern sizes        ' + ''.join('  tau=%-9.0e' % t for t in taus) + '   verdict')
    for i, p in enumerate(pats):
        row = []
        for t in taus:
            c, v = floor_at(p['labels'], 3, t, restarts, rng)
            eq, dd = eq_only(v, p['labels'], 3) if v is not None else (np.inf, 0)
            row.append((c, eq, dd))
        fl = [r[0] for r in row]
        # slope of log(floor) against log(tau) across the four decades
        lt = np.log10(taus)
        lf = np.log10(np.maximum(fl, 1e-300))
        slope = float(np.polyfit(lt, lf, 1)[0])
        verdict = 'TRACKS-TAU' if slope > 0.5 else 'FLAT-IN-TAU'
        print('  %2d %-12s' % (i, p['sizes']) + ''.join('  %.3e' % c for c in fl)
              + '   slope %.2f  %s' % (slope, verdict))
        out.append(dict(i=i, sizes=p['sizes'], taus=taus,
                        floors=[float(x) for x in fl],
                        eq=[float(r[1]) for r in row],
                        det=[float(r[2]) for r in row],
                        slope=slope, verdict=verdict))
        json.dump(dict(restarts=restarts, results=out, completed=(i == len(pats) - 1)),
                  open('results/tausweep_n5_k3.json', 'w'), indent=1)
    deg = [o for o in out if o['verdict'] == 'TRACKS-TAU']
    print()
    print('%d of %d floors track tau; %d are flat in tau.' % (len(deg), len(out), len(out) - len(deg)))
    print('FLAT-IN-TAU IS NOT AN OBSTRUCTION: the class-separation guard is active at')
    print('almost every optimum here and this sweep does not vary it.  For the actual')
    print('result - every exact root of every pattern is four-concyclic - run r2check.py.')
