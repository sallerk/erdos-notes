"""ROUND-2 DECISIVE PROBE.  Drop EVERY guard.  Minimise only the 10 equality residuals,
collect every root, and measure the degeneracy of the roots from the DEFINITIONS.

This is the test neither round has run: no penalty can be "the thing being measured"
because there is no penalty.  A root is then classified post hoc:
  admissible          : min|det4|/scale^1.5 > 1e-6, min 16K^2/scale^2 > 1e-6, mind > 1e-3
  class-merged        : min class separation < 1e-6
If some pattern has an admissible root with class separation bounded away from 0,
h(5) = 3 and the whole directory is wrong.  If every root is degenerate, the negative
is honest and quantified.
"""
# 2026-09-16: absolute paths replaced by paths relative to this file; nothing else changed.
import sys, os, json, itertools
import numpy as np
from scipy.optimize import least_squares

sys.stdout.reconfigure(encoding='utf-8', errors='replace')
os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))  # the p831 directory
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
        r2[i] = a2 * b2 * c2 / s if abs(s) > 1e-300 else np.nan
    return r2, S


def det4(P, q):
    return np.linalg.det(np.array([[P[v, 0] ** 2 + P[v, 1] ** 2, P[v, 0], P[v, 1], 1.0] for v in q]))


def eqres(v, labels):
    P = unpack(v)
    r2, S = quants(P)
    if np.any(~np.isfinite(r2)) or np.any(r2 <= 0):
        return np.full(10, 1e3)
    scale = float(np.mean(r2))
    means = {c: float(np.mean([r2[i] for i in range(10) if labels[i] == c])) for c in range(3)}
    return np.array([(r2[i] - means[labels[i]]) / scale for i in range(10)])


def diag(v, labels):
    P = unpack(v)
    r2, S = quants(P)
    if np.any(~np.isfinite(r2)) or np.any(r2 <= 0):
        return None
    scale = float(np.mean(r2))
    means = {c: float(np.mean([r2[i] for i in range(10) if labels[i] == c])) for c in range(3)}
    return dict(eq=float(max(abs(r2[i] - means[labels[i]]) / scale for i in range(10))),
                sep=float(min(abs(means[a] - means[b]) for a in range(3) for b in range(a + 1, 3)) / scale),
                det=float(min(abs(det4(P, q)) / scale ** 1.5 for q in QUADS)),
                flat=float(np.min(S) / scale ** 2),
                mind=float(min(np.linalg.norm(P[i] - P[j]) for i, j in itertools.combinations(range(5), 2))),
                span=float(np.max(np.abs(P))))


if __name__ == '__main__':
    R = int(sys.argv[1]) if len(sys.argv) > 1 else 600
    pats = json.load(open('results/penum_n5_k3.json'))['patterns']
    tw = {o['i']: o for o in json.load(open('results/tausweep_n5_k3.json'))['results']}
    rng = np.random.default_rng(2026)
    print('NO-GUARD PROBE.  %d restarts per pattern, box uniform(-6,6).' % R, flush=True)
    print('root = max|equality residual| < 1e-10', flush=True)
    print(' i  old-verdict      roots  best-sep   best-det   best-flat  best-mind  |'
          ' any root with sep>1e-3 AND det>1e-6 AND flat>1e-6 ?', flush=True)
    out = []
    for i, p in enumerate(pats):
        lab = p['labels']
        roots = []
        for _ in range(R):
            v0 = rng.uniform(-6, 6, size=6)
            try:
                s = least_squares(eqres, v0, args=(lab,), xtol=1e-15, ftol=1e-15,
                                  gtol=1e-15, max_nfev=3000)
            except Exception:
                continue
            if float(np.max(np.abs(s.fun))) < 1e-10:
                d = diag(s.x, lab)
                if d: roots.append(d)
        if not roots:
            print(' %2d %-16s %5d  -- no root found at all --' % (i, tw[i]['verdict'], 0), flush=True)
            out.append(dict(i=i, roots=0)); continue
        bs = max(r['sep'] for r in roots)
        bd = max(r['det'] for r in roots)
        bf = max(r['flat'] for r in roots)
        bm = max(r['mind'] for r in roots)
        good = [r for r in roots if r['sep'] > 1e-3 and r['det'] > 1e-6 and r['flat'] > 1e-6 and r['mind'] > 1e-3]
        print(' %2d %-16s %5d  %.3e  %.3e  %.3e  %.3e  | %s'
              % (i, tw[i]['verdict'], len(roots), bs, bd, bf, bm,
                 ('YES x%d  <-- REALISATION' % len(good)) if good else 'no'),
              flush=True)
        if good:
            g = max(good, key=lambda r: r['sep'])
            print('        best admissible-looking root: %s' % g, flush=True)
        out.append(dict(i=i, roots=len(roots), best_sep=bs, best_det=bd,
                        best_flat=bf, best_mind=bm, good=len(good),
                        sample=roots[:5]))
    json.dump(out, open('audit_round2/probe_noguard.json', 'w'), indent=1)
