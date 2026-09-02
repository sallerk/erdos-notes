"""Settle the one pattern z3 could not decide: the pentagon pattern at n=5, k=2.

hdecide.py found 18 distance patterns on 5 points with 2 classes, up to relabelling.
Seventeen are UNSAT.  The survivor is

    class 0 (5 pairs): (0,1) (0,2) (1,3) (2,4) (3,4)     -- the 5-cycle 0-1-3-4-2-0
    class 1 (5 pairs): (0,3) (0,4) (1,2) (1,4) (2,3)     -- its complementary 5-cycle

i.e. an equilateral closed pentagon whose five diagonals are also all equal.  z3 returns
unknown on it after 600 s with both the default solver and qfnra-nlsat, so it is settled
here by exact elimination instead.

Plan: fix the isometry and the scale, write the nine polynomial equations, take a
Groebner basis, and read off every real solution branch.  Then test cocircularity on each
branch.  If every branch is cocircular the pattern is excluded and D_gen(5) > 2.
"""
import sys, itertools

sys.stdout.reconfigure(encoding='utf-8', errors='replace')
import sympy as sp

x2, y2, x3, y3, x4, y4, t = sp.symbols('x2 y2 x3 y3 x4 y4 t', real=True)

P = {0: (sp.Integer(0), sp.Integer(0)),
     1: (sp.Integer(1), sp.Integer(0)),
     2: (x2, y2), 3: (x3, y3), 4: (x4, y4)}

SHORT = [(0, 1), (0, 2), (1, 3), (2, 4), (3, 4)]
LONG = [(0, 3), (0, 4), (1, 2), (1, 4), (2, 3)]


def d2(i, j):
    return sp.expand((P[i][0] - P[j][0]) ** 2 + (P[i][1] - P[j][1]) ** 2)


print('=' * 74)
print('THE PENTAGON PATTERN, settled by exact elimination')
print('=' * 74)
print()
print('  scale fixed by |p0 p1| = 1; isometry fixed by p0 = (0,0), p1 = (1,0)')
print('  short class -> squared distance 1,  long class -> squared distance t')
print()

eqs = []
for (i, j) in SHORT:
    if (i, j) != (0, 1):
        eqs.append(sp.expand(d2(i, j) - 1))
for (i, j) in LONG:
    eqs.append(sp.expand(d2(i, j) - t))

for e in eqs:
    print('   ', sp.factor(e), '= 0')
print()
print('  %d equations, 7 unknowns' % len(eqs))
print()

gens = [x2, y2, x3, y3, x4, y4, t]
print('  computing Groebner basis (lex, t last) ...')
G = sp.groebner(eqs, *gens, order='lex')
print('  basis has %d polynomials' % len(G.exprs))

# the last basis element in lex order with t alone is the eliminant
elim = [g for g in G.exprs if g.free_symbols <= {t}]
print()
if elim:
    for e in elim:
        ef = sp.factor(e)
        print('  ELIMINANT in t:', ef)
        roots = sp.solve(sp.Eq(e, 0), t)
        print('  roots:', roots)
        real_roots = [r for r in roots if r.is_real]
        print('  real roots:', real_roots)
        print()
        for r in real_roots:
            print('  --- branch t = %s  (%.6f) ---' % (sp.radsimp(r), float(r)))
            if float(r) <= 0:
                print('      rejected: t must be a positive squared distance')
                continue
            sol = sp.solve([sp.Eq(q.subs(t, r), 0) for q in eqs],
                           [x2, y2, x3, y3, x4, y4], dict=True)
            print('      %d solution(s) for the coordinates' % len(sol))
            for s in sol:
                pts = [(sp.simplify(P[i][0].subs(s) if hasattr(P[i][0], 'subs') else P[i][0]),
                        sp.simplify(P[i][1].subs(s) if hasattr(P[i][1], 'subs') else P[i][1]))
                       for i in range(5)]
                if any(v.free_symbols for v in itertools.chain(*pts)):
                    print('      (branch still has free parameters, skipping)')
                    continue
                if any(not v.is_real for v in itertools.chain(*pts)):
                    print('      complex, not a real configuration')
                    continue
                # degenerate?
                dup = any(sp.simplify((pts[i][0]-pts[j][0])**2+(pts[i][1]-pts[j][1])**2) == 0
                          for i, j in itertools.combinations(range(5), 2))
                if dup:
                    print('      degenerate: coincident points')
                    continue
                cyc = []
                for q in itertools.combinations(range(5), 4):
                    M = sp.Matrix([[pts[a][0]**2 + pts[a][1]**2, pts[a][0], pts[a][1], 1]
                                   for a in q])
                    if sp.simplify(M.det()) == 0:
                        cyc.append(q)
                print('      points:', [(sp.nsimplify(a), sp.nsimplify(b)) for a, b in pts])
                print('      cocircular quadruples: %d %s'
                      % (len(cyc), cyc if cyc else '(NONE -- this would be a counterexample)'))
else:
    print('  no univariate eliminant in t found; printing the basis instead')
    for g in G.exprs:
        print('   ', g)
