"""Re-check, from scratch, the two FATAL defects the code auditor reported.
An inherited claim is not a fact until it is verified against the artifact (L12, L78).
"""
import sys
import json
from itertools import combinations

import numpy as np
from scipy.optimize import least_squares

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

print('=' * 78)
print('RE-CHECK OF THE TWO FATAL DEFECTS')
print('=' * 78)

# ---------------------------------------------------------------- D1
print()
print('D1. ctrlA.py: does normalising by the mean of ALL SIX radii while constraining')
print('    only k of them let the optimiser fake a small residual?')

from caseA import six_radii   # noqa: E402

PAIRS = [(0, 1), (0, 2), (0, 3), (0, 4), (0, 5)]


def res_as_written(v, k):
    r, _, _ = six_radii(v)
    if np.any(~np.isfinite(r)) or np.any(r <= 0):
        return np.full(k, 1e3)
    sc = float(np.mean(r))                       # mean over ALL six
    return np.array([(r[a] - r[b]) / sc for a, b in PAIRS[:k]])


def true_relative_error(v, k):
    """the honest measure: each constrained difference against the size of the radii
    it actually compares, not against a mean an unconstrained radius can inflate"""
    r, _, _ = six_radii(v)
    if np.any(~np.isfinite(r)) or np.any(r <= 0):
        return np.inf
    return max(abs(r[a] - r[b]) / (abs(r[a]) + abs(r[b])) for a, b in PAIRS[:k])


rng = np.random.default_rng(7)
print()
print('   k  reported residual   TRUE relative error   max radius   verdict')
rows = []
for k in range(1, 6):
    best = (1e9, None)
    for _ in range(400):
        v0 = np.array([rng.uniform(-1, 2), rng.uniform(0.2, 2.0),
                       rng.uniform(-2, 3), rng.uniform(-2, 3)])
        try:
            s = least_squares(res_as_written, v0, args=(k,), xtol=1e-15, ftol=1e-15,
                              gtol=1e-15, max_nfev=4000)
        except Exception:
            continue
        c = float(np.max(np.abs(s.fun)))
        if c < best[0]:
            best = (c, s.x.copy())
    v = best[1]
    te = true_relative_error(v, k)
    r, _, _ = six_radii(v)
    verdict = 'GENUINE' if te < 1e-10 else 'FAKE (inflated denominator)'
    print('   %d  %.3e           %.3e             %.3e   %s'
          % (k, best[0], te, float(np.max(r)), verdict))
    rows.append(dict(k=k, reported=best[0], true=float(te), maxr=float(np.max(r)),
                     genuine=bool(te < 1e-10)))

fake = [r for r in rows if not r['genuine'] and r['reported'] < 1e-12]
print()
if fake:
    print('   CONFIRMED FATAL: %d rung(s) reported SOLVED at <1e-12 while the constrained'
          % len(fake))
    print('   radii actually disagree by a relative %s.'
          % ', '.join('%.1f%%' % (100 * r['true']) for r in fake))
    print('   The control is therefore not a control, and the Case A negative that rests')
    print('   on it is unsupported.')
else:
    print('   NOT reproduced: every rung reported as solved is genuine.')

# ---------------------------------------------------------------- D2
print()
print('D2. pscreen.py: are the small residuals actually the concyclicity penalty')
print('    sitting on its hard-coded margin of 1e-6 rather than a real obstruction?')

from pscreen import unpack, quantities, det4 as psdet4   # noqa: E402

d = json.load(open('results/pscreen_n5_k3.json'))
res = sorted(d['results'], key=lambda r: r['residual'])[:4]
tri = list(combinations(range(5), 3))
quads = list(combinations(range(5), 4))
print()
print('   the four smallest-residual patterns, decomposed:')
print('   pattern  residual    largest EQUALITY residual   min |det4|/scale^1.5')
onmargin = 0
for r in res:
    v = np.array(r['v'])
    P = unpack(v, 5)
    r2, S = quantities(P, tri)
    scale = float(np.mean(r2))
    labs = json.load(open('results/penum_n5_k3.json'))['patterns'][r['i']]['labels']
    means = {}
    for c in set(labs):
        means[c] = float(np.mean([r2[i] for i in range(10) if labs[i] == c]))
    eq = max(abs(r2[i] - means[labs[i]]) / scale for i in range(10))
    dd = min(abs(psdet4(P, q)) / (scale ** 1.5) for q in quads)
    flag = 'ON THE 1e-6 MARGIN' if abs(dd - 1e-6) / 1e-6 < 0.05 else ''
    if flag:
        onmargin += 1
    print('   %5d    %.3e   %.3e                  %.6e %s'
          % (r['i'], r['residual'], eq, dd, flag))
print()
if onmargin:
    print('   CONFIRMED: %d of the four smallest sit on the hard-coded concyclicity'
          % onmargin)
    print('   margin, so the reported residual is measuring that constant, not')
    print('   unrealisability.  The patterns approach a four-concyclic configuration.')
else:
    print('   NOT reproduced at this tolerance; the residuals are equality-dominated.')

json.dump(dict(D1=rows, D1_confirmed=bool(fake), D2_on_margin=onmargin,
               completed=True), open('results/audit_recheck.json', 'w'), indent=1)
print()
print('=' * 78)
