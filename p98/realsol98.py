"""Classify EVERY real solution of a zero-dimensional pattern system, exactly (n points, k classes).

Input: <dir>/<i>.sing (sing98.py, plain system: distinct classes, non-zero distances) and
<dir>/<i>.lex, its lexicographic Groebner basis from Singular's fglm.  The basis only proposes
solutions.  For each irreducible factor f of the univariate polynomial in the last variable,
every unknown is written in Q[z]/(f), extended by one square root s with s^2 = G(z) when the
basis has one quadratic unknown, and then, in exact arithmetic:
  * every ORIGINAL equation must reduce to 0 (else the script stops);
  * each non-degeneracy quantity (class differences, distances, the C(n,3) triangle
    orientations, the C(n,4) concyclicity determinants) a + b*s is classified:
      a = b = 0            -> zero at every root of this factor;
      a^2 - G*b^2 != 0     -> non-zero at every root;
      otherwise            -> decided per real root numerically (60 digits) and marked so;
  * real solutions: the real roots of f (rational isolating intervals), and for each one the
    sign of G on the interval (interval arithmetic): G > 0 gives two real solutions, G < 0 none.
A real solution with every quantity non-zero is an admissible realisation of the pattern.

Usage: python realsol98.py <n> <patterns.json> <dir> <i> [<i> ...]
"""
import json
import re
import sys
from fractions import Fraction
from itertools import combinations

import mpmath
import sympy as sp

mpmath.mp.dps = 60


def ivl_eval(poly, lo, hi):
    res = (Fraction(0), Fraction(0))
    for c in poly.all_coeffs():
        prods = [res[0] * lo, res[0] * hi, res[1] * lo, res[1] * hi]
        c = Fraction(int(sp.Rational(c).p), int(sp.Rational(c).q))
        res = (min(prods) + c, max(prods) + c)
    return res


def main():
    n = int(sys.argv[1])
    pats = json.load(open(sys.argv[2]))['patterns']
    d = sys.argv[3]
    pairs = list(combinations(range(n), 2))
    for i in map(int, sys.argv[4:]):
        pat = pats[i]
        k = max(pat) + 1
        src = open('%s/%d.sing' % (d, i)).read()
        names = re.search(r'ring R = 0, \((.*?)\), dp;', src).group(1).split(',')
        S = {v: sp.Symbol(v) for v in names}
        txt = open('%s/%d.lex' % (d, i)).read()
        assert re.fullmatch(r'[0-9a-z+\-*^, \n]*', txt)
        J = [sp.Poly(sp.sympify(p.replace('^', '**'), locals=S), *[S[v] for v in names], domain='QQ')
             for p in txt.split(',') if p.strip()]
        z = S[names[-1]]
        s = sp.Symbol('s')
        uni = [p for p in J if p.free_symbols <= {z}]
        assert len(uni) == 1
        rep = {}
        ext_var, Gexpr = None, None
        for v in reversed(names[:-1]):
            cands = [p for p in J if S[v] in p.free_symbols and
                     all(S[x] not in p.free_symbols for x in names[:names.index(v)])]
            assert cands, 'no equation for ' + v
            pv = sp.Poly(cands[0].as_expr(), S[v])
            if pv.degree() == 1 and not pv.coeff_monomial(S[v]).free_symbols:
                rep[v] = ('lin', -(pv.as_expr() - pv.coeff_monomial(S[v]) * S[v]) / pv.coeff_monomial(S[v]))
            elif pv.degree() == 2 and pv.coeff_monomial(S[v]) == 0 and not pv.coeff_monomial(S[v] ** 2).free_symbols:
                assert ext_var is None, 'more than one square root'
                ext_var = v
                Gexpr = -pv.coeff_monomial(1) / pv.coeff_monomial(S[v] ** 2)
                rep[v] = ('ext', None)
            else:
                raise SystemExit('unsupported basis shape at ' + v)
        out = {'pattern': pat, 'classes': k, 'factors': []}
        for fexpr, _ in sp.factor_list(uni[0].as_expr())[1]:
            f = sp.Poly(fexpr, z)
            nreal = f.count_roots()
            entry = {'factor': str(fexpr), 'degree': int(f.degree()), 'real_roots_of_factor': int(nreal)}
            if nreal == 0:
                out['factors'].append(entry)
                continue
            G = sp.Poly(sp.rem(sp.together(Gexpr.subs({S[x]: 0 for x in []})).as_expr(), f.as_expr(), z), z) \
                if Gexpr is not None else None

            def red(expr):
                q = sp.Poly(sp.expand(expr), s, z)
                a = b = sp.Integer(0)
                for (es, ez), c in q.terms():
                    term = c * z ** ez * (G.as_expr() ** (es // 2) if G is not None else 1)
                    if es % 2:
                        b += term
                    else:
                        a += term
                return sp.expand(sp.rem(sp.expand(a), f.as_expr(), z)), sp.expand(sp.rem(sp.expand(b), f.as_expr(), z))

            val = {names[-1]: z}
            for v in reversed(names[:-1]):
                kind, e = rep[v]
                if kind == 'ext':
                    val[v] = s
                else:
                    a, b = red(e.subs({S[x]: val[x] for x in val}))
                    val[v] = a + b * s
            X = [0, 1] + [val['x%d' % j] for j in range(2, n)]
            Y = [0, 0] + [val['y%d' % j] for j in range(2, n)]
            D = [val['d%d' % c] for c in range(k)]
            for (p, q), c in zip(pairs, pat):
                assert red((X[p] - X[q]) ** 2 + (Y[p] - Y[q]) ** 2 - D[c]) == (0, 0), 'equation fails'
            assert red(D[pat[0]] - 1) == (0, 0)
            quantities = ([('class %d = class %d' % (a, b), D[a] - D[b]) for a, b in combinations(range(k), 2)] +
                          [('distance class %d = 0' % c, D[c]) for c in range(k)] +
                          [('collinear %s' % (t,), (X[t[1]] - X[t[0]]) * (Y[t[2]] - Y[t[0]]) - (X[t[2]] - X[t[0]]) * (Y[t[1]] - Y[t[0]]))
                           for t in combinations(range(n), 3)] +
                          [('concyclic %s' % (q,), sp.Matrix([[X[u] ** 2 + Y[u] ** 2, X[u], Y[u], 1] for u in q]).det())
                           for q in combinations(range(n), 4)])
            classified = []
            for label, e in quantities:
                a, b = red(e)
                if a == 0 and b == 0:
                    classified.append((label, 'zero', a, b))
                elif sp.rem(sp.expand(a * a - (G.as_expr() if G is not None else 0) * b * b), f.as_expr(), z) != 0:
                    classified.append((label, 'nonzero', a, b))
                else:
                    classified.append((label, 'ambiguous', a, b))
            sols = []
            for (lo, hi), _ in f.intervals(eps=sp.Rational(1, 10 ** 40)):
                root = mpmath.mpf(sp.Rational(lo + hi, 2).p) / sp.Rational(lo + hi, 2).q
                if G is None:
                    signs = [0]
                else:
                    glo, ghi = ivl_eval(G, Fraction(int(lo.p), int(lo.q)), Fraction(int(hi.p), int(hi.q)))
                    if ghi < 0:
                        continue
                    if glo <= 0:
                        raise SystemExit('G changes sign on the root interval; refine')
                    signs = [1, -1]
                for sg in signs:
                    sval = sg * mpmath.sqrt(mpmath.polyval([mpmath.mpf(sp.Rational(c).p) / sp.Rational(c).q for c in G.all_coeffs()], root)) if G is not None else 0
                    fails = []
                    for label, kind, a, b in classified:
                        if kind == 'zero':
                            fails.append(label)
                        elif kind == 'ambiguous':
                            num = sp.lambdify((z, s), a + b * s, 'mpmath')(root, sval)
                            if abs(num) < mpmath.mpf(10) ** -40:
                                fails.append(label + ' (numeric)')
                    sols.append({'root_interval': [str(lo), str(hi)], 'sqrt_sign': int(sg), 'degeneracies': fails,
                                 'ADMISSIBLE': not fails})
            entry['real_solutions'] = sols
            out['factors'].append(entry)
        out['any_admissible_real_solution'] = any(sol['ADMISSIBLE'] for fe in out['factors'] for sol in fe.get('real_solutions', []))
        print(json.dumps(out))


if __name__ == '__main__':
    main()
