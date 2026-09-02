"""Corrected branch analysis for the single surviving 6-point 3-distance pattern.

six_pattern.py got the eliminant right, u^3 - 5u^2 + 6u - 1, but then threw all three
roots away: sympy returns them in casus-irreducibilis form (radicals containing I even
though the roots are real), and `is_real` on those expressions does not resolve, so the
script silently classified every branch as non-real and announced a conclusion it had not
earned.  All three roots ARE real and positive, near 0.198, 1.555 and 3.247.

The fix is to use CRootOf / real_roots, which are guaranteed-real algebraic numbers with
reliable exact comparison, instead of radical expressions.
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
    D[(i, j)] = D[(j, i)] = VAL[PAT[idx]]
for i in range(6):
    D[(i, i)] = sp.Integer(0)

G = sp.Matrix(5, 5, lambda a, b: sp.Rational(1, 2) *
              (D[(0, a + 1)] + D[(0, b + 1)] - D[(a + 1, b + 1)]))

minors = set()
for rows in itertools.combinations(range(5), 3):
    for cols in itertools.combinations(range(5), 3):
        e = sp.expand(G[list(rows), list(cols)].det())
        if e != 0:
            minors.add(sp.factor(e))
eqs = sorted(minors, key=sp.count_ops)

print('=' * 74)
print('CORRECTED BRANCH ANALYSIS')
print('=' * 74)
GB = sp.groebner(eqs, v, u, order='lex')
print('  Groebner basis (lex, v > u):')
for g in GB.exprs:
    print('     ', sp.factor(g))
print()

uni = [sp.Poly(g, u) for g in GB.exprs if g.free_symbols <= {u}]
assert uni, 'no univariate eliminant'
P = uni[0]
print('  eliminant:', P.as_expr())
print('  discriminant:', sp.discriminant(P.as_expr(), u),
      '(positive => three distinct real roots)')
roots = sp.real_roots(P.as_expr(), u)
print('  real roots (CRootOf, guaranteed real):')
for r in roots:
    print('     %s  ~ %.9f' % (r, float(r)))
print()

vpolys = [g for g in GB.exprs if v in g.free_symbols]
admissible = []
for r in roots:
    rf = float(r)
    print('  --- u = %.9f ---' % rf)
    if rf <= 0:
        print('      rejected: squared distance must be positive')
        continue
    cands = set()
    for g in vpolys:
        gp = sp.Poly(sp.expand(g), v)
        if gp.degree() < 1:
            continue
        # substitute the algebraic number, then take real roots in v
        coeffs = [sp.simplify(c.subs(u, r)) for c in gp.all_coeffs()]
        pv = sum(c * v ** (gp.degree() - i) for i, c in enumerate(coeffs))
        pv = sp.simplify(pv)
        if pv == 0:
            continue
        try:
            for s in sp.solve(sp.Eq(pv, 0), v):
                cands.add(sp.nsimplify(s))
        except Exception:
            pass
    ok = []
    for s in cands:
        try:
            sf = complex(sp.N(s, 30))
        except Exception:
            continue
        if abs(sf.imag) > 1e-20:
            continue
        sf = sf.real
        # must satisfy EVERY basis polynomial, not just the one it came from
        if any(abs(complex(sp.N(g.subs({u: r, v: s}), 30))) > 1e-20 for g in GB.exprs):
            continue
        ok.append((s, sf))
    print('      consistent real v: %s' % ([round(x[1], 9) for x in ok] or 'none'))
    for s, sf in ok:
        if sf <= 0:
            print('      v = %.9f rejected: not positive' % sf)
            continue
        if abs(sf - rf) < 1e-18 or abs(sf - 1) < 1e-18 or abs(rf - 1) < 1e-18:
            print('      v = %.9f rejected: the three classes must be distinct' % sf)
            continue
        Gs = G.subs({u: r, v: s})
        Gn = sp.Matrix(5, 5, lambda a, b: sp.N(Gs[a, b], 40))
        ev = sorted([sp.N(e, 30) for e in Gn.eigenvals()], key=lambda z: float(sp.re(z)))
        neg = [e for e in ev if float(sp.re(e)) < -1e-20]
        pos = [e for e in ev if float(sp.re(e)) > 1e-20]
        print('      v = %.9f: Gram eigenvalues %s' % (sf, [float(sp.re(e)) for e in ev]))
        print('         negative %d, positive %d  -> PSD %s, rank %d'
              % (len(neg), len(pos), not neg, len(pos)))
        if not neg and len(pos) <= 2:
            admissible.append((r, s))
            print('         *** ADMISSIBLE: realisable in the plane ***')
        else:
            print('         rejected: needs PSD with rank <= 2 for a planar realisation')

print()
print('=' * 74)
if not admissible:
    print('NO admissible (u, v).  The pattern is NOT realisable in the plane.')
    print('Since it was the only surviving candidate, D_gen(6) > 3;')
    print('with the verified 4-distance witness, D_gen(6) = 4.')
else:
    print('ADMISSIBLE branches: %s' % admissible)
    print('These still need the no-3-collinear / no-4-cocircular check.')
