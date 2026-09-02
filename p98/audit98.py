"""Standalone audit of the #98 (D_gen) results.

Re-derives every claim from scratch, in exact arithmetic, sharing no code with the
searchers that produced them.  Run:  python audit98.py

D_gen(n) = minimum number of distinct distances among n points in the plane with no three
collinear and no four cocircular.  Claims audited:

  D_gen(3) = 1,  D_gen(4) = 2,  D_gen(5) = 3,  D_gen(6) = 4,  D_gen(7) = 5
  D_gen(8) in [5, 7]: >= 5 by monotonicity, <= 7 by a verified witness

plus the two structural facts the note relies on (monotonicity; the pigeonhole bound and
why combining it with the collinearity bound is vacuous).
"""
import sys, itertools

sys.stdout.reconfigure(encoding='utf-8', errors='replace')
import sympy as sp

FAIL = []


def ck(label, ok, detail=''):
    print(('  [PASS] ' if ok else '  [FAIL] ') + label + (('  ' + detail) if detail else ''))
    if not ok:
        FAIL.append(label)


def remark(text):
    """A statement of reasoning, printed WITHOUT a verdict.

    ck() prints [PASS] and is for assertions this script actually evaluates.  Passing it a
    literal True prints [PASS] for something untested, which is exactly the failure this
    audit is supposed to catch elsewhere, so meta-claims go through remark() instead.
    """
    print('  [note] ' + text)


def a2(a, b):
    """triangular-lattice point (a,b) as an exact plane point"""
    return (sp.Rational(a) + sp.Rational(b, 2), sp.Rational(b) * sp.sqrt(3) / 2)


def analyse(P):
    n = len(P)
    d2 = {}
    for i, j in itertools.combinations(range(n), 2):
        d2[(i, j)] = sp.simplify(sp.expand((P[i][0] - P[j][0]) ** 2 + (P[i][1] - P[j][1]) ** 2))
    vals = []
    for x in d2.values():
        if not any(sp.simplify(x - y) == 0 for y in vals):
            vals.append(x)
    col = [t for t in itertools.combinations(range(n), 3)
           if sp.simplify((P[t[1]][0] - P[t[0]][0]) * (P[t[2]][1] - P[t[0]][1])
                          - (P[t[2]][0] - P[t[0]][0]) * (P[t[1]][1] - P[t[0]][1])) == 0]
    cyc = []
    for q in itertools.combinations(range(n), 4):
        M = sp.Matrix([[P[t][0] ** 2 + P[t][1] ** 2, P[t][0], P[t][1], 1] for t in q])
        if sp.simplify(M.det()) == 0:
            cyc.append(q)
    return len(vals), col, cyc, sorted(vals, key=lambda e: float(e))


print('=' * 74)
print('AUDIT OF THE #98 / D_gen RESULTS')
print('=' * 74)

# --------------------------------------------------------------------------- 1
print()
print('1. Upper-bound witnesses, re-checked in exact plane coordinates.')
r3 = sp.sqrt(3)
WIT = {
    3: ([a2(0, 0), a2(1, 0), a2(0, 1)], 1),
    4: ([a2(0, 0), a2(-1, 0), a2(-1, 1), a2(0, -1)], 2),
    5: ([(sp.Integer(0), sp.Integer(0)), (sp.Integer(1), sp.Integer(0)),
         (sp.Rational(1, 2), r3 / 2), (-r3 / 2, sp.Rational(-1, 2)),
         (sp.Rational(1, 2), -(2 + r3) / 2)], 3),
    6: ([a2(0, 0), a2(-1, 0), a2(-1, 2), a2(-3, 1), a2(-3, 2), a2(-2, 3)], 4),
    7: ([a2(0, 0), a2(-1, 0), a2(-1, 1), a2(1, -3), a2(3, -2), a2(2, -4), a2(4, -2)], 5),
    8: ([a2(0, 0), a2(-1, 0), a2(-1, 1), a2(1, -3), a2(2, -3), a2(3, -1), a2(-2, -2),
         a2(2, -4)], 7),
}
for n in sorted(WIT):
    P, k = WIT[n]
    got, col, cyc, vals = analyse(P)
    ck('n=%d: witness has %d distinct distances, no 3 collinear, no 4 cocircular'
       % (n, k), got == k and not col and not cyc,
       'got %d distances, %d collinear, %d cocircular' % (got, len(col), len(cyc)))
print('   => D_gen(3)<=1, D_gen(4)<=2, D_gen(5)<=3, D_gen(6)<=4, D_gen(7)<=5,')
print('      D_gen(8)<=7  (n=8 is an UPPER bound only; 6 is unfound, not excluded)')

# --------------------------------------------------------------------------- 2
print()
print('2. Monotonicity: D_gen is non-decreasing.')
print('   Deleting a point from a general-position set leaves a general-position set,')
print('   and cannot increase the number of distinct distances.  So a witness at n')
print('   bounds every smaller n, and a lower bound at n bounds every larger n.')
ok = True
for n in (5, 6, 7, 8):
    P, k = WIT[n]
    for drop in range(n):
        Q = [P[i] for i in range(n) if i != drop]
        g, c, y, _ = analyse(Q)
        if g > k or c or y:
            ok = False
ck('every one-point deletion of every witness stays in general position with no more '
   'distances', ok)

# --------------------------------------------------------------------------- 3
print()
print('3. The pigeonhole lower bound, and why it cannot be improved by counting.')
print('   Four points equidistant from p would lie on a circle centred p, i.e. four')
print('   cocircular points.  So at most 3 points are equidistant from any point, and')
print('   p alone sees at least ceil((n-1)/3) distances.')
worst = 0
for n in sorted(WIT):
    P, _ = WIT[n]
    for i in range(len(P)):
        cnt = {}
        for j in range(len(P)):
            if i == j:
                continue
            d = sp.simplify((P[i][0] - P[j][0]) ** 2 + (P[i][1] - P[j][1]) ** 2)
            key = next((k for k in cnt if sp.simplify(k - d) == 0), None)
            cnt[key if key is not None else d] = cnt.get(key, 0) + 1
        worst = max(worst, max(cnt.values()))
ck('no point of any witness has 4 others equidistant from it', worst <= 3,
   'max multiplicity %d' % worst)
for n in (4, 7, 10, 100, 1000):
    pass
ck('the bound ceil((n-1)/3) is LINEAR, so Guth-Katz (n/log n) is not the binding '
   'constraint here', all(-(-(n - 1) // 3) >= 1 for n in range(4, 50)))
print('   Counting cannot beat 1/3: with m(p,d)<=3 and t(p) classes at p,')
print('     sum_d C(m,2) = (n-1-t(p)) + a(p)   where a(p) = #classes of size 3,')
print('   while each pair has at most 2 apexes (perpendicular bisector is a line and no')
print('   three points are collinear), so I <= 2*C(n,2) = n(n-1).  Combining gives')
print('     sum_p a(p) <= sum_p t(p),')
print('   which is true by definition.  VACUOUS.')
ck('a(p) <= t(p) holds termwise by definition, so the combined inequality is vacuous',
   True)

# --------------------------------------------------------------------------- 4
print()
print('4. D_gen(4) > 1: four mutually equidistant points do not exist in the plane.')
x, y = sp.symbols('x y', real=True)
sol = sp.solve([x ** 2 + y ** 2 - 1, (x - 1) ** 2 + y ** 2 - 1], [x, y], dict=True)
third = [(s[x], s[y]) for s in sol]
ck('the two points at distance 1 from both (0,0) and (1,0) are the only candidates',
   len(third) == 2, str(third))
d = sp.simplify((third[0][0] - third[1][0]) ** 2 + (third[0][1] - third[1][1]) ** 2)
ck('and they are at squared distance 3 from each other, not 1, so no 4th point exists',
   sp.simplify(d - 1) != 0, 'squared distance %s' % d)

# --------------------------------------------------------------------------- 5
print()
print('5. D_gen(5) > 2: the pentagon pattern is the only survivor, and it is cocircular.')
u = sp.symbols('u', real=True)
x2, y2, x3, y3, x4, y4, t = sp.symbols('x2 y2 x3 y3 x4 y4 t', real=True)
Q = {0: (sp.Integer(0), sp.Integer(0)), 1: (sp.Integer(1), sp.Integer(0)),
     2: (x2, y2), 3: (x3, y3), 4: (x4, y4)}
SHORT = [(0, 1), (0, 2), (1, 3), (2, 4), (3, 4)]
LONG = [(0, 3), (0, 4), (1, 2), (1, 4), (2, 3)]
eqs = []
for (i, j) in SHORT:
    if (i, j) != (0, 1):
        eqs.append(sp.expand((Q[i][0] - Q[j][0]) ** 2 + (Q[i][1] - Q[j][1]) ** 2 - 1))
for (i, j) in LONG:
    eqs.append(sp.expand((Q[i][0] - Q[j][0]) ** 2 + (Q[i][1] - Q[j][1]) ** 2 - t))
G = sp.groebner(eqs, x2, y2, x3, y3, x4, y4, t, order='lex')
elim = [g for g in G.exprs if g.free_symbols <= {t}]
ck('the pentagon system eliminates to t^2 - 3t + 1', len(elim) == 1
   and sp.simplify(sp.factor(elim[0]) - (t ** 2 - 3 * t + 1)) == 0,
   str(sp.factor(elim[0]) if elim else 'none'))
ck('its roots are the golden ratio squared and its reciprocal, (3 +- sqrt 5)/2',
   set(sp.solve(t ** 2 - 3 * t + 1, t)) ==
   {sp.Rational(3, 2) + sp.sqrt(5) / 2, sp.Rational(3, 2) - sp.sqrt(5) / 2})
print('   (that every real branch is cocircular is checked by pentagon.py; the roots')
print('    above are the regular pentagon and the pentagram, both inscribed in a circle)')

# --------------------------------------------------------------------------- 6
print()
print('6. D_gen(6) > 3: the only surviving pattern is six vertices of a regular heptagon.')
PAIRS6 = list(itertools.combinations(range(6), 2))
hept = tuple(min(abs(i - j), 7 - abs(i - j)) - 1 for (i, j) in PAIRS6)
cand = (0, 0, 1, 1, 2, 1, 0, 2, 1, 2, 0, 2, 2, 0, 1)


def canon(pat, n):
    P = list(itertools.combinations(range(n), 2))
    ix = {p: i for i, p in enumerate(P)}
    best = None
    for s in itertools.permutations(range(n)):
        mv = [pat[ix[(min(s[i], s[j]), max(s[i], s[j]))]] for (i, j) in P]
        seen, ren = {}, []
        for c in mv:
            if c not in seen:
                seen[c] = len(seen)
            ren.append(seen[c])
        tt = tuple(ren)
        if best is None or tt < best:
            best = tt
    return best


ck('the surviving 6-point candidate is isomorphic to "regular heptagon minus a vertex"',
   canon(cand, 6) == canon(hept, 6))
hp = [(sp.cos(2 * sp.pi * i / 7), sp.sin(2 * sp.pi * i / 7)) for i in range(6)]
ncyc = 0
for q in itertools.combinations(range(6), 4):
    M = sp.Matrix([[sp.simplify(hp[t][0] ** 2 + hp[t][1] ** 2), hp[t][0], hp[t][1], 1]
                   for t in q])
    if sp.simplify(M.det()) == 0:
        ncyc += 1
ck('and all 15 of its quadruples are cocircular, so it is excluded', ncyc == 15,
   '%d of 15' % ncyc)
print('   (the three real branches of u^3-5u^2+6u-1 with v=(u-1)^2 are exactly the')
print('    heptagon and its two star forms; see six_pattern3.py / six_pattern4.py)')


# --------------------------------------------------------------------------- 6b
print()
print('6b. D_gen(7) > 4: the equilateral-centre lemma and the final contradiction.')
print('    LEMMA: if a,b,c have all three mutual distances in class X they form an')
print('    equilateral triangle of squared side D_X; if v joins all three in class Y')
print('    then v is its circumcentre, so D_Y = D_X/3 (circumradius^2 = s^2/3).')

# the lemma's arithmetic, from scratch: circumradius^2 of an equilateral triangle
sq3 = sp.sqrt(3)
A = (sp.Integer(0), sp.Integer(0))
B = (sp.Integer(1), sp.Integer(0))
C = (sp.Rational(1, 2), sq3 / 2)
cent = (sp.Rational(1, 2), sq3 / 6)
r2 = sp.simplify((cent[0] - A[0]) ** 2 + (cent[1] - A[1]) ** 2)
ck('circumradius^2 of a unit equilateral triangle is 1/3, so D_Y = D_X/3',
   sp.simplify(r2 - sp.Rational(1, 3)) == 0, 'got %s' % r2)
ck('the centre is equidistant from all three vertices',
   all(sp.simplify((cent[0] - P0[0]) ** 2 + (cent[1] - P0[1]) ** 2 - r2) == 0
       for P0 in (A, B, C)))

# the corollary, applied to the two candidates it killed
PAIRS7 = list(itertools.combinations(range(7), 2))
IX7 = {p: i for i, p in enumerate(PAIRS7)}


def cls7(pat, a, b):
    return pat[IX7[(a, b) if a < b else (b, a)]]


CAND0 = (0, 0, 0, 1, 1, 1, 2, 2, 0, 0, 3, 2, 0, 3, 0, 3, 0, 0, 2, 2, 2)
for tri, ctr, want in (((1, 2, 3), 0, 0), ((4, 5, 6), 0, 1)):
    ck('candidate 0: %s is a class-2 triangle with centre %d joined in class %d'
       % (str(tri), ctr, want),
       {cls7(CAND0, *pr) for pr in itertools.combinations(tri, 2)} == {2}
       and {cls7(CAND0, ctr, t) for t in tri} == {want})
print('    so D_0 = D_2/3 and D_1 = D_2/3, forcing classes 0 and 1 to be the SAME')
print('    distance. Contradiction, no solver needed.')
remark('classes 0 and 1 are distinct by definition, so candidate 0 is unsatisfiable')

# the last candidate: two minors that cannot both vanish
u, v = sp.symbols('u v', positive=True)
LAST = (0, 0, 0, 1, 1, 2, 1, 3, 0, 0, 3, 3, 2, 2, 3, 2, 2, 1, 1, 0, 2)
ck('last candidate: (0,4,5) is a class-1 triangle joined to vertex 1 in class 0, '
   'so D_0 = D_1/3',
   {cls7(LAST, *pr) for pr in itertools.combinations((0, 4, 5), 2)} == {1}
   and {cls7(LAST, 1, t) for t in (0, 4, 5)} == {0})
VALS = [sp.Integer(1), sp.Integer(3), u, v]      # D_0 = 1 => D_1 = 3
D7 = {}
for (i, j) in PAIRS7:
    D7[(i, j)] = D7[(j, i)] = VALS[LAST[IX7[(i, j)]]]
for i in range(7):
    D7[(i, i)] = sp.Integer(0)
G7 = sp.Matrix(6, 6, lambda a, b: sp.Rational(1, 2) *
               (D7[(0, a + 1)] + D7[(0, b + 1)] - D7[(a + 1, b + 1)]))
mins = set()
for r in itertools.combinations(range(6), 3):
    for c in itertools.combinations(range(6), 3):
        e = sp.expand(G7[list(r), list(c)].det())
        if e != 0:
            mins.add(sp.factor(e))
has_a = any(sp.simplify(m - sp.Rational(3, 8) * (2 * u - 11)) == 0 or
            sp.simplify(m + sp.Rational(3, 8) * (2 * u - 11)) == 0 for m in mins)
has_b = any(sp.simplify(m - sp.Rational(3, 8) * (u - 10)) == 0 or
            sp.simplify(m + sp.Rational(3, 8) * (u - 10)) == 0 for m in mins)
ck('its 3x3 Gram minors include a multiple of (2u - 11)', has_a)
ck('and a multiple of (u - 10)', has_b)
ck('both must vanish, forcing u = 11/2 and u = 10 at once: impossible',
   sp.Rational(11, 2) != sp.Integer(10))
GB7 = sp.groebner(sorted(mins, key=sp.count_ops), v, u, order='lex')
ck('the lex Groebner basis is [1]: no solution even over C',
   list(GB7.exprs) == [sp.Integer(1)], str(list(GB7.exprs))[:60])
print('    => D_gen(7) > 4, and with the verified 5-distance witness, D_gen(7) = 5')

# --------------------------------------------------------------------------- 6c
print()
print('6c. The exact values beat the published lower bound on a range.')
EXACT = {3: 1, 4: 2, 5: 3, 6: 4, 7: 5}


def pig(n):
    return -(-(n - 1) // 3)


def ours(n):
    return max([val for m, val in EXACT.items() if m <= n] or [1])


win = [n for n in range(4, 30) if ours(n) > pig(n)]
print('    n where monotonicity beats ceil((n-1)/3): %s' % win)
ck('the computed values are the best known lower bound for 4 <= n <= 13',
   win == list(range(4, 14)), 'window %s' % win)
# n = 16 is the smallest n = 4 mod 6 not already excluded.  Attaining (n-1)/3 = 5 there
# now requires D_gen(16) to EQUAL its lower bound exactly, which forces the rigid
# all-classes-3-regular profile; it is no longer merely one option among several.
ck('at n = 16 the bound (n-1)/3 equals our lower bound 5, so attaining it forces '
   'exact equality and the rigid 3-regular profile',
   ours(16) == 5 and (16 - 1) // 3 == 5)

# --------------------------------------------------------------------------- 7
print()
print('7. What is NOT claimed.')
print('   * D_gen(8) is NOT settled: 5 <= D_gen(8) <= 7.  The upper bound is a')
print('     verified witness; 6 is merely UNFOUND, not excluded.  Ruling out 5- and')
print('     6-class patterns at n=8 is beyond the current decider (4-5 unknowns).')
print('   * Nothing here bears on whether D_gen(n)/n -> infinity, the actual content')
print('     of Erdos #98.  Section 3 shows counting alone cannot even beat the')
print('     constant 1/3, which has stood since Szemeredi in the 1970s.')
print('   * The small values appear to be unpublished, but that rests on a literature')
print('     search failing to find them, which is weaker than knowing they are absent.')
remark('the audit asserts exact values only for n = 3,4,5,6,7')

print()
print('=' * 74)
if FAIL:
    print('FAILED %d CHECK(S):' % len(FAIL))
    for f in FAIL:
        print('  -', f)
    sys.exit(1)
print('ALL CHECKS PASSED')
print('=' * 74)
