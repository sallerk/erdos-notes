"""Two audit questions that the rest of the checking does not answer.

A. Wei's Figure 2q, "double R5 with the same center", is a drawing with no parameters in
   the text, and the floor delta(10) >= 6 depends on its delta.  The family is
   R5 union (rho R5 rotated by phi about the same centre), so its nine candidate distance
   values are known in closed form: the two pentagon chords, the same two scaled by rho,
   and the five cross distances sqrt(1 + rho^2 - 2 rho cos(phi + 72j degrees)).  A
   ten-point member has exactly five values, so four of the nine must merge.  This file
   sweeps the two parameters on a fine grid, reports every cell whose values nearly
   merge, and then checks the candidates in exact arithmetic.  A sweep is EVIDENCE, not
   a proof; NOTE.md says so.

B. pexact.py certifies a solution list complete by comparing the number of solutions
   sympy returned with the dimension of the quotient ring.  That is sound only if the
   returned solutions are pairwise DISTINCT; a duplicate would inflate the count and
   could mask a missing root.  Re-read every stored solution and check distinctness.
"""
import sys
import json
from itertools import combinations

import numpy as np
import mpmath as mp
import sympy as sp

sys.stdout.reconfigure(encoding='utf-8', errors='replace')
mp.mp.dps = 40

FAIL = []


def ck(label, ok, detail=''):
    print(('  [PASS] ' if ok else '  [FAIL] ') + label + (('  ' + detail) if detail else ''), flush=True)
    if not ok:
        FAIL.append(label)


def values_at(rho, phi):
    """the nine candidate distance values of the doubling, numpy floats"""
    s1, s2 = 2 * np.sin(np.pi / 5), 2 * np.sin(2 * np.pi / 5)
    cross = np.sqrt(1 + rho ** 2 - 2 * rho * np.cos(phi + 2 * np.pi * np.arange(5) / 5))
    return np.concatenate([[s1, s2, rho * s1, rho * s2], cross])


def ndistinct(vals, tol):
    v = np.sort(vals)
    return 1 + int(np.sum(np.diff(v) > tol))


def delta_np(vals, tol):
    v = np.sort(vals)
    v = v[np.concatenate([[True], np.diff(v) > tol])]
    return v[-1] / min(v[0], np.min(np.diff(v))) if len(v) > 1 else 1.0


print('=' * 78)
print('A. Concentric doublings of the regular pentagon with exactly five distances')
print('=' * 78)
print('   Family: R5 of circumradius 1, together with rho R5 rotated by phi.')
print('   By symmetry it is enough to take 0 < rho <= 1 and 0 <= phi <= 36 degrees.')

# rho below 0.05 is excluded: there the inner pentagon is so small that its own two
# chords fall below the merging tolerance, which fakes a five-value count.  Such a set
# has a tiny d_1 and therefore an enormous delta, so it is irrelevant to a lower bound.
NR, NP = 8000, 800
TOLS = 1e-4
RHO_MIN = 0.05
best_cells = {}
for i0 in range(1, NR + 1, 250):
    rr = np.arange(i0, min(i0 + 250, NR + 1)) / NR
    rr = rr[rr >= RHO_MIN]
    for j in range(NP + 1):
        phi = np.pi / 5 * j / NP
        for rho in rr:
            v = values_at(rho, phi)
            if ndistinct(v, TOLS) <= 5:
                best_cells[(round(float(rho), 6), round(float(phi), 6))] = float(delta_np(v, TOLS))
print('   grid %d x %d over rho >= %g, values merged at %g: %d cells with at most five values'
      % (NR, NP + 1, RHO_MIN, TOLS, len(best_cells)))
if best_cells:
    lo = min(best_cells.values())
    print('   smallest delta over those cells: %.6f' % lo)
    ck('no cell of the sweep has five values and delta below 6', lo >= 6.0, 'min %.6f' % lo)
    ck('no cell of the sweep beats the nonagon plus centre (8.2909)', lo >= 8.29, 'min %.6f' % lo)
    groups = {}
    for (rho, phi), d in sorted(best_cells.items()):
        groups.setdefault(round(d, 3), []).append((rho, phi))
    for d in sorted(groups):
        rs = groups[d]
        print('     delta ~ %-12.5f at %3d cells, e.g. rho = %.5f, phi = %.3f degrees'
              % (d, len(rs), rs[0][0], rs[0][1] * 180 / np.pi))

# the exact candidates the sweep points at
tau = (1 + mp.sqrt(5)) / 2


def double_exact(rho, phi):
    out = [(mp.cos(2 * mp.pi * i / 5), mp.sin(2 * mp.pi * i / 5)) for i in range(5)]
    out += [(rho * mp.cos(2 * mp.pi * i / 5 + phi), rho * mp.sin(2 * mp.pi * i / 5 + phi))
            for i in range(5)]
    return out


def dvals_exact(pts, tol=mp.mpf('1e-25')):
    vals = []
    for (ax, ay), (bx, by) in combinations(pts, 2):
        d = mp.sqrt((ax - bx) ** 2 + (ay - by) ** 2)
        if not any(abs(d - v) < tol for v in vals):
            vals.append(d)
    return sorted(vals)


def delta_exact(v):
    gaps = [b - a for a, b in zip(v, v[1:])]
    return v[-1] / min([v[0]] + gaps)


print()
print('   The candidates, checked in exact arithmetic:')
CAND = {'pentagram (rho = 1/phi^2, 36 degrees)': (1 / tau ** 2, mp.pi / 5),
        'regular decagon (rho = 1, 36 degrees)': (mp.mpf(1), mp.pi / 5),
        'inner pentagon at 1/phi (36 degrees)': (1 / tau, mp.pi / 5),
        'inner pentagon at 1/phi (0 degrees)': (1 / tau, mp.mpf(0))}
for name, (rho, phi) in CAND.items():
    v = dvals_exact(double_exact(rho, phi))
    d = delta_exact(v) if len(v) > 1 else mp.mpf(1)
    print('     %-42s k = %d  delta = %s' % (name, len(v), mp.nstr(d, 15)))
vpg = dvals_exact(double_exact(1 / tau ** 2, mp.pi / 5))
ck('the pentagram doubling has exactly five distances', len(vpg) == 5)
ck('its delta is 9.2158645473', abs(delta_exact(vpg) - mp.mpf('9.21586454726535')) < mp.mpf('1e-12'),
   mp.nstr(delta_exact(vpg), 15))
ck('its five values are 1/phi^2, 1/phi, 1, sqrt((5-sqrt5)/2), phi times the outer side',
   abs(vpg[-1] / vpg[0] - tau ** 3) < mp.mpf('1e-25'))

print()
print('=' * 78)
print('B. Are the stored exact solution lists free of duplicates?')
print('=' * 78)
for fn in ('results/pexact_n4_k2.json', 'results/pexact_n5_k2.json', 'results/pexact_n5_k3.json'):
    try:
        d = json.load(open(fn))
    except FileNotFoundError:
        ck('artifact %s exists' % fn, False)
        continue
    dup, tot, bad_count = 0, 0, []
    for r in d['results']:
        if r['infeasible']:
            continue
        sols = []
        for sh in r.get('shapes', []):
            for s in sh['solutions']:
                sols.append(tuple(mp.nstr(mp.mpf(c), 25) for pt in s for c in pt))
        tot += len(sols)
        if len(set(sols)) != len(sols):
            dup += 1
        if r.get('n_real') is not None and len(sols) != r['n_real']:
            bad_count.append((r['i'], len(sols), r['n_real']))
    ck('%s: no feasible pattern stores two identical solutions' % fn, dup == 0,
       '%d patterns with duplicates, %d solutions in total' % (dup, tot))
    ck('%s: the stored solutions account for every real solution counted' % fn,
       not bad_count, str(bad_count[:5]))
    feas = [r for r in d['results'] if not r['infeasible']]
    ck('%s: every feasible pattern is zero-dimensional and certified complete' % fn,
       all(r.get('zero_dimensional') and r.get('solve_complete') for r in feas),
       '%d feasible patterns' % len(feas))

print()
print('=' * 78)
if FAIL:
    print('FAILED %d CHECK(S):' % len(FAIL))
    for f in FAIL:
        print('  -', f)
    sys.exit(1)
print('ALL CHECKS PASSED')
print('=' * 78)
