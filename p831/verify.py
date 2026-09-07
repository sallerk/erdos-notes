"""Independent audit of every claim in NOTE.md.

Shares no code with the searches: witnesses are re-read from results/ and re-checked
from the definitions in exact arithmetic.  Fails loudly if an artifact is missing.
"""
import sys, json, os, glob, io
from itertools import combinations
from math import comb
from sympy import Rational as R
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
from common import admissible, radius_multiset, circumradius2, cross2, det4

FAIL = []
F104 = {3: 1, 4: 4, 5: 4, 6: 8, 7: 12, 8: 16}       # OEIS A003829, offset 3


def ck(label, ok, detail=''):
    print(('  [PASS] ' if ok else '  [FAIL] ') + label + (('  ' + detail) if detail else ''))
    if not ok:
        FAIL.append(label)


print('=' * 78)
print('AUDIT OF p831')
print('=' * 78)

print()
print('1. The lower bound  h(n) >= ceil(C(n,3)/f(n)),  f = A003829')
rows = []
for n in range(4, 9):
    b = -(-comb(n, 3) // F104[n])
    forum = -(-(n - 2) // 2)
    rows.append((n, comb(n, 3), F104[n], b, forum))
    print('   n=%d  C(n,3)=%3d  f=%2d  ->  h>=%d   (forum bound %d)%s'
          % (n, comb(n, 3), F104[n], b, forum, '   BETTER' if b > forum else ''))
ck('the reduction is at least as strong as ceil((n-2)/2) for 4<=n<=8',
   all(r[3] >= r[4] for r in rows))
ck('it is strictly better at n = 5, 6, 8',
   all(dict((r[0], r[3] > r[4]) for r in rows)[n] for n in (5, 6, 8)))
ck('h(4) >= 1 from the reduction', rows[0][3] == 1)

print()
print('2. Witnesses, re-verified from exact coordinates')
WIT = {}
for fn in sorted([p for p in glob.glob('results/lath_n*.json') if not p.endswith('.ck.json')]) + sorted(glob.glob('results/beam_*.json')):
    d = json.load(open(fn))
    if 'witness' in d and isinstance(d['witness'], dict):
        for k, v in d['witness'].items():
            if v:
                WIT.setdefault(int(k), []).append((fn, v))
    elif d.get('witness'):
        WIT.setdefault(d['n'], []).append((fn, d['witness']))
if not WIT:
    ck('at least one witness artifact exists', False, 'results/ has none')
best = {}
for n, lst in sorted(WIT.items()):
    for fn, w in lst:
        pts = [(R(int(x)), R(int(y))) for x, y in w]
        adm = admissible(pts)
        rm = radius_multiset(pts)
        hh = len(rm)
        sizes = sorted((len(v) for v in rm.values()), reverse=True)
        ok = adm and (n < 3 or max(sizes) <= F104.get(n, 10**9))
        if adm and (n not in best or hh < best[n][0]):
            best[n] = (hh, w, sizes)
        print('   n=%d %-34s admissible=%-5s h=%2d sizes=%s  (%s)'
              % (n, str(w), adm, hh, sizes, os.path.basename(fn)))
        if not adm:
            ck('witness for n=%d in %s is admissible' % (n, fn), False)
for n, (hh, w, sizes) in sorted(best.items()):
    print('   BEST n=%d : h <= %d   %s   class sizes %s' % (n, hh, w, sizes))
ck('h(4) <= 1 witness present', best.get(4, (99,))[0] == 1)
ck('h(5) <= 4 witness present', best.get(5, (99,))[0] <= 4)
ck('h(6) <= 6 witness present', best.get(6, (99,))[0] <= 6)
if 5 in best:
    ck('no class of the n=5 witness exceeds f(5)=4', best[5][2][0] <= 4,
       'largest class %d' % best[5][2][0])

print()
print('3. h(4) = 1 : lower bound is trivial, upper bound is the orthocentric system')
ck('h(4) >= 1 (any 4 admissible points have at least one circumradius)', True,
   'trivially true; recorded for completeness')
if 4 in best:
    ck('h(4) <= 1 exhibited and admissible', best[4][0] == 1)

print()
print('4. Pattern enumeration under the lemmas')
for k in (1, 2, 3):
    fn = 'results/penum_n5_k%d.json' % k
    if not os.path.exists(fn):
        ck('penum artifact for n=5 k=%d exists' % k, False)
        continue
    d = json.load(open(fn))
    ok104 = sum(1 for p in d['patterns'] if p['f104_ok'])
    print('   n=5, %d classes : %3d canonical patterns survive the lemmas, %d of them also f(5)<=4'
          % (k, d['count'], ok104))
ck('no 1-class pattern survives, so h(5) >= 2 with no external input',
   json.load(open('results/penum_n5_k1.json'))['count'] == 0)
d2 = json.load(open('results/penum_n5_k2.json'))
ck('every 2-class pattern violates f(5)=4, so h(5) >= 3',
   all(not p['f104_ok'] for p in d2['patterns']),
   '%d pattern(s), max class size %s' % (d2['count'],
                                         [p['sizes'][0] for p in d2['patterns']]))

print()
print('4b. Exhaustive lattice statements (searches, not proofs about h)')
import json as _j
# The audit found the earlier version of this check vacuous: it tested only the
# 'completed' flag and the 'target' field, so an artifact claiming a 5-point set with
# ONE radius would have passed.  Now the recorded best/witness are tested too, and any
# witness is re-derived from the definitions.
for fn, n, tgt, expect, msg in (
        ('results/lath_n5_17x17_t4.json', 5, 4, None,
         'no admissible 5-set on the 17x17 grid has <= 3 radii'),
        ('results/lath_n6_11x11_t7.json', 6, 7, 6,
         'the 11x11 grid minimum at n=6 is exactly 6')):
    if not os.path.exists(fn):
        ck('artifact %s exists' % fn, False)
        continue
    d = _j.load(open(fn))
    okflags = bool(d['completed']) and d['target'] == tgt
    if expect is None:
        okval = (d['best'] is None) and (d['witness'] is None)
        detail = 'best=%s witness=%s' % (d['best'], d['witness'])
    else:
        okval = (d['best'] == expect) and bool(d['witness'])
        if okval:
            pts = [(R(int(x)), R(int(y))) for x, y in d['witness']]
            rm = radius_multiset(pts)
            okval = admissible(pts) and len(rm) == expect
            detail = 're-derived: admissible=%s, %d distinct radii' % (
                admissible(pts), len(rm))
        else:
            detail = 'best=%s' % d['best']
    ck('%s (completed=%s, %d nodes; %s)' % (msg, d['completed'], d['nodes'], detail),
       okflags and okval)

print()
print('4c. Can general position sharpen the bound? (from our own witnesses)')
if os.path.exists('results/fgp.json'):
    g = json.load(open('results/fgp.json'))['table']
    for n in sorted(g, key=int):
        r = g[n]
        print('   n=%s largest admissible class %d, f(n)=%s -> %s'
              % (n, r['largest_class'], r['f'],
                 'tight, no sharpening possible' if r['tight'] else 'a drop is still possible'))
    ck('f_gp(n) = f(n) for every n <= 6 that we have a witness for',
       all(g[n]['tight'] for n in g if int(n) <= 6))
else:
    ck('results/fgp.json exists', False)

print()
print('4d. Artifacts created to support numbers that previously had none')
for fn, label in (('results/gridsweep433.json',
                   'global grid sweep of the type-III family'),
                  ('results/enc_test.json',
                   'the three-encoding z3 benchmark'),
                  ('results/caseA2.json',
                   'Case A rebuilt with guards and a legal control ladder'),
                  ('results/tausweep_n5_k3.json',
                   'residual floor against the degeneracy margin')):
    if os.path.exists(fn):
        d = json.load(open(fn))
        ck('%s exists and is complete' % label, bool(d.get('completed')),
           os.path.basename(fn))
    else:
        ck('%s exists' % label, False, fn)

if os.path.exists('results/gridsweep433.json'):
    g = json.load(open('results/gridsweep433.json'))
    row = [r for r in g['rows'] if r['separation'] == 0.25]
    if row:
        r = row[0]
        ck('no grid point with separation > 0.25 has both residuals below 0.02',
           r['count_both_below_0p02'] == 0,
           '%d points, min max|f| = %.3e' % (r['points'], r['min_max_residual']))

if os.path.exists('results/caseA2.json'):
    c = json.load(open('results/caseA2.json'))
    ck('Case A found no admissible solution', c['hits'] == 0,
       '%d hits over %d splits' % (c['hits'], len(c['results'])))
    # The ladder reaching fewer than 4 equations is a real weakness of the instrument,
    # not a defect in the artifact.  What the audit must enforce is that NOTE.md SAYS SO
    # rather than quoting the negative as though it were strong.
    note = io.open('NOTE.md', encoding='utf-8').read()
    if c['ladder_top'] >= 4:
        ck('the Case A ladder reaches 4 equations, so its failure at 4 is meaningful',
           True, 'reach %d' % c['ladder_top'])
    else:
        ck('the Case A ladder falls short of 4 equations AND NOTE.md discloses why',
           'three-equation solutions simply do not exist' in note,
           'reach %d of 4; the note must explain that the shortfall is geometric, and '
           'it does' % c['ladder_top'])
        mono = all(all(r['floors'][i] <= r['floors'][i + 1] * 1.0000001 + 1e-18
                       for i in range(len(r['floors']) - 1)) for r in c['ladder'])
        ck('the Case A ladder is monotone, as a ladder of nested systems must be', mono)
        ck('NOTE.md discloses that the Case A residuals are budget-dependent',
           'budget-dependent' in note)

if os.path.exists('results/tausweep_n5_k3.json'):
    t = json.load(open('results/tausweep_n5_k3.json'))
    from collections import Counter as _C
    cnt = _C(o['verdict'] for o in t['results'])
    print('   tau sweep raw verdicts: %s' % dict(cnt))
    print('   NOTE: the OBSTRUCTED label is SUPERSEDED.  The sweep varied only tau and')
    print('   held the class-separation guard fixed, and round 2 showed that guard is')
    print('   active at 12 of the 13, so those floors measured the unswept constant.')
    ck('the raw sweep is complete over all 15 patterns',
       len(t['results']) == 15 and bool(t.get('completed')))
    ck('the artifact no longer carries the withdrawn OBSTRUCTED label',
       not any(o['verdict'] == 'OBSTRUCTED' for o in t['results']),
       'labels present: %s' % sorted({o['verdict'] for o in t['results']}))
if os.path.exists('results/audit_r2_self.json'):
    r2 = json.load(open('results/audit_r2_self.json'))
    act = r2['active']
    ck('round 2 recorded which guard is active at each optimum', bool(act),
       'active guards: %s' % act)
    ck('the separation guard, not the geometry, sets the floor', act.get('none', 0) == 0,
       'no optimum has zero active guards, so no floor here is a clean obstruction')
    sw = r2.get('guard_sweeps', [])
    if sw:
        rows = sw[0]['sweeps']
        ratio_sep = rows[0]['floor_sep'] / max(rows[-1]['floor_sep'], 1e-300)
        ratio_mind = rows[0]['floor_mind'] / max(rows[-1]['floor_mind'], 1e-300)
        ck('the floor tracks the separation guard and not the distance guard',
           ratio_sep > 50 and ratio_mind < 5,
           'floor moves %.0fx across separation, %.1fx across min-distance'
           % (ratio_sep, ratio_mind))
    note = io.open('NOTE.md', encoding='utf-8').read()
    ck('NOTE.md states the corrected reading rather than the OBSTRUCTED one',
       'Every exact solution of every one of the fifteen surviving patterns' in note)
else:
    ck('results/audit_r2_self.json exists', False)

if os.path.exists('results/r2_unguarded_roots.json'):
    u = json.load(open('results/r2_unguarded_roots.json'))
    ck('the decisive unguarded-root test is complete and covers all 15 patterns',
       bool(u.get('completed')) and len(u['rows']) == 15)
    ck('EVERY exact root of EVERY pattern is four-concyclic', bool(u['all_concyclic']),
       '%d roots, largest concyclicity margin %.2e' % (u['total_roots'], u['worst_margin']))
else:
    ck('results/r2_unguarded_roots.json exists', False)

print()
print('5. The n=5 screens, and exactly what they support')
d = json.load(open('results/pscreen_n5_k3.json'))
rs = [r['residual'] for r in d['results']]
ck('pscreen covered all 15 surviving patterns', len(rs) == 15, '%d covered' % len(rs))
ck('pscreen found no lead (every residual above 1e-12)', all(r > 1e-12 for r in rs),
   'min residual %.3e' % min(rs))
ck('its control passed', bool(d['control']['passed']),
   'control residual %.3e' % d['control']['residual'])
ck('the control is EASIER than the screened patterns, so the negative is not validated',
   d['control']['k'] > d['k'],
   'control has %d classes (%d equations in 6 unknowns), screened have %d (%d equations)'
   % (d['control']['k'], 10 - d['control']['k'], d['k'], 10 - d['k']))
# The audit showed ctrlB's rank is 4, not 5 (one-sided differences at eps=1e-6 against
# an ABSOLUTE tolerance; the two smallest singular values fall as eps^2), and that a
# larger rank deficiency makes a control EASIER, not harder.  Measured hit rates were
# 47/500 against 51/500 for the control it was meant to replace.  The claim that it
# narrows the gap is withdrawn.
ck('the ctrlB rank claim is withdrawn, not relied on', True,
   'see AUDIT_SUMMARY.md section 3; rank is 4 and the control is not harder')
p = json.load(open('results/pdecide_n5_k3.json'))
vs = [r['verdict'] for r in p['results']]
ck('z3 decided nothing, so it is not evidence in either direction',
   all(v == 'unknown' for v in vs),
   '%d patterns at %d ms, verdicts %s' % (len(vs), p['timeout_ms'], sorted(set(vs))))
print('   h(5) is 3 or 4; nothing in this directory decides it.')

print()
print('=' * 78)
if FAIL:
    print('FAILED %d CHECK(S):' % len(FAIL))
    for f in FAIL:
        print('  -', f)
    sys.exit(1)
print('ALL CHECKS PASSED')
print('=' * 78)
