"""Exact circle counting for Erdos #506.

m(n) = the minimum number of DISTINCT CIRCLES determined by n points in the
plane, not all concyclic and not all collinear.

Convention (settled in the problem's forum thread): a COLLINEAR triple determines
a line, not a circle, and contributes nothing to the count.

Representation.  A circle or line is the zero set of
        A (x^2 + y^2) + B x + C y + D = 0.
A = 0 gives a line, A != 0 a genuine circle.  Three points determine (A,B,C,D) up
to scale as the null vector of the 3x4 matrix whose rows are
        [ x^2+y^2 , x , y , 1 ].
Two triples lie on the same circle exactly when their null vectors are
proportional, so normalising the 4-vector gives an exact key.

Everything is done in exact rational arithmetic (fractions.Fraction), so the
counts are exact -- no tolerance, no floating point anywhere.
"""
from fractions import Fraction as F
from itertools import combinations
from math import gcd


def _det3(m):
    return (m[0][0] * (m[1][1] * m[2][2] - m[1][2] * m[2][1])
            - m[0][1] * (m[1][0] * m[2][2] - m[1][2] * m[2][0])
            + m[0][2] * (m[1][0] * m[2][1] - m[1][1] * m[2][0]))


def circle_key(p, q, r):
    """Exact normalised (A,B,C,D) for the circle/line through three points.
    Returns (is_circle, key).  key is a canonical integer 4-tuple."""
    rows = []
    for (x, y) in (p, q, r):
        x = F(x); y = F(y)
        rows.append([x * x + y * y, x, y, F(1)])
    # null vector via 3x3 cofactors of the 3x4 matrix (Cramer / cross product)
    cof = []
    for j in range(4):
        sub = [[rows[i][k] for k in range(4) if k != j] for i in range(3)]
        c = _det3(sub)
        cof.append(c if j % 2 == 0 else -c)
    A, B, C, D = cof
    if A == 0 and B == 0 and C == 0 and D == 0:
        raise ValueError('degenerate: repeated points?')
    # canonicalise: clear denominators, divide by gcd, fix sign
    dens = [v.denominator for v in (A, B, C, D)]
    L = 1
    for d in dens:
        L = L * d // gcd(L, d)
    ints = [int(v * L) for v in (A, B, C, D)]
    g = 0
    for v in ints:
        g = gcd(g, abs(v))
    if g:
        ints = [v // g for v in ints]
    for v in ints:
        if v != 0:
            if v < 0:
                ints = [-w for w in ints]
            break
    return (ints[0] != 0, tuple(ints))


def count_circles(pts, want_detail=False):
    """Exact number of distinct circles determined by the point set."""
    circles = {}
    lines = {}
    for (i, j, k) in combinations(range(len(pts)), 3):
        is_c, key = circle_key(pts[i], pts[j], pts[k])
        tgt = circles if is_c else lines
        tgt.setdefault(key, set()).update((i, j, k))
    if want_detail:
        return len(circles), {'circles': {k: sorted(v) for k, v in circles.items()},
                              'lines': {k: sorted(v) for k, v in lines.items()}}
    return len(circles)


def valid(pts):
    """the problem forbids all-concyclic and all-collinear"""
    n = len(pts)
    if n < 4:
        return False
    nc, det = count_circles(pts, True)
    for v in det['lines'].values():
        if len(v) == n:
            return False           # all collinear
    for v in det['circles'].values():
        if len(v) == n:
            return False           # all concyclic
    return True


if __name__ == '__main__':
    # sanity checks with known answers, all exact
    # 1. n-1 points on a line plus one off it -> C(n-1,2) circles
    for n in range(4, 9):
        pts = [(i, 0) for i in range(n - 1)] + [(0, 1)]
        c = count_circles(pts)
        exp = (n - 1) * (n - 2) // 2
        print('line(%d)+1 : circles=%d  expected C(%d,2)=%d  %s'
              % (n - 1, c, n - 1, exp, 'OK' if c == exp else 'MISMATCH'))
    # 2. square plus centre: the 4 corners are concyclic (1 circle); centre with
    #    any 2 adjacent corners gives more
    sq = [(0, 0), (1, 0), (1, 1), (0, 1)]
    print('unit square (all concyclic, so invalid):', count_circles(sq),
          'valid =', valid(sq))
    print('square + centre:', count_circles(sq + [(F(1, 2), F(1, 2))]),
          'valid =', valid(sq + [(F(1, 2), F(1, 2))]))
    # 3. Purdy-Smith formula value, for reference only (proved for n > 393)
    for n in range(4, 13):
        print('  n=%2d  Purdy-Smith C(n-1,2)+1-floor((n-1)/2) = %d'
              % (n, (n - 1) * (n - 2) // 2 + 1 - (n - 1) // 2))
