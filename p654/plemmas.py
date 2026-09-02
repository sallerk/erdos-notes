"""Solver-free rejection lemmas for pinned patterns, for Erdos #654.

Each lemma is a purely combinatorial test on the colouring that a realisable pattern must
pass.  They are cheap, so they run before any algebra.  What matters here, and differs
from p98/lemmas.py, is WHICH HYPOTHESIS each one needs, because #654's own statement
assumes only "no four on a circle" and permits collinear points.

    cls(p, q) = the colour of edge {p, q}

L3  BISECTOR.  At most two points are equidistant from a given PAIR.
    Points equidistant from q and r lie on the perpendicular bisector of qr, which is a
    line; three points on a line violate no-three-collinear.
    *** REQUIRES N3.  Valid in mode 'g' ONLY. ***

L4  CIRCUMCENTRE.  At most one point is equidistant from a given TRIPLE.
    If q, r, s are not collinear they have a unique circumcentre, so at most one point can
    be equidistant from all three.  If q, r, s ARE collinear then the perpendicular
    bisectors of qr and rs are distinct parallel lines, so NO point is equidistant from
    all three, and the count is zero.  Either way the count is at most one.
    *** VALID IN BOTH MODES. ***  This extension to the collinear case is what makes it
    usable for the #654 page's own hypothesis, and it is the lemma that settles the one
    n=5, m=2 pattern the Groebner decider could not triangulate.

L5  EQUILATERAL CENTRE.  If three points are pairwise in colour X they form an equilateral
    triangle of squared side D_X; a fourth point joined to all three in colour Y is that
    triangle's circumcentre, so D_Y = D_X / 3.  Hence one colour X cannot have two
    disjoint such triangles whose centres lie in the set via DIFFERENT colours Y and Z,
    for that would force D_Y = D_X/3 = D_Z with Y != Z.
    Three mutually equidistant points are never collinear, so this needs no hypothesis.
    *** VALID IN BOTH MODES. ***

Note L4 subsumes p98's L2 (no K(2,3) inside one colour class): two points joined to the
same three points all in colour c are two distinct points equidistant from a triple.

The per-vertex colour count and the at-most-3-per-colour-per-vertex cap are NOT lemmas
here; penum.py enforces them while enumerating.
"""
import itertools


def _cls_fn(pat, n):
    P = list(itertools.combinations(range(n), 2))
    idx = {p: i for i, p in enumerate(P)}

    def cls(a, b):
        return pat[idx[(a, b) if a < b else (b, a)]]
    return cls


def l3_bisector(pat, n):
    """at most 2 points equidistant from any pair -- MODE 'g' ONLY"""
    cls = _cls_fn(pat, n)
    for q, r in itertools.combinations(range(n), 2):
        apex = sum(1 for p in range(n)
                   if p != q and p != r and cls(p, q) == cls(p, r))
        if apex > 2:
            return False
    return True


def l4_circumcentre(pat, n):
    """at most 1 point equidistant from any triple -- valid in BOTH modes"""
    cls = _cls_fn(pat, n)
    for q, r, s in itertools.combinations(range(n), 3):
        c = sum(1 for p in range(n)
                if p not in (q, r, s) and cls(p, q) == cls(p, r) == cls(p, s))
        if c > 1:
            return False
    return True


def l5_equilateral(pat, n):
    """one colour cannot hold two triangles centred in the set via different colours"""
    cls = _cls_fn(pat, n)
    centre = {}                      # colour X -> set of centre-colours Y seen
    for a, b, c in itertools.combinations(range(n), 3):
        x = cls(a, b)
        if cls(a, c) != x or cls(b, c) != x:
            continue
        for v in range(n):
            if v in (a, b, c):
                continue
            y = cls(v, a)
            if cls(v, b) == y and cls(v, c) == y:
                centre.setdefault(x, set()).add(y)
    for x, ys in centre.items():
        if len(ys) > 1:
            return False             # D_y = D_x/3 for two different colours y
    return True


def survives(pat, n, mode):
    """True if no lemma valid under `mode` rejects the pattern"""
    if mode == 'g' and not l3_bisector(pat, n):
        return False, 'L3 bisector'
    if not l4_circumcentre(pat, n):
        return False, 'L4 circumcentre'
    if not l5_equilateral(pat, n):
        return False, 'L5 equilateral centre'
    return True, 'survives'
