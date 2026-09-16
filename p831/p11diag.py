"""Numerical diagnostic for a third-shape pattern: where do its complex solutions live?

msolve collapses six of the seven third-shape systems to {1} within a minute (mod p), but
pattern 11 ran past 10 GB without an answer.  That hints, without proving, that pattern 11
has complex solutions outside the degenerate loci.  This finds complex roots of the ten
radius equations (G1 gauge, P0 = (0,0), P1 = (1,0), unknowns x2..y4 and r0, r1, r2) by
damped Gauss-Newton from random complex starts, then for each root reports

  * degeneracy: the smallest |squared distance| and the smallest |r_a - r_b|, relative
    to the size of the configuration (both are exactly the saturated factors);
  * local dimension: 9 minus the numerical rank of the 10 x 9 Jacobian at the root;
  * whether it is real, and if real, whether it is admissible.

It proves nothing.  Its job is to say which exact computation fits: none needed if every
root is degenerate (as for pattern 5, the control), a zero-dimensional solve if there are
isolated non-degenerate roots, a curve analysis if the Jacobian drops rank.

Usage: python p11diag.py PATTERN [STARTS] [SEED]
"""
import json
import sys
from itertools import combinations

import numpy as np
import sympy as sp

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

TRI = list(combinations(range(5), 3))
pat = int(sys.argv[1])
starts = int(sys.argv[2]) if len(sys.argv) > 2 else 3000
rng = np.random.default_rng(int(sys.argv[3]) if len(sys.argv) > 3 else 831)
lab = json.load(open('results/penum_n5_k3.json'))['patterns'][pat]['labels']

X = sp.symbols('x2 y2 x3 y3 x4 y4')
R = sp.symbols('r0 r1 r2')
V = list(X) + list(R)
P = [(0, 0), (1, 0), (X[0], X[1]), (X[2], X[3]), (X[4], X[5])]


def d2(a, b):
    return (a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2


def cr(a, b, c):
    return (b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0])


F = [sp.expand(d2(P[j], P[k]) * d2(P[k], P[i]) * d2(P[i], P[j])
               - 4 * R[lab[n]] * cr(P[i], P[j], P[k]) ** 2) for n, (i, j, k) in enumerate(TRI)]
J = sp.Matrix(F).jacobian(V)
f_num = sp.lambdify(V, F, 'numpy')
j_num = sp.lambdify(V, J, 'numpy')
dists = sp.lambdify(V, [d2(P[a], P[b]) for a, b in combinations(range(5), 2)], 'numpy')


def solve(z):
    lam = 1e-3
    for _ in range(200):
        f = np.array(f_num(*z), dtype=complex)
        Jm = np.array(j_num(*z), dtype=complex)
        step = np.linalg.lstsq(Jm, -f, rcond=None)[0]
        z_new = z + step
        f_new = np.array(f_num(*z_new), dtype=complex)
        if np.linalg.norm(f_new) < np.linalg.norm(f):
            z = z_new
        else:
            z = z + 0.3 * step
        if np.linalg.norm(f_new) < 1e-13 * (1 + np.linalg.norm(z)) ** 6:
            break
    return z


roots = []
for s in range(starts):
    z0 = rng.normal(size=9) + 1j * rng.normal(size=9)
    try:
        z = solve(z0)
    except Exception:
        continue
    f = np.array(f_num(*z), dtype=complex)
    scale = 1 + float(np.max(np.abs(z[:6])))
    if not np.all(np.isfinite(z)) or np.linalg.norm(f) > 1e-10 * scale ** 6:
        continue
    dd = np.abs(np.array(dists(*z), dtype=complex))
    mind = float(np.min(np.abs(np.array([1.0] + list(dd))))) / scale ** 2
    rr = z[6:]
    rsep = min(abs(rr[a] - rr[b]) for a, b in ((0, 1), (0, 2), (1, 2))) / (1 + float(np.max(np.abs(rr))))
    sv = np.linalg.svd(np.array(j_num(*z), dtype=complex), compute_uv=False)
    rank = int(np.sum(sv > 1e-8 * sv[0]))
    real = float(np.max(np.abs(z.imag))) < 1e-8 * scale
    roots.append(dict(mind=mind, rsep=float(rsep), rank=rank, real=real,
                      smallest_sv=float(sv[-1] / sv[0]), z=[complex(c) for c in z]))

deg = [r for r in roots if r['mind'] < 1e-6 or r['rsep'] < 1e-6]
nondeg = [r for r in roots if not (r['mind'] < 1e-6 or r['rsep'] < 1e-6)]
print('pattern %d: %d starts, %d converged roots' % (pat, starts, len(roots)))
print('  degenerate (a saturated factor below 1e-6): %d' % len(deg))
print('  NON-degenerate: %d' % len(nondeg))
if nondeg:
    from collections import Counter
    print('    Jacobian rank at non-degenerate roots (9 = isolated):',
          dict(Counter(r['rank'] for r in nondeg)))
    print('    real non-degenerate roots: %d' % sum(1 for r in nondeg if r['real']))
    print('    smallest relative separation seen: dist %.2e, radii %.2e'
          % (min(r['mind'] for r in nondeg), min(r['rsep'] for r in nondeg)))
json.dump(dict(pattern=pat, starts=starts, converged=len(roots), degenerate=len(deg),
               nondegenerate=len(nondeg),
               ranks=sorted({r['rank'] for r in nondeg}),
               real_nondegenerate=sum(1 for r in nondeg if r['real']),
               sample=[dict(mind=r['mind'], rsep=r['rsep'], rank=r['rank'], real=r['real'],
                            z=[[c.real, c.imag] for c in r['z']]) for r in nondeg[:20]]),
          open('results/p11diag_pattern%d.json' % pat, 'w'), indent=1)
