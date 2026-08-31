#!/usr/bin/env python
"""
search_alt.py -- COMPLETE search of the "alternating 2m-gon" family for Erdos #97.

THEORY (derived in RESULTS.md, reproduced here so the code is self-explaining).

Let the configuration have dihedral symmetry D_m (m>=2) with EVERY vertex lying on
a mirror line.  A line through the symmetry centre meets a convex curve twice, so
each of the m mirror lines carries at most 2 vertices, giving n <= 2m, and n = 2m
forces the vertex set to be

        v_j = rho_j * exp(i*pi*j/m),  j = 0..2m-1,   rho_j = 1 (j even), b (j odd)

i.e. 2m points at equally spaced angles pi/m with alternating radii 1 and b.
Convex position <=> cos(pi/m) < b < 1/cos(pi/m).

Because a mirror through vertex v fixes v, the multiset of distances from v is
invariant under that mirror, so every distance from v occurs an even number of
times EXCEPT the distance to the one other vertex on v's own mirror line.
Hence a distance can be attained 4 times only by two distinct "pair classes"
coinciding.  From the vertex at radius 1 the pair classes are

    to radius-1 vertices : d^2 = 2 - 2cos(2 pi k/m),  k=1..floor((m-1)/2)
    to radius-b vertices : d^2 = 1 + b^2 - 2 b cos(j pi/m),  j odd, 1<=j<m

and two classes of the same kind never coincide, so a radius-1 vertex has 4
equidistant vertices  <=>   b^2 - 2 cos(j pi/m) b + (2 cos(2 pi k/m) - 1) = 0.
Swapping the roles of the two radii (i.e. b -> 1/b) gives the condition at a
radius-b vertex:  (1 - 2 cos(2 pi k'/m)) b^2 + 2 cos(j' pi/m) b - 1 = 0.

So a counterexample in this family exists iff for some m the two quadratics have
a common root inside the convexity window.  Both are quadratics over the real
cyclotomic field Q(2cos(pi/m)); a common root exists iff their resultant vanishes
there, which is decided EXACTLY by integer polynomial arithmetic modulo the
minimal polynomial of u = 2cos(pi/m).

k=3 version is also handled (--k 3): there a multiplicity 3 needs one pair class
to coincide with the singleton class (the antipodal vertex on the same mirror).

Usage:
  python search_alt.py --mmax 200 --k 4
  python search_alt.py --mmax 60 --k 3
  python search_alt.py --mmax 40 --k 4 --exact-all      (exact resultant on EVERY combo)
"""
import argparse, json, sys, time
from fractions import Fraction
import sympy as sp
import mpmath as mp

mp.mp.dps = 60


# ---------------------------------------------------------------- exact layer
def minpoly_2cos(m):
    """minimal polynomial of u = 2 cos(pi/m), as a list of int coeffs, low->high."""
    u = sp.Symbol('u')
    p = sp.Poly(sp.minimal_polynomial(2 * sp.cos(sp.pi / m), u), u)
    return [int(c) for c in p.all_coeffs()[::-1]]


def polmulmod(a, b, mod):
    """multiply int-coefficient polys (low->high) modulo monic int poly `mod`."""
    r = [0] * (len(a) + len(b) - 1)
    for i, x in enumerate(a):
        if x:
            for j, y in enumerate(b):
                if y:
                    r[i + j] += x * y
    d = len(mod) - 1
    while len(r) > d:
        c = r.pop()
        if c:
            k = len(r) - d
            for i in range(d):
                r[k + i] -= c * mod[i]
    while len(r) > 1 and r[-1] == 0:
        r.pop()
    return r


def poladd(a, b, s=1):
    n = max(len(a), len(b))
    r = [0] * n
    for i, x in enumerate(a):
        r[i] += x
    for i, y in enumerate(b):
        r[i] += s * y
    while len(r) > 1 and r[-1] == 0:
        r.pop()
    return r


def chebC(m, mod):
    """C[j] = 2 cos(j pi/m) as an int poly in u = 2cos(pi/m), reduced mod `mod`.
    Recurrence C_0=2, C_1=u, C_{j+1} = u*C_j - C_{j-1}."""
    C = [[2], [0, 1]]
    for j in range(2, 2 * m + 1):
        C.append(poladd(polmulmod([0, 1], C[j - 1], mod), C[j - 2], -1))
    return C


def is_zero(p):
    return all(c == 0 for c in p)


def resultant_quadratics(p2, p1, p0, q2, q1, q0, mod):
    """Res of p2 x^2+p1 x+p0 and q2 x^2+q1 x+q0 (all int polys in u)."""
    M = lambda a, b: polmulmod(a, b, mod)
    X = poladd(M(p2, q0), M(p0, q2), -1)
    Y = poladd(M(p2, q1), M(p1, q2), -1)
    Z = poladd(M(p1, q0), M(p0, q1), -1)
    return poladd(M(X, X), M(Y, Z), -1)


# -------------------------------------------------------------- numeric layer
def roots_in_window(a, b_, c, lo, hi):
    """real roots of a x^2 + b_ x + c inside (lo,hi), high precision.

    NUMERICALLY STABLE.  The naive quadratic formula catastrophically cancels
    when |a| is tiny (which happens here exactly when 1-2cos(2 pi k/m)=0, i.e.
    6 | m), and an earlier version of this function reported 214 spurious roots
    at b=1 for m divisible by 6 because of it."""
    out = []
    scale = max(abs(b_), abs(c), mp.mpf(1))
    if abs(a) < mp.mpf('1e-40') * scale:          # genuinely linear
        if abs(b_) > mp.mpf('1e-40') * scale:
            r = -c / b_
            if lo < r < hi:
                out.append(r)
        return out
    disc = b_ * b_ - 4 * a * c
    if disc < 0:
        return out
    s = mp.sqrt(disc)
    q = -(b_ + (s if b_ >= 0 else -s)) / 2        # the well-conditioned root
    rs = [q / a]
    if q != 0:
        rs.append(c / q)
    for r in rs:
        if lo < r < hi:
            out.append(r)
    return out


def search_m(m, k, exact_all=False):
    """returns (hits, min_separation, n_condA, n_condB)"""
    c1 = mp.cos(mp.pi / m)
    lo, hi = c1, 1 / c1
    C = lambda j: 2 * mp.cos(j * mp.pi / m)

    # A-vertex (radius 1) pair classes
    kk = [k_ for k_ in range(1, m) if 2 * k_ < m]                     # A-A pairs
    jj = [j for j in range(1, m, 2)]                                  # A-B pairs (j odd, j<m)
    condA = []
    if k == 4:
        for k_ in kk:
            for j in jj:
                # b^2 - C(j) b + (C(2k)-1) = 0
                condA.append((k_, j, mp.mpf(1), -C(j), C(2 * k_) - 1))
    else:  # k == 3 : one pair class must equal the singleton (antipodal) distance
        if m % 2 == 0:
            sing = mp.mpf(4)                       # antipode is a radius-1 vertex, d=2
            for j in jj:
                condA.append((0, j, mp.mpf(1), -C(j), 1 - sing))       # 1+b^2-C(j)b = 4
            for k_ in kk:
                condA.append((k_, 0, mp.mpf(0), mp.mpf(0), 2 - C(2 * k_) - sing))
        else:
            for j in jj:                            # antipode is radius-b: d^2=(1+b)^2
                condA.append((0, j, mp.mpf(0), -C(j) - 2, mp.mpf(0)))  # 1+b^2-C(j)b=(1+b)^2
            for k_ in kk:
                condA.append((k_, 0, mp.mpf(-1), mp.mpf(-2), 2 - C(2 * k_) - 1))

    # B-vertex (radius b): swap roles, i.e. b -> 1/b
    condB = []
    if k == 4:
        for k_ in kk:
            for j in jj:
                # (1 - C(2k')) b^2 + C(j') b - 1 = 0
                condB.append((k_, j, 1 - C(2 * k_), C(j), mp.mpf(-1)))
    else:
        if m % 2 == 0:                              # antipode of a b-vertex is a b-vertex
            for j in jj:
                condB.append((0, j, mp.mpf(1) - 4, -C(j), mp.mpf(1)))  # b^2+1-C(j)b = 4b^2
            for k_ in kk:
                condB.append((k_, 0, 2 - C(2 * k_) - 4, mp.mpf(0), mp.mpf(0)))
        else:
            for j in jj:                            # antipode is radius-1: d = 1+b
                condB.append((0, j, mp.mpf(0), -C(j) - 2, mp.mpf(0)))
            for k_ in kk:
                condB.append((k_, 0, 2 - C(2 * k_) - 1, mp.mpf(-2), mp.mpf(-1)))

    RA = []
    for (k_, j, a, b_, c) in condA:
        for r in roots_in_window(a, b_, c, lo, hi):
            RA.append((r, k_, j))
    RB = []
    for (k_, j, a, b_, c) in condB:
        for r in roots_in_window(a, b_, c, lo, hi):
            RB.append((r, k_, j))

    hits, sep = [], mp.mpf('1e99')
    for (ra, ka, ja) in RA:
        for (rb, kb, jb) in RB:
            d = abs(ra - rb)
            if d < sep:
                sep = d
            if d < mp.mpf('1e-40'):
                hits.append({"m": m, "b_approx": mp.nstr(ra, 40),
                             "A": [ka, ja], "B": [kb, jb], "gap": mp.nstr(d, 5)})
    return hits, sep, len(RA), len(RB), condA, condB


def exact_confirm(m, A, B, k):
    """EXACT test: do the two quadratics really share a root?  (resultant in
    Z[u]/(minpoly of 2cos(pi/m)))"""
    mod = minpoly_2cos(m)
    C = chebC(m, mod)
    ka, ja = A
    kb, jb = B
    if k == 4:
        p2, p1, p0 = [1], [-c for c in C[ja]], poladd(C[2 * ka], [1], -1)
        q2, q1, q0 = poladd([1], C[2 * kb], -1), C[jb], [-1]
    else:
        raise SystemExit("exact_confirm implemented for k=4")
    R = resultant_quadratics(p2, p1, p0, q2, q1, q0, mod)
    return is_zero(R), R


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--mmax', type=int, default=200)
    ap.add_argument('--mmin', type=int, default=2)
    ap.add_argument('--k', type=int, default=4)
    ap.add_argument('--exact-all', type=int, default=0,
                    help='run the exact resultant on EVERY combination for m<=this')
    ap.add_argument('--out', default=None)
    args = ap.parse_args()
    t0 = time.time()
    allhits, rows = [], []
    for m in range(args.mmin, args.mmax + 1):
        hits, sep, na, nb, condA, condB = search_m(m, args.k)
        exact_note = ""
        if args.k == 4 and m <= args.exact_all:
            mod = minpoly_2cos(m)
            C = chebC(m, mod)
            kk = [k_ for k_ in range(1, m) if 2 * k_ < m]
            jj = [j for j in range(1, m, 2)]
            nz = 0
            for ka in kk:
                p0 = poladd(C[2 * ka], [1], -1)
                for ja in jj:
                    p1 = [-c for c in C[ja]]
                    for kb in kk:
                        q2 = poladd([1], C[2 * kb], -1)
                        for jb in jj:
                            R = resultant_quadratics([1], p1, p0, q2, C[jb], [-1], mod)
                            if is_zero(R):
                                nz += 1
                                allhits.append({"m": m, "A": [ka, ja], "B": [kb, jb],
                                                "exact_resultant_zero": True})
            exact_note = " EXACT: %d/%d combos with vanishing resultant" % (
                nz, len(kk) ** 2 * len(jj) ** 2)
        rows.append({"m": m, "n": 2 * m, "roots_A_in_window": na, "roots_B_in_window": nb,
                     "min_separation": mp.nstr(sep, 8), "numeric_hits": len(hits)})
        allhits += hits
        print("m=%3d n=%3d  |A-roots|=%3d |B-roots|=%3d  min gap=%s%s"
              % (m, 2 * m, na, nb, mp.nstr(sep, 6), exact_note))
    wall = time.time() - t0
    gaps = [float(r["min_separation"]) for r in rows if r["roots_A_in_window"] and r["roots_B_in_window"]]
    out = {"problem": "erdos97", "family": "alternating 2m-gon, D_m symmetry, all vertices on mirrors",
           "k_version": args.k, "mmin": args.mmin, "mmax": args.mmax,
           "exact_all_upto_m": args.exact_all,
           "arithmetic": "60-dps mpmath screen; exact Z[u]/minpoly(2cos(pi/m)) resultant where stated",
           "status": "COMPLETED", "wall_sec": wall, "cmd": " ".join(sys.argv),
           "global_min_separation": min(gaps) if gaps else None,
           "hits": allhits, "per_m": rows}
    fn = args.out or ("alt2m_k%d_m%d.json" % (args.k, args.mmax))
    json.dump(out, open(fn, "w"), indent=1)
    print("\nwall %.1fs   hits=%d   global min separation=%s   -> %s"
          % (wall, len(allhits), out["global_min_separation"], fn))


if __name__ == '__main__':
    main()
