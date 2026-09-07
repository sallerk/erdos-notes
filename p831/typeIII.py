"""n=5, the size-4 class whose four circles share a common point (class type III).

Setup.  Suppose the triples 012, 013, 024, 034 all have circumradius r.  All four
circumcircles pass through point 0.  Put 0 at the origin and r = 1.  The centre of
each circle is then a unit vector o_j, and two unit circles through the origin with
centres o_i, o_j meet again at exactly

        o_i + o_j

(the triangle 0-o_i-o_j is isosceles, so the foot of the perpendicular from 0 to the
line o_i o_j is the midpoint of that segment, and the reflection of 0 is the sum).

Reading off which pair of circles produces which point:

        P0 = 0,  P1 = o1+o2,  P2 = o1+o3,  P3 = o2+o4,  P4 = o3+o4

so the whole configuration is four angles, and after fixing the rotation only THREE
essential parameters remain.  The other six triples (014, 023, 123, 124, 134, 234)
must collapse onto two radii for h(5) = 3, which is four equations in three unknowns.

This sweeps the three parameters on a grid and polishes every local minimum, which is
a far stronger negative than random restarts in six dimensions.

Usage: python typeIII.py [grid steps] [top k to polish]
"""
import sys, json, os, time
import numpy as np
from itertools import combinations
from scipy.optimize import least_squares

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

CLASS = [(0, 1, 2), (0, 1, 3), (0, 2, 4), (0, 3, 4)]
REST = [t for t in combinations(range(5), 3) if t not in CLASS]


def points(th):
    o = np.stack([np.cos(th), np.sin(th)], axis=1)          # o1..o4
    return np.array([[0.0, 0.0], o[0]+o[1], o[0]+o[2], o[1]+o[3], o[2]+o[3]])


def r2_of(P, t):
    A, B, C = P[t[0]], P[t[1]], P[t[2]]
    a2 = np.sum((B-C)**2); b2 = np.sum((C-A)**2); c2 = np.sum((A-B)**2)
    S = 2*(a2*b2 + b2*c2 + c2*a2) - (a2*a2 + b2*b2 + c2*c2)
    if S <= 1e-13:
        return np.nan, S
    return a2*b2*c2/S, S


def evaluate(th4):
    """returns (points, radii of the 6 remaining triples, min |16K^2|)"""
    th = np.concatenate([[0.0], th4])                        # fix the rotation
    P = points(th)
    rs = []; Ss = []
    for t in REST:
        r, S = r2_of(P, t)
        rs.append(r); Ss.append(S)
    for t in CLASS:                                          # sanity: should all be 1
        r, S = r2_of(P, t)
        Ss.append(S)
    return P, np.array(rs), np.array(Ss)


def splits():
    """partitions of the six remaining triples into two classes, each of size <= 4
    (f(5) = 4), respecting Lemma 1 (no pair in three triples of one class) and
    Lemma 4 (no class holds exactly three of the four triples of a 4-set)."""
    out = []; seen = set()
    quads = list(combinations(range(5), 4))
    for mask in range(1, 1 << 6):
        c0 = [i for i in range(6) if mask >> i & 1]
        c1 = [i for i in range(6) if not mask >> i & 1]
        if not c1 or max(len(c0), len(c1)) > 4:
            continue
        key = tuple(sorted([tuple(c0), tuple(c1)]))
        if key in seen:
            continue
        seen.add(key)
        bad = False
        for cl in (c0, c1):
            ts = [REST[i] for i in cl]
            deg = {}
            for t in ts:
                for p in combinations(t, 2):
                    deg[p] = deg.get(p, 0) + 1
            if any(v > 2 for v in deg.values()):
                bad = True
            for q in quads:
                if sum(1 for t in ts if set(t) <= set(q)) == 3:
                    bad = True
        if not bad:
            out.append((c0, c1))
    return out


def det4(P, q):
    M = np.array([[P[v, 0]**2 + P[v, 1]**2, P[v, 0], P[v, 1], 1.0] for v in q])
    return np.linalg.det(M)


QUADS = list(combinations(range(5), 4))


def resid(th4, c0, c1):
    """WITH the geometric side conditions.  Without the concyclicity penalties the
    optimiser converges instantly onto a configuration in which points 1,2,3,4 lie on
    a common circle: four concyclic points trivially give their four triples a common
    circumradius, so the equalities are satisfied and the configuration is worthless.
    That branch is inadmissible and must be excluded inside the objective (L73)."""
    P, rs, Ss = evaluate(th4)
    if np.any(~np.isfinite(rs)) or np.any(rs <= 0):
        return np.full(6, 1e3)
    sc = float(np.mean(rs))
    out = []
    for cl in (c0, c1):
        for t in cl[1:]:
            out.append((rs[t] - rs[cl[0]]) / sc)
    while len(out) < 4:
        out.append(0.0)
    flat = float(np.min(np.abs(Ss)))
    out.append(0.0 if flat > 1e-8 else (1e-8 - flat) * 1e6)
    m0 = float(np.mean(rs[c0])); m1 = float(np.mean(rs[c1]))
    sep = abs(m0 - m1) / sc
    out.append(0.0 if sep > 1e-4 else (1e-4 - sep) * 1e3)
    # the two new radii must also differ from the class radius, which is 1
    for m in (m0, m1):
        out.append(0.0 if abs(m - 1.0) > 1e-4 else (1e-4 - abs(m - 1.0)) * 1e3)
    # no four concyclic
    for q in QUADS:
        dd = abs(det4(P, q))
        out.append(0.0 if dd > 1e-6 else (1e-6 - dd) * 1e4)
    # points distinct
    mind = min(float(np.linalg.norm(P[i]-P[j])) for i, j in combinations(range(5), 2))
    out.append(0.0 if mind > 1e-3 else (1e-3 - mind) * 1e3)
    return np.array(out)


def run(steps, topk):
    S = splits()
    print('%d admissible splits of the six remaining triples' % len(S), flush=True)
    grid = np.linspace(0.01, 2*np.pi - 0.01, steps)
    rng = np.random.default_rng(4242)
    res = []
    t0 = time.time()
    for si, (c0, c1) in enumerate(S):
        vals = []
        for a in grid:
            for b in grid:
                for c in grid:
                    v = np.array([a, b, c])
                    f = resid(v, c0, c1)
                    vals.append((float(np.max(np.abs(f))), v))
        vals.sort(key=lambda z: z[0])
        cand = [v for _, v in vals[:topk]]
        cand += [rng.uniform(0.05, 6.2, 3) for _ in range(600)]   # the grid alone
        best = 1e9; bv = None                                     # missed a real basin
        for v in cand:
            try:
                s = least_squares(resid, v, args=(c0, c1), xtol=1e-15, ftol=1e-15,
                                  gtol=1e-15, max_nfev=3000)
            except Exception:
                continue
            c = float(np.max(np.abs(s.fun)))
            if c < best:
                best, bv = c, s.x.copy()
        res.append(dict(split=[c0, c1], best=best, theta=list(map(float, bv))))
        print('  [%2d/%2d] classes %-13s %-13s best relative residual %.3e %s'
              % (si+1, len(S), c0, c1, best, 'LEAD' if best < 1e-12 else ''), flush=True)
        json.dump(dict(steps=steps, topk=topk, results=res,
                       elapsed_s=round(time.time()-t0, 1), completed=(si == len(S)-1)),
                  open('results/typeIII_n5.json', 'w'), indent=1)
    leads = [r for r in res if r['best'] < 1e-12]
    print('%d leads, %.0fs' % (len(leads), time.time()-t0))


if __name__ == '__main__':
    run(int(sys.argv[1]) if len(sys.argv) > 1 else 24,
        int(sys.argv[2]) if len(sys.argv) > 2 else 30)
