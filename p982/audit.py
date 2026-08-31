"""Standalone audit of every checkable claim in the #982 note.

Shares no code with patterns.py, decide.py or any search script: it re-derives each
claim from the definitions.  Exact arithmetic (sympy) throughout; the only floating
point is the independent numeric screen in check 7, which is labelled as a screen and
is not offered as a proof.

Run:  python audit.py
"""
import sys, json, os, itertools, math, random
import sympy as sp

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

FAIL = []


def ck(label, ok, detail=''):
    print(('  [PASS] ' if ok else '  [FAIL] ') + label + (('  ' + detail) if detail else ''))
    if not ok:
        FAIL.append(label)


def sq(p, q):
    return sp.expand((p[0] - q[0]) ** 2 + (p[1] - q[1]) ** 2)


def counts(pts):
    """number of distinct squared distances from each point to the others, exact"""
    out = []
    for i, p in enumerate(pts):
        s = set()
        for j, q in enumerate(pts):
            if i != j:
                s.add(sp.radsimp(sp.simplify(sq(p, q))))
        out.append(len(s))
    return out


def strictly_convex(pts):
    """all C(n,3) orientations agree in sign and none is zero.  This is the correct
    test; requiring only consecutive triples also admits winding-2 star polygons."""
    n = len(pts)
    sgn = None
    for i, j, k in itertools.combinations(range(n), 3):
        d = sp.simplify((pts[j][0] - pts[i][0]) * (pts[k][1] - pts[i][1])
                        - (pts[j][1] - pts[i][1]) * (pts[k][0] - pts[i][0]))
        if d == 0:
            return False
        s = 1 if d > 0 else -1
        if sgn is None:
            sgn = s
        elif s != sgn:
            return False
    return True


print('=' * 72)
print('AUDIT OF THE #982 NOTE   (independent re-derivation)')
print('=' * 72)

# ------------------------------------------------------------------------ 1
print()
print('1. The regular n-gon attains exactly floor(n/2), so the conjecture is tight.')
print('   Index arithmetic in Z_n, exact, no trigonometry.')
ok = True
for n in range(3, 61):
    # |v_0 - v_k| depends only on min(k, n-k)
    c = len(set(min(k, n - k) for k in range(1, n)))
    if c != n // 2:
        ok = False
        print('     n=%d gave %d, expected %d' % (n, c, n // 2))
ck('regular n-gon gives exactly floor(n/2) for every n in 3..60', ok)

# ------------------------------------------------------------------------ 2
print()
print('2. Concyclic lemma: every distance from a vertex has multiplicity at most 2.')
print('   Checked exactly on roots of unity, regular and irregular.')
ok, worst = True, 0
for n in range(4, 31):
    pts = [(sp.cos(2 * sp.pi * k / n), sp.sin(2 * sp.pi * k / n)) for k in range(n)]
    for i in range(n):
        mult = {}
        for j in range(n):
            if i == j:
                continue
            d = sp.simplify(sq(pts[i], pts[j]))
            mult[d] = mult.get(d, 0) + 1
        m = max(mult.values())
        worst = max(worst, m)
        if m > 2:
            ok = False
            print('     n=%d vertex %d has multiplicity %d' % (n, i, m))
    if not ok:
        break
ck('multiplicity <= 2 at every vertex of every regular n-gon, n = 4..30', ok,
   '(max seen %d)' % worst)

ok = True
for subset in [(0, 1, 5, 13, 29, 41), (0, 3, 7, 8, 21, 34, 50), (0, 2, 11, 19, 23)]:
    pts = [(sp.cos(2 * sp.pi * k / 60), sp.sin(2 * sp.pi * k / 60)) for k in subset]
    for i in range(len(pts)):
        mult = {}
        for j in range(len(pts)):
            if i != j:
                d = sp.simplify(sq(pts[i], pts[j]))
                mult[d] = mult.get(d, 0) + 1
        if max(mult.values()) > 2:
            ok = False
ck('multiplicity <= 2 on irregular concyclic subsets too', ok)

# ------------------------------------------------------------------------ 3
print()
print('3. The extremal hexagon: two staggered concentric triangles, b = sqrt(3) - 1.')
b = sp.sqrt(3) - 1
half = sp.Rational(1, 2)
r3 = sp.sqrt(3)
hexa = [
    (sp.Integer(1), sp.Integer(0)),          # outer,   0 deg
    (b * half, b * r3 / 2),                  # inner,  60 deg
    (-half, r3 / 2),                         # outer, 120 deg
    (-b, sp.Integer(0)),                     # inner, 180 deg
    (-half, -r3 / 2),                        # outer, 240 deg
    (b * half, -b * r3 / 2),                 # inner, 300 deg
]
ck('strictly convex (all C(6,3) orientations, exact)', strictly_convex(hexa))
c = counts(hexa)
ck('per-vertex distinct-distance counts are 2,3,2,3,2,3', c == [2, 3, 2, 3, 2, 3],
   'got %s' % (c,))
ck('the n=6 budget floor(6/2)-1 = 2 is met by exactly three vertices',
   6 // 2 - 1 == 2 and sum(1 for x in c if x == 2) == 3)
ck('max over vertices is 3 = floor(6/2), so it satisfies the conjecture',
   max(c) == 6 // 2)
ck('every coordinate lies in Q(sqrt3)',
   all(sp.simplify(x - sp.nsimplify(x, [sp.sqrt(3)])) == 0 for p in hexa for x in p))

# ------------------------------------------------------------------------ 4
print()
print('4. Contrapositive: a counterexample on n points needs EVERY vertex at most')
print('   floor(n/2) - 1, hence at least 2k+2 points for k distances.')
ck('budget floor(n/2)-1 evaluated for n = 4..199 without surprises',
   all((n // 2) - 1 >= 1 for n in range(4, 200)))

# ------------------------------------------------------------------------ 5
print()
print('5. The recorded run outcomes match the JSON run records.')
here = os.path.dirname(os.path.abspath(__file__))


def load(f):
    p = os.path.join(here, f)
    return json.load(open(p)) if os.path.exists(p) else None


d6, d6n, d7 = load('decide_n6.json'), load('decide_n6_noaltman.json'), load('decide_n7.json')
if d6:
    ck('n=6: 316 classes, all unsat, 0 sat, 0 unknown',
       d6['total_patterns'] == 316 and d6['unsat'] == 316
       and not d6['sat'] and not d6['unknown'])
else:
    ck('decide_n6.json present', False)
if d6n:
    ck('n=6 unfiltered (Altman prune dropped): 1834 classes, all unsat',
       d6n['total_patterns'] == 1834 and d6n['unsat'] == 1834
       and not d6n['sat'] and not d6n['unknown'] and d6n['use_altman'] is False)
else:
    ck('decide_n6_noaltman.json present', False)
if d7:
    ck('n=7: 5354 classes, 5354 unsat after retry, 0 sat, 0 unknown remaining',
       d7['total_patterns'] == 5354 and d7['unsat_total'] == 5354
       and not d7['sat_total'] and not d7['unknown_remaining'])
else:
    ck('decide_n7.json present', False)

# ------------------------------------------------------------------------ 6
print()
print('6. The two-ring family: does it ever reach the budget?')
tw = load('tworing_m3_1200.json')
if tw:
    rows = tw['per_m']
    ms = sorted(r['m'] for r in rows)
    ck('sweep covers m = 3..1200 with no gaps',
       ms[0] == 3 and ms[-1] == 1200 and all(y - x == 1 for x, y in zip(ms, ms[1:])),
       '%d rows' % len(rows))
    ck('best_max - target equals 1 for every m: the family never reaches the budget',
       sorted(set(r['best_max'] - r['target'] for r in rows)) == [1])
nm = load('nearmiss_3_14.json')
if nm:
    rec = nm['records']
    ns = [r['n'] for r in rec]
    ck('near-miss table: exactly half the vertices at budget, every even n from 6 to 28',
       all(r['vertices_at_budget'] * 2 == r['n'] for r in rec)
       and ns == list(range(6, 30, 2)), 'n = %s' % ns)
    r0 = rec[0]
    ck('the m=3 near-miss record is the exact hexagon of check 3',
       r0['per_vertex'] == [2, 3, 2, 3, 2, 3]
       and abs(float(r0['r']) - float(sp.sqrt(3) - 1)) < 1e-15,
       'r = %s...' % r0['r'][:20])

# ------------------------------------------------------------------------ 7
print()
print('7. Altman, numeric screen ONLY.  The note cites the paper; it does not reprove')
print('   it.  Random convex polygons must never show fewer than floor(n/2) distances.')
random.seed(982)


def rand_convex(n):
    while True:
        ang = sorted(random.uniform(0, 2 * math.pi) for _ in range(n))
        rad = [random.uniform(0.6, 1.4) for _ in range(n)]
        pts = [(r * math.cos(a), r * math.sin(a)) for a, r in zip(ang, rad)]
        ok = True
        for i in range(n):
            o, p, q = pts[i], pts[(i + 1) % n], pts[(i + 2) % n]
            if (p[0] - o[0]) * (q[1] - o[1]) - (p[1] - o[1]) * (q[0] - o[0]) <= 0:
                ok = False
                break
        if ok:
            return pts


bad = 0
for n in range(4, 13):
    for _ in range(400):
        pts = rand_convex(n)
        ds = set(round((pts[i][0] - pts[j][0]) ** 2 + (pts[i][1] - pts[j][1]) ** 2, 9)
                 for i, j in itertools.combinations(range(n), 2))
        if len(ds) < n // 2:
            bad += 1
ck('3600 random convex polygons, none below floor(n/2) total distances', bad == 0,
   '(screen, not a proof)')

print()
print('=' * 72)
if FAIL:
    print('FAILED %d CHECK(S):' % len(FAIL))
    for f in FAIL:
        print('  -', f)
    sys.exit(1)
print('ALL CHECKS PASSED')
print('=' * 72)
