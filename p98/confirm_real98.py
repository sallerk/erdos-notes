"""Exact confirmation that an n = 5, k = 4 pattern has a real admissible realisation.

Input: <dir>/<i>.lex, a lexicographic Groebner basis (Singular fglm, order t > u > w > x2 > x3 >
x4 > y2 > y3 > y4 > d0 > d1 > d2 > d3) of the sing98.py 'genfull' system for pattern i.  The
basis is only used to PROPOSE a solution; everything is then checked against the ORIGINAL
conditions, in exact arithmetic, without trusting Singular or msolve:

  1. factor the univariate polynomial in d3 over Q; take an irreducible factor f with a real
     root (Sturm count);
  2. the basis gives y4^2 = G(d3) and every other unknown as a polynomial in d3 and y4; all
     arithmetic is done in Q[d3]/(f) extended by y4 with y4^2 = G, exactly;
  3. every distance equation of the pattern and d_class(01) = 1 must reduce to exactly 0;
  4. every class difference, every d_c, the 10 triangle orientations and the 5 concyclicity
     determinants must be non-zero: for a + b*y4 this is shown by a^2 - G*b^2 != 0 in
     Q[d3]/(f), which forces a + b*y4 != 0 at every root;
  5. reality: a rational isolating interval for the real root of f, and interval arithmetic
     showing G > 0 on it, so y4 is real and so is every coordinate.
Then the configuration is printed to 30 digits for inspection.

Usage: python confirm_real98.py <patterns.json> <dir> <i> [<i> ...]
"""
import json
import re
import sys
from fractions import Fraction
from itertools import combinations

import sympy as sp

N = 5
PAIRS = list(combinations(range(N), 2))


def ivl_eval(poly, lo, hi):
    """rigorous interval enclosure of a univariate rational polynomial on [lo, hi]"""
    res = (Fraction(0), Fraction(0))
    for c in poly.all_coeffs():  # Horner with interval multiplication
        prods = [res[0] * lo, res[0] * hi, res[1] * lo, res[1] * hi]
        c = Fraction(int(sp.Rational(c).p), int(sp.Rational(c).q))
        res = (min(prods) + c, max(prods) + c)
    return res


def main():
    patfile, d = sys.argv[1], sys.argv[2]
    pats = json.load(open(patfile))['patterns']
    d3, y4 = sp.symbols('d3 y4')
    for i in map(int, sys.argv[3:]):
        pat = pats[i]
        k = max(pat) + 1
        names = ['t', 'u', 'w', 'x2', 'x3', 'x4', 'y2', 'y3', 'y4'] + ['d%d' % c for c in range(k)]
        S = {v: sp.Symbol(v) for v in names}
        txt = open('%s/%d.lex' % (d, i)).read()
        assert re.fullmatch(r'[0-9a-z+\-*^, \n]*', txt), 'unexpected characters'
        J = [sp.Poly(sp.sympify(p.replace('^', '**'), locals=S), *[S[v] for v in names], domain='QQ')
             for p in txt.split(',') if p.strip()]
        uni = [p for p in J if p.free_symbols <= {S['d3']}]
        assert len(uni) == 1
        P = sp.Poly(uni[0].as_expr(), d3)
        factors = [sp.Poly(f, d3) for f, _ in sp.factor_list(P.as_expr())[1]]
        yq = [p for p in J if S['y4'] in p.free_symbols and p.free_symbols <= {S['y4'], S['d3']}]
        assert len(yq) == 1
        e = sp.Poly(yq[0].as_expr(), y4)
        assert e.degree() == 2 and e.coeff_monomial(y4) == 0, 'expected A*y4^2 + B(d3)'
        Gexpr = -e.coeff_monomial(1) / e.coeff_monomial(y4 ** 2)
        report = {'pattern': pat, 'univariate_degree': P.degree(), 'factor_degrees': [f.degree() for f in factors]}
        confirmed = False
        for f in factors:
            if f.count_roots() == 0:
                continue
            Gp = sp.Poly(sp.rem(sp.Poly(sp.together(Gexpr), d3).as_expr(), f.as_expr(), d3), d3)

            def red(expr):
                """reduce to a + b*y4 with a, b in Q[d3]/(f)"""
                q = sp.Poly(sp.expand(expr), y4, d3)
                a = b = sp.Integer(0)
                for (ey, ed), c in q.terms():
                    term = c * d3 ** ed * Gp.as_expr() ** (ey // 2)
                    if ey % 2:
                        b += term
                    else:
                        a += term
                a = sp.rem(sp.expand(a), f.as_expr(), d3)
                b = sp.rem(sp.expand(b), f.as_expr(), d3)
                return sp.expand(a), sp.expand(b)

            val = {'d3': d3, 'y4': y4}
            for v in reversed(names[:-1]):          # d2, d1, d0, y4 (known), y3, ..., t
                if v == 'y4':
                    continue
                cands = [p for p in J if S[v] in p.free_symbols and
                         all(S[x] not in p.free_symbols for x in names[:names.index(v)])]
                cands = [p for p in cands if sp.Poly(p.as_expr(), S[v]).degree() == 1]
                assert cands, 'no linear equation for %s' % v
                pv = sp.Poly(cands[0].as_expr(), S[v])
                lead = pv.coeff_monomial(S[v])
                assert lead.free_symbols == set(), 'non-constant leading coefficient for %s' % v
                rest = -(pv.as_expr() - lead * S[v]) / lead
                sub = {S[x]: val[x] for x in val}
                a, b = red(rest.subs(sub))
                val[v] = a + b * y4
            X = [0, 1, val['x2'], val['x3'], val['x4']]
            Y = [0, 0, val['y2'], val['y3'], val['y4']]
            D = [val['d%d' % c] for c in range(k)]
            eq_ok = all(red((X[a] - X[b]) ** 2 + (Y[a] - Y[b]) ** 2 - D[c]) == (0, 0)
                        for (a, b), c in zip(PAIRS, pat)) and red(D[pat[0]] - 1) == (0, 0)

            def nonzero(expr):
                a, b = red(expr)
                return sp.rem(sp.expand(a * a - Gp.as_expr() * b * b), f.as_expr(), d3) != 0

            nz = {
                'classes_distinct': all(nonzero(D[a] - D[b]) for a, b in combinations(range(k), 2)),
                'distances_nonzero': all(nonzero(D[c]) for c in range(k)),
                'no_three_collinear': all(nonzero((X[b] - X[a]) * (Y[c] - Y[a]) - (X[c] - X[a]) * (Y[b] - Y[a]))
                                          for a, b, c in combinations(range(N), 3)),
                'no_four_concyclic': all(nonzero(sp.Matrix([[X[u] ** 2 + Y[u] ** 2, X[u], Y[u], 1] for u in q]).det())
                                         for q in combinations(range(N), 4)),
            }
            real_ok = False
            for lo, hi in [iv for iv, _ in f.intervals(eps=sp.Rational(1, 10 ** 30))]:
                glo, ghi = ivl_eval(Gp, Fraction(int(lo.p), int(lo.q)), Fraction(int(hi.p), int(hi.q)))
                if glo > 0:
                    real_ok = True
                    root = sp.Rational(lo + hi, 2)
                    num = {v: sp.N(val[v].subs({d3: root, y4: sp.sqrt(Gp.as_expr().subs(d3, root))}), 30)
                           for v in ('x2', 'x3', 'x4', 'y2', 'y3', 'y4')}
                    report['sample_points'] = [['0', '0'], ['1', '0']] + [[str(num['x%d' % j]), str(num['y%d' % j])] for j in (2, 3, 4)]
                    break
            report['factor_used'] = str(f.as_expr())
            report['equations_exact'] = eq_ok
            report['nondegeneracy_exact'] = nz
            report['real'] = real_ok
            if eq_ok and all(nz.values()) and real_ok:
                confirmed = True
                break
        report['CONFIRMED_REAL_ADMISSIBLE'] = confirmed
        print(json.dumps(report, indent=1))


if __name__ == '__main__':
    main()
