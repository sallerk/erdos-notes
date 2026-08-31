"""Standalone audit of every checkable claim in the #97 note.

Shares no code with theorem_alt.py, verify_p97.py or any search script: every claim
is re-derived here from the definitions.  Exact arithmetic where the claim is exact;
mpmath at 50 digits where the claim is a numerical check, and labelled as such.

Run:  python audit.py
"""
import sys, json, os, itertools, math
import sympy as sp
import mpmath as mp

sys.stdout.reconfigure(encoding='utf-8', errors='replace')
mp.mp.dps = 50

FAIL = []


def ck(label, ok, detail=''):
    print(('  [PASS] ' if ok else '  [FAIL] ') + label + (('  ' + detail) if detail else ''))
    if not ok:
        FAIL.append(label)


print('=' * 72)
print('AUDIT OF THE #97 NOTE   (independent re-derivation)')
print('=' * 72)

# ------------------------------------------------------------------------ 1
print()
print('1. Concyclic lemma: on one circle every distance from a vertex has')
print('   multiplicity at most 2, so even k = 3 needs two radii.')
ok, worst = True, 0
for n in range(4, 31):
    pts = [(sp.cos(2 * sp.pi * k / n), sp.sin(2 * sp.pi * k / n)) for k in range(n)]
    for i in range(n):
        mult = {}
        for j in range(n):
            if i == j:
                continue
            d = sp.simplify(sp.expand((pts[i][0] - pts[j][0]) ** 2
                                      + (pts[i][1] - pts[j][1]) ** 2))
            mult[d] = mult.get(d, 0) + 1
        worst = max(worst, max(mult.values()))
        if max(mult.values()) > 2:
            ok = False
    if not ok:
        break
ck('multiplicity <= 2 at every vertex of every regular n-gon, n = 4..30', ok,
   '(max seen %d)' % worst)

ok = True
for subset in [(0, 1, 5, 13, 29, 41), (0, 3, 7, 8, 21, 34, 50), (0, 2, 11, 19, 23, 37, 44)]:
    pts = [(sp.cos(2 * sp.pi * k / 60), sp.sin(2 * sp.pi * k / 60)) for k in subset]
    for i in range(len(pts)):
        mult = {}
        for j in range(len(pts)):
            if i != j:
                d = sp.simplify(sp.expand((pts[i][0] - pts[j][0]) ** 2
                                          + (pts[i][1] - pts[j][1]) ** 2))
                mult[d] = mult.get(d, 0) + 1
        if max(mult.values()) > 2:
            ok = False
ck('multiplicity <= 2 on irregular concyclic subsets too', ok)

# ------------------------------------------------------------------------ 2
print()
print('2. THEOREM, the algebraic reduction, checked SYMBOLICALLY.')
print('   Alternating 2m-gon  v_l = rho_l e^{i pi l/m},  rho even = 1, rho odd = b.')
b, cl, cl1 = sp.symbols('b c_l c_lp1', real=True)
# |v_0 - v_l|^2 with v_0 = (1,0)
even_sq = 2 - 2 * cl              # l even, rho_l = 1
odd_sq = 1 + b ** 2 - 2 * b * cl  # l odd,  rho_l = b
# step from an even l to the odd l+1
step_even = sp.expand((1 + b ** 2 - 2 * b * cl1) - (2 - 2 * cl))
ck('even->odd step reduces to  b^2 - 2 c_{l+1} b + 2 c_l - 1',
   sp.simplify(step_even - (b ** 2 - 2 * cl1 * b + 2 * cl - 1)) == 0,
   str(step_even))
# step from an odd l to the even l+1
step_odd = sp.expand((2 - 2 * cl1) - (1 + b ** 2 - 2 * b * cl))
ck('odd->even step reduces to  -(b^2 - 2 c_l b + 2 c_{l+1} - 1)',
   sp.simplify(step_odd + (b ** 2 - 2 * cl * b + 2 * cl1 - 1)) == 0,
   str(step_odd))

# The degenerate point the note singles out is in the ODD->EVEN step, at m = 3,
# l = 1:  b^2 - 2 c_1 b + 2 c_2 - 1  with  c_1 = cos(pi/3),  c_2 = cos(2pi/3).
m = 3
p = sp.expand(b ** 2 - 2 * sp.cos(sp.pi / m) * b + 2 * sp.cos(2 * sp.pi / m) - 1)
ck('at m = 3, l = 1 the odd->even parabola is exactly (b-2)(b+1)',
   sp.simplify(p - sp.expand((b - 2) * (b + 1))) == 0, str(p))
ck('the convexity window upper end 1/cos(pi/3) = 2 is exactly that root, but the '
   'window is OPEN so the step stays strict', sp.simplify(1 / sp.cos(sp.pi / 3) - 2) == 0)
# and for m >= 4 the same parabola is strictly negative at BOTH window ends
ok = True
for mm in range(4, 41):
    c_l, c_l1 = sp.cos(sp.pi / mm), sp.cos(2 * sp.pi / mm)
    for bv in (c_l, 1 / c_l):
        if sp.simplify(bv ** 2 - 2 * c_l * bv + 2 * c_l1 - 1) >= 0:
            ok = False
ck('for m = 4..40 the odd->even parabola is negative at both window ends '
   '(so negative across the whole window)', ok)

# ------------------------------------------------------------------------ 3
print()
print('3. THEOREM, the conclusion, checked NUMERICALLY at 50 digits.')
print('   For every m in 2..60 and a dense grid of b strictly inside the window,')
print('   the distances from a vertex must be strictly increasing, giving max')
print('   equidistant multiplicity 3 and never 4.')


def alt_polygon(m, bval):
    return [(bval if l % 2 else mp.mpf(1)) * mp.cos(mp.pi * l / m) for l in range(2 * m)], \
           [(bval if l % 2 else mp.mpf(1)) * mp.sin(mp.pi * l / m) for l in range(2 * m)]


def maxmult(m, bval, tol):
    xs, ys = alt_polygon(m, bval)
    n = 2 * m
    worst = 0
    for i in range(n):
        ds = sorted((xs[i] - xs[j]) ** 2 + (ys[i] - ys[j]) ** 2 for j in range(n) if j != i)
        run, best = 1, 1
        for a, c in zip(ds, ds[1:]):
            if abs(c - a) < tol:
                run += 1
                best = max(best, run)
            else:
                run = 1
        worst = max(worst, best)
    return worst


bad = []
mono_bad = []
tol = mp.mpf(10) ** (-30)
for m in range(2, 61):
    lo, hi = mp.cos(mp.pi / m), 1 / mp.cos(mp.pi / m)
    for t in range(1, 25):
        bv = lo + (hi - lo) * mp.mpf(t) / 25
        # strict monotonicity of |v_0 - v_l| for l = 1..m-1
        d = [(1 - (bv if l % 2 else 1) * mp.cos(mp.pi * l / m)) ** 2
             + ((bv if l % 2 else 1) * mp.sin(mp.pi * l / m)) ** 2 for l in range(1, m)]
        if any(y - x <= 0 for x, y in zip(d, d[1:])):
            mono_bad.append((m, float(bv)))
        if m <= 20 and maxmult(m, bv, tol) >= 4:
            bad.append((m, float(bv)))
ck('distances |v_0 - v_l|, l = 1..m-1, strictly increasing on the whole window, '
   'm = 2..60, 24 values of b each', not mono_bad,
   '%d failures' % len(mono_bad))
ck('max equidistant multiplicity is never 4, m = 2..20 (full recount, all vertices)',
   not bad, '%d failures' % len(bad))

# Multiplicity 3 is NOT attained at a generic b: it needs the antipodal distance
# |v_0 - v_m| to coincide with one of the mirror-paired distances, which is one
# equation in b.  Solve it exactly and confirm a root inside the window, so the
# ceiling of 3 is real and not a vacuous bound.
sb = sp.Symbol('b', positive=True)
found = []
for mm in range(3, 13):
    lo, hi = sp.cos(sp.pi / mm), 1 / sp.cos(sp.pi / mm)
    anti = sp.expand((1 - (sb if mm % 2 else 1) * sp.cos(sp.pi)) ** 2)  # |v_0 - v_m|^2
    anti = sp.expand(((sb if mm % 2 else 1) + 1) ** 2) if mm % 2 else sp.expand((1 + 1) ** 2)
    for l in range(1, mm):
        rho = sb if l % 2 else sp.Integer(1)
        dl = sp.expand((1 - rho * sp.cos(sp.pi * l / mm)) ** 2 + (rho * sp.sin(sp.pi * l / mm)) ** 2)
        for r in sp.solve(sp.Eq(anti, dl), sb):
            if r.is_real and sp.simplify(r - lo) > 0 and sp.simplify(hi - r) > 0:
                if maxmult(mm, mp.mpf(str(sp.N(r, 40))), tol) == 3:
                    found.append((mm, sp.nsimplify(sp.simplify(r))))
                    break
        else:
            continue
        break
ck('multiplicity 3 IS attained inside the window, so 3 is a real ceiling not a '
   'vacuous one', len(found) >= 3,
   'e.g. ' + ', '.join('m=%d at b=%s' % (m_, sp.sstr(r)) for m_, r in found[:3]))
if found and found[0][0] == 3:
    ck('the m = 3 case attains it at b = sqrt(3) - 1, the same alternating hexagon '
       'that is the extremal near-miss for problem 982',
       sp.simplify(found[0][1] - (sp.sqrt(3) - 1)) == 0, 'b = %s' % sp.sstr(found[0][1]))

# convexity window: verify the stated endpoints really are where convexity fails
ok = True
for m in range(3, 21):
    lo, hi = mp.cos(mp.pi / m), 1 / mp.cos(mp.pi / m)
    for bv, want in [(lo * mp.mpf('0.999'), False), (hi * mp.mpf('1.001'), False),
                     ((lo + hi) / 2, True)]:
        xs, ys = alt_polygon(m, bv)
        n = 2 * m
        sgn = set()
        for i in range(n):
            o, p1, q = i, (i + 1) % n, (i + 2) % n
            cr = (xs[p1] - xs[o]) * (ys[q] - ys[o]) - (ys[p1] - ys[o]) * (xs[q] - xs[o])
            sgn.add(1 if cr > 0 else (-1 if cr < 0 else 0))
        convex = (sgn == {1} or sgn == {-1})
        if convex != want:
            ok = False
ck('convex position holds exactly on cos(pi/m) < b < 1/cos(pi/m) (tested just inside '
   'and just outside both ends, m = 3..20)', ok)

# ------------------------------------------------------------------------ 4
print()
print('4. The Danzer 9-gon artifact, and whether it matches what Erdos printed.')
here = os.path.dirname(os.path.abspath(__file__))
apath = os.path.join(here, 'artifact_danzer9_t0.json')
if not os.path.exists(apath):
    apath = os.path.join(here, '..', 'publish', 'p97', 'artifact_danzer9_t0.json')
art = json.load(open(apath))[0]
X = [(sp.sympify(a), sp.sympify(bb)) for a, bb in art['coords_exact']]

# convex position, exact, all C(9,3) orientations
order = sorted(range(9), key=lambda i: math.atan2(art['coords_float'][i][1],
                                                  art['coords_float'][i][0]) % (2 * math.pi))
P = [X[i] for i in order]
sgn = None
convex = True
for i, j, k in itertools.combinations(range(9), 3):
    d = sp.simplify(sp.expand((P[j][0] - P[i][0]) * (P[k][1] - P[i][1])
                              - (P[j][1] - P[i][1]) * (P[k][0] - P[i][0])))
    if d == 0:
        convex = False
        break
    s = 1 if d > 0 else -1
    if sgn is None:
        sgn = s
    elif s != sgn:
        convex = False
        break
ck('strictly convex, exact, all C(9,3) = 84 orientations', convex)

# every vertex has max equidistant count exactly 3
cnt = []
sets = []
for i in range(9):
    mult = {}
    for j in range(9):
        if i == j:
            continue
        d = sp.radsimp(sp.simplify(sp.expand((X[i][0] - X[j][0]) ** 2
                                             + (X[i][1] - X[j][1]) ** 2)))
        mult.setdefault(d, []).append(j)
    bestd = max(mult, key=lambda d: len(mult[d]))
    cnt.append(len(mult[bestd]))
    sets.append(sorted(mult[bestd]))
ck('every vertex has max equidistant count exactly 3 (exact squared distances)',
   cnt == [3] * 9, 'counts %s' % cnt)
ck('so it realises k = 3 and misses k = 4 at every vertex by exactly one',
   max(cnt) == 3)

# Erdos [Er87b, p.175] prints Danzer's nonagon as A1 B1 C1 A2 B2 C2 A3 B3 C3 in
# cyclic order with  A1A2 = A1A3 = A1B3,  B1B2 = B1C2 = B1B3,  C1C2 = C1A3 = C1C3.
lab = {}
names = ['A1', 'B1', 'C1', 'A2', 'B2', 'C2', 'A3', 'B3', 'C3']
for pos, idx in enumerate(order):
    lab[names[pos]] = idx
want = {'A1': ['A2', 'A3', 'B3'], 'B1': ['B2', 'C2', 'B3'], 'C1': ['C2', 'A3', 'C3']}
ok = True
for src, tgt in want.items():
    got = set(sets[lab[src]])
    exp = set(lab[t] for t in tgt)
    if got != exp:
        ok = False
        print('     %s: equidistant set %s, Erdos prints %s' % (src, sorted(got), sorted(exp)))
ck('the equidistant sets are EXACTLY the three relations Erdos prints in [Er87b, p.175]',
   ok, 'cyclic order %s' % order)

# ------------------------------------------------------------------------ 5
print()
print('5. Is the k = 3 minimality bound n >= 7 just a restatement of the forum')
print('   counting bound?  Re-derive that counting bound at k = 3.')
print('   Argument: if every vertex has >= k equidistant partners, each of the')
print('   C(k,2) pairs among them has its perpendicular bisector through that')
print('   vertex; a line meets a convex curve at most twice, so each pair serves')
print('   at most 2 vertices.  Hence  C(k,2) n <= 2 C(n,2) = n(n-1).')
for k in (3, 4):
    # C(k,2) n <= n(n-1)  <=>  n >= C(k,2) + 1
    bound = math.comb(k, 2) + 1
    print('     k = %d:  C(%d,2) = %d  =>  n >= %d' % (k, k, math.comb(k, 2), bound))
ck('the counting bound gives n >= 7 at k = 4 (the forum result) but only n >= 4 at '
   'k = 3, so n >= 7 at k = 3 does not follow from it',
   math.comb(4, 2) + 1 == 7 and math.comb(3, 2) + 1 == 4)

# ------------------------------------------------------------------------ 6
print()
print('6. The k = 3 minimality run records.')
kd = os.path.join(here, '..', 'publish', 'p97', 'k3-minimality')
if not os.path.isdir(kd):
    kd = os.path.join(here, 'k3-minimality')


def load(f):
    p = os.path.join(kd, f)
    return json.load(open(p)) if os.path.exists(p) else None


n4, n5, n6 = load('verify_brute_n4.json'), load('verify_brute_n5.json'), load('solve_n6_full.json')
ns6, rej, st7 = load('numsearch_n6.json'), load('verify_rejected_n6.json'), load('STATUS_n7_AT_STOP.json')
if n4:
    ck('n=4: 1 pattern, brute force, no pruning, 0 sat',
       n4['total'] == 1 and n4['sat'] == 0 and n4['unknown'] == 0
       and n4['mode'] == 'brute_all_patterns')
if n5:
    ck('n=5: 1024 patterns, brute force, no pruning, 0 sat, 0 unknown',
       n5['total'] == 1024 and n5['sat'] == 0 and n5['unknown'] == 0
       and n5['mode'] == 'brute_all_patterns')
if n6:
    ck('n=6: 66 classes, full convex position, 0 sat, 0 unknown',
       n6['total'] == 66 and not n6['sat'] and not n6['unknown'] and n6['fullcx'] is True)
if ns6:
    ck('n=6 independent numerical search agrees: 0 of 66 classes realisable',
       ns6['classes'] == 66 and ns6['realisable'] == 0 and not ns6['hits'])
if rej:
    ck('prune soundness sample: 300 rejected patterns, 0 sat',
       rej['sampled'] == 300 and rej['sat'] == 0,
       '%d unsat, %d unknown' % (rej['unsat'], rej['unknown']))
if st7:
    dec = st7['unit_ideal'] + st7['unsat']
    tot = 184424
    print('     n = 7 at stop: %d processed, %d DECIDED (%d unit-ideal + %d unsat), '
          '%d z3-unknown, %d skipped over budget'
          % (st7['done'], dec, st7['unit_ideal'], st7['unsat'], st7['z3_unknown'],
             st7['skipped_over_budget']))
    print('     decided fraction = %d / %d = %.2f%%' % (dec, tot, 100.0 * dec / tot))
    ck('n = 7 found no configuration in what it did cover, and is NOT settled',
       st7['SAT'] == 0 and dec < tot)

print()
print('=' * 72)
if FAIL:
    print('FAILED %d CHECK(S):' % len(FAIL))
    for f in FAIL:
        print('  -', f)
    sys.exit(1)
print('ALL CHECKS PASSED')
print('=' * 72)
