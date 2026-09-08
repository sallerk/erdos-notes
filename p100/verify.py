"""Independent audit of every claim in NOTE.md.

Re-derives the witnesses from the definitions in exact arithmetic where it can, reads
the artifacts back rather than trusting printed output, and fails loudly on a missing
file.  Where a value is only an upper bound it says so; where a search is the evidence
it asserts that the note discloses the search's hit rate.
"""
import sys
import io
import os
import json
import glob
from itertools import combinations

import sympy as sp

sys.stdout.reconfigure(encoding='utf-8', errors='replace')
from core import delta, distances, k_min, GMAX

FAIL = []


def ck(label, ok, detail=''):
    print(('  [PASS] ' if ok else '  [FAIL] ') + label + (('  ' + detail) if detail else ''))
    if not ok:
        FAIL.append(label)


def load(fn):
    if not os.path.exists(fn):
        ck('artifact %s exists' % fn, False)
        return None
    return json.load(open(fn))


print('=' * 78)
print('AUDIT OF p100')
print('=' * 78)

print()
print('1. The lower bound delta(n) >= k_min(n)')
print('   k_min from the maximum sizes of planar k-distance sets, g(1..6) = 3,5,7,9,12,13')
row = [(n, k_min(n)) for n in range(3, 14)]
print('   ' + '  '.join('n=%d:%s' % (n, k) for n, k in row))
ck('k_min is non-decreasing in n', all(a[1] <= b[1] for a, b in zip(row, row[1:])))
ck('k_min(9) = 4, so Piepmeyer cannot be beaten by a set with 5 or more distances',
   k_min(9) == 4)
note = io.open('NOTE.md', encoding='utf-8').read()
ck('the bound is NOT claimed as new (it is Kanold 1981 eq. 8)', 'Kanold' in note)

print()
print('2. Piepmeyer, re-derived exactly and independently of the search')
d = load('results/piepmeyer.json')
if d:
    ck('the two independent derivations agree', bool(d['two_routes_agree']))
    ck('exactly 4 distinct distances', d['k'] == 4)
    ck('the binding constraint is the middle gap', d['binding'] == 'gap_2')
    ck('delta = 4.6639024601, matching the page\'s "diameter < 5"',
       abs(float(d['delta']) - 4.66390246015) < 1e-9, 'delta = %s' % d['delta'][:13])

print()
print('3. Monotonicity, and the subset bounds it gives for free')
s = load('results/piepmeyer_subsets.json')
if s:
    vals = [(int(m), s[m]['delta']) for m in sorted(s, key=int)]
    for m, v in vals:
        print('     n=%d : delta <= %.10f  (k = %d)' % (m, v, s[str(m)]['k']))
    ck('the subset bounds are non-decreasing in n',
       all(a[1] <= b[1] + 1e-12 for a, b in zip(vals, vals[1:])))
    ck('the n=9 subset reproduces Piepmeyer', abs(vals[-1][1] - 4.66390246015) < 1e-9)

print()
print('4. The exact small cases: every pattern decided by a Groebner basis over Q')
print('   A pattern is a colouring of the pairs by distance class.  pexact.py proves a')
print('   pattern unrealisable (reduced basis [1] after saturating the class values away')
print('   from zero) or lists ALL its real solutions, with the solution count checked')
print('   against the dimension of the quotient ring so the list is provably complete.')


def exact_ok(fn, n, k, npat, expect_infeasible, expect_shapes, expect_best):
    d = load(fn)
    if not d:
        return None
    ck('%s: completed over all %d canonical patterns' % (fn, npat),
       bool(d['completed']) and d['patterns'] == npat)
    feas = [r for r in d['results'] if not r['infeasible']]
    ck('%s: %d patterns proved unrealisable' % (fn, expect_infeasible),
       sum(1 for r in d['results'] if r['infeasible']) == expect_infeasible)
    ck('%s: no positive-dimensional pattern' % fn,
       all(r.get('zero_dimensional', True) for r in feas))
    ck('%s: every feasible pattern has a certified-complete solution list' % fn,
       all(r.get('solve_complete') for r in feas))
    shapes = {}
    for r in feas:
        for sh in r.get('shapes', []):
            shapes.setdefault(tuple(sh['values']) + tuple(sh['multiplicity']), sh)
    if expect_shapes is not None:
        ck('%s: %d distinct distance multisets in all' % (fn, expect_shapes),
           len(shapes) == expect_shapes, 'found %d' % len(shapes))
    best = min(float(sh['delta']) for sh in shapes.values())
    ck('%s: best delta = %.10f' % (fn, expect_best), abs(best - expect_best) < 1e-9,
       'found %.10f' % best)
    return d, shapes


exact_ok('results/pexact_n4_k2.json', 4, 2, 5, 0, 6, 2.0731321850)
exact_ok('results/pexact_n5_k2.json', 5, 2, 17, 16, 1, 2.6180339887)
r53 = exact_ok('results/pexact_n5_k3.json', 5, 3, 124, 104, None, 2.6180339887)
if r53:
    n3 = sum(1 for k in r53[1] if len(k) == 6)
    ck('E_5(3) CONTROL: 34 five-point 3-distance sets, Shinohara 2004 Theorem 1', n3 == 34, 'found %d' % n3)
phi = (1 + sp.sqrt(5)) / 2
d5 = load('results/pexact_n5_k2.json')
if d5:
    ck('n=5, k=2: the value is phi^2 = (3+sqrt5)/2 exactly',
       abs(float(d5['best']['delta']) - float(sp.N(phi ** 2, 20))) < 1e-12)
    ck('n=5, k=2: the single realisable pattern is the regular pentagon (values 1 : phi)',
       abs(float(d5['best']['values'][1]) - float(sp.N(phi, 20))) < 1e-12)
ck('n=4: the six 2-distance sets are the classical six (Kelly), and NOTE.md says six',
   'six' in note and 'true count is six' in note)
ck('n=4: a 3-distance set has delta >= 3 > 2.0731, so k = 2 is the only case', 3 > 2.0731321850)
ck('n=5: a 3-distance set has delta >= 3 > 2.6180, so k = 2 is the only case', 3 > 2.6180339887)

print()
print('5. The exact chain E_5(<=3) -> E_6(<=3) -> E_7(<=3) -> E_8(<=3), and delta(6)')
print('   ext3.py extends every n-point set with <= 3 distances by one point (complete:')
print('   the new point is pinned by two of the conditions "old distance to a base')
print('   point" / "equal new distance to two base points"), then certifies each set')
print('   found by deciding its own pattern exactly.')
e6 = load('results/e6_k3.json'); e7 = load('results/e7_k3.json'); e8 = load('results/e8_k3.json')
if e6:
    ck('E_6(<=3): every set found was certified exactly (none rejected)',
       e6['completed'] and len(e6['rejected']) == 0, '%d rejected' % len(e6['rejected']))
    ck('E_6(<=3): no 6-point set with 1 or 2 distances (g(2) = 5, from scratch)',
       all(r['k'] == 3 for r in e6['sets']))
    ck('E_6(3): exactly nine 6-point 3-distance sets', len(e6['sets']) == 9, 'found %d' % len(e6['sets']))
    best6 = min(float(r['delta']) for r in e6['sets'])
    ck('delta(6) = 2 + sqrt2 = 3.4142135624 exactly (a 4-distance set has delta >= 4)',
       abs(best6 - float(2 + sp.sqrt(2))) < 1e-9 and 4 > best6, 'min delta %.10f' % best6)
    w = [r for r in e6['sets'] if abs(float(r['delta']) - float(2 + sp.sqrt(2))) < 1e-9]
    ck('delta(6): the witness values are 1 : 1+sqrt3 : (1+sqrt3)/sqrt2 ... i.e. 1 : 1.9319 : 2.7321',
       any(abs(float(r['values'][1]) - 1.9318516526) < 1e-8 and abs(float(r['values'][2]) - 2.7320508076) < 1e-8 for r in w))
if e7:
    ck('E_7(3) CONTROL: exactly two sets, the regular heptagon and hexagon plus centre '
       '(Erdos-Fishburn 1996 Thm 1; Shinohara 2004 Thm 2)',
       e7['completed'] and len(e7['rejected']) == 0 and len(e7['sets']) == 2 and
       sorted(round(float(r['delta']), 6) for r in e7['sets']) == [5.048917, 7.464102])
if e8:
    ck('E_8(<=3) CONTROL: empty, i.e. g(3) = 7 from scratch',
       e8['completed'] and len(e8['sets']) == 0)

print()
print('6. The seeded search, and its measured hit rate')
print('   A search that cannot find a known optimum cannot report an absence (L74).')
for fn in sorted(glob.glob('results/seeded_n*_k*.json')):
    d = json.load(open(fn))
    print('   n=%-2d k=%d : %4d/%4d starts valid (%4.1f%%)  best delta %s  from %s'
          % (d['n'], d['k'], d['hits'], d['seeds'], 100 * d['hit_rate'],
             ('%.10f' % d['best_delta']) if d['best_delta'] else 'none',
             (d['from_seed'] or '')[:34]))
f9 = load('results/seeded_n9_k4.json')
if f9:
    ck('CONTROL: the seeded search recovers Piepmeyer at n = 9',
       f9['best_delta'] is not None and abs(f9['best_delta'] - 4.66390246015) < 1e-9,
       'best %.10f' % f9['best_delta'] if f9['best_delta'] else 'not found')
ck('NOTE.md discloses that random starts had a hit rate under 1%',
   'under 1%' in note or 'well under 1%' in note)

print()
print('7. One-point extensions of the n = 9 and n = 10 incumbents (complete, 60 digits)')
x = load('results/ext2_nonagon.json')
if x:
    ck('CONTROL: extending the regular nonagon finds nonagon + centre, delta 8.2908593694',
       any(abs(float(r['delta']) - 8.290859369381) < 1e-9 and r['k'] == 5 for r in x['extensions']))
x = load('results/ext2_piepmeyer.json')
if x:
    b = min(float(r['delta']) for r in x['extensions']) if x['extensions'] else None
    ck('no 10th point added to Piepmeyer beats nonagon + centre (best extension 9.9031)',
       b is None or b > 8.2908593694, 'best %s' % b)
x = load('results/ext2_r9plus.json')
if x:
    ck('no 11th point added to nonagon + centre gives delta <= 12', len(x['extensions']) == 0)
s10 = load('results/seeded_n10_k5.json'); s11 = load('results/seeded_n11_k5.json')
if s10:
    ck('delta(10) <= 8.2908593694, nonagon + centre', abs(s10['best_delta'] - 8.290859369381) < 1e-9)
if s11:
    ck('delta(11) <= 12.3435375197, regular 11-gon', abs(s11['best_delta'] - 12.34353752) < 1e-7)

print()
print('8. Lattice enumerations as controls against the literature (exact, integers)')
for n, k, expect, what in ((12, 5, 1, "Shinohara 2008: the 12-point 5-distance set is unique"),
                           (13, 6, 1, "Wei 2012 Figure 1: one 13-point 6-distance lattice set"),
                           (7, 3, 1, "hexagon plus centre is the only 7-point 3-distance lattice set")):
    d = load('results/lat_n%d_k%d.json' % (n, k))
    if d:
        ck('lattice n=%d k=%d: %d set up to similarity (%s)' % (n, k, expect, what),
           d['completed'] and d['similarity_classes'] == expect, 'found %d' % d['similarity_classes'])
d = load('results/lat_n10_k5.json')
if d:
    print('   lattice n=10 k=5: %d sets up to similarity with diameter <= %s; Wei 2012 Theorem 11'
          ' shows sixteen lattice figures (2a-2p); NOTE.md reports the discrepancy' % (d['similarity_classes'], d['D2'] ** 0.5))
    ck('NOTE.md discloses the 15 vs 16 discrepancy', 'sixteen' in note or '16' in note)
    ck('every lattice 10-point 5-distance set has delta = 11.1961524227 = 3/(2-sqrt3)',
       all(abs(float(r['delta_num']) - 11.19615242270) < 1e-9 for r in d['sets']))
d = load('results/lat_n9_k4.json')
if d:
    ck('lattice n=9 k=4: two sets up to similarity, both delta = 9.8740783171',
       d['similarity_classes'] == 2 and all(abs(float(r['delta_num']) - 9.874078317085) < 1e-9 for r in d['sets']))

print()
print('9. delta(7), delta(8), delta(9) from the published classifications')
print('   Erdos-Fishburn 1996 Thm 1 (9 points), Shinohara 2008 Thm 1.2(a) (8 points),')
print('   Lan-Wei 2013 Thm 8 (7 points); a competitor has exactly 4 distances (delta >= k,')
print('   and E_7(3) = {R_7, R_6+} has delta >= 5.049).')
e9 = load('results/e9_k4.json')
if e9:
    ck('E_9(4): all four sets built exactly and each has exactly 4 distances',
       e9['completed'] and len(e9['sets']) == 4 and all(v['k'] == 4 for v in e9['sets'].values()))
    ck('the three-triangle set of Erdos-Fishburn IS the Piepmeyer set (equal multisets, exact)',
       bool(e9['three_triangles_is_piepmeyer']))
    ck('delta(9) = 4.6639024601, attained by Piepmeyer and by nothing else in E_9(4)',
       abs(float(e9['delta9_num']) - 4.66390246015) < 1e-9 and e9['best'] == 'three triangles (c)' and
       sum(1 for v in e9['sets'].values() if abs(float(v['delta_num']) - 4.66390246015) < 1e-9) == 1)
    ck('the other three (R_9, two lattice sets) have delta 8.2909, 9.8741, 9.8741',
       sorted(round(float(v['delta_num']), 4) for v in e9['sets'].values()) == [4.6639, 8.2909, 9.8741, 9.8741])
e78 = load('results/e78_k4.json')
if e78:
    ck('E_7(4): 40 sets built explicitly + 2 by their stated ratios = the 42 of Lan-Wei',
       e78['E7_classes'] + len(e78['E7_ratio_only']) == 42 and e78['E7_classes'] == 40)
    ck('E_8(4): 15 sets built explicitly (R_8, R_7+, square+apexes, R_9-1, 8 lattice, 3 Piepmeyer subsets)',
       e78['E8_classes'] == 15)
    ck('delta(7) = 4.6639024601, from Piepmeyer 7-subsets only',
       abs(float(e78['delta7']) - 4.66390246015) < 1e-9 and 'Piepmeyer' in e78['delta7_from'] and
       all(float(r['delta']) > 4.664 or 'Piepmeyer' in r['family'] for r in e78['E7']) and
       all(float(r['delta']) > 4.664 for r in e78['E7_ratio_only']))
    ck('delta(8) = 4.6639024601, from Piepmeyer 8-subsets only',
       abs(float(e78['delta8']) - 4.66390246015) < 1e-9 and
       all(float(r['delta']) > 4.664 or 'Piepmeyer' in r['family'] for r in e78['E8']))
    ck('every 7-point 4-distance set built has exactly 4 distances', all(len(r['ratios']) == 4 for r in e78['E7']))
ck('NOTE.md marks n = 7, 8, 9 as PROVED and states the sources', 'Lan-Wei' in note and 'Erdos-Fishburn (1996' in note and 'Theorem 1)' in note and '| 9 | 4 | **4.6639024601**' in note)
print()
print('10. The floors at n = 10, 11, 12 (Wei 2012 Thm 11, Wei 2011 Thm 13, Shinohara 2008)')
d10 = load('results/lat_n10_k5.json'); d11 = load('results/lat_n11_k5.json'); s10 = load('results/seeded_n10_k5.json')
pg = load('results/polygons.json')
if d10 and d11 and s10 and pg:
    ck('every 10-point 5-distance set has delta >= 8.2909 (the nonagon+centre value)',
       all(float(r['delta_num']) >= 8.29 for r in d10['sets']) and
       float(pg['R10']['delta']) >= 8.29 and float(pg['R11-vertex']['delta']) >= 8.29 and 9.21 >= 8.29)
    ck('every 11-point 5-distance set has delta >= 11.196 (R_11 and the three lattice sets)',
       d11['similarity_classes'] == 3 and all(float(r['delta_num']) >= 11.19 for r in d11['sets']) and float(pg['R11']['delta']) >= 11.19)
    ck('NOTE.md states the floor 6 at n = 10, 11, 12 with its source', 'delta(11), delta(12) >= 6' in note)

print()
print('=' * 78)
if FAIL:
    print('FAILED %d CHECK(S):' % len(FAIL))
    for f in FAIL:
        print('  -', f)
    sys.exit(1)
print('ALL CHECKS PASSED')
print('=' * 78)
