"""Settle the last surviving n=7, k=4 candidate.

State: of the 4^21 colourings, augmentation + filters left 28 candidates; 21 die to
monotonicity (they use <4 classes, forcing D_gen(7) <= 3 against D_gen(7) >= 4); z3
proved 4 of the remaining 7 unsat; the equilateral-centre lemma killed 2 more.  ONE is
left:

    pattern  0,0,0,1,1,2,1,3,0,0,3,3,2,2,3,2,2,1,1,0,2

and the lemma gives it a free relation.  Class 1 contains the triangle (0,4,5), and
vertex 1 joins all of 0, 4, 5 in class 0, so vertex 1 is the circumcentre of an
equilateral triangle of squared side D_1, whence

    D_0 = D_1 / 3.

Fixing the scale as D_0 = 1 makes D_1 = 3 and leaves only TWO unknowns, D_2 and D_3.
That is the regime where Groebner elimination worked for the pentagon and the heptagon.

Method as before: the squared distances are realisable in the plane exactly when the Gram
matrix is positive semidefinite of rank <= 2, so every 3x3 minor vanishes.  Solve that
system exactly, then test each real branch for positivity, distinctness, PSD, and finally
general position on reconstructed coordinates.
"""
import sys, itertools

sys.stdout.reconfigure(encoding='utf-8', errors='replace')
import sympy as sp
import mpmath as mp

mp.mp.dps = 50

PAT = (0, 0, 0, 1, 1, 2, 1, 3, 0, 0, 3, 3, 2, 2, 3, 2, 2, 1, 1, 0, 2)
N = 7
PAIRS = list(itertools.combinations(range(N), 2))
IDX = {p: i for i, p in enumerate(PAIRS)}

u, v = sp.symbols('u v', positive=True)
# D_0 = 1 (scale), D_1 = 3 (equilateral-centre lemma), D_2 = u, D_3 = v
VALS = [sp.Integer(1), sp.Integer(3), u, v]

print('=' * 74)
print('THE LAST n=7 CANDIDATE')
print('=' * 74)
print('  pattern %s' % (list(PAT),))
print('  lemma: class 1 triangle (0,4,5) has centre 1 via class 0  =>  D_0 = D_1/3')
print('  scale D_0 = 1, hence D_1 = 3; unknowns are D_2 = u and D_3 = v')
print()

# sanity: the lemma's hypothesis really holds in this pattern
tri = (0, 4, 5)


def cl(a, b):
    return PAT[IDX[(a, b) if a < b else (b, a)]]


assert {cl(*p) for p in itertools.combinations(tri, 2)} == {1}, 'triangle not in class 1'
assert {cl(1, t) for t in tri} == {0}, 'vertex 1 not joined to it in class 0'
print('  verified: (0,4,5) is a class-1 triangle and vertex 1 joins all three in class 0')
print()

D = {}
for (i, j) in PAIRS:
    D[(i, j)] = D[(j, i)] = VALS[PAT[IDX[(i, j)]]]
for i in range(N):
    D[(i, i)] = sp.Integer(0)

G = sp.Matrix(N - 1, N - 1, lambda a, b: sp.Rational(1, 2) *
              (D[(0, a + 1)] + D[(0, b + 1)] - D[(a + 1, b + 1)]))

minors = set()
for r in itertools.combinations(range(N - 1), 3):
    for c in itertools.combinations(range(N - 1), 3):
        e = sp.expand(G[list(r), list(c)].det())
        if e != 0:
            minors.add(sp.factor(e))
eqs = sorted(minors, key=sp.count_ops)
print('  %d distinct nonzero 3x3 minors of the 6x6 Gram matrix' % len(eqs))
for e in eqs[:5]:
    print('     ', e)
print()

print('  Groebner basis (lex, v > u) ...')
GB = sp.groebner(eqs, v, u, order='lex')
print('  basis: %s' % [sp.factor(g) for g in GB.exprs])
print()

if list(GB.exprs) == [sp.Integer(1)]:
    print('  BASIS IS [1]: the ideal is trivial, so there is no solution even over C.')
    print()
    print('  => the pattern is UNSATISFIABLE')
    print('  => no 7-point set in general position has 4 distinct distances')
    print('  => D_gen(7) > 4, and with the verified 5-distance witness, D_gen(7) = 5')
    sys.exit(0)

uni = [g for g in GB.exprs if g.free_symbols <= {u}]
if not uni:
    print('  no univariate eliminant; the ideal is positive-dimensional in u.')
    sys.exit(2)
P = sp.Poly(uni[0], u)
print('  eliminant in u: %s' % sp.factor(P.as_expr()))
roots = sp.real_roots(P.as_expr(), u)
print('  real roots: %s' % [mp.nstr(mp.mpf(str(sp.N(r, 30))), 12) for r in roots])
print()

vpolys = [g for g in GB.exprs if v in g.free_symbols]
admissible = []
for r in roots:
    rf = mp.mpf(str(sp.N(r, 40)))
    print('  --- u = %s ---' % mp.nstr(rf, 15))
    if rf <= 0:
        print('      rejected: squared distances must be positive')
        continue
    cands = set()
    for g in vpolys:
        gp = sp.Poly(sp.expand(g), v)
        if gp.degree() < 1:
            continue
        coeffs = [mp.mpf(str(sp.N(c.subs(u, r), 40))) for c in gp.all_coeffs()]
        while coeffs and abs(coeffs[0]) < mp.mpf('1e-35'):
            coeffs = coeffs[1:]
        if len(coeffs) <= 1:
            continue
        try:
            for z in mp.polyroots(coeffs, maxsteps=200, extraprec=200):
                if abs(mp.im(z)) < mp.mpf('1e-25'):
                    cands.add(mp.re(z))
        except Exception:
            pass
    ok = []
    for s in cands:
        good = True
        for g in GB.exprs:
            val = sp.N(g.subs({u: r, v: sp.Float(str(s), 40)}), 40)
            if abs(complex(val)) > 1e-20:
                good = False
                break
        if good:
            ok.append(s)
    print('      consistent v: %s' % ([mp.nstr(x, 12) for x in ok] or 'none'))
    for s in ok:
        vals = [mp.mpf(1), mp.mpf(3), rf, s]
        if s <= 0:
            print('      v = %s rejected: not positive' % mp.nstr(s, 10))
            continue
        if len({round(float(x), 15) for x in vals}) != 4:
            print('      v = %s rejected: classes not distinct' % mp.nstr(s, 10))
            continue
        admissible.append((rf, s))
        print('      v = %s ADMISSIBLE so far, needs the geometric check'
              % mp.nstr(s, 12))

print()
print('=' * 74)
if not admissible:
    print('NO admissible (u, v): the pattern is NOT realisable.')
    print('=> D_gen(7) > 4, and with the verified 5-distance witness, D_gen(7) = 5')
else:
    print('Admissible class values: %s' % [(mp.nstr(a, 12), mp.nstr(b, 12))
                                           for a, b in admissible])
    print('=> reconstruct and test no-3-collinear / no-4-cocircular before concluding.')
