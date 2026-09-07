"""n=5, Case A: four of the five points form an ORTHOCENTRIC system.

Two lemmas, both proved in NOTE.md, set this case up:

  L3. If four points have four equal circumradii they are an orthocentric system
      {A,B,C,H}, H the orthocentre; and then every pair of them already uses BOTH
      circles of that radius through it, so no fifth point can make a triple of that
      same radius with any two of them.
  So the radius class of the orthocentric quadruple has size exactly 4, and the other
  six triples - all of which contain the fifth point P - must supply the remaining
  classes.  For h = 3 those six must take exactly TWO distinct circumradii.

Unknowns: the triangle shape (cx, cy) with A=(0,0), B=(1,0), C=(cx,cy), and P=(px,py).
Four unknowns.  Requiring the six values R(P,X,Y) to collapse onto two values is four
equations, so solutions can exist; this searches for them.

IMPORTANT, after the audit of 2026-09-07. This objective has NO concyclicity,
distinctness or class-separation penalty, which is exactly the failure mode LESSONS P7
records. Its output is therefore not evidence; the Case A conclusion now rests on an
independent search by the mathematical auditor, who redid it with those penalties on a
200x200 angle grid crossed with a 241x241 point grid plus 4000 restarts per split and
found 0 admissible roots in all nine splits. Kept here for the record, not as support.
An earlier docstring named a verifyA.py that was never written.

Usage: python caseA.py [restarts] [seed]
"""
import sys, json, os, time
import numpy as np
from itertools import combinations
from scipy.optimize import least_squares

sys.stdout.reconfigure(encoding='utf-8', errors='replace')
rng = None


def ortho(cx, cy):
    """orthocentre of A=(0,0), B=(1,0), C=(cx,cy)"""
    # altitude from C is x = cx ; altitude from A has direction perp to BC
    # H = (cx, cx*(1-cx)/cy)
    return np.array([cx, cx*(1.0-cx)/cy])


def circumr2(P, Q, R):
    a2 = np.sum((Q-R)**2); b2 = np.sum((R-P)**2); c2 = np.sum((P-Q)**2)
    S = 2*(a2*b2 + b2*c2 + c2*a2) - (a2*a2 + b2*b2 + c2*c2)
    if abs(S) < 1e-14:
        return np.nan
    return a2*b2*c2/S


PAIRS = list(combinations(range(4), 2))          # pairs of {A,B,C,H}


def six_radii(v):
    cx, cy, px, py = v
    A = np.array([0.0, 0.0]); B = np.array([1.0, 0.0]); C = np.array([cx, cy])
    H = ortho(cx, cy); P = np.array([px, py])
    pts = [A, B, C, H]
    return np.array([circumr2(P, pts[i], pts[j]) for i, j in PAIRS]), pts, P


def splits():
    """partitions of the six P-triples into two classes, sizes (4,2) or (3,3),
    with no vertex-pair {P,X} having all three of its triples in one class."""
    out = []
    seen = set()
    for mask in range(1, 1 << 6):
        c0 = [i for i in range(6) if mask >> i & 1]
        c1 = [i for i in range(6) if not mask >> i & 1]
        if not c1:
            continue
        sizes = tuple(sorted([len(c0), len(c1)], reverse=True))
        if sizes not in ((4, 2), (3, 3)):
            continue
        key = tuple(sorted([tuple(c0), tuple(c1)]))
        if key in seen:
            continue
        seen.add(key)
        # Lemma 1 on the pairs {P,X}: triples containing vertex X
        bad = False
        for X in range(4):
            idx = [t for t, (i, j) in enumerate(PAIRS) if i == X or j == X]
            for cl in (c0, c1):
                if len([t for t in idx if t in cl]) > 2:
                    bad = True
        if bad:
            continue
        out.append((c0, c1))
    return out


def residual(v, c0, c1):
    """RELATIVE residuals.  Absolute differences of R^2 are meaningless when the
    configuration is allowed to spread out: a difference of 1e-7 between radii of
    size 1e6 is not a near-solution.  Also penalise degeneracy so the optimiser
    cannot buy a small residual by sending the configuration to infinity or by
    flattening the triangle."""
    r, pts, P = six_radii(v)
    if np.any(~np.isfinite(r)) or np.any(r <= 0):
        return np.full(6, 1e3)
    scale = float(np.mean(r))
    res = []
    for cl in (c0, c1):
        for t in cl[1:]:
            res.append((r[t] - r[cl[0]]) / scale)
    while len(res) < 4:
        res.append(0.0)
    cx, cy, px, py = v
    res.append(0.0 if abs(cy) > 0.05 else (0.05 - abs(cy)) * 20)      # non-degenerate triangle
    big = max(abs(cx), abs(cy), abs(px), abs(py))
    res.append(0.0 if big < 40 else (big - 40) * 0.01)                # bounded
    return np.array(res)


def run(restarts, seed):
    global rng
    rng = np.random.default_rng(seed)
    S = splits()
    print('%d admissible splits of the six P-triples' % len(S))
    hits = []
    t0 = time.time()
    for si, (c0, c1) in enumerate(S):
        best = None
        for k in range(restarts):
            v0 = np.array([rng.uniform(-1, 2), rng.uniform(0.2, 2.0),
                           rng.uniform(-2, 3), rng.uniform(-2, 3)])
            try:
                sol = least_squares(residual, v0, args=(c0, c1), xtol=1e-15,
                                    ftol=1e-15, gtol=1e-15, max_nfev=4000)
            except Exception:
                continue
            cost = float(np.max(np.abs(sol.fun)))
            if best is None or cost < best[0]:
                best = (cost, sol.x.copy())
        cost, v = best
        r, pts, P = six_radii(v)
        # the two class radii must be DIFFERENT from each other and from the
        # orthocentric radius, and everything must stay non-degenerate (L73)
        ok = np.all(np.isfinite(r))
        info = dict(split=[c0, c1], maxres=cost, v=list(map(float, v)),
                    radii=[float(x) for x in r] if ok else None)
        if ok and cost < 1e-9:
            r0 = float(np.mean(r[c0])); r1 = float(np.mean(r[c1]))
            rort = circumr2(pts[0], pts[1], pts[2])
            info['r_classes'] = [r0, r1, float(rort)]
            info['distinct'] = (abs(r0-r1) > 1e-6 and abs(r0-rort) > 1e-6
                                and abs(r1-rort) > 1e-6)
            hits.append(info)
            print('  HIT split=%s res=%.2e radii=%.6f %.6f orth=%.6f distinct=%s'
                  % (c0, cost, r0, r1, rort, info['distinct']), flush=True)
        else:
            print('  [%2d/%2d] split=%-14s best residual %.3e' % (si+1, len(S), c0, cost),
                  flush=True)
    os.makedirs('results', exist_ok=True)
    json.dump(dict(restarts=restarts, seed=seed, nsplits=len(S), hits=hits,
                   seconds=round(time.time()-t0, 1), completed=True),
              open('results/caseA_n5.json', 'w'), indent=1)
    print('%d hits, %.1fs' % (len(hits), time.time()-t0))


if __name__ == '__main__':
    run(int(sys.argv[1]) if len(sys.argv) > 1 else 200,
        int(sys.argv[2]) if len(sys.argv) > 2 else 12345)
