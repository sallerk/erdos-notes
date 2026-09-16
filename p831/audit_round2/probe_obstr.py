"""ROUND-2 PROBE: independent replication of the s^2/2 obstruction, hard constraint,
plus what ELSE degenerates at the reported minimiser (obstruction433.py guards nothing
but the angular separation of the centres)."""
# 2026-09-16: absolute paths replaced by paths relative to this file; nothing else changed.
import sys, os, json, itertools
import numpy as np
from scipy.optimize import minimize, NonlinearConstraint

sys.stdout.reconfigure(encoding='utf-8', errors='replace')
os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))  # the p831 directory


def pts(th):
    a = np.concatenate([[0.0], th])
    o = np.stack([np.cos(a), np.sin(a)], axis=1)
    return np.array([[0.0, 0.0], o[0] + o[1], o[0] + o[2], o[1] + o[3], o[2] + o[3]])


def r2(P, t):
    X, Y, Z = P[t[0]], P[t[1]], P[t[2]]
    a2 = ((Y - Z) ** 2).sum(); b2 = ((Z - X) ** 2).sum(); c2 = ((X - Y) ** 2).sum()
    S = 2 * (a2 * b2 + b2 * c2 + c2 * a2) - (a2 * a2 + b2 * b2 + c2 * c2)
    return (a2 * b2 * c2 / S) if abs(S) > 1e-300 else np.nan, S


def f12(th):
    P = pts(th)
    a = r2(P, (0, 1, 4))[0]; b = r2(P, (1, 2, 3))[0]
    c = r2(P, (0, 2, 3))[0]; d = r2(P, (1, 2, 4))[0]
    if not all(np.isfinite([a, b, c, d])):
        return None
    return (a - b) / (abs(a) + abs(b)), (c - d) / (abs(c) + abs(d))


def sep(th):
    a = np.concatenate([[0.0], th])
    m = 9.0
    for i in range(4):
        for j in range(i + 1, 4):
            d = abs(a[i] - a[j]) % (2 * np.pi)
            m = min(m, min(d, 2 * np.pi - d))
    return m


def obj(th):
    v = f12(th)
    return 1e3 if v is None else max(abs(v[0]), abs(v[1]))


rng = np.random.default_rng(13579)
print('INDEPENDENT replication with a HARD constraint sep(theta) >= s  (SLSQP), and the')
print('other degeneracies at the minimiser, which obstruction433.py does not guard.')
print('   s        min max|f1,f2|   s^2/2      ratio    minpairdist  min|det4|  min16K^2')
art = {r['min_separation']: r['best'] for r in json.load(open('results/obstruction433.json'))['sweep']}
for s in (0.35, 0.25, 0.15, 0.08, 0.03, 0.01):
    nc = NonlinearConstraint(lambda t: sep(t), s, np.inf)
    best = (9e9, None)
    for _ in range(400):
        t0 = rng.uniform(0, 2 * np.pi, 3)
        if sep(t0) < s:
            continue
        try:
            r = minimize(obj, t0, method='SLSQP', constraints=[
                dict(type='ineq', fun=lambda t: sep(t) - s)],
                options=dict(maxiter=400, ftol=1e-14))
        except Exception:
            continue
        if sep(r.x) >= s - 1e-9 and r.fun < best[0]:
            best = (float(r.fun), r.x.copy())
    P = pts(best[1])
    md = min(np.linalg.norm(P[i] - P[j]) for i, j in itertools.combinations(range(5), 2))
    dets = []
    for q in itertools.combinations(range(5), 4):
        M = np.array([[P[v, 0] ** 2 + P[v, 1] ** 2, P[v, 0], P[v, 1], 1.0] for v in q])
        dets.append(abs(np.linalg.det(M)))
    minS = min(abs(r2(P, t)[1]) for t in itertools.combinations(range(5), 3))
    print('  %.2f   %.6e   %.3e  %.4f   %.3e    %.3e  %.3e'
          % (s, best[0], s * s / 2, best[0] / (s * s / 2), md, min(dets), minS))
    if s in art:
        print('        obstruction433.json reports %.6e  (ratio to mine %.4f)'
              % (art[s], art[s] / best[0]))
