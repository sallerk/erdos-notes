"""Exact primitives for Erdos #831.  All arithmetic is sympy Rational / algebraic.

Circumradius of a triangle with squared side lengths.  For a triangle with vertices
P,Q,R write a2=|QR|^2, b2=|RP|^2, c2=|PQ|^2 and let
    S = 4*K^2 = 2*(a2*b2 + b2*c2 + c2*a2) - (a2^2 + b2^2 + c2^2)      (Heron, squared)
so K = area = sqrt(S)/4 wait: 16K^2 = 2(a2b2+b2c2+c2a2) - (a2^2+b2^2+c2^2).
Then R^2 = (a2*b2*c2) / (16*K^2).   We work with R2 = R^2 as an exact rational when
the coordinates are rational, so two triples share a circumradius iff their R2 agree.
Degenerate (collinear) triples have 16K^2 = 0 and no circumcircle.
"""
from sympy import Rational, simplify, sqrt, Matrix, nsimplify
from itertools import combinations


def d2(P, Q):
    """exact squared distance"""
    return (P[0] - Q[0])**2 + (P[1] - Q[1])**2


def sixteen_K2(P, Q, R):
    """16 * (area)^2, exact.  Zero iff the three points are collinear."""
    a2, b2, c2 = d2(Q, R), d2(R, P), d2(P, Q)
    return 2*(a2*b2 + b2*c2 + c2*a2) - (a2**2 + b2**2 + c2**2)


def cross2(P, Q, R):
    """twice the signed area; zero iff collinear.  Cheaper collinearity test."""
    return (Q[0]-P[0])*(R[1]-P[1]) - (Q[1]-P[1])*(R[0]-P[0])


def circumradius2(P, Q, R):
    """R^2 of the circumcircle, exact.  Raises if the triple is collinear."""
    a2, b2, c2 = d2(Q, R), d2(R, P), d2(P, Q)
    S = sixteen_K2(P, Q, R)
    if S == 0:
        raise ValueError('collinear triple has no circumcircle')
    return simplify(Rational(1, 1) * a2 * b2 * c2 / S)


def det4(P, Q, R, S):
    """4x4 concyclicity determinant.  Zero iff the four points are concyclic OR
    collinear, so it must be used together with a collinearity test."""
    def row(X):
        return [X[0]**2 + X[1]**2, X[0], X[1], 1]
    return Matrix([row(P), row(Q), row(R), row(S)]).det()


def no_three_collinear(pts):
    return all(cross2(*t) != 0 for t in combinations(pts, 3))


def no_four_concyclic(pts):
    """assumes no three collinear has already been checked"""
    return all(det4(*q) != 0 for q in combinations(pts, 4))


def admissible(pts):
    """the site's hypothesis: no three on a line, no four on a circle"""
    if len(set(map(tuple, pts))) != len(pts):
        return False
    return no_three_collinear(pts) and no_four_concyclic(pts)


def radius_multiset(pts):
    """exact R^2 for every triple, as a dict value -> list of triples"""
    out = {}
    for t in combinations(range(len(pts)), 3):
        r2 = circumradius2(pts[t[0]], pts[t[1]], pts[t[2]])
        out.setdefault(r2, []).append(t)
    return out


def h_of(pts):
    """number of DISTINCT circumradii; only meaningful for admissible pts"""
    return len(radius_multiset(pts))


def orthocentre(A, B, C):
    """exact orthocentre of a triangle with exact coordinates"""
    # H = A + B + C - 2*O where O is the circumcentre; derive O exactly.
    ax, ay = A; bx, by = B; cx, cy = C
    d = 2*(ax*(by-cy) + bx*(cy-ay) + cx*(ay-by))
    if d == 0:
        raise ValueError('collinear')
    a2 = ax**2 + ay**2; b2 = bx**2 + by**2; c2 = cx**2 + cy**2
    ox = (a2*(by-cy) + b2*(cy-ay) + c2*(ay-by)) / d
    oy = (a2*(cx-bx) + b2*(ax-cx) + c2*(bx-ax)) / d
    return (simplify(ax + bx + cx - 2*ox), simplify(ay + by + cy - 2*oy))
