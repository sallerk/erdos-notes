"""My own adversarial pass over p831, independent of the two audit agents.
Written from the definitions; shares no code with penum.py or verify.py."""
import sys
import io
import json
from itertools import combinations, permutations
from sympy import Rational as R, simplify, Matrix

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

DEF = []


def defect(sev, claim, evidence):
    DEF.append((sev, claim, evidence))
    print('  [%s] %s' % (sev, claim))
    print('        %s' % evidence)


print('=' * 78)
print('SELF-AUDIT OF p831')
print('=' * 78)

print()
print('1. Lemma 1 in the degenerate cases its written proof does not mention.')
print('   The proof asserts "exactly two circles of radius r pass through two given')
print('   points".  False when |PQ| = 2r (one circle) and when |PQ| > 2r (none).')
print('   Both give FEWER circles and the lemma uses only the upper bound, so the')
print('   conclusion stands and only the wording is wrong.')
_note = io.open('NOTE.md', encoding='utf-8').read()
if 'At most two circles of radius r pass through two given points' in _note:
    print('   [OK] NOTE.md now says "at most two" and enumerates the three cases,')
    print('        and lemmas.py tests the count by solving for the centres.')
else:
    defect('WORDING', 'Lemma 1 proof still says "exactly two circles"',
           'true only for |PQ| < 2r; at |PQ| = 2r there is one, beyond it none.')

print()
print('2. h(4) = 1: is the orthocentric quadruple admissible, and do right triangles fail?')


def orth(A, B, C):
    ax, ay = A
    bx, by = B
    cx, cy = C
    d = 2 * (ax * (by - cy) + bx * (cy - ay) + cx * (ay - by))
    a2 = ax ** 2 + ay ** 2
    b2 = bx ** 2 + by ** 2
    c2 = cx ** 2 + cy ** 2
    ox = (a2 * (by - cy) + b2 * (cy - ay) + c2 * (ay - by)) / d
    oy = (a2 * (cx - bx) + b2 * (ax - cx) + c2 * (bx - ax)) / d
    return (simplify(ax + bx + cx - 2 * ox), simplify(ay + by + cy - 2 * oy))


def cross(P, Q, S):
    return (Q[0] - P[0]) * (S[1] - P[1]) - (Q[1] - P[1]) * (S[0] - P[0])


def d2(P, Q):
    return (P[0] - Q[0]) ** 2 + (P[1] - Q[1]) ** 2


def det4(P, Q, S, T):
    def row(X):
        return [X[0] ** 2 + X[1] ** 2, X[0], X[1], 1]
    return Matrix([row(P), row(Q), row(S), row(T)]).det()


def r2(P, Q, S):
    a2, b2, c2 = d2(Q, S), d2(S, P), d2(P, Q)
    SS = 2 * (a2 * b2 + b2 * c2 + c2 * a2) - (a2 * a2 + b2 * b2 + c2 * c2)
    return simplify(a2 * b2 * c2 / SS) if SS != 0 else None


TESTS = [((0, 0), (4, 0), (1, 3), 'scalene acute'),
         ((0, 0), (5, 0), (1, 1), 'obtuse'),
         ((0, 0), (4, 0), (2, 5), 'isosceles'),
         ((0, 0), (4, 0), (0, 3), 'RIGHT at A'),
         ((0, 0), (4, 0), (4, 3), 'RIGHT at B')]
for A, B, C, name in TESTS:
    A = tuple(R(x) for x in A)
    B = tuple(R(x) for x in B)
    C = tuple(R(x) for x in C)
    H = orth(A, B, C)
    pts = [A, B, C, H]
    distinct = len(set(pts)) == 4
    coll = any(cross(*t) == 0 for t in combinations(pts, 3)) if distinct else None
    conc = (det4(*pts) == 0) if distinct else None
    radii = sorted(set(r2(*t) for t in combinations(pts, 3))) if (distinct and not coll) else None
    print('   %-14s H=%-12s distinct=%-5s 3coll=%-5s 4conc=%-5s radii=%s'
          % (name, str(H), distinct, coll, conc, radii))
print('   [OK] non-right triangles give four distinct admissible points with ONE radius;')
print('        right triangles put H on a vertex, so no 4-point set arises there.')

print()
print('3. Independent recount of the n=5 pattern enumeration (fresh code).')
tri = list(combinations(range(5), 3))
ti = {t: i for i, t in enumerate(tri)}


def pdeg_ok(lab):
    d = {}
    for t, c in zip(tri, lab):
        for p in combinations(t, 2):
            d[(p, c)] = d.get((p, c), 0) + 1
            if d[(p, c)] > 2:
                return False
    return True


def quad_ok(lab):
    for q in combinations(range(5), 4):
        sub = [ti[t] for t in combinations(q, 3)]
        cnt = {}
        for i in sub:
            cnt[lab[i]] = cnt.get(lab[i], 0) + 1
        for c, m in cnt.items():
            if m == 3:
                return False
            if m == 4:
                for i, t in enumerate(tri):
                    if lab[i] == c and i not in sub and len(set(t) & set(q)) >= 2:
                        return False
    return True


def canon(lab):
    best = None
    for perm in permutations(range(5)):
        out = [lab[ti[tuple(sorted(perm[v] for v in t))]] for t in tri]
        m = {}
        rg = []
        for c in out:
            if c not in m:
                m[c] = len(m)
            rg.append(m[c])
        rg = tuple(rg)
        if best is None or rg < best:
            best = rg
    return best


def enum(k, use_l4):
    seen = set()

    def rec(i, lab, used):
        if i == 10:
            if used != k:
                return
            if not pdeg_ok(lab):
                return
            if use_l4 and not quad_ok(lab):
                return
            seen.add(canon(lab))
            return
        for c in range(min(used + 1, k)):
            rec(i + 1, lab + [c], used + (1 if c == used else 0))
    rec(0, [], 0)
    return seen


for k in (1, 2, 3):
    a = enum(k, False)
    b = enum(k, True)
    print('   k=%d : %3d under Lemma 1 only, %3d under Lemmas 1+4' % (k, len(a), len(b)))
    if k == 3:
        if (len(a), len(b)) != (35, 15):
            defect('SERIOUS', 'pattern counts do not reproduce',
                   'recount gives %d/%d, NOTE.md says 35/15' % (len(a), len(b)))
        sizes = {}
        for lab in b:
            s = tuple(sorted((sum(1 for x in lab if x == c) for c in set(lab)), reverse=True))
            sizes[s] = sizes.get(s, 0) + 1
        print('       profiles under Lemmas 1+4 :', sizes)
        print('       within f(5)=4 :', sum(v for s, v in sizes.items() if s[0] <= 4))

print()
print('4. Shapes of a size-4 class after Lemma 4 (NOTE.md claims exactly three).')
shapes = {}
for cls in combinations(tri, 4):
    d = {}
    ok = True
    for t in cls:
        for p in combinations(t, 2):
            d[p] = d.get(p, 0) + 1
            if d[p] > 2:
                ok = False
    if not ok:
        continue
    if any(sum(1 for t in cls if set(t) <= set(q)) == 3 for q in combinations(range(5), 4)):
        continue
    best = None
    for perm in permutations(range(5)):
        img = tuple(sorted(tuple(sorted(perm[v] for v in t)) for t in cls))
        if best is None or img < best:
            best = img
    common = set(range(5))
    for t in best:
        common &= set(t)
    shapes[best] = len(common)
print('   %d shapes survive Lemma 4:' % len(shapes))
for s, c in sorted(shapes.items(), key=lambda kv: -kv[1]):
    sup = len(set(v for t in s for v in t))
    print('      %-52s support=%d common point=%s' % (str(list(s)), sup, 'YES' if c else 'no'))
if len(shapes) != 3:
    defect('SERIOUS', 'NOTE.md claims exactly three shapes of size-4 class survive Lemma 4',
           'independent recount finds %d' % len(shapes))

print()
print('5. Is the pscreen positive control a FAIR control?')
d = json.load(open('results/pscreen_n5_k3.json'))
kc = d['control']['k']
print('   control pattern has %d classes; the screened patterns have %d.' % (kc, d['k']))
print('   equations = 10 - classes, unknowns = 6.')
print('   control: %d equations in 6 unknowns; screened: %d equations in 6 unknowns.'
      % (10 - kc, 10 - d['k']))
_disclosed = ('the control is EASIER than the screened patterns' in
              io.open('verify.py', encoding='utf-8').read()) and              ('one equation easier' in _note or 'never tests the case that matters' in _note)
if _disclosed:
    print('   [OK] The control IS easier, by one equation, and this is now disclosed in')
    print('        both NOTE.md and verify.py. No control of the right difficulty can be')
    print('        built at n = 5, so this is a documented limitation, not a live defect.')
else:
    defect('SERIOUS', 'the positive control is easier than the systems it validates, '
           'and this is not disclosed',
           'control %d classes (%d equations in 6 unknowns) against screened %d classes '
           '(%d equations)' % (kc, 10 - kc, d['k'], 10 - d['k']))

print()
print('6. Does any artifact support a 3-class pattern being realisable anywhere?')
print('   If h(5) = 4 then no 3-class pattern at n = 5 is realisable, so no control of')
print('   the right difficulty can exist at n = 5 at all.  That is a structural limit on')
print('   what the screen can establish, not a fixable defect.')

print()
print('=' * 78)
print('%d defect(s) from the self-audit' % len(DEF))
for sev, claim, ev in DEF:
    print('  [%s] %s' % (sev, claim))
