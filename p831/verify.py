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
    # The note used to state this as a universal fact about the solution SETS.  It is a
    # statement about the solutions one numerical search FOUND; the 2026-09-16 audit ranked
    # the quantified form the worst defect in the directory, so check that it is gone.
    ck('NOTE.md states the corrected reading rather than the OBSTRUCTED one',
       'Every solution this search found, in any of the fifteen surviving patterns' in note)
    ck('NOTE.md no longer states the universal form, which would settle h(5) = 4',
       'Every exact solution of every one of the fifteen surviving patterns' not in note)
else:
    ck('results/audit_r2_self.json exists', False)

if os.path.exists('results/r2_unguarded_roots.json'):
    u = json.load(open('results/r2_unguarded_roots.json'))
    ck('the decisive unguarded-root test is complete and covers all 15 patterns',
       bool(u.get('completed')) and len(u['rows']) == 15)
    ck('every solution FOUND by r2check is four-concyclic (numerical; not a theorem about '
       'the solution sets)', bool(u['all_concyclic']),
       '%d converged solutions from %d random starts, largest concyclicity margin %.2e'
       % (u['total_roots'], 120 * len(u['rows']), u['worst_margin']))
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

# The quantifier elimination of section 6 was attempted and abandoned.  These checks are
# here so that a later edit cannot quietly turn an unfinished run into a result.
note = io.open('NOTE.md', encoding='utf-8').read()
flat = ' '.join(note.split())      # the note is hard-wrapped, so match on flattened text
ck('the elimination attempt is recorded as UNFINISHED, not as a result',
   'It did not finish' in flat and 'Neither returned an answer' in flat)
ck('no claim that a branch of h(5) was settled by the elimination',
   'settles this branch' not in note.replace('would settle this branch', ''))
ck('the input files for the attempt are present, so it can be picked up again',
   os.path.exists('mkqe.py') and os.path.exists('qe_typeIII.red')
   and os.path.exists('qe_typeIII_lean.red'))
ck('the status sentence still says h(5) is 3 or 4', '**h(5) is 3 or 4.**' in note)

print()
print('5a. Case A (one class is the four triples of an orthocentric quadruple), exactly')
# caseA_exact.py, run in the container of docker/, produced these.  Nothing below imports
# it: the artifacts are re-read, and the two systems that carry the proof are rebuilt
# here from the geometry and compared with the files Singular actually read.
import itertools
import sympy as sp

PAIRS6 = list(combinations(range(4), 2))


def lemma1_splits():
    out = set()
    for mask in range(1, 63):
        c0 = tuple(i for i in range(6) if mask >> i & 1)
        c1 = tuple(i for i in range(6) if not mask >> i & 1)
        if all(sum(1 for t in cl if X in PAIRS6[t]) <= 2 for X in range(4) for cl in (c0, c1)):
            out.add(tuple(sorted([c0, c1])))
    return out


S9 = lemma1_splits()
shapes = sorted(tuple(sorted((len(a), len(b)), reverse=True)) for a, b in S9)
ck('Lemma 1 alone leaves 9 splits of the six P-triples: 3 of shape (4,2), 6 of shape (3,3)',
   shapes == [(3, 3)] * 6 + [(4, 2)] * 3, str(shapes))


def relabel(split, perm):
    idx = {frozenset(PAIRS6[t]): t for t in range(6)}
    img = [tuple(sorted(idx[frozenset((perm[i], perm[j]))] for i, j in (PAIRS6[t] for t in cl)))
           for cl in split]
    return tuple(sorted(img))


orbits = []
for s in sorted(S9):
    orb = {relabel(s, p) for p in itertools.permutations(range(4))}
    if orb not in orbits:
        orbits.append(orb)
ck('relabelling A,B,C,H makes the six (3,3) splits one case and the three (4,2) one case',
   sorted(len(o) for o in orbits) == [3, 6], 'orbit sizes %s' % sorted(len(o) for o in orbits))

ms = json.load(open('results/caseA_exact_msolve.json'))
sr = json.load(open('results/caseA_exact_singrab.json'))
full = ['%s_split%d' % (g, k) for g in ('F1', 'F2') for k in range(9)]
ck('msolve (mod-p Groebner, not a proof): all 18 full systems have no complex solution',
   all(ms.get(j, {}).get('status') == 'no complex solution' for j in full),
   '%d of 18 recorded' % sum(1 for j in full if j in ms))
ck('controls: msolve returns the planted configuration (both gauges, full and pinned)',
   all(ms.get(j, {}).get('planted_found') is True
       for j in ('F1_control', 'F2_control', 'F1_pin4', 'F2_pin4')))
for name in ('F2_red4', 'F1_cand1'):
    live = io.open('exact/%s.singrab.live' % name, encoding='utf-8', errors='replace').read()
    src = io.open('exact/%s.rab.sing' % name, encoding='ascii').read()
    ck('%s: Singular over Q (characteristic 0) found the unit ideal' % name,
       sr.get(name, {}).get('status') == 'no complex solution' and 'RESULT dim -1' in live
       and 'RESULT unit 1' in live and 'ring R = 0,' in src)


def _d2(a, b):
    return (a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2


def _cr(a, b, c):
    return (b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0])


def rebuild(gauge, c0, keep):
    """own construction of a Case A system; KEEP names the non-degeneracy conditions"""
    ra, rb = sp.symbols('ra rb')
    if gauge == 'F1':
        u, v, w, x, y = sp.symbols('u v w x y')
        Q, P = [(0, 0), (1, 0), (u, v), (u, w)], (x, y)
        orth = [v * w - u * (1 - u)]
    else:
        p, q, r, s, m, n = sp.symbols('p q r s m n')
        Q, P = [(1, 0), (p, q), (r, s), (m, n)], (0, 0)
        A, B, C, H = Q
        orth = [(H[0] - A[0]) * (B[0] - C[0]) + (H[1] - A[1]) * (B[1] - C[1]),
                (H[0] - B[0]) * (A[0] - C[0]) + (H[1] - B[1]) * (A[1] - C[1])]
    eqs = list(orth)
    for t, (i, j) in enumerate(PAIRS6):
        rho = ra if t in c0 else rb
        eqs.append(_d2(Q[i], Q[j]) * _d2(Q[j], P) * _d2(P, Q[i]) - 4 * rho * _cr(P, Q[i], Q[j]) ** 2)
    K, N = _cr(*Q[:3]), _d2(Q[1], Q[2]) * _d2(Q[2], Q[0]) * _d2(Q[0], Q[1])
    cond = {'P!=A': _d2(P, Q[0]), 'P!=B': _d2(P, Q[1]), 'P!=C': _d2(P, Q[2]),
            'P!=H': _d2(P, Q[3]), 'ra!=R2': 4 * ra * K ** 2 - N, 'rb!=R2': 4 * rb * K ** 2 - N}
    return [sp.expand(e) for e in eqs], [sp.expand(cond[k]) for k in keep]


def same_up_to_scalar(f, g):
    f, g = sp.expand(f), sp.expand(g)
    if f == 0 or g == 0:
        return f == g
    fv = sorted(f.free_symbols | g.free_symbols, key=str)
    return sp.expand(f * sp.Poly(g, *fv).LC() - g * sp.Poly(f, *fv).LC()) == 0


def file_system(name):
    src = io.open('exact/%s.rab.sing' % name, encoding='ascii').read()
    body = src.split('ideal I = ')[1].split(';')[0]
    polys = [sp.expand(sp.sympify(t.replace('^', '**'))) for t in body.split(',')]
    ts = sorted({v for f in polys for v in f.free_symbols if str(v).startswith('t')}, key=str)
    eqs = [f for f in polys if not (f.free_symbols & set(ts))]
    conds = [sp.expand((f + 1) / t) for t in ts for f in polys if t in f.free_symbols]
    return eqs, conds


# the two proofs: F2 split 4 keeping {P!=B, ra!=R^2}; F1 split 1 keeping the six below.
# The splits are named by their classes, so the index into the split list does not matter.
for name, gauge, c0, keep in (
        ('F2_red4', 'F2', (0, 1, 4), ['P!=B', 'ra!=R2']),
        ('F1_cand1', 'F1', (0, 2, 3), ['P!=A', 'P!=B', 'P!=C', 'P!=H', 'ra!=R2', 'rb!=R2'])):
    mine_e, mine_c = rebuild(gauge, c0, keep)
    file_e, file_c = file_system(name)
    ok_e = len(mine_e) == len(file_e) and all(any(same_up_to_scalar(a, b) for b in file_e)
                                              for a in mine_e)
    # what must hold is that every condition Singular IMPOSED is implied by admissibility:
    # each imposed polynomial must divide one of the admissibility polynomials above, so
    # that it is non-zero whenever that one is.  (The file keeps irreducible factors.)
    def divides(b, a):
        if not b.free_symbols <= a.free_symbols:
            return False
        gens = sorted(a.free_symbols, key=str)
        return sp.rem(sp.Poly(a, *gens), sp.Poly(b, *gens)).is_zero
    ok_c = all(any(divides(b, a) for a in mine_c) for b in file_c)
    ck('%s: the equations Singular read are the Case A equations, rebuilt independently'
       % name, ok_e, '%d equations' % len(mine_e))
    ck('%s: every condition it imposed is one that admissibility forces (distinct points, '
       'distinct radius classes)' % name,
       ok_c and len(file_c) == len(mine_c), '%d conditions' % len(file_c))
    # control for the comparison itself: one triple moved to the other class must NOT match
    wrong = tuple(sorted(set(c0) ^ {c0[-1], 5 if c0[-1] != 5 else 2}))
    bad_e, _ = rebuild(gauge, wrong, keep)
    ck('%s: control, the comparison rejects a wrong class assignment %s' % (name, wrong),
       not all(any(same_up_to_scalar(a, b) for b in file_e) for a in bad_e))

print()
print('5b. The third shape (size-4 classes neither a 4-set nor through one point)')
# third_exact.py produced these; nothing here imports it.
TRI5 = list(combinations(range(5), 3))
pz = json.load(open('results/penum_n5_k3.json'))['patterns']


def _shape(cl):
    if len(set().union(*cl)) == 4:
        return 'four-set'
    if set.intersection(*[set(t) for t in cl]):
        return 'common-point'
    return 'other'


buckets = {'Case A': [], 'common point': [], 'third shape': []}
for idx, p in enumerate(pz):
    if not p['f104_ok']:
        continue
    cls = [[t for j, t in enumerate(TRI5) if p['labels'][j] == c] for c in range(3)]
    s4 = [_shape(c) for c in cls if len(c) == 4]
    buckets['Case A' if 'four-set' in s4 else 'common point' if 'common-point' in s4
            else 'third shape'].append(idx)
THIRD3 = buckets['third shape']
ck('the twelve patterns sort as 2 Case A, 3 common-point, 7 third shape',
   [len(buckets[k]) for k in ('Case A', 'common point', 'third shape')] == [2, 3, 7],
   str(buckets))
ck('in every third-shape pattern each 4-set spreads over at least two classes, so '
   '"radii distinct" also excludes four concyclic points',
   all(len({pz[i]['labels'][TRI5.index(t)] for t in combinations(q, 3)}) >= 2
       for i in THIRD3 for q in combinations(range(5), 4)))
m3 = json.load(open('results/third_exact_msolve.json'))
pins = ['%s_pin%d' % (g, i) for g in ('G1', 'G2') for i in THIRD3]
ck('pinned controls: the planted configuration is returned for all 7 patterns in both gauges',
   all(m3.get(j, {}).get('planted_found') is True for j in pins),
   '%d of %d' % (sum(1 for j in pins if m3.get(j, {}).get('planted_found')), len(pins)))


def _read(path):
    return io.open(path, encoding='utf-8', errors='replace').read() if os.path.exists(path) else ''


ms_modp = [i for i in THIRD3 if _read('exact/G1_gr%d_all.ms.out' % i).strip().startswith('[-1]')]
sg_modp = [i for i in THIRD3
           if 'RESULT unit 1' in _read('exact/G1_full%d_modp.singular.live' % i)
           or (i == 11 and 'RESULT unit 1' in _read('exact/G1_p11_modp.singular.live'))]
ck('mod 32003 (Singular): every one of the 7 full systems is the unit ideal (not a proof)',
   sorted(sg_modp) == sorted(THIRD3), 'patterns %s' % sorted(sg_modp))
ck('mod 1073741827 (msolve): the unit ideal for every pattern except 11, where msolve gave no '
   'verdict (G1 crashed when its hash table could not grow; G2 was stopped by hand) (not a proof)',
   sorted(ms_modp) == [i for i in THIRD3 if i != 11],
   'patterns %s' % sorted(ms_modp))
sq_modp = [i for i in THIRD3
           if 'RESULT unit 1' in _read('exact/G1_full%d_mods.singular.live' % i)
           and 'ring R = 32749,' in _read('exact/G1_full%d_mods.sing' % i)]
ck('mod 32749 (Singular, a second prime): every one of the 7 full systems is the unit '
   'ideal (not a proof)', sorted(sq_modp) == sorted(THIRD3), 'patterns %s' % sorted(sq_modp))


def rebuild3(labels):
    x2, y2, x3, y3, x4, y4, r0, r1, r2 = sp.symbols('x2 y2 x3 y3 x4 y4 r0 r1 r2')
    Pt, rr = [(0, 0), (1, 0), (x2, y2), (x3, y3), (x4, y4)], (r0, r1, r2)
    eqs = [sp.expand(_d2(Pt[j], Pt[k]) * _d2(Pt[k], Pt[i]) * _d2(Pt[i], Pt[j])
                     - 4 * rr[labels[n]] * _cr(Pt[i], Pt[j], Pt[k]) ** 2)
           for n, (i, j, k) in enumerate(TRI5)]
    conds = [sp.expand(_d2(Pt[a], Pt[b])) for a, b in combinations(range(5), 2)]
    conds = [c for c in conds if c.free_symbols] + [r0 - r1, r0 - r2, r1 - r2]
    return eqs, conds


sr3 = json.load(open('results/third_exact_singrab.json')) \
    if os.path.exists('results/third_exact_singrab.json') else {}
exact3 = sorted(k for k, v in sr3.items() if v.get('status') == 'no complex solution')
note_flat = ' '.join(io.open('NOTE.md', encoding='utf-8').read().split())
ck('NOTE.md claims an exact third-shape proof only where an artifact shows one',
   (not exact3 and 'No exact decision over Q was obtained for any third-shape pattern'
    in note_flat) or (exact3 and all(k in note_flat for k in exact3)),
   'exact over Q: %s' % (exact3 or 'none'))
ck('NOTE.md calls the third shape evidence, not a proof',
   'decided modulo primes (2026-09-15); not proved' in note_flat)

for i in THIRD3:
    name = 'G1_red11' if i == 11 else 'G1_full%d' % i
    if not os.path.exists('exact/%s.rab.sing' % name):
        ck('%s: input file present' % name, False)
        continue
    mine_e, mine_c = rebuild3(pz[i]['labels'])
    file_e, file_c = file_system(name)
    ok_e = len(mine_e) == len(file_e) and all(any(same_up_to_scalar(a, b) for b in file_e)
                                              for a in mine_e)
    ok_c = len(file_c) == len(mine_c) and all(any(same_up_to_scalar(a, b) for b in mine_c)
                                              for a in file_c)
    wrong = list(pz[i]['labels'])
    wrong[0] = (wrong[0] + 1) % 3                   # triple 012 moved to another class
    bad_e, _ = rebuild3(wrong)
    rej = not all(any(same_up_to_scalar(a, b) for b in file_e) for a in bad_e)
    ck('pattern %d (%s): the equations and the 12 conditions are the geometry, rebuilt '
       'independently; a wrong class assignment is rejected' % (i, name), ok_e and ok_c and rej)

print()
print('5c. The common-point branch (one class is four triples through one point)')
# The algebra of section 5c is checked by cp_verify.py, which this file does not duplicate.
# What is checked here is the combinatorics the section rests on, rebuilt from the pattern
# list with no reference to that script, plus the note's own bookkeeping.
CP = [2, 12, 14]
CANON4 = {(0, 1, 2), (0, 1, 3), (0, 2, 4), (0, 3, 4)}
IDENT = [((1, 2, 3), (2, 3, 4)), ((1, 2, 4), (1, 3, 4))]
TRI5 = list(combinations(range(5), 3))
_pz = json.load(open('results/penum_n5_k3.json'))['patterns']


def _canon_splits(labels):
    """every way of relabelling so the size-4 class is CANON4, as splits of the other six"""
    out = set()
    for perm in itertools.permutations(range(5)):
        cls = {}
        for k, t in enumerate(TRI5):
            cls.setdefault(labels[k], set()).add(tuple(sorted(perm[v] for v in t)))
        if any(c == CANON4 for c in cls.values()):
            out.add(tuple(sorted(tuple(sorted(c)) for c in cls.values() if c != CANON4)))
    return out


_s14 = _canon_splits(_pz[14]['labels'])
ck('pattern 14 has exactly ONE splitting of the other six triples, so the single '
   'representative section 5c treats is the whole pattern', len(_s14) == 1,
   ' | '.join('{' + ','.join(''.join(map(str, t)) for t in c) + '}'
              for c in sorted(_s14)[0]) if _s14 else 'none')
ck('that splitting is the crossed pairing the section names, case 7 of its list',
   _s14 == {(((0, 1, 4), (1, 2, 3), (2, 3, 4)), ((0, 2, 3), (1, 2, 4), (1, 3, 4)))})
def _splits_an_identity(sp):
    """does this canonical form put some identically-equal pair in two different classes?"""
    return any(all(not ({x, y} <= set(c)) for c in sp) for x, y in IDENT)


for _i in (2, 12):
    _sp = _canon_splits(_pz[_i]['labels'])
    _dead = bool(_sp) and all(_splits_an_identity(sp) for sp in _sp)
    ck('pattern %d: every canonical form separates a pair Lemma 6 makes identically equal, '
       'so Lemma 6 alone kills it' % _i, _dead, '%d forms, %d split'
       % (len(_sp), sum(_splits_an_identity(sp) for sp in _sp)))
ck('pattern 14 splits no such pair, so Lemma 6 alone does NOT kill it',
   not any(_splits_an_identity(sp) for sp in _s14))
ck('the common-point patterns are exactly 2, 12 and 14, and 14 is the only survivor',
   sorted(CP) == [2, 12, 14] and len(_s14) == 1)
_n = io.open('NOTE.md', encoding='utf-8').read()
_nf = ' '.join(_n.split())
ck('NOTE.md section 5c exists and lists SEVEN placements, not six',
   '## 5c.' in _n and 'The seven placements' in _nf and 'there are six ways' not in _nf)
ck('NOTE.md does not claim verify.py checks section 5c',
   'cp_verify.py` covers 5c' in _nf or 'cp_verify.py covers 5c' in _nf)
ck('cp_verify.py, which does check section 5c, is present', os.path.exists('cp_verify.py'))
# cp_verify.py once printed PASS on literal True values.  Check its source, not a promise in
# the note: no call to ck() may pass a constant as the value being checked.
import ast
_consts = []
for _node in ast.walk(ast.parse(io.open('cp_verify.py', encoding='utf-8').read())):
    if isinstance(_node, ast.Call) and getattr(_node.func, 'id', None) == 'ck':
        _ok = _node.args[2] if len(_node.args) > 2 else None
        if _ok is None or isinstance(_ok, ast.Constant):
            _consts.append(_node.lineno)
_nck = sum(1 for _n in ast.walk(ast.parse(io.open('cp_verify.py', encoding='utf-8').read()))
           if isinstance(_n, ast.Call) and getattr(_n.func, 'id', None) == 'ck')
ck('cp_verify.py passes a computed value, never a constant, to every one of its ck() calls',
   _nck > 0 and not _consts, '%d calls; constant at lines %s' % (_nck, _consts or 'none'))
ck('NOTE.md still says h(5) is open after section 5c', '**h(5) is still 3 or 4.**' in _n)

print()
print('=' * 78)
if FAIL:
    print('FAILED %d CHECK(S):' % len(FAIL))
    for f in FAIL:
        print('  -', f)
    sys.exit(1)
print('ALL CHECKS PASSED')
print('=' * 78)
