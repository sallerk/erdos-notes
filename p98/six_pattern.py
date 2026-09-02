"""SUPERSEDED AND UNSOUND -- DO NOT USE. See six_pattern2/3/4.py instead.

This script reaches the correct verdict by faulty reasoning and is kept only as a record
of the error.  It computes the eliminant u^3 - 5u^2 + 6u - 1 correctly, but sympy returns
that cubic's roots in casus-irreducibilis form (radicals containing I although all three
roots are real), `is_real` does not resolve on those expressions, and every branch is
therefore silently discarded as non-real.  The printed conclusion is right; the argument
for it is not.

Redone properly in six_pattern2.py (CRootOf, guaranteed-real roots), six_pattern3.py
(PSD test on the surviving branches) and six_pattern4.py (reconstruction and the
general-position check, which is what actually kills the pattern).
"""

"""Settle the single surviving 6-point 3-distance pattern, by exact elimination.

Augmentation reduced the whole question "is D_gen(6) = 3?" from 3^15 = 14,348,907 raw
colourings to ONE candidate pattern, on which the generic Gram decider returns
inconclusive (sympy.solve leaves branches unevaluated).  This settles it directly.

The pattern splits the 15 edges of K6 into three classes of five, each of which is a
Hamiltonian path:

    class 0 (squared distance 1):  4-2-0-1-3-5
    class 1 (squared distance u):  3-0-4-5-1-2
    class 2 (squared distance v):  0-5-2-3-4-1

Method.  Realisability in the plane is equivalent to the Gram matrix
G_ij = (d_0i + d_0j - d_ij)/2, i,j = 1..5, being positive semidefinite of rank <= 2.
Rank <= 2 means every 3x3 minor vanishes.  Those minors are polynomials in u and v only,
so a lex Groebner basis gives a univariate eliminant; each root is then checked for
reality, positivity, distinctness of the three classes, PSD-ness, and finally the
geometric side conditions on reconstructed coordinates.

Scale is fixed by taking the class-0 squared distance to be 1.
"""
import sys, itertools

sys.stdout.reconfigure(encoding='utf-8', errors='replace')
import sympy as sp

u, v = sp.symbols('u v', real=True)

PAT = (0, 0, 1, 1, 2, 1, 0, 2, 1, 2, 0, 2, 2, 0, 1)
PAIRS = list(itertools.combinations(range(6), 2))
VAL = {0: sp.Integer(1), 1: u, 2: v}
D = {}
for idx, (i, j) in enumerate(PAIRS):
    D[(i, j)] = VAL[PAT[idx]]
    D[(j, i)] = VAL[PAT[idx]]
for i in range(6):
    D[(i, i)] = sp.Integer(0)

print('=' * 74)
print('THE SINGLE SURVIVING 6-POINT 3-DISTANCE PATTERN')
print('=' * 74)
print()
print('  squared distances (class 0 = 1, class 1 = u, class 2 = v):')
for (i, j) in PAIRS:
    print('     d(%d,%d)^2 = %s' % (i, j, D[(i, j)]))
print()

G = sp.Matrix(5, 5, lambda a, b: sp.Rational(1, 2) *
              (D[(0, a + 1)] + D[(0, b + 1)] - D[(a + 1, b + 1)]))
print('  Gram matrix (base point 0):')
sp.pprint(G)
print()

minors = set()
for rows in itertools.combinations(range(5), 3):
    for cols in itertools.combinations(range(5), 3):
        e = sp.expand(G[list(rows), list(cols)].det())
        if e != 0:
            minors.add(sp.factor(e))
eqs = sorted(minors, key=sp.count_ops)
print('  %d distinct nonzero 3x3 minors; rank <= 2 forces every one to vanish' % len(eqs))
for e in eqs[:6]:
    print('     ', e)
if len(eqs) > 6:
    print('      ... and %d more' % (len(eqs) - 6))
print()

print('  lex Groebner basis, eliminating v ...')
GB = sp.groebner(eqs, v, u, order='lex')
print('  basis size %d' % len(GB.exprs))
uni = [g for g in GB.exprs if g.free_symbols <= {u}]
print()
if not uni:
    print('  NO univariate eliminant in u: the ideal is positive-dimensional in u.')
    for g in GB.exprs:
        print('     ', sp.factor(g))
    sys.exit(2)

for e in uni:
    print('  ELIMINANT in u:', sp.factor(e))
allroots = set()
for e in uni:
    for r in sp.solve(sp.Eq(e, 0), u):
        allroots.add(sp.simplify(r))
print('  roots:', sorted(allroots, key=lambda z: (sp.im(z) != 0, sp.re(z))))
print()

found = []
for r in allroots:
    if not r.is_real:
        continue
    if r <= 0:
        print('  u = %s rejected: squared distances must be positive' % r)
        continue
    print('  --- branch u = %s  (%.6f) ---' % (sp.radsimp(r), float(r)))
    rest = [sp.simplify(g.subs(u, r)) for g in GB.exprs]
    rest = [g for g in rest if g != 0 and g.free_symbols]
    vs = set()
    for g in rest:
        for s in sp.solve(sp.Eq(g, 0), v):
            vs.add(sp.simplify(s))
    vs = {s for s in vs if all(sp.simplify(g.subs(v, s)) == 0 for g in rest)}
    print('      consistent v values: %s' % (sorted(vs, key=lambda z: (sp.im(z) != 0, sp.re(z))) or 'none'))
    for s in vs:
        if not s.is_real or s <= 0:
            print('      v = %s rejected (not a positive real)' % s)
            continue
        if sp.simplify(s - r) == 0 or sp.simplify(s - 1) == 0 or sp.simplify(r - 1) == 0:
            print('      v = %s rejected: the three classes must be DISTINCT' % s)
            continue
        Gs = G.subs({u: r, v: s})
        rk = Gs.rank()
        psd = all(Gs[list(c), list(c)].det() >= 0
                  for m in (1, 2) for c in itertools.combinations(range(5), m))
        print('      v = %s: Gram rank %s, PSD %s' % (sp.radsimp(s), rk, psd))
        if rk <= 2 and psd:
            found.append((r, s))
            print('      *** REALISABLE IN THE PLANE -- needs the geometric check ***')

print()
print('=' * 74)
if not found:
    print('NO admissible (u, v): the pattern is NOT realisable.')
    print('=> D_gen(6) > 3, and with the verified 4-distance witness, D_gen(6) = 4.')
else:
    print('Admissible class values found: %s' % found)
    print('=> reconstruct coordinates and test no-3-collinear / no-4-cocircular.')
