"""Heuristic search for a general-position point set with few distinct distances.

Purpose: upper bounds on D_gen(n).  A witness is a certificate whatever found it, so a
float search is legitimate here PROVIDED anything it finds is afterwards re-derived
exactly.  This script only proposes candidates; `verify.py` and exact reconstruction
decide whether they are real.

Objective.  For n points, take the C(n,2) squared distances, cluster them into k groups
(1-D k-means, which is exact by sorting), and minimise the within-cluster spread.  Zero
spread means exactly k distinct distances.  Two penalties keep the configuration honest:

  * collinearity: penalise small triangle areas (no three collinear)
  * cocircularity: penalise small 4x4 cocircularity determinants (no four cocircular)

Both are scale-sensitive, so everything is normalised by the diameter each step.

A hit is only a LEAD.  It gets re-solved exactly before it counts.

Usage:  python numsearch.py <n> <k> [restarts] [seed]
"""
import sys, itertools, json, math, random, time

sys.stdout.reconfigure(encoding='utf-8', errors='replace')
import numpy as np
from scipy.optimize import minimize, least_squares

n = int(sys.argv[1])
k = int(sys.argv[2])
RESTARTS = int(sys.argv[3]) if len(sys.argv) > 3 else 400
SEED = int(sys.argv[4]) if len(sys.argv) > 4 else 1
BUDGET = float(sys.argv[5]) if len(sys.argv) > 5 else 0.0   # seconds; 0 = unlimited

TRI = list(itertools.combinations(range(n), 3))
QUAD = list(itertools.combinations(range(n), 4))
PAIR = list(itertools.combinations(range(n), 2))
TRI_I = np.array(TRI)
QUAD_I = np.array(QUAD)


def unpack(z):
    p = np.zeros((n, 2))
    p[1, 0] = z[0]
    p[2:, :] = z[1:].reshape(n - 2, 2)
    return p


def d2s(p):
    d = p[:, None, :] - p[None, :, :]
    s = (d ** 2).sum(-1)
    return np.array([s[i, j] for i, j in PAIR])


def kmeans1d(v, k):
    """exact 1-D k-means cost by dynamic programming over the sorted values"""
    x = np.sort(v)
    m = len(x)
    pre = np.concatenate([[0.0], np.cumsum(x)])
    pre2 = np.concatenate([[0.0], np.cumsum(x ** 2)])

    def cost(a, b):
        c = b - a
        if c <= 0:
            return 0.0
        s = pre[b] - pre[a]
        return max(pre2[b] - pre2[a] - s * s / c, 0.0)
    INF = 1e18
    dp = [[INF] * (k + 1) for _ in range(m + 1)]
    dp[0][0] = 0.0
    for j in range(1, k + 1):
        for i in range(1, m + 1):
            best = INF
            for t in range(j - 1, i):
                c = dp[t][j - 1] + cost(t, i)
                if c < best:
                    best = c
            dp[i][j] = best
    return dp[m][k]


def obj(z):
    """Vectorised objective.

    The old version looped over C(n,4) cocircularity determinants and C(n,3) triangle
    areas in Python, calling np.linalg.det once per quadruple; at n=8 that is 70 + 56
    calls per evaluation and Nelder-Mead makes thousands.  That is why the n=8 run timed
    out.  Both families are now built as single stacked arrays and evaluated in one call.
    """
    p = unpack(z)
    s = d2s(p)
    diam = s.max()
    if diam <= 1e-12:
        return 1e6
    sn = s / diam
    f = kmeans1d(sn, k)
    f += 1e-3 * np.sum(np.maximum(0.0, 0.02 - sn) ** 2)
    # all triangle areas at once
    A = p[TRI_I]
    ar = np.abs((A[:, 1, 0] - A[:, 0, 0]) * (A[:, 2, 1] - A[:, 0, 1])
                - (A[:, 2, 0] - A[:, 0, 0]) * (A[:, 1, 1] - A[:, 0, 1])) / diam
    f += 1e-4 * np.sum(np.maximum(0.0, 0.03 - ar) ** 2)
    # all cocircularity determinants at once
    Q = p[QUAD_I]
    M = np.empty((Q.shape[0], 4, 4))
    M[:, :, 0] = (Q ** 2).sum(axis=2)
    M[:, :, 1] = Q[:, :, 0]
    M[:, :, 2] = Q[:, :, 1]
    M[:, :, 3] = 1.0
    dt = np.abs(np.linalg.det(M)) / (diam ** 2)
    f += 1e-4 * np.sum(np.maximum(0.0, 0.02 - dt) ** 2)
    return f


def cluster(sv, k):
    """split normalised squared distances into k contiguous groups; None if it fails"""
    srt = list(np.argsort(sv))
    gaps = sorted(range(len(srt) - 1),
                  key=lambda i: -(sv[srt[i + 1]] - sv[srt[i]]))[:k - 1]
    cuts = sorted(gaps)
    lab, ci, at = {}, 0, 0
    for i, idx in enumerate(srt):
        lab[int(idx)] = ci
        if at < len(cuts) and i == cuts[at]:
            ci += 1
            at += 1
    if len(set(lab.values())) != k:
        return None
    return tuple(lab[i] for i in range(len(sv)))


def polish(z0, pat, k):
    """Gauss-Newton onto the EXACT equalities for a fixed pattern.

    Variables: the free coordinates plus the k class values.  Residuals: every squared
    distance minus its class value.  A genuine configuration drives this to ~1e-15; a
    near-miss does not, which is exactly the distinction the raw objective blurs.
    """
    def resid(w):
        p = unpack(w[:len(z0)])
        D = w[len(z0):]
        sv = d2s(p)
        return np.array([sv[i] - D[pat[i]] for i in range(len(PAIR))])
    p0 = unpack(z0)
    s0 = d2s(p0)
    D0 = np.array([np.mean([s0[i] for i in range(len(PAIR)) if pat[i] == c])
                   for c in range(k)])
    w0 = np.concatenate([z0, D0])
    r = least_squares(resid, w0, xtol=1e-15, ftol=1e-15, gtol=1e-15, max_nfev=20000)
    return r, float(np.max(np.abs(r.fun)))


rng = random.Random(SEED)
np.random.seed(SEED)
hits = []
print('searching n=%d k=%d, %d restarts, seed %d' % (n, k, RESTARTS, SEED))
bestobj = 1e18
T_START = time.time()
stopped_early = False
done = 0
for r in range(RESTARTS):
    # A wall-clock budget removes the need to PREDICT the restart count.  Estimating it
    # from a small sample was wrong three times running and each miss produced a capped
    # run with no completion record at all.  Now the run always finishes cleanly and
    # reports how many restarts it actually managed.
    if BUDGET and (time.time() - T_START) > BUDGET:
        stopped_early = True
        break
    done = r + 1
    z0 = np.concatenate([[1.0], np.random.randn(2 * (n - 2)) * 0.8])
    try:
        res = minimize(obj, z0, method='Nelder-Mead',
                       options={'maxiter': 8000, 'xatol': 1e-10, 'fatol': 1e-12})
    except Exception:
        continue
    bestobj = min(bestobj, res.fun)
    if res.fun > 1e-3:
        continue
    p = unpack(res.x)
    sv = d2s(p)
    sv = sv / sv.max()
    pat = cluster(sv, k)
    if pat is None:
        continue
    # POLISH: a near-miss dies here; only a genuine configuration reaches ~1e-15
    pr, worst = polish(res.x, pat, k)
    if worst > 1e-12:
        continue
    pp = unpack(pr.x[:len(res.x)])
    ss = d2s(pp)
    if ss.min() <= 1e-9:
        continue
    # general position, on the polished coordinates
    diam = ss.max()
    ok = True
    for (a, b, c) in TRI:
        ar = abs((pp[b, 0] - pp[a, 0]) * (pp[c, 1] - pp[a, 1])
                 - (pp[c, 0] - pp[a, 0]) * (pp[b, 1] - pp[a, 1])) / diam
        if ar < 1e-7:
            ok = False
    for q in QUAD:
        M = np.array([[(pp[t] ** 2).sum(), pp[t, 0], pp[t, 1], 1.0] for t in q])
        if abs(np.linalg.det(M)) / diam ** 2 < 1e-7:
            ok = False
    if not ok:
        continue
    key = tuple(sorted(np.round(ss / diam, 9)))
    if all(key != h[0] for h in hits):
        hits.append((key, pat, pp.tolist(), worst))
        print('  restart %4d: GENUINE hit, residual %.2e, pattern %s' % (r, worst, pat))
        # Dump immediately.  Dumping only after the loop means a run killed by its time
        # cap yields nothing at all, even if it had already found the answer (L63, and
        # rule 3.3: save partial progress at the moment of stopping).
        json.dump({'n': n, 'k': k, 'restarts_done': r + 1, 'complete': False,
                   'hits': [{'pattern': list(h[1]), 'points': h[2], 'residual': h[3]}
                            for h in hits]},
                  open('numsearch_hits_n%d_k%d.json' % (n, k), 'w'), indent=1)

print()
print('best raw objective seen: %.3e' % bestobj)
print('genuine polished hits  : %d' % len(hits))
json.dump({'n': n, 'k': k, 'seed': SEED, 'restarts_requested': RESTARTS,
           'restarts_done': done, 'budget_seconds': BUDGET,
           'stopped_on_budget': stopped_early, 'complete': True,
           'elapsed': round(time.time() - T_START, 1),
           'hits': [{'pattern': list(h[1]), 'points': h[2], 'residual': h[3]}
                    for h in hits]},
          open('numsearch_hits_n%d_k%d_s%d.json' % (n, k, SEED), 'w'), indent=1)
print('restarts actually done: %d of %d  (%.0f s, stopped on budget: %s)'
      % (done, RESTARTS, time.time() - T_START, stopped_early))
print('written: numsearch_hits_n%d_k%d_s%d.json' % (n, k, SEED))
for key, pat, pts, w in hits[:5]:
    print('   pattern %s   residual %.2e' % (pat, w))
    print('      decide exactly: python decide1.py %d %d %s'
          % (n, k, ','.join(map(str, pat))))
if not hits:
    print()
    print('No genuine %d-distance configuration found. Heuristic: this is evidence of' % k)
    print('difficulty, NOT a proof that none exists.')
