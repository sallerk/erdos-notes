#!/usr/bin/env python
"""
fr_mirror.py -- reconstruct a Fishburn-Reeds style configuration: 2h points in
convex position whose UNIT-distance graph is bipartite between two sets A and B
separated by a line, with every vertex of unit-degree >= d.

ANSATZ.  Put the separating line on the y-axis and take B to be the mirror image
of A, so with A = {(-x_i, y_i)} and B = {(x_i, y_i)}, x_i > 0,

     |a_i - b_j| = 1   <=>   (x_i + x_j)^2 + (y_i - y_j)^2 = 1,

a SYMMETRIC relation in (i,j).  So the unit-distance graph is determined by an
undirected graph G on h = n/2 indices (a loop at i means x_i = 1/2), and vertex
degrees in the point set equal degrees in G.  Unknowns: 2h coordinates minus 1
(translation along the axis) = 2h-1.  Equations: |E(G)| = dh/2.  For d=3, h=10
that is 15 equations in 19 unknowns -- a 4-dimensional family, so the system is
easy; the whole difficulty is convex position, which is imposed as a penalty and
then checked.

Usage:
  python fr_mirror.py --h 10 --d 3 --graphs 4000 --starts 6 --seed 1
  python fr_mirror.py --h 10 --d 4 --graphs 4000 --starts 6 --seed 1   (k=4!)
"""
import argparse, json, math, sys, time
import numpy as np
from scipy.optimize import least_squares


def random_regular(h, d, rng, loops=True, tries=200):
    """random graph on h vertices, every degree exactly d, loops allowed
    (a loop contributes 1 to the degree here, matching the geometry)."""
    for _ in range(tries):
        deg = [0] * h
        E = []
        order = list(range(h))
        ok = True
        for i in order:
            while deg[i] < d:
                cand = [j for j in range(h) if deg[j] < d and (i, j) not in E and (j, i) not in E]
                if loops and deg[i] < d and (i, i) not in E and rng.random() < 0.10:
                    cand.append(i)
                cand = [j for j in cand if j != i or loops]
                if not cand:
                    ok = False
                    break
                j = int(rng.choice(cand))
                E.append((min(i, j), max(i, j)))
                deg[i] += 1
                if j != i:
                    deg[j] += 1
            if not ok:
                break
        if ok and all(x == d for x in deg):
            return E
    return None


def build(z, h):
    x = np.abs(z[:h]) + 1e-9
    y = np.concatenate([[0.0], z[h:2 * h - 1]])
    return x, y


def points(z, h):
    x, y = build(z, h)
    o = np.argsort(y)
    x, y = x[o], y[o]
    P = np.concatenate([np.stack([x, y], 1), np.stack([-x[::-1], y[::-1]], 1)], 0)
    return P


def resid(z, h, E, wc):
    x, y = build(z, h)
    r = [np.array([(x[i] + x[j]) ** 2 + (y[i] - y[j]) ** 2 - 1.0 for (i, j) in E])]
    P = points(z, h)
    n = len(P)
    Q = np.roll(P, -1, 0) - P
    cr = Q[:, 0] * np.roll(Q, -1, 0)[:, 1] - Q[:, 1] * np.roll(Q, -1, 0)[:, 0]
    r.append(wc * np.maximum(0.0, 2e-4 - cr))
    D = np.sqrt(((P[:, None, :] - P[None, :, :]) ** 2).sum(-1)) + np.eye(n) * 9
    r.append(np.array([10.0 * max(0.0, 0.05 - D.min())]))
    return np.concatenate(r)


def check(z, h, tol=1e-9):
    P = points(z, h)
    n = len(P)
    D = np.sqrt(((P[:, None, :] - P[None, :, :]) ** 2).sum(-1))
    Q = np.roll(P, -1, 0) - P
    cr = Q[:, 0] * np.roll(Q, -1, 0)[:, 1] - Q[:, 1] * np.roll(Q, -1, 0)[:, 0]
    Dm = D + np.eye(n) * 9
    deg = [int(((np.abs(D[i] - 1) < tol) & (np.arange(n) != i)).sum()) for i in range(n)]
    return cr.min(), Dm.min(), deg, P


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--h', type=int, default=10)
    ap.add_argument('--d', type=int, default=3)
    ap.add_argument('--graphs', type=int, default=2000)
    ap.add_argument('--starts', type=int, default=6)
    ap.add_argument('--seed', type=int, default=1)
    ap.add_argument('--workers', type=int, default=1)
    ap.add_argument('--out', default=None)
    args = ap.parse_args()
    rng = np.random.default_rng(args.seed)
    t0 = time.time()
    best = []
    ngr = 0
    for g in range(args.graphs):
        E = random_regular(args.h, args.d, rng)
        if E is None:
            continue
        ngr += 1
        for s in range(args.starts):
            z0 = np.concatenate([rng.uniform(.25, .55, args.h),
                                 np.sort(rng.uniform(-1.2, 1.2, args.h - 1))])
            # homotopy: solve the unit-distance system first (the easy,
            # underdetermined part), then push the solution along its 4-dimensional
            # solution manifold towards convex position by raising the weight.
            try:
                z = z0
                for wc in (0.0, 0.3, 3.0, 30.0, 300.0, 3000.0):
                    sol = least_squares(resid, z, args=(args.h, E, wc), method='lm',
                                        max_nfev=1200, xtol=1e-15, ftol=1e-15)
                    z = sol.x
            except Exception:
                continue
            cr, md, deg, P = check(sol.x, args.h)
            eqres = np.abs(resid(sol.x, args.h, E, 0.0)[:len(E)]).max()
            if md < 0.03:
                continue
            score = (0 if (cr > 0 and eqres < 1e-11) else 1, -min(deg), float(eqres), -float(cr))
            best.append((score, float(cr), float(eqres), min(deg), deg, sol.x.copy(), list(E)))
            best.sort(key=lambda u: u[0])
            best = best[:6]
    recs = []
    for sc, cr, eqres, mind, deg, z, E in best:
        cr2, md, deg2, P = check(z, args.h)
        recs.append({"convex": bool(cr2 > 0), "min_cross": float(cr2), "min_pair_dist": float(md),
                     "max_equation_residual": float(eqres), "min_unit_degree": int(mind),
                     "unit_degrees": deg2, "graph_edges": [list(e) for e in E],
                     "coords_float": [[float(u), float(v)] for u, v in P]})
    out = {"problem": "erdos97 common-distance version, mirror ansatz", "n": 2 * args.h,
           "d_target": args.d, "graphs_tried": ngr, "starts_per_graph": args.starts,
           "seed": args.seed, "workers": 1, "wall_sec": time.time() - t0,
           "status": "COMPLETED", "arithmetic": "float64 -- NOT exact",
           "cmd": " ".join(sys.argv), "best": recs}
    fn = args.out or ("frmirror_h%d_d%d_s%d.json" % (args.h, args.d, args.seed))
    json.dump(out, open(fn, "w"), indent=1)
    print("n=%d d=%d graphs=%d wall=%.0fs -> %s" % (2 * args.h, args.d, ngr, time.time() - t0, fn))
    for r in recs[:6]:
        print("   convex=%s min_cross=%+.5f eqres=%.1e min_unit_degree=%d degs=%s"
              % (r["convex"], r["min_cross"], r["max_equation_residual"],
                 r["min_unit_degree"], r["unit_degrees"]))


if __name__ == '__main__':
    main()
