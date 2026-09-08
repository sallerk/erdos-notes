"""Exact decision of every pattern by a Groebner basis over Q.

patterns.py finds realisations numerically.  A failed numerical search is not a proof
that a pattern is unrealisable, and at n = 5 three patterns came within 1e-5 of the
residual threshold, which is what a search converging to a DEGENERATE limit (two points
merging) looks like.  This file settles each pattern exactly.

For a pattern (a k-colouring of the pairs of K_n) the system is

    |P_a - P_b|^2 = v_{colour(ab)}   for every pair,
    P_0 = (0,0), P_1 = (1,0)          (translation, rotation, scale),
    t * prod_{c != colour(01)} v_c = 1 (every class value nonzero).

Every pair's squared distance is some v_c, so "all v_c nonzero" is exactly "all points
distinct"; the last equation saturates the degenerate solutions away.  A reduced Groebner
basis equal to [1] means the system has no solution over C, hence none over R: the
pattern is unrealisable with distinct points, and that is a proof (modulo sympy's
Buchberger implementation, which is the only thing trusted here).

For realisable patterns the zero-dimensional system is solved exactly and every real
solution is listed; shapes are grouped by their scale-free sorted distance multiset,
which is the only thing delta depends on.

Usage: python pexact.py <n> <k>
"""
import sys
import json
import time
from itertools import combinations

import sympy as sp

sys.stdout.reconfigure(encoding='utf-8', errors='replace')
from patterns import enumerate_patterns


def system(n, pairs, labels, k):
    P = {0: (sp.Integer(0), sp.Integer(0)), 1: (sp.Integer(1), sp.Integer(0))}
    var = []
    for i in range(2, n):
        xi, yi = sp.symbols('x%d y%d' % (i, i))
        P[i] = (xi, yi)
        var += [xi, yi]
    c0 = labels[pairs.index((0, 1))]
    v = {}
    for c in range(k):
        if c == c0:
            v[c] = sp.Integer(1)
        else:
            v[c] = sp.Symbol('v%d' % c)
            var.append(v[c])
    t = sp.Symbol('t')
    eqs = []
    for (a, b), c in zip(pairs, labels):
        if (a, b) == (0, 1):
            continue
        d2 = (P[a][0] - P[b][0]) ** 2 + (P[a][1] - P[b][1]) ** 2
        eqs.append(sp.expand(d2 - v[c]))
    prod = sp.Integer(1)
    for c in range(k):
        if c != c0:
            prod *= v[c]
    eqs.append(sp.expand(t * prod - 1))
    return var + [t], eqs, P, v


def count_solutions(G, var):
    """number of solutions over C with multiplicity of a zero-dimensional ideal: the number
    of standard monomials (monomials not divisible by any leading monomial of the reduced
    Groebner basis).  If sympy's solve returns exactly this many distinct solutions, the
    solution list is complete and every root is simple."""
    lead = [sp.Poly(g, *var).monoms(order='grevlex')[0] for g in G.exprs]
    nv = len(var)
    seen = set()
    stack = [tuple([0] * nv)]
    while stack:
        m = stack.pop()
        if m in seen:
            continue
        if any(all(m[i] >= L[i] for i in range(nv)) for L in lead):
            continue
        seen.add(m)
        if len(seen) > 100000:
            return None
        for i in range(nv):
            mm = list(m); mm[i] += 1
            stack.append(tuple(mm))
    return len(seen)


def real_solutions(var, eqs):
    """all real solutions of a zero-dimensional system, exactly"""
    sols = sp.solve(eqs, var, dict=True)
    out = []
    for s in sols:
        if all(sp.im(sp.N(s[x], 60)) == 0 or abs(sp.im(sp.N(s[x], 60))) < sp.Float('1e-50', 60)
               for x in var):
            out.append(s)
    return out, len(sols)


def shapes_of(n, pairs, P, sols):
    """group real solutions by scale-free sorted distance multiset; compute delta exactly"""
    groups = {}
    for s in sols:
        # sympy writes real algebraic numbers through complex radicals (casus
        # irreducibilis), so a real solution can evaluate with an imaginary part of
        # 1e-58 at 60 digits; real_solutions() has already checked it is below 1e-50
        pts = [(sp.re(sp.N(P[i][0].subs(s), 60)) if i >= 2 else P[i][0],
                sp.re(sp.N(P[i][1].subs(s), 60)) if i >= 2 else P[i][1]) for i in range(n)]
        d = sorted(sp.sqrt((pts[a][0] - pts[b][0]) ** 2 + (pts[a][1] - pts[b][1]) ** 2)
                   for a, b in pairs)
        d = [sp.N(x, 60) for x in d]
        if d[0] < sp.Float('1e-40', 60):
            continue                                        # cannot happen after saturation
        key = tuple(str(sp.N(x / d[0], 25)) for x in d)
        # distinct values
        vals = []
        for x in d:
            if not vals or abs(x - vals[-1]) > sp.Float('1e-40', 60):
                vals.append(x)
        gaps = [vals[i + 1] - vals[i] for i in range(len(vals) - 1)]
        g = min([vals[0]] + gaps)
        delta = vals[-1] / g
        groups.setdefault(key, dict(delta=str(sp.N(delta, 20)), k=len(vals),
                                    values=[str(sp.N(x / vals[0], 20)) for x in vals],
                                    multiplicity=[sum(1 for x in d if abs(x - y) < sp.Float('1e-40', 60)) for y in vals],
                                    count=0, solutions=[]))
        groups[key]['count'] += 1
        # every real solution's coordinates, 60 digits, for the extension step
        groups[key]['solutions'].append([[str(sp.N(pts[i][0], 60)), str(sp.N(pts[i][1], 60))]
                                         for i in range(n)])
    return list(groups.values())


if __name__ == '__main__':
    n = int(sys.argv[1]); k = int(sys.argv[2])
    t0 = time.time()
    pairs, pats = enumerate_patterns(n, k)
    print('n=%d k=%d : %d canonical patterns' % (n, k, len(pats)), flush=True)
    out = dict(n=n, k=k, patterns=len(pats), results=[], completed=False)
    fn = 'results/pexact_n%d_k%d.json' % (n, k)
    for i, lab in enumerate(pats):
        t1 = time.time()
        var, eqs, P, v = system(n, pairs, lab, k)
        G = sp.groebner(eqs, *var, order='grevlex')
        infeasible = (len(G.exprs) == 1 and G.exprs[0] == 1)
        row = dict(i=i, labels=lab, infeasible=infeasible)
        if infeasible:
            print('  pattern %2d : NO solution over C with distinct points  (%.1fs)'
                  % (i, time.time() - t1), flush=True)
        else:
            zd = G.is_zero_dimensional
            row['zero_dimensional'] = bool(zd)
            if zd:
                bound = count_solutions(G, var)
                sols, ncomplex = real_solutions(var, eqs)
                sh = shapes_of(n, pairs, P, sols)
                complete = (bound is not None and ncomplex == bound)
                row.update(n_complex=ncomplex, n_complex_bound=bound, solve_complete=complete,
                           n_real=len(sols), shapes=sh)
                print('  pattern %2d : %d solutions over C (quotient dimension %s%s), %d real, %d distinct distance multisets  (%.1fs)'
                      % (i, ncomplex, bound, ', COMPLETE' if complete else ', NOT CERTIFIED COMPLETE',
                         len(sols), len(sh), time.time() - t1), flush=True)
                for s in sh:
                    print('               delta = %s  values %s  mult %s'
                          % (s['delta'][:14], [x[:10] for x in s['values']], s['multiplicity']))
            else:
                print('  pattern %2d : POSITIVE-DIMENSIONAL solution set, not handled here' % i,
                      flush=True)
        out['results'].append(row)
        json.dump(out, open(fn, 'w'), indent=1)
    out['completed'] = True
    out['seconds'] = round(time.time() - t0, 1)
    nin = sum(1 for r in out['results'] if r['infeasible'])
    best = None
    for r in out['results']:
        for s in r.get('shapes', []):
            if best is None or float(s['delta']) < float(best['delta']):
                best = dict(pattern=r['i'], **s)
    out['infeasible'] = nin
    out['best'] = best
    json.dump(out, open(fn, 'w'), indent=1)
    print()
    print('%d of %d patterns unrealisable (exact); best delta over the rest: %s'
          % (nin, len(pats), best['delta'] if best else 'none'))
