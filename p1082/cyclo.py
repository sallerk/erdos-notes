"""A richer, NON-lattice pool: the ring Z[sqrt3] x Z[sqrt3].

A point is (a + b*sqrt3, c + d*sqrt3) with a,b,c,d integers, stored as the
integer 4-tuple (a,b,c,d).  All arithmetic below is exact integer arithmetic on
elements u + v*sqrt3 of Z[sqrt3]; nothing is ever evaluated as a float.

Why this pool.  Z[sqrt3]^2 simultaneously contains
  * the square lattice Z^2,
  * a scaled copy of the triangular lattice A2  (2i+j, j*sqrt3),
  * every regular triangle / square / hexagon / 12-gon on those lattices,
  * Harborth's 8-point set (+-1,+-1), (0,+-(1+sqrt3)), (+-(1+sqrt3),0)
    -- the configuration that refutes the SECOND question of #1082.
So it is strictly richer than either lattice alone and contains the one known
non-lattice extremal configuration for this problem.

Squared distance between two such points is again an element of Z[sqrt3]:
    (dA)^2 + (dC)^2  where dA, dC in Z[sqrt3],
so distances compare exactly as integer pairs (u, v) <-> u + v*sqrt3.
Collinearity is the vanishing of the Z[sqrt3] cross product, i.e. BOTH integer
components vanish.
"""
import numpy as np
from search import _build_coll  # unused; kept for symmetry
from numba import njit


# ------------------------------------------------------------ Z[sqrt3] ops
def mul3(x, y):
    """(x0 + x1 s)(y0 + y1 s), s = sqrt3."""
    return (x[0] * y[0] + 3 * x[1] * y[1], x[0] * y[1] + x[1] * y[0])


def sub3(x, y):
    return (x[0] - y[0], x[1] - y[1])


def add3(x, y):
    return (x[0] + y[0], x[1] + y[1])


def sign3(x):
    """Exact sign of x0 + x1*sqrt3."""
    p, q = x
    if p == 0 and q == 0:
        return 0
    if p >= 0 and q >= 0:
        return 1
    if p <= 0 and q <= 0:
        return -1
    # opposite signs: compare p^2 with 3q^2
    if p > 0:                       # p>0, q<0 : positive iff p^2 > 3q^2
        return 1 if p * p > 3 * q * q else (-1 if p * p < 3 * q * q else 0)
    else:                           # p<0, q>0 : positive iff 3q^2 > p^2
        return 1 if 3 * q * q > p * p else (-1 if 3 * q * q < p * p else 0)


def norm2(P):
    """Squared distance from the origin; P = (a,b,c,d) -> (a+b s, c+d s)."""
    A = (P[0], P[1])
    C = (P[2], P[3])
    return add3(mul3(A, A), mul3(C, C))


def d2(P, Q):
    A = (P[0] - Q[0], P[1] - Q[1])
    C = (P[2] - Q[2], P[3] - Q[3])
    return add3(mul3(A, A), mul3(C, C))


def cross3(P, Q, R):
    """Z[sqrt3] cross product (Q-P) x (R-P); zero iff P,Q,R collinear."""
    ux = (Q[0] - P[0], Q[1] - P[1])
    uy = (Q[2] - P[2], Q[3] - P[3])
    vx = (R[0] - P[0], R[1] - P[1])
    vy = (R[2] - P[2], R[3] - P[3])
    a = mul3(ux, vy)
    b = mul3(uy, vx)
    return sub3(a, b)


# ------------------------------------------------------------ pool builder
def build_pool_z3(B, Dsq):
    """Points with |a|,|b|,|c|,|d| <= B and squared norm <= Dsq (an integer)."""
    pts = []
    for a in range(-B, B + 1):
        for b in range(-B, B + 1):
            for c in range(-B, B + 1):
                for d in range(-B, B + 1):
                    P = (a, b, c, d)
                    nz = norm2(P)
                    if sign3((nz[0] - Dsq, nz[1])) <= 0:
                        pts.append(P)
    # Distinct integer 4-tuples give distinct points, since 1 and sqrt3 are
    # Q-independent.  Sort by exact squared norm (integer comparison), origin
    # first.
    import functools
    key = {P: norm2(P) for P in pts}

    def cmp(P, Q):
        s = sign3(sub3(key[P], key[Q]))
        if s:
            return s
        return -1 if P < Q else (1 if P > Q else 0)

    pts.sort(key=functools.cmp_to_key(cmp))
    assert pts[0] == (0, 0, 0, 0)
    return pts


# ------------------------------------------------------------ table builder
def prepare_z3(pts, Dsq):
    m = len(pts)
    ids = {}
    dmat = np.full((m, m), -1, dtype=np.int32)
    adj = np.zeros((m, m), dtype=np.uint8)
    for i in range(m):
        for j in range(i + 1, m):
            v = d2(pts[i], pts[j])
            if sign3((v[0] - Dsq, v[1])) > 0:
                continue
            t = ids.setdefault(v, len(ids))
            dmat[i, j] = t
            dmat[j, i] = t
            adj[i, j] = 1
            adj[j, i] = 1
    V = len(ids)
    DW = (V + 63) // 64
    MW = (m + 63) // 64
    dmask = np.zeros((m, m, DW), dtype=np.uint64)
    for i in range(m):
        for j in range(m):
            t = dmat[i, j]
            if t >= 0:
                dmask[i, j, t >> 6] |= np.uint64(1) << np.uint64(t & 63)

    P = np.array(pts, dtype=np.int64)
    collmask = np.zeros((m, m, MW), dtype=np.uint64)
    _coll_z3(P, collmask)
    return dict(m=m, V=V, DW=DW, MW=MW, dmask=dmask, adj=adj,
                collmask=collmask, dmat=dmat, ids=ids)


@njit(cache=False)
def _coll_z3(P, collmask):
    """Exact Z[sqrt3] collinearity: both components of the cross product zero."""
    m = P.shape[0]
    for i in range(m):
        for j in range(i + 1, m):
            ux0 = P[j, 0] - P[i, 0]; ux1 = P[j, 1] - P[i, 1]
            uy0 = P[j, 2] - P[i, 2]; uy1 = P[j, 3] - P[i, 3]
            for t in range(m):
                if t == i or t == j:
                    continue
                vx0 = P[t, 0] - P[i, 0]; vx1 = P[t, 1] - P[i, 1]
                vy0 = P[t, 2] - P[i, 2]; vy1 = P[t, 3] - P[i, 3]
                # (ux*vy - uy*vx) in Z[sqrt3]
                r0 = (ux0 * vy0 + 3 * ux1 * vy1) - (uy0 * vx0 + 3 * uy1 * vx1)
                r1 = (ux0 * vy1 + ux1 * vy0) - (uy0 * vx1 + uy1 * vx0)
                if r0 == 0 and r1 == 0:
                    w = t >> 6
                    bit = np.uint64(1) << np.uint64(t & 63)
                    collmask[i, j, w] |= bit
                    collmask[j, i, w] |= bit
