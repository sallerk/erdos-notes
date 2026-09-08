"""Audit computation: 7-point 4-distance sets that contain a 5-point set with at most 3
distances, rebuilt from scratch, and compared with the Lan-Wei list used in e78.py.

E_5(<= 3) is known exactly (pexact.py).  Extending each member by one point with at most
4 distances in total, and each result by one more point, enumerates every 7-point
4-distance set that contains a 5-point subset with at most 3 distances (the extension
step is complete by the argument in ext3.py, which for K = 4 needs n > 4, satisfied at
n = 5 and 6).  Lan-Wei obtain 34 of their 42 sets this way (their p. 507); the other 8
have a diameter graph forcing |X_D| >= 5 and may or may not contain such a subset.

So the list produced here must be a subset of the 42, must contain everything in the
42 that has a 5-point <= 3-distance subset, and in particular should contain the two
sets (741, 742) that e78.py could only take from their stated ratios.  Anything found
here that is NOT among the 42 would contradict Lan-Wei's theorem and must be examined.

Output: results/chain4.json and a comparison printed against results/e78_k4.json.
"""
import sys
import json
import time
from itertools import combinations, product

import mpmath as mp
import sympy as sp

sys.stdout.reconfigure(encoding='utf-8', errors='replace')
from ext2 import dist, values_of, circle_circle, bisector, circle_line, line_line, delta_of
from ext3 import load_bases, multiset_key, pattern_of
from pexact import system

mp.mp.dps = 60
TOL = mp.mpf('1e-45')


def extend(pts, K):
    vals = values_of(pts, TOL)
    n = len(pts)
    circles = [(pts[i], v) for i in range(n) for v in vals]
    lines = [bisector(pts[i], pts[j]) for i, j in combinations(range(n), 2)]
    cands = []
    for (A, rA), (B, rB) in combinations(circles, 2):
        if A is not B:
            cands += circle_circle(A, rA, B, rB, TOL)
    for (C, r), L in product(circles, lines):
        cands += circle_line(C, r, L, TOL)
    for L1, L2 in combinations(lines, 2):
        cands += line_line(L1, L2, TOL)
    out = {}
    for P in cands:
        if any(dist(P, Q) < TOL for Q in pts):
            continue
        S = pts + [P]
        if len(values_of(S, TOL)) <= K:
            out.setdefault(multiset_key(S), S)
    return out


def groebner_feasible(pts):
    """exact: the pattern of pts is realisable with distinct points and zero-dimensional"""
    pairs, lab, k = pattern_of(pts)
    var, eqs, P, v = system(len(pts), pairs, lab, k)
    G = sp.groebner(eqs, *var, order='grevlex')
    if G.exprs == [1]:
        return 'infeasible'
    return 'feasible, zero-dimensional' if G.is_zero_dimensional else 'feasible, positive-dimensional'


if __name__ == '__main__':
    t0 = time.time()
    bases = load_bases(5, 3)
    print('%d base solutions in E_5(<=3)' % len(bases), flush=True)
    six = {}
    for B in bases:
        for kk, S in extend(B, 4).items():
            six.setdefault(kk, S)
    print('  %d distinct 6-point sets with <= 4 distances containing a 5-point <=3-distance subset (%.0fs)'
          % (len(six), time.time() - t0), flush=True)
    seven = {}
    for i, S6 in enumerate(six.values()):
        for kk, S in extend(S6, 4).items():
            if len(values_of(S, TOL)) == 4:
                seven.setdefault(kk, S)
        if i % 50 == 49:
            print('    %d/%d bases done, %d seven-point 4-distance multisets so far (%.0fs)'
                  % (i + 1, len(six), len(seven), time.time() - t0), flush=True)
    print('  %d distinct 7-point 4-distance multisets (%.0fs)' % (len(seven), time.time() - t0), flush=True)

    # compare with e78's explicit list and ratio-only sets
    e78 = json.load(open('results/e78_k4.json'))
    known = {}
    for r in e78['E7']:
        pts = [(mp.mpf(x), mp.mpf(y)) for x, y in r['points']]
        known[multiset_key(pts)] = r['family']
    ratio_only = {nm['name']: [mp.mpf(x) for x in nm['ratios']] for nm in e78['E7_ratio_only']}
    rows = []
    for kk, S in seven.items():
        vals = values_of(S, TOL)
        rat = [v / vals[0] for v in vals]
        tag = known.get(kk)
        if tag is None:
            for nm, w in ratio_only.items():
                if all(abs(rat[i] - w[i] / w[0]) < mp.mpf('1e-20') for i in range(4)):
                    tag = 'RATIO-ONLY %s (now explicit)' % nm
        if tag is None:
            tag = 'NOT IN THE 42'
        rows.append(dict(family=tag, ratios=[mp.nstr(x, 20) for x in rat], delta=mp.nstr(delta_of(vals), 20),
                         points=[[mp.nstr(x, 50), mp.nstr(y, 50)] for x, y in S]))
    for r in rows:
        if 'NOT IN' in r['family'] or 'RATIO-ONLY' in r['family']:
            r['groebner'] = groebner_feasible([(mp.mpf(x), mp.mpf(y)) for x, y in r['points']])
    print()
    fams = {}
    for r in rows:
        fams[r['family']] = fams.get(r['family'], 0) + 1
    for f, c in sorted(fams.items()):
        print('  %-45s %d' % (f, c))
    for r in rows:
        if 'NOT IN' in r['family'] or 'RATIO-ONLY' in r['family']:
            print('  %s : ratios %s  delta %s  groebner: %s' % (r['family'], [x[:10] for x in r['ratios']],
                                                              r['delta'][:12], r['groebner']))
    print('  minimum delta over all found: %s' % mp.nstr(min(mp.mpf(r['delta']) for r in rows), 15))
    json.dump(dict(six_point_sets=len(six), seven_point_sets=len(rows), sets=rows,
                   seconds=round(time.time() - t0, 1), completed=True),
              open('results/chain4.json', 'w'), indent=1)
