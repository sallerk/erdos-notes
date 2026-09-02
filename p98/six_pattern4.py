"""Reconstruct the three realisable branches and test general position.

six_pattern3.py showed the surviving 6-point 3-distance pattern IS metrically realisable:
all three roots of u^3 - 5u^2 + 6u - 1 give a positive-semidefinite rank-2 Gram matrix
with v = (u-1)^2.  So the pattern is not killed by the algebra, and everything depends on
the two geometric side conditions.

Suspicion worth stating up front: u ~ 3.246980 and v ~ 5.048917 are the squared-distance
ratios of the REGULAR HEPTAGON (with the short chord as unit, the medium and long chords
squared are sin^2(2pi/7)/sin^2(pi/7) and sin^2(3pi/7)/sin^2(pi/7)).  If these branches are
six of the seven vertices of a regular 7-gon, every point lies on one circle and the
configuration is excluded outright.  The other two roots are the Galois conjugates, the
"star" heptagons {7/2} and {7/3}, whose vertex sets are the same 7 concyclic points.

This script does not assume that.  It reconstructs coordinates from the Gram matrix at
60-digit precision, checks the reconstruction reproduces the intended distances, and then
evaluates every collinearity and cocircularity determinant.
"""
import sys, itertools

sys.stdout.reconfigure(encoding='utf-8', errors='replace')
import sympy as sp
import mpmath as mp

mp.mp.dps = 60

u = sp.symbols('u', real=True)
CUBIC = u ** 3 - 5 * u ** 2 + 6 * u - 1
PAT = (0, 0, 1, 1, 2, 1, 0, 2, 1, 2, 0, 2, 2, 0, 1)
PAIRS = list(itertools.combinations(range(6), 2))


def dmatrix(uu, vv):
    VAL = {0: mp.mpf(1), 1: uu, 2: vv}
    D = [[mp.mpf(0)] * 6 for _ in range(6)]
    for idx, (i, j) in enumerate(PAIRS):
        D[i][j] = D[j][i] = VAL[PAT[idx]]
    return D


print('=' * 74)
print('RECONSTRUCTION AND GENERAL-POSITION TEST')
print('=' * 74)

# the heptagon reference values, for comparison only
s1, s2, s3 = (mp.sin(mp.pi / 7) ** 2, mp.sin(2 * mp.pi / 7) ** 2,
              mp.sin(3 * mp.pi / 7) ** 2)
print('  regular heptagon squared-chord ratios (short = 1): %.12f, %.12f'
      % (s2 / s1, s3 / s1))
print()

roots = sp.real_roots(CUBIC, u)
concl = []
for ridx, r in enumerate(roots):
    uu = mp.mpf(str(sp.N(r, 60)))
    vv = (uu - 1) ** 2
    print('  --- branch %d:  u = %s' % (ridx, mp.nstr(uu, 20)))
    print('                 v = %s' % mp.nstr(vv, 20))
    D = dmatrix(uu, vv)
    G = mp.matrix(5, 5)
    for a in range(5):
        for b in range(5):
            G[a, b] = (D[0][a + 1] + D[0][b + 1] - D[a + 1][b + 1]) / 2
    E, V = mp.eigsy(G)
    order = sorted(range(5), key=lambda i: -E[i])
    keep = order[:2]
    print('      Gram eigenvalues: %s' % [mp.nstr(E[i], 12) for i in order])
    pts = [(mp.mpf(0), mp.mpf(0))]
    for i in range(5):
        pts.append(tuple(mp.sqrt(max(E[k], mp.mpf(0))) * V[i, k] for k in keep))

    # validate the reconstruction against the intended distances
    worst = mp.mpf(0)
    for (i, j) in PAIRS:
        got = (pts[i][0] - pts[j][0]) ** 2 + (pts[i][1] - pts[j][1]) ** 2
        worst = max(worst, abs(got - D[i][j]))
    print('      reconstruction error vs intended distances: %s' % mp.nstr(worst, 5))
    if worst > mp.mpf('1e-40'):
        print('      reconstruction unreliable, skipping')
        concl.append('unreliable')
        continue

    col = []
    for (a, b, c) in itertools.combinations(range(6), 3):
        d = ((pts[b][0] - pts[a][0]) * (pts[c][1] - pts[a][1])
             - (pts[c][0] - pts[a][0]) * (pts[b][1] - pts[a][1]))
        col.append((abs(d), (a, b, c)))
    cyc = []
    for q in itertools.combinations(range(6), 4):
        M = mp.matrix(4, 4)
        for rr, t in enumerate(q):
            M[rr, 0] = pts[t][0] ** 2 + pts[t][1] ** 2
            M[rr, 1] = pts[t][0]
            M[rr, 2] = pts[t][1]
            M[rr, 3] = mp.mpf(1)
        cyc.append((abs(mp.det(M)), q))
    mincol = min(col)
    maxcyc = max(cyc)
    print('      smallest |collinearity det| : %s   at %s'
          % (mp.nstr(mincol[0], 8), mincol[1]))
    print('      LARGEST  |cocircularity det|: %s   at %s'
          % (mp.nstr(maxcyc[0], 8), maxcyc[1]))
    ncyc = sum(1 for m, q in cyc if m < mp.mpf('1e-40'))
    print('      cocircular quadruples (|det| < 1e-40): %d of 15' % ncyc)
    if ncyc:
        print('      => EXCLUDED: four or more points lie on a circle')
        concl.append('excluded: cocircular')
    elif mincol[0] < mp.mpf('1e-40'):
        print('      => EXCLUDED: three points are collinear')
        concl.append('excluded: collinear')
    else:
        print('      => IN GENERAL POSITION: this would give D_gen(6) = 3')
        concl.append('GENERAL POSITION')
    print()

print('=' * 74)
print('branch verdicts: %s' % concl)
print()
if all(c.startswith('excluded') for c in concl):
    print('Every realisation of the only surviving candidate violates general position.')
    print('    => D_gen(6) > 3, and with the verified 4-distance witness, D_gen(6) = 4.')
else:
    print('At least one branch is in general position => D_gen(6) = 3.')
