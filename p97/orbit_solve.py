#!/usr/bin/env python
"""
orbit_solve.py -- solve the C_m-symmetric COMMON-DISTANCE ansatz exhaustively
over its combinatorial choices.

Setting: n = m*c points, c orbits under the rotation by 2 pi/m, orbit i having
radius a_i and phase phi_i.  All the required distances equal 1 (this is the
"same distance for every vertex" version -- Fishburn-Reeds for k=3).

An orbit pair (i,l) joined "at offset k" means

    a_i^2 + a_l^2 - 2 a_i a_l cos(phi_l - phi_i + 2 pi k/m) = 1,

and then EVERY vertex of orbit i has exactly one unit-neighbour in orbit l and
vice versa.  So if the multigraph on the c orbits is d-regular, every one of the
n vertices has unit-degree d.  Unknowns: c radii + c phases - 1 (rotation) =
2c-1; equations: dc/2.  For d=3 and c=4 that is 6 equations in 7 unknowns.

This script enumerates the d-regular orbit graphs and ALL offset assignments,
solves each system numerically from several starts, and keeps the solutions that
are in strictly convex position.

Usage:
  python orbit_solve.py --m 5 --c 4 --d 3 --starts 6        (Fishburn-Reeds size, n=20)
  python orbit_solve.py --m 4 --c 5 --d 4 --starts 6        (k=4, n=20)
  python orbit_solve.py --sweep --d 4 --nmax 40
"""
import argparse, itertools, json, math, sys, time
import numpy as np
from scipy.optimize import least_squares


def regular_graphs(c, d):
    """all d-regular simple graphs on c labelled vertices, up to nothing."""
    edges = list(itertools.combinations(range(c), 2))
    out = []
    need = d * c // 2
    if d * c % 2:
        return out
    for sub in itertools.combinations(edges, need):
        deg = [0] * c
        for u, v in sub:
            deg[u] += 1
            deg[v] += 1
        if all(x == d for x in deg):
            out.append(sub)
    return out


def make_res(m, c, E, off, pin=None):
    """pin: if given, an extra residual log(a_0)-log(pin) so the system is square
    and the (generically 1-dimensional) solution family gets swept."""
    def res(z):
        a = np.exp(z[:c])
        ph = np.concatenate([[0.0], z[c:c + c - 1]])
        r = []
        for (u, v), k in zip(E, off):
            ang = ph[v] - ph[u] + 2 * math.pi * k / m
            r.append(a[u] ** 2 + a[v] ** 2 - 2 * a[u] * a[v] * math.cos(ang) - 1.0)
        if pin is not None:
            r.append(z[0] - math.log(pin))
        return np.array(r)
    return res


def points(z, m, c):
    a = np.exp(z[:c])
    ph = np.concatenate([[0.0], z[c:c + c - 1]])
    ang, rad = [], []
    for i in range(c):
        for t in range(m):
            ang.append(ph[i] + 2 * math.pi * t / m)
            rad.append(a[i])
    ang = np.array(ang) % (2 * math.pi)
    rad = np.array(rad)
    o = np.argsort(ang)
    ang, rad = ang[o], rad[o]
    return np.stack([rad * np.cos(ang), rad * np.sin(ang)], 1)


def analyse(P, tol=1e-9):
    n = len(P)
    D = np.sqrt(((P[:, None, :] - P[None, :, :]) ** 2).sum(-1))
    Q = np.roll(P, -1, 0) - P
    cr = Q[:, 0] * np.roll(Q, -1, 0)[:, 1] - Q[:, 1] * np.roll(Q, -1, 0)[:, 0]
    dd = D + np.eye(n) * 9
    deg = [int(((np.abs(D[i] - 1) < tol) & (np.arange(n) != i)).sum()) for i in range(n)]
    return cr.min(), dd.min(), deg


def solve_one(m, c, d, starts, seed, nmax):
    rng = np.random.default_rng(seed)
    hits = []
    graphs = regular_graphs(c, d)
    ncombo = 0
    pins = np.exp(np.linspace(math.log(0.45), math.log(3.2), starts))
    for E in graphs:
        for off in itertools.product(range(m), repeat=len(E)):
            ncombo += 1
            for s in range(starts):
                res = make_res(m, c, E, off, pin=pins[s])
                z0 = np.concatenate([math.log(pins[s]) + rng.normal(0, .12, c),
                                     np.sort(rng.uniform(0, 2 * math.pi / m, c - 1))])
                try:
                    sol = least_squares(res, z0, method='lm', max_nfev=400,
                                        xtol=1e-15, ftol=1e-15)
                except Exception:
                    continue
                if np.abs(sol.fun).max() > 1e-12:
                    continue
                P = points(sol.x, m, c)
                cr, md, deg = analyse(P)
                if cr > 1e-9 and md > 1e-6 and min(deg) >= d:
                    hits.append({"graph": [list(e) for e in E], "offsets": list(off),
                                 "min_cross": float(cr), "min_pair_dist": float(md),
                                 "unit_degrees": deg, "min_unit_degree": int(min(deg)),
                                 "radii": [float(x) for x in np.exp(sol.x[:c])],
                                 "phases": [0.0] + [float(x) for x in sol.x[c:]],
                                 "coords_float": [[float(u), float(v)] for u, v in P],
                                 "max_residual": float(np.abs(sol.fun).max())})
                    break
    return hits, ncombo, len(graphs)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--m', type=int, default=5)
    ap.add_argument('--c', type=int, default=4)
    ap.add_argument('--d', type=int, default=3)
    ap.add_argument('--starts', type=int, default=6)
    ap.add_argument('--seed', type=int, default=1)
    ap.add_argument('--nmax', type=int, default=40)
    ap.add_argument('--sweep', action='store_true')
    ap.add_argument('--out', default=None)
    args = ap.parse_args()
    t0 = time.time()
    jobs = []
    if args.sweep:
        for m in range(2, 11):
            for c in range(args.d + 1, 9):
                if m * c > args.nmax or (args.d * c) % 2:
                    continue
                if m ** (args.d * c // 2) > 4e5:
                    continue
                jobs.append((m, c))
    else:
        jobs = [(args.m, args.c)]
    allres = []
    for (m, c) in jobs:
        hits, ncombo, ng = solve_one(m, c, args.d, args.starts, args.seed, args.nmax)
        best = sorted(hits, key=lambda h: -h["min_cross"])[:3]
        allres.append({"m": m, "c": c, "n": m * c, "d": args.d, "graphs": ng,
                       "combinations_tried": ncombo, "n_convex_hits": len(hits), "best": best})
        print("m=%d c=%d n=%2d d=%d : %d graphs, %d offset combos -> %d convex hits%s"
              % (m, c, m * c, args.d, ng, ncombo, len(hits),
                 ("  best min_cross=%.4f" % best[0]["min_cross"]) if best else ""))
        sys.stdout.flush()
    out = {"problem": "erdos97 common-distance version", "d_min_unit_degree": args.d,
           "status": "COMPLETED", "wall_sec": time.time() - t0, "seed": args.seed,
           "starts_per_combo": args.starts, "workers": 1,
           "arithmetic": "float64; solutions accepted at residual < 1e-12 -- NOT exact",
           "cmd": " ".join(sys.argv), "runs": allres}
    fn = args.out or ("orbit_d%d_%s.json" % (args.d, "sweep" if args.sweep else "m%dc%d" % (args.m, args.c)))
    json.dump(out, open(fn, "w"), indent=1)
    print("-> %s (%.0fs)" % (fn, time.time() - t0))


if __name__ == '__main__':
    main()
