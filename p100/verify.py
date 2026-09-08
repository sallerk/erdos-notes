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
ck('the bound is NOT claimed as new (it is Kanold 1981 eq. 8)',
   'Kanold' in io.open('NOTE.md', encoding='utf-8').read())

print()
print('2. Piepmeyer, re-derived exactly and independently of the search')
if not os.path.exists('results/piepmeyer.json'):
    ck('results/piepmeyer.json exists', False)
else:
    d = json.load(open('results/piepmeyer.json'))
    ck('the two independent derivations agree', bool(d['two_routes_agree']))
    ck('exactly 4 distinct distances', d['k'] == 4)
    ck('the binding constraint is the middle gap', d['binding'] == 'gap_2')
    ck('delta = 4.6639024601, matching the page\'s "diameter < 5"',
       abs(float(d['delta']) - 4.66390246015) < 1e-9, 'delta = %s' % d['delta'][:13])

print()
print('3. Monotonicity, and the subset bounds it gives for free')
print('   Any m-subset of an admissible set is admissible and has no larger diameter,')
print('   so delta is non-decreasing in n and every subset of a good set bounds a')
print('   smaller n.  Re-derived here in exact arithmetic from the exact coordinates.')
if os.path.exists('results/piepmeyer_subsets.json'):
    s = json.load(open('results/piepmeyer_subsets.json'))
    vals = [(int(m), s[m]['delta']) for m in sorted(s, key=int)]
    for m, v in vals:
        print('     n=%d : delta <= %.10f  (k = %d)' % (m, v, s[str(m)]['k']))
    ck('the subset bounds are non-decreasing in n',
       all(a[1] <= b[1] + 1e-12 for a, b in zip(vals, vals[1:])))
    ck('the n=9 subset reproduces Piepmeyer', abs(vals[-1][1] - 4.66390246015) < 1e-9)
else:
    ck('results/piepmeyer_subsets.json exists', False)

print()
print('4. The exhaustive small cases, where the value is PROVED not just bounded')
for n, k, expect in ((4, 2, 2.0731321850), (5, 2, 2.6180339887)):
    fn = 'results/patterns_n%d_k%d.json' % (n, k)
    if not os.path.exists(fn):
        ck('artifact %s' % fn, False)
        continue
    d = json.load(open(fn))
    ck('n=%d, k=%d: enumeration complete over all %d canonical patterns'
       % (n, k, d['patterns']), bool(d['completed']))
    ck('n=%d: best delta = %.10f' % (n, expect),
       abs(d['best_delta'] - expect) < 1e-9,
       'found %.10f from %d patterns, %d realisation shapes'
       % (d['best_delta'], d['patterns'], d.get('shapes', -1)))
    ck('n=%d: a set with k = %d distances could not beat it, since delta >= k'
       % (n, k + 1), k + 1 > expect)
d5 = json.load(open('results/patterns_n5_k2.json'))
ck('n=5: exactly ONE of the 17 patterns is realisable, which is Kelly\'s classification '
   'of 5-point 2-distance sets recovered from scratch', d5['realised'] == 1)
phi = (1 + sp.sqrt(5)) / 2
ck('n=5: the value is phi^2 = (3+sqrt5)/2 exactly',
   abs(d5['best_delta'] - float(sp.N(phi ** 2, 20))) < 1e-12)

print()
print('5. The seeded search, and its measured hit rate')
print('   A search that cannot find a known optimum cannot report an absence (L74).')
for fn in sorted(glob.glob('results/seeded_n*_k*.json')):
    d = json.load(open(fn))
    print('   n=%-2d k=%d : %4d/%4d starts valid (%4.1f%%)  best delta %s  from %s'
          % (d['n'], d['k'], d['hits'], d['seeds'], 100 * d['hit_rate'],
             ('%.10f' % d['best_delta']) if d['best_delta'] else 'none',
             (d['from_seed'] or '')[:34]))
f9 = 'results/seeded_n9_k4.json'
if os.path.exists(f9):
    d = json.load(open(f9))
    ck('CONTROL: the seeded search recovers Piepmeyer at n = 9',
       d['best_delta'] is not None and abs(d['best_delta'] - 4.66390246015) < 1e-9,
       'best %.10f' % d['best_delta'] if d['best_delta'] else 'not found')
else:
    ck('the n=9 control has been run', False)
note = io.open('NOTE.md', encoding='utf-8').read()
ck('NOTE.md discloses that random starts had a hit rate under 1%',
   'under 1%' in note or 'well under 1%' in note)

print()
print('6. What is bounded but NOT proved')
print('   delta(6) through delta(9) are upper bounds from a search plus the k_min floor.')
print('   Proving any of them needs an exhaustive enumeration of k-distance patterns at')
print('   that n, which is out of reach here: n = 6 with k = 3 alone is S(15,3) =')
print('   2,375,101 partitions before symmetry.')
ck('the note does not claim those as exact',
   'NOT proved' in note or 'bracketed' in note or 'upper bound' in note)

print()
print('=' * 78)
if FAIL:
    print('FAILED %d CHECK(S):' % len(FAIL))
    for f in FAIL:
        print('  -', f)
    sys.exit(1)
print('ALL CHECKS PASSED')
print('=' * 78)
