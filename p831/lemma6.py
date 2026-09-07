"""LEMMA 6, verified symbolically.

Suppose four triples of a 5-point set share a circumradius r and all four contain the
same point.  Label so that the class is {012, 013, 024, 034}; then all four circles
pass through P0.  Put P0 at the origin and r = 1.  Each circle has its centre on the
unit circle about the origin, say o1, o2, o3, o4, and two unit circles through the
origin with centres o_i, o_j meet again at exactly o_i + o_j (the triangle 0-o_i-o_j is
isosceles, so the foot of the perpendicular from 0 to the line o_i o_j is the midpoint,
and reflecting 0 in that line gives the sum).  Reading off which two circles carry each
point:

        P0 = 0,  P1 = o1+o2,  P2 = o1+o3,  P3 = o2+o4,  P4 = o3+o4.

CLAIM.  Triangles P1P2P3 and P2P3P4 are congruent, and so are P1P2P4 and P1P3P4.
Hence R(123) = R(234) and R(124) = R(134) IDENTICALLY on this family: a class of this
shape forces two coincidences among the six remaining triples for free.

Proof (verified below): every side length of one triangle appears as a side of the
other.  |P1P2| = |o2-o3| = |P3P4|, |P1P3| = |o1-o4| = |P2P4|, and |P2P3| is common.
"""
import sys
from sympy import symbols, simplify, expand, Matrix, factor
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

FAIL = []


def ck(label, ok):
    print(('  [PASS] ' if ok else '  [FAIL] ') + label)
    if not ok:
        FAIL.append(label)


# generic centres on a circle of radius R about the origin, as free coordinates with
# the constraint |o_i|^2 = R^2 imposed symbolically where needed
a1, b1, a2, b2, a3, b3, a4, b4 = symbols('a1 b1 a2 b2 a3 b3 a4 b4', real=True)
o = [(a1, b1), (a2, b2), (a3, b3), (a4, b4)]


def add(u, v):
    return (u[0]+v[0], u[1]+v[1])


def sub(u, v):
    return (u[0]-v[0], u[1]-v[1])


def n2(u):
    return expand(u[0]**2 + u[1]**2)


P = {0: (0, 0), 1: add(o[0], o[1]), 2: add(o[0], o[2]),
     3: add(o[1], o[3]), 4: add(o[2], o[3])}

print('=' * 74)
print('LEMMA 6 : the two forced congruences, symbolic in the four centres')
print('=' * 74)
print()
print('Side lengths, squared, as polynomials in the centres:')
pairs = [(1, 2), (1, 3), (2, 3), (1, 4), (2, 4), (3, 4)]
L = {}
for i, j in pairs:
    L[(i, j)] = simplify(n2(sub(P[i], P[j])))
    print('   |P%dP%d|^2 = %s' % (i, j, L[(i, j)]))

print()
print('Triangle 123 has sides {|P1P2|,|P1P3|,|P2P3|}, triangle 234 has {|P2P3|,|P2P4|,|P3P4|}.')
ck('|P1P2|^2 == |P3P4|^2', simplify(L[(1, 2)] - L[(3, 4)]) == 0)
ck('|P1P3|^2 == |P2P4|^2', simplify(L[(1, 3)] - L[(2, 4)]) == 0)
ck('|P2P3|^2 is shared by both triangles', True)

print()
print('Triangle 124 has sides {|P1P2|,|P1P4|,|P2P4|}, triangle 134 has {|P1P3|,|P1P4|,|P3P4|}.')
ck('|P1P2|^2 == |P3P4|^2 again', simplify(L[(1, 2)] - L[(3, 4)]) == 0)
ck('|P2P4|^2 == |P1P3|^2 again', simplify(L[(2, 4)] - L[(1, 3)]) == 0)
ck('|P1P4|^2 is shared by both triangles', True)

print()
print('Note the identities hold for ANY four centres, with no use of |o_i| = R.')
print('The equal-radius hypothesis is what puts the centres on a common circle and so')
print('produces the parametrisation; the congruences then come for free.')

print()
print('Consequence: with a class of this shape the six remaining triples take at most')
print('FOUR distinct circumradii, so such a configuration has at most 1 + 4 = 5')
print('distinct circumradii before any further coincidence is imposed.')

print()
print('=' * 74)
if FAIL:
    print('FAILED %d CHECK(S)' % len(FAIL))
    sys.exit(1)
print('ALL CHECKS PASSED')
print('=' * 74)
