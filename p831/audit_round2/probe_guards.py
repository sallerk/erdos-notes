"""ROUND-2 PROBE 1.  Which guard is active at the tausweep optimum?

Written from the definitions.  Reimplements the tausweep objective (span<60,
flat>tau, sep>sep_tau, det4>tau) but records EVERY margin at the optimum, and
lets each guard be swept independently.
"""
# 2026-09-16: absolute paths replaced by paths relative to this file; nothing else changed.
import sys, json, itertools, numpy as np
from scipy.optimize import least_squares

sys.stdout.reconfigure(encoding='utf-8', errors='replace')
TRI = list(itertools.combinations(range(5), 3))
QUADS = list(itertools.combinations(range(5), 4))


def unpack(v):
    P = np.zeros((5, 2)); P[1, 0] = 1.0; P[2:, :] = v.reshape(3, 2); return P


def quants(P):
    r2 = np.empty(10); S = np.empty(10)
    for i, (a, b, c) in enumerate(TRI):
        A, B, C = P[a], P[b], P[c]
        a2 = ((B - C) ** 2).sum(); b2 = ((C - A) ** 2).sum(); c2 = ((A - B) ** 2).sum()
        s = 2 * (a2 * b2 + b2 * c2 + c2 * a2) - (a2 * a2 + b2 * b2 + c2 * c2)
        S[i] = s
        r2[i] = a2 * b2 * c2 / s if s > 1e-300 else np.nan
    return r2, S


def det4(P, q):
    return np.linalg.det(np.array([[P[v, 0] ** 2 + P[v, 1] ** 2, P[v, 0], P[v, 1], 1.0] for v in q]))


def margins(v, labels, k):
    """all raw margins at a point, in the SAME normalisation tausweep uses"""
    P = unpack(v)
    r2, S = quants(P)
    if np.any(~np.isfinite(r2)) or np.any(r2 <= 0):
        return None
    scale = float(np.mean(r2))
    means = {c: float(np.mean([r2[i] for i in range(10) if labels[i] == c])) for c in range(k)}
    eq = max(abs(r2[i] - means[labels[i]]) / scale for i in range(10))
    span = float(np.max(np.abs(P)))
    flat = float(np.min(S)) / scale ** 2
    sep = min(abs(means[a] - means[b]) for a in range(k) for b in range(a + 1, k)) / scale
    dmin = min(abs(det4(P, q)) / scale ** 1.5 for q in QUADS)
    pdist = min(float(np.linalg.norm(P[i] - P[j])) for i, j in itertools.combinations(range(5), 2))
    return dict(eq=eq, span=span, flat=flat, sep=sep, det=dmin, pdist=pdist, scale=scale)


def make(labels, k, tau, sep_tau, span_tau, mind_tau):
    nout = 10 + 3 + len(QUADS) + (1 if mind_tau else 0)

    def f(v):
        P = unpack(v)
        r2, S = quants(P)
        if np.any(~np.isfinite(r2)) or np.any(r2 <= 0):
            return np.full(nout, 1e3)
        scale = float(np.mean(r2))
        means = {c: float(np.mean([r2[i] for i in range(10) if labels[i] == c])) for c in range(k)}
        out = [(r2[i] - means[labels[i]]) / scale for i in range(10)]
        span = float(np.max(np.abs(P)))
        out.append(0.0 if span < span_tau else (span - span_tau) * 1e-2)
        flat = float(np.min(S)) / (scale ** 2 + 1e-30)
        out.append(0.0 if flat > tau else (tau - flat) * 1e3)
        sep = min(abs(means[a] - means[b]) for a in range(k) for b in range(a + 1, k)) / scale
        out.append(0.0 if sep > sep_tau else (sep_tau - sep) * 1e2)
        for q in QUADS:
            d = abs(det4(P, q)) / (scale ** 1.5 + 1e-30)
            out.append(0.0 if d > tau else (tau - d) * 1e3)
        if mind_tau:
            pd = min(float(np.linalg.norm(P[i] - P[j])) for i, j in itertools.combinations(range(5), 2))
            out.append(0.0 if pd > mind_tau else (mind_tau - pd) * 1e2)
        return np.array(out)
    return f


def floor_at(labels, k, tau, sep_tau, span_tau, mind_tau, restarts, rng, box=2.0, lo=-2.0):
    f = make(labels, k, tau, sep_tau, span_tau, mind_tau)
    best = (np.inf, None)
    for _ in range(restarts):
        v0 = rng.uniform(lo, box + 0.5, size=6)
        try:
            s = least_squares(f, v0, xtol=1e-15, ftol=1e-15, gtol=1e-15, max_nfev=3000)
        except Exception:
            continue
        c = float(np.max(np.abs(s.fun)))
        if c < best[0]:
            best = (c, s.x.copy())
    return best


if __name__ == '__main__':
    import os
    os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))  # the p831 directory
    pats = json.load(open('results/penum_n5_k3.json'))['patterns']
    tw = {o['i']: o for o in json.load(open('results/tausweep_n5_k3.json'))['results']}
    R = int(sys.argv[1]) if len(sys.argv) > 1 else 60
    rng = np.random.default_rng(4242)
    print('PROBE 1a: margins at the optimum, tau=1e-6, sep=1e-3, span=60, no mind guard')
    print('  (this is EXACTLY tausweep\'s objective)  %d restarts' % R)
    print('  i  verdict          floor      eq         sep/1e-3   det/tau    flat/tau   span/60   pdist')
    rows = []
    for i, p in enumerate(pats):
        c, v = floor_at(p['labels'], 3, 1e-6, 1e-3, 60.0, None, R, rng)
        m = margins(v, p['labels'], 3)
        rows.append((i, c, m))
        print('  %2d %-15s %.3e  %.3e  %8.3f   %8.2e   %8.2e   %6.3f  %8.2e'
              % (i, tw[i]['verdict'], c, m['eq'], m['sep'] / 1e-3, m['det'] / 1e-6,
                 m['flat'] / 1e-6, m['span'] / 60.0, m['pdist']))
    json.dump([dict(i=r[0], floor=r[1], **r[2]) for r in rows],
              open('audit_round2/probe1a.json', 'w'), indent=1)
