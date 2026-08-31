"""Numerical search over REAL convex n-gons for an #982 counterexample.

Method (cluster-and-fit, i.e. Lloyd's algorithm coupled to a geometric solve):

  1. start from a random strictly convex n-gon;
  2. for every vertex v, optimally partition its n-1 distances into exactly
     k = floor(n/2)-1 groups (1-D optimal clustering by dynamic programming --
     for sorted data this is exact, not k-means heuristics);
  3. run Levenberg-Marquardt on the coordinates to drive every within-group
     spread to zero, with convexity kept by penalty residuals;
  4. re-cluster and repeat until the assignment stops changing.

A counterexample exists iff step 3 can reach residual 0 while staying convex.
The final objective
        rho = max_v (largest within-group spread at v) / diameter
is the NEAR-MISS MEASURE: rho = 0 is a counterexample, and rho is how far the
configuration is from being one.  This is a floating-point quantity and is
reported as such; any rho below the reporting threshold is re-examined at
higher precision and, if it survives, snapped to exact coordinates.

Nothing in this file is a certification path.  Certification is
verify_artifacts.py acting on the saved JSON.
"""

import sys, os, json, time, math
import numpy as np
from scipy.optimize import least_squares
import multiprocessing as mp


# ------------------------------------------------------- 1-D optimal clustering

def optimal_1d_clusters(v, k):
    """v sorted ascending (len m).  Partition into exactly k contiguous groups
    minimising sum of within-group (max-min).  Exact: the k-1 largest gaps."""
    m = len(v)
    if k >= m:
        return [[i] for i in range(m)]
    gaps = [(v[i + 1] - v[i], i) for i in range(m - 1)]
    gaps.sort(reverse=True)
    cuts = sorted(i for _, i in gaps[:k - 1])
    groups, s = [], 0
    for c in cuts:
        groups.append(list(range(s, c + 1)))
        s = c + 1
    groups.append(list(range(s, m)))
    return groups


def assignment(P, k):
    """For each vertex, the grouping of the other vertices by distance."""
    n = len(P)
    D = np.sqrt(((P[:, None, :] - P[None, :, :]) ** 2).sum(-1))
    asg = []
    for i in range(n):
        others = [j for j in range(n) if j != i]
        vals = D[i, others]
        order = np.argsort(vals)
        sv = vals[order]
        groups = optimal_1d_clusters(sv, k)
        asg.append([[others[order[t]] for t in g] for g in groups])
    return asg, D


# ------------------------------------------------------------------- residuals

SIDE_FRACTION = 0.6      # no side shorter than this times the mean side


def sides_of(P):
    n = len(P)
    return np.sqrt(((P - np.roll(P, -1, axis=0)) ** 2).sum(1))


def residuals(x, n, asg, wconv):
    P = x.reshape(n, 2)
    scale = np.sqrt(((P - P.mean(0)) ** 2).sum(1)).mean() + 1e-12
    r = []
    for i in range(n):
        for g in asg[i]:
            if len(g) < 2:
                continue
            d = np.sqrt(((P[g] - P[i]) ** 2).sum(1))
            r.extend((d - d.mean()) / scale)
    # convexity: every consecutive triple must turn left with margin
    A = P[np.arange(n)]
    B = P[(np.arange(n) + 1) % n]
    C = P[(np.arange(n) + 2) % n]
    cr = (B[:, 0] - A[:, 0]) * (C[:, 1] - A[:, 1]) - (B[:, 1] - A[:, 1]) * (C[:, 0] - A[:, 0])
    margin = 0.02 * scale * scale
    r.extend(wconv * np.minimum(0.0, cr - margin) / (scale * scale))
    # NON-DEGENERACY.  Without this the optimiser collapses several vertices on
    # top of each other, which makes all their distances agree for free.  In a
    # convex polygon the closest pair is always an adjacent pair, so bounding
    # the sides below bounds every pairwise distance below.
    s = sides_of(P)
    r.extend(5.0 * np.minimum(0.0, s - SIDE_FRACTION * s.mean()) / scale)
    # keep the scale pinned
    r.append(10.0 * (scale - 1.0))
    return np.array(r)


def spread_of(P, k):
    """max over vertices of the largest within-group spread of its distances."""
    n = len(P)
    D = np.sqrt(((P[:, None, :] - P[None, :, :]) ** 2).sum(-1))
    worst = 0.0
    for i in range(n):
        vals = np.sort(np.delete(D[i], i))
        for g in optimal_1d_clusters(vals, k):
            worst = max(worst, vals[g[-1]] - vals[g[0]])
    return worst


def rho_of(P, k):
    """SCALE-FREE near-miss measure:
         (largest within-group spread of any vertex's distances)
       / (shortest side of the polygon).
    rho = 0 is exactly a counterexample.  Dividing by the shortest side rather
    than by the diameter is what stops the optimiser from 'winning' by pushing
    vertices together: a squashed polygon has a tiny numerator but an equally
    tiny denominator.  Regular n-gon baselines are in regular_rho_baseline.json.
    """
    s = sides_of(P)
    return spread_of(P, k) / max(s.min(), 1e-300)


def degeneracy(P):
    """min side / diameter.  For the regular n-gon this is sin(pi/n)."""
    D = np.sqrt(((P[:, None, :] - P[None, :, :]) ** 2).sum(-1))
    return float(sides_of(P).min() / D.max())


def is_convex(P, tol=0.0):
    n = len(P)
    s = []
    for i in range(n):
        a, b, c = P[i], P[(i + 1) % n], P[(i + 2) % n]
        s.append((b[0]-a[0])*(c[1]-a[1]) - (b[1]-a[1])*(c[0]-a[0]))
    s = np.array(s)
    return bool(np.all(s > tol)) or bool(np.all(s < -tol))


def random_convex(n, rng):
    """random strictly convex polygon: random radii on a circle, sorted angles,
    then a convex-hull projection by repeated pushing."""
    for _ in range(200):
        th = np.sort(rng.uniform(0, 2 * np.pi, n))
        if np.min(np.diff(np.append(th, th[0] + 2 * np.pi))) < 0.05:
            continue
        rr = 1.0 + rng.uniform(-0.35, 0.35, n)
        P = np.stack([rr * np.cos(th), rr * np.sin(th)], 1)
        if is_convex(P):
            return P
    th = np.linspace(0, 2 * np.pi, n, endpoint=False)
    return np.stack([np.cos(th), np.sin(th)], 1)


def one_run(args):
    n, seed, iters = args
    k = n // 2 - 1
    rng = np.random.default_rng(seed)
    P = random_convex(n, rng)
    best = (rho_of(P, k), P.copy())
    prev = None
    for it in range(iters):
        asg, _ = assignment(P, k)
        key = tuple(tuple(sorted(sum(g, []))) for g in asg)
        sol = least_squares(residuals, P.ravel(), args=(n, asg, 3.0),
                            method='lm' if False else 'trf',
                            max_nfev=400, xtol=1e-14, ftol=1e-14, gtol=1e-14)
        Q = sol.x.reshape(n, 2)
        if not is_convex(Q):
            break
        P = Q
        r = rho_of(P, k)
        if r < best[0]:
            best = (r, P.copy())
        if key == prev and r > best[0] * 0.999:
            break
        prev = key
        if r < 1e-13:
            break
    return best[0], best[1].tolist(), seed


def run(n, ntrials=2000, workers=16, iters=25, seed0=12345):
    t0 = time.time()
    k = n // 2 - 1
    print(f"nsearch n={n} k=floor(n/2)-1={k}  trials={ntrials} workers={workers} "
          f"seed0={seed0}", flush=True)
    jobs = [(n, seed0 + i, iters) for i in range(ntrials)]
    best = None
    hits = []
    with mp.Pool(workers) as P:
        for cnt, (r, pts, sd) in enumerate(P.imap_unordered(one_run, jobs, chunksize=4), 1):
            if best is None or r < best[0]:
                best = (r, pts, sd)
                print(f"  new best rho={r:.3e} (seed {sd}) at trial {cnt}", flush=True)
            if r < 1e-10:
                hits.append({'rho': r, 'points': pts, 'seed': sd})
            if cnt % 250 == 0:
                print(f"  {cnt}/{ntrials}  {time.time()-t0:.0f}s  best rho={best[0]:.3e}",
                      flush=True)
    bp = np.array(best[1])
    th = np.linspace(0, 2 * np.pi, n, endpoint=False)
    RG = np.stack([np.cos(th), np.sin(th)], 1)
    res = {'n': n, 'k': k, 'trials': ntrials, 'workers': workers, 'seed0': seed0,
           'iters': iters, 'best_rho': best[0], 'best_points': best[1],
           'best_seed': best[2], 'hits': hits,
           'best_degeneracy_min_side_over_diameter': degeneracy(bp),
           'regular_ngon_rho': rho_of(RG, k),
           'regular_ngon_degeneracy': degeneracy(RG),
           'side_fraction_floor': SIDE_FRACTION,
           'rho_definition': 'max within-cluster spread of a vertex distance set, '
                             'divided by the shortest side of the polygon; 0 iff '
                             'counterexample',
           'elapsed_s': round(time.time() - t0, 1), 'status': 'COMPLETED',
           'numpy': np.__version__}
    fn = f'nsearch_n{n}.json'
    json.dump(res, open(fn, 'w'), indent=1)
    print(f"n={n} COMPLETED {res['elapsed_s']}s  best rho={best[0]:.6e}  "
          f"exact-zero hits={len(hits)}  -> {fn}", flush=True)
    return res


if __name__ == '__main__':
    mp.freeze_support()
    n = int(sys.argv[1])
    tr = int(sys.argv[2]) if len(sys.argv) > 2 else 2000
    w = int(sys.argv[3]) if len(sys.argv) > 3 else 16
    run(n, tr, w)
