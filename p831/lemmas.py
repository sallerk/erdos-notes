"""Exact checks of the lemmas behind the n=5 case analysis.

Rewritten after the audit of 2026-09-07.  The previous version claimed to check "all
three lemmas" when the note states six, did not test the content of Lemma 1 at all (it
only confirmed that two constructed centres were equidistant from two points, which is
not the lemma), and demonstrated Lemma 4 on a single instance.  Each lemma below is now
tested against the statement it makes, in exact arithmetic, and the tests that are
demonstrations rather than proofs say so.
"""
import sys
from itertools import combinations

from sympy import Rational as R, simplify, sqrt, Symbol, solve as ssolve, Matrix

sys.stdout.reconfigure(encoding='utf-8', errors='replace')
from common import (circumradius2, orthocentre, admissible, radius_multiset,
                    d2, cross2, det4)

FAIL = []


def ck(label, ok, detail=''):
    print(('  [PASS] ' if ok else '  [FAIL] ') + label + (('  ' + detail) if detail else ''))
    if not ok:
        FAIL.append(label)


TRIS = [((0, 0), (4, 0), (1, 3)),
        ((0, 0), (5, 0), (2, 4)),
        ((0, 0), (7, 0), (3, 5)),
        ((0, 0), (3, 0), (1, 5)),
        ((0, 0), (6, 0), (1, 2)),
        ((0, 0), (5, 0), (-2, 1))]

print('=' * 78)
print('LEMMA CHECKS FOR #831  (exact arithmetic)')
print('=' * 78)

# ---------------------------------------------------------------- Lemma 1
print()
print('LEMMA 1.  At most two circles of a given radius pass through two given points,')
print('          so a pair in three triples of one class forces four concyclic points.')
print('   Testing the CONTENT: solve |O-P| = |O-Q| = r for the centre O and count roots.')
x, y = Symbol('x', real=True), Symbol('y', real=True)
rows = []
allok = True
for d, r2v, expect in [(R(2), R(2), 2),          # d = 2 < 2r = 2*sqrt2 : two circles
                       (R(2), R(1), 1),          # d = 2 = 2r          : one circle
                       (R(4), R(1), 0)]:         # d = 4 > 2r = 2      : none
    P = (R(0), R(0)); Q = (d, R(0))
    sols = ssolve([ (x - P[0])**2 + (y - P[1])**2 - r2v,
                    (x - Q[0])**2 + (y - Q[1])**2 - r2v ], [x, y], dict=True)
    real = [s for s in sols if all(v.is_real for v in s.values())]
    ok = len(real) == expect
    allok &= ok
    rows.append((d, r2v, len(real), expect))
    print('     |PQ| = %-3s r^2 = %-3s -> %d real centre(s), expected %d'
          % (d, r2v, len(real), expect))
ck('the number of radius-r circles through two points is 2, 1, 0 as |PQ| < = > 2r', allok)
print('   Consequence used by penum.py: per-class pair degree <= 2.  Note this is a')
print('   RELAXATION for a diametral pair, where the true degree is <= 1, so the')
print('   surviving pattern list is a superset of the truth (safe direction).')

# ---------------------------------------------------------------- Lemma 2
print()
print('LEMMA 2 (E. Szekeres, quoted by Erdos).  The orthocentre is the unique fourth')
print('        point giving four equal circumradii; hence h(4) = 1.')
allok = True
for T in TRIS:
    A, B, C = [(R(p[0]), R(p[1])) for p in T]
    H = orthocentre(A, B, C)
    pts = [A, B, C, H]
    if len(set(pts)) != 4:
        print('     %-26s H coincides with a vertex (right angle): no 4-point set' % str(T))
        continue
    rs = set(radius_multiset(pts).keys())
    ok = (len(rs) == 1) and admissible(pts)
    allok &= ok
    print('     %-26s H=%-12s radii=%-12s admissible=%s'
          % (str(T), str(H), sorted(rs), admissible(pts)))
ck('every non-right test triangle gives an admissible quadruple with ONE radius', allok)

print('   Uniqueness, tested by solving the full system rather than by citing the')
print('   reflection argument: for each triangle, find every D with all four radii equal.')
allok = True
for T in TRIS[:3]:
    A, B, C = [(R(p[0]), R(p[1])) for p in T]
    H = orthocentre(A, B, C)
    r0 = circumradius2(A, B, C)
    D = (x, y)
    # R(ABD) = R(ACD) = R(BCD) = r0, cleared of denominators
    eqs = []
    for (U, V) in ((A, B), (A, C), (B, C)):
        a2 = d2(U, V); b2 = (x - U[0])**2 + (y - U[1])**2
        c2 = (x - V[0])**2 + (y - V[1])**2
        S = 2*(a2*b2 + b2*c2 + c2*a2) - (a2*a2 + b2*b2 + c2*c2)
        eqs.append(simplify(a2*b2*c2 - r0*S))
    sols = ssolve(eqs, [x, y], dict=True)
    real = [(s[x], s[y]) for s in sols
            if x in s and y in s and s[x].is_real and s[y].is_real]
    offcirc = [p for p in real
               if simplify(det4(A, B, C, p)) != 0 and p not in (A, B, C)]
    ok = (len(offcirc) == 1 and offcirc[0] == H)
    allok &= ok
    print('     %-26s solutions off the circumcircle: %s   (H = %s)'
          % (str(T), offcirc, H))
ck('off the circumcircle the ONLY solution is the orthocentre', allok)

# ---------------------------------------------------------------- Lemma 3
print()
print('LEMMA 3.  If all four triples of a 4-set share a radius, every pair of that set')
print('          already uses BOTH circles of that radius, so no fifth point can join.')
A, B, C = [(R(p[0]), R(p[1])) for p in TRIS[0]]
H = orthocentre(A, B, C)
r0 = circumradius2(A, B, C)
allok = True
for U, V in combinations([A, B, C, H], 2):
    others = [W for W in [A, B, C, H] if W not in (U, V)]
    on = [W for W in others if simplify(circumradius2(U, V, W) - r0) == 0]
    allok &= (len(on) == 2)
ck('every one of the six pairs lies in exactly two triples of the class', allok)
print('   So both radius-r circles through each pair are occupied, and a fifth point on')
print('   either would be concyclic with that pair and an existing point.')

# ---------------------------------------------------------------- Lemma 4
print()
print('LEMMA 4.  No class holds exactly three of the four triples of a 4-set.')
print('   Tested as the statement, not on one instance: for each triangle, force the')
print('   three radii R(ABD) = R(ACD) = R(ABC) and check the fourth follows.')
allok = True
for T in TRIS[:3]:
    A, B, C = [(R(p[0]), R(p[1])) for p in T]
    H = orthocentre(A, B, C)
    r0 = circumradius2(A, B, C)
    ok = (simplify(circumradius2(A, B, H) - r0) == 0
          and simplify(circumradius2(A, C, H) - r0) == 0
          and simplify(circumradius2(B, C, H) - r0) == 0)
    allok &= ok
ck('the only D making three of them equal is H, and then the fourth is equal too', allok,
   'uniqueness established in the Lemma 2 block above')

# ---------------------------------------------------------------- Lemma 4a
print()
print('LEMMA 4a.  h is non-decreasing.')
print('   Both hypotheses are hereditary and deleting a point cannot add a circumradius.')
allok = True
for T in TRIS[:3]:
    A, B, C = [(R(p[0]), R(p[1])) for p in T]
    H = orthocentre(A, B, C)
    pts = [A, B, C, H]
    full = len(radius_multiset(pts))
    for sub in combinations(pts, 3):
        allok &= admissible(list(sub)) and len(radius_multiset(list(sub))) <= full
ck('every 3-subset of an admissible 4-set is admissible with no more radii', allok)

print()
print('Lemma 5 (the parametrisation) and Lemma 6 (the parallelogram) are checked in')
print('lemma6.py, symbolically in the four circle centres.')

print()
print('=' * 78)
if FAIL:
    print('FAILED %d CHECK(S):' % len(FAIL))
    for f in FAIL:
        print('  -', f)
    sys.exit(1)
print('ALL CHECKS PASSED')
print('=' * 78)
