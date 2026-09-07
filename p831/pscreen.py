"""Numerical screen of radius patterns, with a positive control (L74).

For a pattern (an assignment of each triple to a radius class) this asks whether some
configuration realises it, by least squares on

    residual(T) = ( R^2(T) - mean of R^2 over T's class ) / scale        for every T

with RELATIVE residuals (absolute ones are meaningless: a configuration can shrink a
difference by spreading out) plus penalties that stop the optimiser buying a small
residual with a degenerate configuration - a flat triangle, four concyclic points, two
classes whose radii have merged, or points running off to infinity (L73).

A small residual here is only a LEAD.  Certification is exact and lives in verify.py.
A large residual is only a failed search; it becomes evidence only against the control,
which screens a pattern KNOWN to be realisable and must come out at machine precision.

Usage: python pscreen.py <n> <k> [restarts] [seed]
"""
import sys, json, os, time
import numpy as np
from itertools import combinations
from scipy.optimize import least_squares

sys.stdout.reconfigure(encoding='utf-8', errors='replace')


def unpack(v, n):
    P = np.zeros((n, 2))
    P[1, 0] = 1.0
    P[2:, :] = v.reshape(n-2, 2)
    return P


def quantities(P, tri):
    r2 = np.empty(len(tri)); S = np.empty(len(tri))
    for i, (a, b, c) in enumerate(tri):
        A, B, C = P[a], P[b], P[c]
        a2 = np.sum((B-C)**2); b2 = np.sum((C-A)**2); c2 = np.sum((A-B)**2)
        s = 2*(a2*b2 + b2*c2 + c2*a2) - (a2*a2 + b2*b2 + c2*c2)
        S[i] = s
        r2[i] = a2*b2*c2/s if s > 1e-300 else np.nan
    return r2, S


def det4(P, q):
    M = np.array([[P[v, 0]**2 + P[v, 1]**2, P[v, 0], P[v, 1], 1.0] for v in q])
    return np.linalg.det(M)


def make_residual(n, labels, k, tri, quads, tau=1e-6, mind_tau=1e-2):
    """tau is the degeneracy margin.  It is a PARAMETER, not a constant, because the
    audit showed that for some patterns the optimum sits exactly on it, so the reported
    residual measures tau rather than the geometry; see tausweep.py, which fits the
    floor against tau and reads the slope.  mind_tau excludes coincident points, a guard
    the first version lacked entirely."""
    nres = len(tri) + 4 + len(quads)

    def f(v):
        P = unpack(v, n)
        r2, S = quantities(P, tri)
        if np.any(~np.isfinite(r2)) or np.any(r2 <= 0):
            return np.full(nres, 1e3)
        scale = float(np.mean(r2))
        out = []
        means = {}
        for c in range(k):
            idx = [i for i in range(len(tri)) if labels[i] == c]
            means[c] = float(np.mean(r2[idx]))
        for i in range(len(tri)):
            out.append((r2[i] - means[labels[i]]) / scale)
        # penalties -- all zero on a genuinely admissible configuration
        span = float(np.max(np.abs(P)))
        out.append(0.0 if span < 60 else (span - 60) * 1e-2)
        flat = float(np.min(S)) / (scale**2 + 1e-30)
        out.append(0.0 if flat > tau else (tau - flat) * 1e3)
        mind = min(float(np.linalg.norm(P[i]-P[j]))
                   for i, j in combinations(range(n), 2))
        out.append(0.0 if mind > mind_tau else (mind_tau - mind) * 1e2)
        sep = min(abs(means[a] - means[b]) for a in range(k) for b in range(a+1, k)) / scale
        out.append(0.0 if sep > 1e-3 else (1e-3 - sep) * 1e2)
        for q in quads:
            d = abs(det4(P, q)) / (scale**1.5 + 1e-30)
            out.append(0.0 if d > tau else (tau - d) * 1e3)
        return np.array(out)
    return f


def screen(n, k, labels, restarts, rng, tau=1e-6, mind_tau=1e-2, box=8.0):
    tri = list(combinations(range(n), 3))
    quads = list(combinations(range(n), 4))
    f = make_residual(n, labels, k, tri, quads, tau, mind_tau)
    best = (1e9, None)
    for _ in range(restarts):
        # the audit noted the old box, uniform(-2.0, 2.5), was 2.8e-9 of the volume the
        # span penalty permits, and that one recorded optimum lay outside it
        v0 = rng.uniform(-box, box, size=2*(n-2))
        try:
            s = least_squares(f, v0, xtol=1e-15, ftol=1e-15, gtol=1e-15, max_nfev=3000)
        except Exception:
            continue
        c = float(np.max(np.abs(s.fun)))
        if c < best[0]:
            best = (c, s.x.copy())
        if c < 1e-13:
            break
    return best


def control(n, rng, restarts):
    """the 11x11 lattice witness at n=5: an admissible configuration whose pattern is
    therefore realisable by construction.  The screen MUST find it."""
    if n != 5:
        return None
    W = np.array([[0, 0], [0, 7], [2, 6], [4, 3], [6, 9]], dtype=float)
    tri = list(combinations(range(5), 3))
    r2, S = quantities(W, tri)
    vals = sorted(set(np.round(r2, 9)))
    lab = [vals.index(round(x, 9)) for x in r2]
    kk = len(vals)
    c, v = screen(5, kk, lab, restarts, rng)
    return dict(k=kk, labels=lab, residual=c, passed=bool(c < 1e-12))


if __name__ == '__main__':
    n = int(sys.argv[1]); k = int(sys.argv[2])
    restarts = int(sys.argv[3]) if len(sys.argv) > 3 else 120
    seed = int(sys.argv[4]) if len(sys.argv) > 4 else 99
    rng = np.random.default_rng(seed)
    ctl = control(n, rng, restarts)
    if ctl is not None:
        print('CONTROL (known-realisable %d-class pattern): residual %.3e -> %s'
              % (ctl['k'], ctl['residual'], 'PASS' if ctl['passed'] else 'FAIL'), flush=True)
        if not ctl['passed']:
            print('control failed; a negative from this screen would be worthless (L74)')
            sys.exit(1)
    pats = json.load(open('results/penum_n%d_k%d.json' % (n, k)))['patterns']
    res = []
    t0 = time.time()
    for i, p in enumerate(pats):
        c, v = screen(n, k, p['labels'], restarts, rng)
        res.append(dict(i=i, sizes=p['sizes'], f104_ok=p['f104_ok'], residual=c,
                        v=(list(map(float, v)) if v is not None else None),
                        lead=bool(c < 1e-12)))
        json.dump(dict(n=n, k=k, restarts=restarts, seed=seed, control=ctl,
                       results=res, elapsed_s=round(time.time()-t0, 1)),
                  open('results/pscreen_n%d_k%d.json' % (n, k), 'w'), indent=1)
        print('  [%3d/%3d] sizes=%-12s f104=%-5s residual %.3e %s'
              % (i+1, len(pats), p['sizes'], p['f104_ok'], c, 'LEAD' if c < 1e-12 else ''),
              flush=True)
    leads = [r for r in res if r['lead']]
    print('%d leads out of %d patterns, %.0fs' % (len(leads), len(pats), time.time()-t0))
