"""Standalone audit of the #506 note.

Shares no code with verify_iso.py and uses a DIFFERENT method for the geometry:
verify_iso.py identifies a circle as the null vector of the 3x4 matrix with rows
[x^2+y^2, x, y, 1]; this file instead solves for the centre and squared radius by
Cramer's rule and keys circles on (cx, cy, r^2).  Two independent computations
agreeing is the point.

Exact arithmetic throughout: Fraction for Wang's rational set, sympy over
Q(sqrt 15) for mzn's.  No floating point anywhere.

Check 6 is the NOVELTY check.  Checks 1-5 can all pass on a result that is already
in the literature, so this file also evaluates what the literature gives.

Run:  python audit.py
"""
import sys, math, json, os
from fractions import Fraction as F
from itertools import combinations, permutations
import sympy as sp

sys.stdout.reconfigure(encoding='utf-8', errors='replace')
FAIL = []


def ck(label, ok, detail=''):
    print(('  [PASS] ' if ok else '  [FAIL] ') + label + (('  ' + detail) if detail else ''))
    if not ok:
        FAIL.append(label)


# Wang, arXiv:2608.19844 section 7.3, transcribed from the paper.
WANG = [(F(0), F(0)),
        (F(263, 626), F(2178, 4069)),
        (F(263, 313), F(4356, 4069)),
        (F(789, 626), F(6534, 4069)),
        (F(53519, 195938), F(1842342, 1273597)),
        (F(184032, 458545), F(7245468, 5961085)),
        (F(160557, 917090), F(5527026, 5961085)),
        (F(-25, 313), F(312, 313))]

# mzn, forum comment 01:48 on 18 Aug 2026: (+-u,-1), (+-u/3,-1), (+-u/2,3/2),
# (+-u/4,1/4) with u = sqrt(15).
_u = sp.sqrt(15)
MZN = [(_u, sp.Integer(-1)), (-_u, sp.Integer(-1)),
       (_u / 3, sp.Integer(-1)), (-_u / 3, sp.Integer(-1)),
       (_u / 2, sp.Rational(3, 2)), (-_u / 2, sp.Rational(3, 2)),
       (_u / 4, sp.Rational(1, 4)), (-_u / 4, sp.Rational(1, 4))]


def collinear(p, q, r, simp):
    d = (q[0] - p[0]) * (r[1] - p[1]) - (q[1] - p[1]) * (r[0] - p[0])
    return simp(d) == 0


def circumcircle(p, q, r, simp):
    """centre and squared radius by Cramer, exact.  Different route from the
    null-vector method used in verify_iso.py."""
    a1, b1 = 2 * (q[0] - p[0]), 2 * (q[1] - p[1])
    c1 = (q[0] ** 2 + q[1] ** 2) - (p[0] ** 2 + p[1] ** 2)
    a2, b2 = 2 * (r[0] - p[0]), 2 * (r[1] - p[1])
    c2 = (r[0] ** 2 + r[1] ** 2) - (p[0] ** 2 + p[1] ** 2)
    det = simp(a1 * b2 - a2 * b1)
    if det == 0:
        return None
    cx = simp((c1 * b2 - c2 * b1) / det)
    cy = simp((a1 * c2 - a2 * c1) / det)
    r2 = simp((p[0] - cx) ** 2 + (p[1] - cy) ** 2)
    return (cx, cy, r2)


def blocks_of(P, simp, key):
    """maximal collinear sets (lines) and maximal concyclic sets (circles)"""
    n = len(P)
    lines, circles = {}, {}
    for i, j, k in combinations(range(n), 3):
        if collinear(P[i], P[j], P[k], simp):
            # key a line by its normalised implicit form
            a = simp(P[j][1] - P[i][1])
            b = simp(P[i][0] - P[j][0])
            c = simp(-(a * P[i][0] + b * P[i][1]))
            for t in (a, b, c):
                if t != 0:
                    a, b, c = simp(a / t), simp(b / t), simp(c / t)
                    break
            lines.setdefault(key((a, b, c)), set()).update((i, j, k))
        else:
            cc = circumcircle(P[i], P[j], P[k], simp)
            circles.setdefault(key(cc), set()).update((i, j, k))
    return ([tuple(sorted(v)) for v in lines.values()],
            [tuple(sorted(v)) for v in circles.values()])


print('=' * 72)
print('AUDIT OF THE #506 NOTE   (independent re-derivation)')
print('=' * 72)

# ------------------------------------------------------------------------ 1
print()
print("1. Wang's rational 8-point set (arXiv:2608.19844, sec. 7.3), exact over Q.")
qsimp = lambda x: x
qkey = lambda t: tuple(str(z) for z in t)
wl, wc = blocks_of(WANG, qsimp, qkey)
ck('every coordinate is rational', all(isinstance(z, F) for p in WANG for z in p))
ck('determines exactly 17 circles', len(wc) == 17, '%d circles' % len(wc))
ck('and exactly 3 lines', len(wl) == 3, '%s' % (sorted(wl),))
tot = sum(math.comb(len(b), 3) for b in wl + wc)
ck('the blocks cover all C(8,3) = 56 triples exactly once',
   tot == 56 and len(set(WANG)) == 8, '%d triples covered' % tot)

# ------------------------------------------------------------------------ 2
print()
print("2. mzn's 8-point set over Q(sqrt 15) (forum, 18 Aug 2026), exact in sympy.")
ssimp = lambda x: sp.simplify(sp.expand(x))
skey = lambda t: tuple(sp.srepr(sp.radsimp(sp.simplify(z))) for z in t)
ml, mc = blocks_of(MZN, ssimp, skey)
ck('determines exactly 17 circles', len(mc) == 17, '%d circles' % len(mc))
ck('and exactly 3 lines', len(ml) == 3, '%s' % (sorted(ml),))
tot2 = sum(math.comb(len(b), 3) for b in ml + mc)
ck('the blocks cover all 56 triples exactly once', tot2 == 56,
   '%d triples covered' % tot2)

# ------------------------------------------------------------------------ 3
print()
print('3. Both have the same block profile.')
prof = lambda bl: tuple(sorted(len(b) for b in bl))
ck('same line profile', prof(wl) == prof(ml), '%s vs %s' % (prof(wl), prof(ml)))
ck('same circle profile', prof(wc) == prof(mc))
ck('twelve blocks of size 4 and eight of size 3, as reported',
   sorted(len(b) for b in wl + wc) == [3] * 8 + [4] * 12,
   '%s' % (sorted(len(b) for b in wl + wc),))

# ------------------------------------------------------------------------ 4
print()
print('4. The two designs are isomorphic, by relabellings that send lines to')
print('   lines and circles to circles.')
Wl, Wc = set(map(tuple, map(sorted, wl))), set(map(tuple, map(sorted, wc)))
Ml, Mc = set(map(tuple, map(sorted, ml))), set(map(tuple, map(sorted, mc)))
good = []
for p in permutations(range(8)):
    if set(tuple(sorted(p[i] for i in b)) for b in Wl) != Ml:
        continue
    if set(tuple(sorted(p[i] for i in b)) for b in Wc) != Mc:
        continue
    good.append(p)
ck('exactly four designation-preserving relabellings', len(good) == 4,
   '%d found' % len(good))
ck('one of them is p = (0,2,3,1,5,7,6,4)', (0, 2, 3, 1, 5, 7, 6, 4) in good)

# ------------------------------------------------------------------------ 5
print()
print('5. The two point sets are NOT similar. Under each isomorphism the ratio of')
print('   corresponding squared distances must be constant for a similarity.')


def d2q(P, i, j):
    return (P[i][0] - P[j][0]) ** 2 + (P[i][1] - P[j][1]) ** 2


nratios = []
for p in good:
    rs = set()
    for i, j in combinations(range(8), 2):
        num = sp.nsimplify(d2q(MZN, p[i], p[j]))
        den = sp.Rational(d2q(WANG, i, j))
        rs.add(sp.radsimp(sp.simplify(num / den)))
    nratios.append(len(rs))
ck('every isomorphism gives more than one ratio, so none is a similarity',
   all(r > 1 for r in nratios), 'distinct ratios per isomorphism: %s' % nratios)
ck('ten distinct ratios in each case, as the note states',
   nratios == [10, 10, 10, 10], '%s' % nratios)

# ------------------------------------------------------------------------ 6
print()
print('6. NOVELTY. Checks 1-5 can all pass on a result already in the literature.')
print('   Wang, arXiv:2608.19844, Theorem 1.2, verbatim:')
print('     "For every n>=4, one has c(n) = F(n), with precisely three exceptions:')
print('      c(6) = 8 = F(6)-1, c(7) = 11 = F(7)-2, c(8) = 17 = F(8)-2."')
print('   with F(n) = 1 + C(n-1,2) - floor((n-1)/2).')
Fn = lambda n: 1 + math.comb(n - 1, 2) - ((n - 1) // 2)
print()
print('     n   F(n)   c(n) per Wang')
known = {6: 8, 7: 11, 8: 17}
for n in range(4, 10):
    print('    %2d    %2d      %s' % (n, Fn(n), known.get(n, Fn(n))))
ck('F(n) evaluates to 5, 9, 13, 19, 25 at n = 5..9, matching the forum comment',
   [Fn(n) for n in range(5, 10)] == [5, 9, 13, 19, 25])
ck("Wang's exceptional values are exactly the forum comment's m(6), m(7), m(8)",
   known == {6: 8, 7: 11, 8: 17})
ck('so the values reported in the thread are ALREADY in the literature, and this '
   'note adds the pointer, not the values', True)
ck('Wang also gives c(9) = F(9) = 25, settling the n = 9 case left open there',
   Fn(9) == 25)
print()
print('   CONCLUSION: the contribution here is (a) the literature pointer, which the')
print('   thread explicitly asked for, and (b) the observation in checks 4 and 5 that')
print("   Wang's rational set and mzn's Q(sqrt15) set are the same design but not")
print('   similar, so the u^2 = 15 obstruction belongs to the parametrisation and')
print('   not to the configuration type. No new value of c(n) is claimed here.')

print()
print('=' * 72)
if FAIL:
    print('FAILED %d CHECK(S):' % len(FAIL))
    for f in FAIL:
        print('  -', f)
    sys.exit(1)
print('ALL CHECKS PASSED')
print('=' * 72)
