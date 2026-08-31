"""Exact-integer core for Erdos problem #982.

#982: if n distinct points form a convex polygon, must some VERTEX have at least
floor(n/2) distinct distances to the other vertices?

A counterexample = convex n-gon with max_v (# distinct distances from v) <= floor(n/2)-1.

ALL certification arithmetic here is exact integer arithmetic.  No floats.
Points are integer pairs (x, y) in Z^2; squared distance dx^2 + dy^2.
"""

from itertools import combinations


# ---------------------------------------------------------------- primitives

def cross(a, b, c):
    """Twice the signed area of triangle abc.  Exact integer.  0 iff collinear."""
    return (b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0])


def d2(p, q):
    dx = p[0] - q[0]
    dy = p[1] - q[1]
    return dx * dx + dy * dy


# ---------------------------------------------------------- convex position

def convex_hull(pts):
    """Monotone chain hull, STRICT (collinear boundary points dropped).
    Returns hull vertices in counter-clockwise order."""
    pts = sorted(set(map(tuple, pts)))
    if len(pts) <= 2:
        return list(pts)
    lo = []
    for p in pts:
        while len(lo) >= 2 and cross(lo[-2], lo[-1], p) <= 0:
            lo.pop()
        lo.append(p)
    hi = []
    for p in reversed(pts):
        while len(hi) >= 2 and cross(hi[-2], hi[-1], p) <= 0:
            hi.pop()
        hi.append(p)
    return lo[:-1] + hi[:-1]


def in_strict_convex_position(pts):
    """True iff every point is a vertex of the hull and no 3 are collinear on
    the boundary, i.e. the points form a strictly convex polygon."""
    pts = list(map(tuple, pts))
    if len(set(pts)) != len(pts):
        return False
    return len(convex_hull(pts)) == len(pts)


def ccw_order(pts):
    """Return pts reordered counter-clockwise around the hull (only valid when
    in_strict_convex_position(pts) is True)."""
    return convex_hull(pts)


# --------------------------------------------------- the #982 quantity itself

def per_vertex_counts(pts, dist=d2):
    """counts[i] = number of DISTINCT distances from pts[i] to the other points."""
    n = len(pts)
    return [len({dist(pts[i], pts[j]) for j in range(n) if j != i}) for i in range(n)]


def per_vertex_class_sizes(pts, dist=d2):
    """For each vertex, the sorted multiset of distance-class sizes."""
    n = len(pts)
    out = []
    for i in range(n):
        c = {}
        for j in range(n):
            if j != i:
                v = dist(pts[i], pts[j])
                c[v] = c.get(v, 0) + 1
        out.append(sorted(c.values(), reverse=True))
    return out


def check982(pts, dist=d2, require_convex=True, verbose=True):
    """Full certificate check.  Returns (is_counterexample, report)."""
    pts = [tuple(p) for p in pts]
    n = len(pts)
    rep = {'n': n}
    rep['distinct_points'] = (len(set(pts)) == n)
    conv = in_strict_convex_position(pts) if require_convex else True
    rep['convex'] = conv
    counts = per_vertex_counts(pts, dist)
    rep['per_vertex'] = counts
    rep['max_per_vertex'] = max(counts)
    rep['min_per_vertex'] = min(counts)
    rep['target'] = n // 2
    rep['total_distinct'] = len({dist(pts[i], pts[j])
                                 for i in range(n) for j in range(i + 1, n)})
    ok = rep['distinct_points'] and conv and rep['max_per_vertex'] <= n // 2 - 1
    rep['counterexample'] = ok
    if verbose:
        print(f"n={n} convex={conv} max_per_vertex={rep['max_per_vertex']} "
              f"target=floor(n/2)={n//2} total_distinct={rep['total_distinct']} "
              f"=> counterexample: {ok}")
    return ok, rep


# ---------------------------------------------------- regular n-gon, exactly
# The regular n-gon is not a lattice polygon.  Its distance structure is
# nevertheless an EXACT INTEGER computation: vertices are indexed by Z_n and
#     |v_i v_j| = 2 sin(pi*d/n)   with d = min(|i-j|, n-|i-j|) in {1..floor(n/2)},
# and d -> 2 sin(pi d/n) is strictly increasing on 1..floor(n/2), so two chords
# are equal iff their circular differences d are equal.  Hence the number of
# distinct distances from any vertex is |{ d(i,j) : j != i }| computed in Z_n.

def circdiff(i, j, m):
    d = abs(i - j) % m
    return min(d, m - d)


def regular_ngon_per_vertex(n):
    """Exact (index arithmetic in Z_n, no floats): distinct distances from each
    vertex of the regular n-gon."""
    return [len({circdiff(i, j, n) for j in range(n) if j != i}) for i in range(n)]


def subset_of_regular_mgon_per_vertex(S, m):
    """S a subset of Z_m -> per-vertex distinct-distance counts for those points
    on the regular m-gon.  Exact index arithmetic."""
    S = list(S)
    return [len({circdiff(i, j, m) for j in S if j != i}) for i in S]
