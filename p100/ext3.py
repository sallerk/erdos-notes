"""E_{n+1}(<= K) from E_n(<= K): complete one-point extension, then exact certification.

Every (n+1)-point set with at most K distances contains n-point subsets with at most K
distances, so extending every member of E_n(<= K) by one point finds every member of
E_{n+1}(<= K).  A new point P is pinned by two independent conditions among "P is at an
old distance from a base point" (a circle) and "P is at the same new distance from two
base points" (a bisector), unless P has fewer than two such conditions, in which case
its n distances to the base are all new and pairwise distinct except at most one pair,
giving at least n - 1 new values; that exceeds K - k_base whenever n - 1 > K - 1, i.e.
n > K, which holds for every step used here (n >= 5, K = 3).  So the candidate set
(circle-circle, circle-line, line-line intersections) is complete.

Candidates are evaluated at 60 digits.  Every extension that survives is CERTIFIED
exactly afterwards: its colouring of the pairs is a pattern, and pexact.system() plus a
Groebner basis decides that pattern over Q; the set is kept only if the pattern is
feasible and one of its exact real solutions has the same distance multiset.  So the
list that comes out is exact, and the 60-digit arithmetic only steers the search.

Usage: python ext3.py <n> <K>      reads results/e{n}_k{K}.json (or pexact_n{n}_k*.json for n=5)
                                   writes results/e{n+1}_k{K}.json
"""
import sys
import json
import time
from itertools import combinations, product

import mpmath as mp
import sympy as sp

sys.stdout.reconfigure(encoding='utf-8', errors='replace')
from ext2 import dist, values_of, circle_circle, bisector, circle_line, line_line, delta_of
from pexact import system

mp.mp.dps = 60
TOL = mp.mpf('1e-45')


def load_bases(n, K):
    bases = []
    if n == 5:
        for k in range(1, K + 1):
            try:
                d = json.load(open('results/pexact_n5_k%d.json' % k))
            except FileNotFoundError:
                continue
            assert d['completed']
            for r in d['results']:
                for sh in r.get('shapes', []):
                    for sol in sh['solutions']:
                        bases.append([(mp.mpf(x), mp.mpf(y)) for x, y in sol])
    else:
        d = json.load(open('results/e%d_k%d.json' % (n, K)))
        assert d['completed']
        for r in d['sets']:
            bases.append([(mp.mpf(x), mp.mpf(y)) for x, y in r['points']])
    return bases


def classify(P, pts, vals):
    new = []
    for Q in pts:
        d = dist(P, Q)
        if d < TOL:
            return None
        if any(abs(d - v) < TOL for v in vals):
            continue
        if not any(abs(d - w) < TOL for w in new):
            new.append(d)
    return new


def extend(pts, K):
    vals = values_of(pts, TOL)
    n = len(pts)
    circles = [(pts[i], v) for i in range(n) for v in vals]
    lines = [bisector(pts[i], pts[j]) for i, j in combinations(range(n), 2)]
    cands = []
    for (A, rA), (B, rB) in combinations(circles, 2):
        if A is B:
            continue
        cands += circle_circle(A, rA, B, rB, TOL)
    for (C, r), L in product(circles, lines):
        cands += circle_line(C, r, L, TOL)
    for L1, L2 in combinations(lines, 2):
        cands += line_line(L1, L2, TOL)
    out = []
    for P in cands:
        new = classify(P, pts, vals)
        if new is None:
            continue
        if len(vals) + len(new) <= K:
            out.append(pts + [P])
    return out


def multiset_key(pts):
    ds = sorted(dist(P, Q) for P, Q in combinations(pts, 2))
    return tuple(mp.nstr(d / ds[0], 30) for d in ds)


def pattern_of(pts):
    pairs = list(combinations(range(len(pts)), 2))
    vals = values_of(pts, TOL)
    lab = []
    for a, b in pairs:
        d = dist(pts[a], pts[b])
        lab.append(next(i for i, v in enumerate(vals) if abs(d - v) < TOL))
    return pairs, lab, len(vals)


def certify(pts):
    """exact: the pattern of pts is feasible over Q and has an exact real solution with
    the same distance multiset (to 30 digits)"""
    n = len(pts)
    pairs, lab, k = pattern_of(pts)
    var, eqs, P, v = system(n, pairs, lab, k)
    G = sp.groebner(eqs, *var, order='grevlex')
    if G.exprs == [1]:
        return False, 'pattern infeasible'
    if not G.is_zero_dimensional:
        return False, 'positive-dimensional'
    sols = sp.solve(eqs, var, dict=True)
    target = multiset_key(pts)
    for s in sols:
        if any(abs(sp.im(sp.N(s[x], 60))) > sp.Float('1e-50', 60) for x in var):
            continue
        q = [(mp.mpf(str(sp.re(sp.N(P[i][0].subs(s), 60)))) if i >= 2 else mp.mpf(int(P[i][0])),
              mp.mpf(str(sp.re(sp.N(P[i][1].subs(s), 60)))) if i >= 2 else mp.mpf(int(P[i][1])))
             for i in range(n)]
        if multiset_key(q) == target:
            return True, '%d exact solutions' % len(sols)
    return False, 'no exact real solution matches'


if __name__ == '__main__':
    n = int(sys.argv[1]); K = int(sys.argv[2])
    t0 = time.time()
    bases = load_bases(n, K)
    print('n=%d -> %d, K=%d : %d base solutions' % (n, n + 1, K, len(bases)), flush=True)
    found = {}
    for B in bases:
        for S in extend(B, K):
            found.setdefault(multiset_key(S), S)
    print('  %d distinct distance multisets among the extensions (%.0fs)' % (len(found), time.time() - t0), flush=True)
    rows = []
    for key, S in found.items():
        vals = values_of(S, TOL)
        ok, why = certify(S)
        rows.append(dict(points=[[mp.nstr(x, 60), mp.nstr(y, 60)] for x, y in S], k=len(vals),
                         values=[mp.nstr(v / vals[0], 25) for v in vals],
                         delta=mp.nstr(delta_of(vals), 25), certified=ok, note=why))
        print('  k=%d delta=%-16s values %s  %s: %s' % (len(vals), mp.nstr(delta_of(vals), 12),
              [mp.nstr(v / vals[0], 8) for v in vals], 'CERTIFIED' if ok else 'REJECTED', why), flush=True)
    rows.sort(key=lambda r: mp.mpf(r['delta']))
    json.dump(dict(n=n + 1, K=K, bases=len(bases), sets=[r for r in rows if r['certified']],
                   rejected=[r for r in rows if not r['certified']],
                   seconds=round(time.time() - t0, 1), completed=True),
              open('results/e%d_k%d.json' % (n + 1, K), 'w'), indent=1)
    good = [r for r in rows if r['certified']]
    print('E_%d(<=%d): %d certified sets; by k: %s' % (n + 1, K, len(good),
          {k: sum(1 for r in good if r['k'] == k) for k in range(1, K + 1)}))
    if good:
        print('  min delta over them: %s' % good[0]['delta'][:16])
