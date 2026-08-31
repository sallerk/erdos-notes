"""Artifact + independent verifier for the #506 rationalizability note.

Establishes three things, all in exact arithmetic:
  A. Wang's 8-point RATIONAL set (arXiv:2608.19844 sec. 7.3) determines exactly 17
     circles.  Checked over Fraction.
  B. mzn's 8-point set over Q(sqrt 15) (forum comment, 18 Aug 2026) determines
     exactly 17 circles.  Checked in sympy over Q(sqrt 15).
  C. The two are the SAME configuration: there is a relabelling of the 8 points
     carrying blocks to blocks AND lines to lines, circles to circles.

Consequence: the 17-circle configuration on 8 points admits a rational
realisation, so u^2 = 15 is not forced by the configuration.

A circle or line is the zero set of A(x^2+y^2) + Bx + Cy + D = 0; three points give
(A,B,C,D) up to scale as the null vector of the 3x4 matrix with rows
[x^2+y^2, x, y, 1].  A = 0 <=> the three points are collinear.
"""
from fractions import Fraction as F
from itertools import combinations, permutations
import sympy as sp
import json

# ---------------------------------------------------------------- A. Wang, rational
WANG = [(F(0), F(0)),
        (F(263, 626), F(2178, 4069)),
        (F(263, 313), F(4356, 4069)),
        (F(789, 626), F(6534, 4069)),
        (F(53519, 195938), F(1842342, 1273597)),
        (F(184032, 458545), F(7245468, 5961085)),
        (F(160557, 917090), F(5527026, 5961085)),
        (F(-25, 313), F(312, 313))]

# ---------------------------------------------------------------- B. mzn, Q(sqrt15)
u = sp.sqrt(15)
MZN = [(u, sp.Integer(-1)), (-u, sp.Integer(-1)),
       (u / 3, sp.Integer(-1)), (-u / 3, sp.Integer(-1)),
       (u / 2, sp.Rational(3, 2)), (-u / 2, sp.Rational(3, 2)),
       (u / 4, sp.Rational(1, 4)), (-u / 4, sp.Rational(1, 4))]


def blocks(P, exact_sympy):
    """maximal blocks, split into lines and circles, exactly"""
    n = len(P)
    if exact_sympy:
        zero = lambda e: sp.simplify(e) == 0
        norm = lambda v, piv: sp.nsimplify(sp.simplify(v / piv))
    else:
        zero = lambda e: e == 0
        norm = lambda v, piv: v / piv
    circ, lin = {}, {}
    for t in combinations(range(n), 3):
        rows = []
        for i in t:
            x, y = P[i]
            rows.append([x * x + y * y, x, y, 1])
        cof = []
        for j in range(4):
            m = [[rows[i][k] for k in range(4) if k != j] for i in range(3)]
            d = (m[0][0] * (m[1][1] * m[2][2] - m[1][2] * m[2][1])
                 - m[0][1] * (m[1][0] * m[2][2] - m[1][2] * m[2][0])
                 + m[0][2] * (m[1][0] * m[2][1] - m[1][1] * m[2][0]))
            cof.append(d if j % 2 == 0 else -d)
        piv = None
        for v in cof:
            if not zero(v):
                piv = v
                break
        key = tuple(str(norm(v, piv)) for v in cof)
        (circ if not zero(cof[0]) else lin).setdefault(key, set()).update(t)
    C = sorted(tuple(sorted(v)) for v in circ.values())
    L = sorted(tuple(sorted(v)) for v in lin.values())
    return C, L


print('=== A. Wang (rational) ===')
WC, WL = blocks(WANG, False)
print('  circles: %d   lines: %d' % (len(WC), len(WL)))
print('  circle blocks:', WC)
print('  line blocks  :', WL)

print('=== B. mzn (Q(sqrt 15)) ===')
MC, ML = blocks(MZN, True)
print('  circles: %d   lines: %d' % (len(MC), len(ML)))
print('  circle blocks:', MC)
print('  line blocks  :', ML)

print('=== C. designation-preserving isomorphism ===')
SC, SL = set(WC), set(WL)
TC, TL = set(MC), set(ML)
found = []
for p in permutations(range(8)):
    if (set(tuple(sorted(p[x] for x in b)) for b in SL) == TL and
            set(tuple(sorted(p[x] for x in b)) for b in SC) == TC):
        found.append(p)
print('  number of designation-preserving relabellings: %d' % len(found))
if found:
    p = found[0]
    print('  one of them: Wang index i -> mzn index p[i], p =', p)
    print('  line correspondence:')
    for b in WL:
        print('     Wang %s -> mzn %s' % (str(b), str(tuple(sorted(p[x] for x in b)))))

ok = (len(WC) == 17 and len(MC) == 17 and len(found) > 0)
print()
print('VERDICT:', 'CONFIRMED - same configuration, one rational and one over Q(sqrt15)'
      if ok else 'FAILED')
json.dump({'wang_circles': len(WC), 'wang_lines': [list(b) for b in WL],
           'wang_circle_blocks': [list(b) for b in WC],
           'mzn_circles': len(MC), 'mzn_lines': [list(b) for b in ML],
           'mzn_circle_blocks': [list(b) for b in MC],
           'designation_preserving_relabellings': len(found),
           'example_permutation': list(found[0]) if found else None,
           'wang_points': [[str(a), str(b)] for a, b in WANG],
           'mzn_points': [[str(a), str(b)] for a, b in MZN],
           'verdict': 'same configuration' if ok else 'FAILED',
           'status': 'COMPLETED'},
          open('artifact_iso_n8.json', 'w'), indent=1)
