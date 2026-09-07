"""VACUOUS - RETAINED ONLY AS A RECORD.  DO NOT CITE THIS RUN.

The audit of 2026-09-07 showed this search cannot succeed and therefore confirms
nothing.  Its own parametrisation forces P1 + P4 = P2 + P3, so the four points are
always a parallelogram, and NOTE.md Lemma 6 proves no parallelogram is orthocentric.
The constraint imposed below is thus unsatisfiable by construction, all 80,000 restarts
were guaranteed to fail, and a version with a bug would have produced an identical
artifact.  The geometric fact is still proved - just not by this file.

The non-degenerate branch of the (4,4,2) pattern at n=5.

Pattern: the type-III class {012,013,024,034} at one radius; the four triples of the
4-set {1,2,3,4} at a second radius; and {014,023} at a third.  By Lemma 2 four equal
circumradii on a 4-set means the 4-set is EITHER concyclic (inadmissible here) OR
orthocentric.  A plain least-squares solve converges onto the concyclic branch every
time, so this searches the orthocentric branch explicitly by imposing
P4 = orthocentre(P1,P2,P3) as an equation rather than hoping to land on it.

Unknowns: the three free angles of the type-III parametrisation.
Equations: P4 = orthocentre(P1,P2,P3)  (two), and R(014) = R(023)  (one).
Three equations, three unknowns.
"""
import sys, json
import numpy as np
from itertools import combinations, permutations
from scipy.optimize import least_squares
sys.stdout.reconfigure(encoding='utf-8', errors='replace')


def points(th4):
    th = np.concatenate([[0.0], th4])
    o = np.stack([np.cos(th), np.sin(th)], axis=1)
    return np.array([[0.0, 0.0], o[0]+o[1], o[0]+o[2], o[1]+o[3], o[2]+o[3]])


def r2_of(P, t):
    A, B, C = P[t[0]], P[t[1]], P[t[2]]
    a2 = np.sum((B-C)**2); b2 = np.sum((C-A)**2); c2 = np.sum((A-B)**2)
    S = 2*(a2*b2 + b2*c2 + c2*a2) - (a2*a2 + b2*b2 + c2*c2)
    return (a2*b2*c2/S if abs(S) > 1e-14 else np.nan), S


def ortho(A, B, C):
    ax, ay = A; bx, by = B; cx, cy = C
    d = 2*(ax*(by-cy) + bx*(cy-ay) + cx*(ay-by))
    a2 = ax*ax+ay*ay; b2 = bx*bx+by*by; c2 = cx*cx+cy*cy
    ox = (a2*(by-cy) + b2*(cy-ay) + c2*(ay-by))/d
    oy = (a2*(cx-bx) + b2*(ax-cx) + c2*(bx-ax))/d
    return np.array([ax+bx+cx-2*ox, ay+by+cy-2*oy])


def det4(P, q):
    M = np.array([[P[v, 0]**2 + P[v, 1]**2, P[v, 0], P[v, 1], 1.0] for v in q])
    return np.linalg.det(M)


def make_res(which):
    """which = the index (among 1,2,3,4) that is required to be the orthocentre"""
    def res(th4):
        P = points(th4)
        sc = float(np.mean(np.abs(P))) + 1.0
        others = [i for i in (1, 2, 3, 4) if i != which]
        H = ortho(P[others[0]], P[others[1]], P[others[2]])
        if not np.all(np.isfinite(H)):
            return np.full(3, 1e3)
        e = list((H - P[which]) / sc)
        r1, s1 = r2_of(P, (0, 1, 4)); r2v, s2 = r2_of(P, (0, 2, 3))
        if not np.isfinite(r1) or not np.isfinite(r2v):
            return np.full(3, 1e3)
        e.append((r1 - r2v) / (abs(r1) + abs(r2v)))
        return np.array(e)
    return res


if __name__ == '__main__':
    rng = np.random.default_rng(11)
    found = []
    for which in (1, 2, 3, 4):
        res = make_res(which)
        best = (1e9, None)
        for k in range(20000):
            v0 = rng.uniform(0.02, 6.26, 3)
            try:
                s = least_squares(res, v0, xtol=1e-15, ftol=1e-15, gtol=1e-15, max_nfev=600)
            except Exception:
                continue
            c = float(np.max(np.abs(s.fun)))
            if c < best[0]:
                best = (c, s.x.copy())
            if c < 1e-13:
                P = points(s.x)
                r2s = [r2_of(P, t)[0] for t in combinations(range(5), 3)]
                if not np.all(np.isfinite(r2s)):
                    continue
                dets = [abs(det4(P, q)) for q in combinations(range(5), 4)]
                mind = min(np.linalg.norm(P[i]-P[j]) for i, j in combinations(range(5), 2))
                vals = sorted(set(np.round(r2s, 8)))
                rec = dict(which=which, theta=list(map(float, s.x)),
                           points=P.tolist(), r2=list(map(float, r2s)),
                           distinct=len(vals), min_det4=float(min(dets)),
                           min_dist=float(mind), residual=c)
                if min(dets) > 1e-7 and mind > 1e-4:
                    found.append(rec)
                    print('  ADMISSIBLE, which=%d, %d distinct radii, min|det4|=%.2e'
                          % (which, len(vals), min(dets)), flush=True)
                    break
        print('which=%d : best residual %.3e  (%d admissible hits so far)'
              % (which, best[0], len(found)), flush=True)
    json.dump(dict(found=found, completed=True), open('results/orthobranch.json', 'w'), indent=1)
    print('%d admissible solutions' % len(found))
