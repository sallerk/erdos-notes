"""Case A of n = 5, rebuilt after the audit.  Replaces caseA.py and ctrlA.py.

CASE A.  Four of the five points have four equal circumradii, so by Lemma 2 they are an
orthocentric system {A,B,C,H}, and by Lemma 3 that class holds exactly those four
triples.  The other six triples all contain the fifth point P, and for h(5) = 3 they
must fall into exactly TWO radius classes.  Unknowns: the triangle shape (cx, cy) with
A = (0,0), B = (1,0), C = (cx,cy), and P = (px,py).  Four unknowns, four equations.

THREE DEFECTS THIS FILE FIXES.

1. The old objective divided every residual by the mean of all six radii.  With only
   some radii constrained the optimiser inflated that mean by flattening one triangle,
   sending an unconstrained radius to 1e15, and the residual divided away.  Here each
   equation is measured against its OWN two radii, (r_a - r_b)/(|r_a| + |r_b|), which
   nothing else can inflate.

2. The old objective had no concyclicity, distinctness or class-separation guard at all
   - the failure mode this directory's own LESSONS P7 records.  All three are present
   below, and the margins are parameters so their influence can be measured rather than
   assumed (LESSONS P11).

3. The old control dropped equations in the order r0=r1=r2=..., which puts the pair
   {P,A} in three triples of one class.  Lemma 1 forbids that, so every rung of the old
   ladder was asking for a configuration that forces four concyclic points, and its
   failures meant nothing.  The ladder here takes an ADMISSIBLE split and imposes its
   equations one at a time, so every rung is a genuine relaxation of a legal target.

Usage:  python caseA2.py [restarts] [seed]
"""
import sys
import json
from itertools import combinations

import numpy as np
from scipy.optimize import least_squares

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

PAIRS = list(combinations(range(4), 2))          # the six pairs of {A,B,C,H}


def ortho(cx, cy):
    return np.array([cx, cx * (1.0 - cx) / cy])


def config(v):
    cx, cy, px, py = v
    A = np.array([0.0, 0.0])
    B = np.array([1.0, 0.0])
    C = np.array([cx, cy])
    H = ortho(cx, cy)
    P = np.array([px, py])
    return np.array([A, B, C, H, P])


def r2_S(X, Y, Z):
    a2 = np.sum((Y - Z) ** 2)
    b2 = np.sum((Z - X) ** 2)
    c2 = np.sum((X - Y) ** 2)
    S = 2 * (a2 * b2 + b2 * c2 + c2 * a2) - (a2 * a2 + b2 * b2 + c2 * c2)
    return (a2 * b2 * c2 / S if abs(S) > 1e-300 else np.nan), S


def six_radii(v):
    pts = config(v)
    out = []
    for i, j in PAIRS:
        out.append(r2_S(pts[4], pts[i], pts[j])[0])
    return np.array(out), pts


def det4(pts, q):
    return np.linalg.det(np.array(
        [[pts[t, 0] ** 2 + pts[t, 1] ** 2, pts[t, 0], pts[t, 1], 1.0] for t in q]))


def guards(v, mind_tau, conc_tau):
    """returns the penalty vector and the raw margins, so both can be reported"""
    pts = config(v)
    if not np.all(np.isfinite(pts)):
        return None, None
    mind = min(np.linalg.norm(pts[i] - pts[j]) for i, j in combinations(range(5), 2))
    minS = min(abs(r2_S(pts[a], pts[b], pts[c])[1])
               for a, b, c in combinations(range(5), 3))
    scale = float(np.mean(np.abs(pts))) + 1.0
    mindet = min(abs(det4(pts, q)) / scale ** 3 for q in combinations(range(5), 4))
    pen = [0.0 if mind > mind_tau else (mind_tau - mind) * 1e2,
           0.0 if minS > 1e-8 else (1e-8 - minS) * 1e4,
           0.0 if mindet > conc_tau else (conc_tau - mindet) * 1e3,
           0.0 if scale < 40 else (scale - 40) * 1e-2]
    return np.array(pen), dict(min_dist=float(mind), min_16K2=float(minS),
                               min_det4=float(mindet))


def equations(v, eqs):
    """eqs is a list of (a,b) index pairs into the six P-triples"""
    r, _ = six_radii(v)
    if np.any(~np.isfinite(r)) or np.any(r <= 0):
        return None
    return np.array([(r[a] - r[b]) / (abs(r[a]) + abs(r[b])) for a, b in eqs])


def residual(v, eqs, mind_tau, conc_tau, sep_tau, c0, c1):
    e = equations(v, eqs)
    if e is None:
        return np.full(len(eqs) + 5, 1e3)
    g, _ = guards(v, mind_tau, conc_tau)
    if g is None:
        return np.full(len(eqs) + 5, 1e3)
    r, _ = six_radii(v)
    out = list(e) + list(g)
    if c0 is not None and c1 is not None:
        m0 = float(np.mean(r[c0]))
        m1 = float(np.mean(r[c1]))
        s = abs(m0 - m1) / (abs(m0) + abs(m1))
        out.append(0.0 if s > sep_tau else (sep_tau - s) * 1e2)
    else:
        out.append(0.0)
    return np.array(out)


def splits():
    """the (4,2) and (3,3) partitions of the six P-triples that satisfy Lemma 1"""
    out = []
    seen = set()
    for mask in range(1, 1 << 6):
        c0 = [i for i in range(6) if mask >> i & 1]
        c1 = [i for i in range(6) if not mask >> i & 1]
        if not c1:
            continue
        if tuple(sorted([len(c0), len(c1)], reverse=True)) not in ((4, 2), (3, 3)):
            continue
        key = tuple(sorted([tuple(c0), tuple(c1)]))
        if key in seen:
            continue
        seen.add(key)
        bad = False
        for X in range(4):
            idx = [t for t, (i, j) in enumerate(PAIRS) if i == X or j == X]
            for cl in (c0, c1):
                if len([t for t in idx if t in cl]) > 2:
                    bad = True
        if not bad:
            out.append((c0, c1))
    return out


def eqs_of(c0, c1):
    return [(cl[0], t) for cl in (c0, c1) for t in cl[1:]]


def solve(eqs, restarts, rng, mind_tau, conc_tau, sep_tau, c0=None, c1=None):
    best = (np.inf, None)
    for _ in range(restarts):
        v0 = np.array([rng.uniform(-1.5, 2.5), rng.uniform(0.15, 2.5),
                       rng.uniform(-3, 4), rng.uniform(-3, 4)])
        try:
            s = least_squares(residual, v0,
                              args=(eqs, mind_tau, conc_tau, sep_tau, c0, c1),
                              xtol=1e-15, ftol=1e-15, gtol=1e-15, max_nfev=4000)
        except Exception:
            continue
        e = equations(s.x, eqs)
        if e is None:
            continue
        c = float(np.max(np.abs(e)))          # judge on the EQUATIONS, not the penalties
        g, m = guards(s.x, mind_tau, conc_tau)
        if m['min_dist'] < mind_tau * 0.99 or m['min_det4'] < conc_tau * 0.99:
            continue                           # guard violated: not an admissible point
        if c < best[0]:
            best = (c, s.x.copy())
    return best


if __name__ == '__main__':
    restarts = int(sys.argv[1]) if len(sys.argv) > 1 else 400
    seed = int(sys.argv[2]) if len(sys.argv) > 2 else 20260907
    MIND, CONC, SEP = 1e-2, 1e-4, 1e-3
    rng = np.random.default_rng(seed)
    S = splits()
    print('%d admissible splits (Lemma 1 respected)' % len(S))

    print()
    print('CONTROL LADDER.  Equations are taken from an admissible split and imposed one')
    print('at a time, so every rung is a relaxation of a legal target.  4 unknowns.')
    print()
    print('  split                 1 eq       2 eq       3 eq       4 eq')
    ladder = []
    for c0, c1 in S[:4]:
        eqs = eqs_of(c0, c1)
        # A k-equation system is a relaxation of a (k+1)-equation one, so its floor can
        # never be worse.  Solving each rung with independent random restarts broke that:
        # rung 4 came back better than rung 3 and the reported reach was restart noise.
        # Every point found at any rung is now evaluated at every shorter prefix too.
        pts = []
        row = []
        for k in range(1, len(eqs) + 1):
            c, v = solve(eqs[:k], restarts, rng, MIND, CONC, SEP)
            if v is not None:
                pts.append(v)
            row.append(c)
        for k in range(1, len(eqs) + 1):
            for v in pts:
                e = equations(v, eqs[:k])
                if e is None:
                    continue
                g, m = guards(v, MIND, CONC)
                if m['min_dist'] < MIND * 0.99 or m['min_det4'] < CONC * 0.99:
                    continue
                row[k - 1] = min(row[k - 1], float(np.max(np.abs(e))))
        assert all(row[i] <= row[i + 1] * 1.0000001 + 1e-18
                   for i in range(len(row) - 1)), 'ladder still not monotone: %s' % row
        ladder.append(dict(split=[c0, c1], floors=[float(x) for x in row]))
        print('  %-20s' % (str(c0) + '|' + str(c1))
              + ''.join('  %.2e' % x for x in row))
    solved = [i + 1 for i in range(4)
              if all(r['floors'][i] < 1e-12 for r in ladder if len(r['floors']) > i)]
    top = max(solved) if solved else 0
    print()
    print('  every split solves its first %d equation(s) to machine precision.' % top)

    print()
    print('THE SEARCH.  All %d splits, 4 equations each.' % len(S))
    res = []
    for c0, c1 in S:
        eqs = eqs_of(c0, c1)
        c, v = solve(eqs, restarts, rng, MIND, CONC, SEP, c0, c1)
        m = guards(v, MIND, CONC)[1] if v is not None else None
        res.append(dict(split=[c0, c1], best=float(c),
                        v=(list(map(float, v)) if v is not None else None), margins=m))
        print('  %-20s best equation residual %.3e%s'
              % (str(c0) + '|' + str(c1), c,
                 '   ADMISSIBLE SOLUTION' if c < 1e-12 else ''))
    hits = [r for r in res if r['best'] < 1e-12]
    json.dump(dict(restarts=restarts, seed=seed,
                   margins=dict(min_dist=MIND, concyclic=CONC, separation=SEP),
                   ladder=ladder, ladder_top=top, results=res, hits=len(hits),
                   completed=True), open('results/caseA2.json', 'w'), indent=1)
    print()
    print('%d admissible solutions found.' % len(hits))
    if top >= 4:
        print('The ladder reaches 4 equations, so the failure at 4 is meaningful.')
    else:
        print('The ladder reaches only %d equations; a failure at 4 is correspondingly'
              % top)
        print('weaker evidence, and is reported as such.')
