"""Exact integer geometry primitives for Erdos problem 1082 (first question).

ALL arithmetic here is exact integer arithmetic.  No floats anywhere.

Points are integer pairs (x, y) interpreted in one of two ways:

  basis 'Z2'  : the point is (x, y) in the square lattice.
                squared distance = dx^2 + dy^2
  basis 'A2'  : the point is x*(1,0) + y*(1/2, sqrt(3)/2) in the triangular
                lattice.  squared distance (in units where the lattice minimum
                is 1) = dx^2 + dx*dy + dy^2   (the Eisenstein norm form).

Both bases use an INVERTIBLE linear map from Z^2 to the plane, therefore
three points are collinear in the plane iff the 3x3 integer determinant of
their homogeneous integer coordinates vanishes.  Collinearity testing is
therefore basis-independent and purely integral.
"""

from itertools import combinations


# --------------------------------------------------------------------------
# squared distances
# --------------------------------------------------------------------------

def d2_Z2(p, q):
    dx = p[0] - q[0]
    dy = p[1] - q[1]
    return dx * dx + dy * dy


def d2_A2(p, q):
    dx = p[0] - q[0]
    dy = p[1] - q[1]
    return dx * dx + dx * dy + dy * dy


D2 = {'Z2': d2_Z2, 'A2': d2_A2}


# --------------------------------------------------------------------------
# collinearity  (exact 3x3 integer determinant)
# --------------------------------------------------------------------------

def cross(a, b, c):
    """Twice the signed area of triangle abc, as an exact integer.

    Zero iff a, b, c are collinear.  Valid for both bases: the map
    Z^2 -> R^2 is linear and invertible, so it scales this determinant by a
    fixed nonzero constant (1 for Z2, sqrt(3)/2 for A2) and never changes
    whether it is zero.
    """
    return (b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0])


def collinear_triples(pts):
    """Return the list of index triples (i,j,k) that are collinear."""
    out = []
    n = len(pts)
    for i, j, k in combinations(range(n), 3):
        if cross(pts[i], pts[j], pts[k]) == 0:
            out.append((i, j, k))
    return out


def has_collinear_triple(pts):
    n = len(pts)
    for i in range(n):
        for j in range(i + 1, n):
            for k in range(j + 1, n):
                if cross(pts[i], pts[j], pts[k]) == 0:
                    return True
    return False


# --------------------------------------------------------------------------
# distance sets
# --------------------------------------------------------------------------

def distance_set(pts, basis='Z2'):
    f = D2[basis]
    return frozenset(f(pts[i], pts[j])
                     for i in range(len(pts)) for j in range(i + 1, len(pts)))


def num_distances(pts, basis='Z2'):
    return len(distance_set(pts, basis))


def per_point_distance_counts(pts, basis='Z2'):
    """For each point, how many distinct distances it sees.  (Second question.)"""
    f = D2[basis]
    return [len({f(p, q) for q in pts if q != p}) for p in pts]


# --------------------------------------------------------------------------
# full certificate check for the FIRST question of #1082
# --------------------------------------------------------------------------

def check_counterexample(pts, basis='Z2', verbose=True):
    """Is `pts` a counterexample to: n points, no 3 collinear => >= floor(n/2)
    distinct distances?

    Returns (is_counterexample, report dict).
    """
    n = len(pts)
    assert len(set(map(tuple, pts))) == n, "duplicate points"
    tri = collinear_triples(pts)
    ds = distance_set(pts, basis)
    k = len(ds)
    need = n // 2
    ok = (len(tri) == 0) and (k < need)
    rep = dict(n=n, k=k, need=need, collinear=len(tri),
               distances=sorted(ds), basis=basis)
    if verbose:
        print(f"n={n}  distinct distances={k}  floor(n/2)={need}  "
              f"collinear triples={len(tri)}  ==> counterexample: {ok}")
    return ok, rep


# --------------------------------------------------------------------------
# exact arithmetic in Z[sqrt(3)] -- needed for the Harborth 8-point set
# --------------------------------------------------------------------------

class Q3:
    """Exact element a + b*sqrt(3) with a, b rational (stored as Fractions)."""
    __slots__ = ('a', 'b')

    def __init__(self, a, b=0):
        from fractions import Fraction
        self.a = Fraction(a)
        self.b = Fraction(b)

    def __add__(self, o):
        o = _q3(o)
        return Q3(self.a + o.a, self.b + o.b)

    def __sub__(self, o):
        o = _q3(o)
        return Q3(self.a - o.a, self.b - o.b)

    def __mul__(self, o):
        o = _q3(o)
        return Q3(self.a * o.a + 3 * self.b * o.b, self.a * o.b + self.b * o.a)

    __radd__ = __add__
    __rmul__ = __mul__

    def __rsub__(self, o):
        return _q3(o) - self

    def __neg__(self):
        return Q3(-self.a, -self.b)

    def __eq__(self, o):
        o = _q3(o)
        return self.a == o.a and self.b == o.b

    def __hash__(self):
        return hash((self.a, self.b))

    def is_zero(self):
        return self.a == 0 and self.b == 0

    def __repr__(self):
        return f"({self.a}+{self.b}*sqrt3)"


def _q3(o):
    return o if isinstance(o, Q3) else Q3(o)


def d2_q3(p, q):
    dx = p[0] - q[0]
    dy = p[1] - q[1]
    return dx * dx + dy * dy


def cross_q3(a, b, c):
    return (b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0])


def analyse_q3(pts, name=""):
    """Exact analysis of a point set with coordinates in Q(sqrt 3)."""
    n = len(pts)
    ds = set()
    for i in range(n):
        for j in range(i + 1, n):
            ds.add(d2_q3(pts[i], pts[j]))
    coll = 0
    for i, j, k in combinations(range(n), 3):
        if cross_q3(pts[i], pts[j], pts[k]).is_zero():
            coll += 1
    per = []
    for i in range(n):
        per.append(len({d2_q3(pts[i], pts[j]) for j in range(n) if j != i}))
    print(f"{name}: n={n} total distinct distances={len(ds)} "
          f"floor(n/2)={n//2} collinear triples={coll} "
          f"max per-point distances={max(per)} per-point={per}")
    return dict(n=n, k=len(ds), collinear=coll, per_point=per)
