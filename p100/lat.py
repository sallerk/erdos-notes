"""All n-point k-distance subsets of the triangular lattice, exactly, up to similarity.

Integer arithmetic throughout: a lattice point is (a, b) in the basis (1,0), (1/2, sqrt3/2)
and the squared distance is a^2 + ab + b^2 (a Loeschian number).  The search fixes the
lexicographically least point of the set at the origin (translation), requires every
other point to be lex-greater (so each set is generated exactly once per translation
class), and prunes as soon as the set of squared distances exceeds k.  Rotations and
reflections (the 12-element point group) are removed afterwards by a canonical form,
and sets similar by a lattice similarity are merged on their normalised distance
multiset.

The diameter bound D2 (squared) is a search parameter and is reported: every pair of
points is required to be at squared distance <= D2, so the enumeration is complete for
sets of diameter <= sqrt(D2).  Every set found is exact.

Controls: Erdos-Fishburn give a 9-point 4-distance subset of the lattice; Wei (EJC 2012,
Theorem 11, Figure 2a-2p) shows sixteen 10-point 5-distance lattice sets; Shinohara's
unique 12-point 5-distance set is a lattice set; Wei's Figure 1 is a 13-point 6-distance
lattice set.

Usage: python lat.py <n> <k> [D2]
"""
import sys
import json
import time
from itertools import combinations
from math import gcd

import sympy as sp

sys.stdout.reconfigure(encoding='utf-8', errors='replace')


def q(p):
    a, b = p
    return a * a + a * b + b * b


def sub(p, r):
    return (p[0] - r[0], p[1] - r[1])


# the 12 symmetries of the triangular lattice about the origin, as integer matrices on (a,b)
ROT = [((1, 0), (0, 1)), ((0, -1), (1, 1)), ((-1, -1), (1, 0)),
       ((-1, 0), (0, -1)), ((0, 1), (-1, -1)), ((1, 1), (-1, 0))]
REF = ((0, 1), (1, 0))


def apply(M, p):
    return (M[0][0] * p[0] + M[0][1] * p[1], M[1][0] * p[0] + M[1][1] * p[1])


def mul(M, N):
    return ((M[0][0] * N[0][0] + M[0][1] * N[1][0], M[0][0] * N[0][1] + M[0][1] * N[1][1]),
            (M[1][0] * N[0][0] + M[1][1] * N[1][0], M[1][0] * N[0][1] + M[1][1] * N[1][1]))


SYM = ROT + [mul(R, REF) for R in ROT]
assert q(((3 * 2 + 1) // 7, (2 * 1 - 2) // 7)) * 7 == q((2, 1))
assert q(((2 * 1 - 2) // 7, (1 + 3 * 2) // 7)) * 7 == q((1, 2))
assert q(((4 * 3 + 1) // 13, (3 * 1 - 3) // 13)) * 13 == q((3, 1))
assert q(((4 * 1 + 3 * 3) // 13, (3 - 3 * 1) // 13)) * 13 == q((1, 3))
assert all(q(apply(M, (3, 5))) == q((3, 5)) for M in SYM)


def canon(pts):
    best = None
    for M in SYM:
        im = [apply(M, p) for p in pts]
        m = min(im, key=lambda p: (p[1], p[0]))
        im = tuple(sorted(sub(p, m) for p in im))
        if best is None or im < best:
            best = im
    return best


def search(n, k, D2):
    patch = [(a, b) for a in range(-D2, D2 + 1) for b in range(-D2, D2 + 1)
             if 0 < q((a, b)) <= D2 and (b > 0 or (b == 0 and a > 0))]
    patch.sort(key=lambda p: (p[1], p[0]))
    found = set()
    cnt = [0]

    def rec(chosen, dset, start):
        if len(chosen) == n:
            cnt[0] += 1
            if len(dset) == k:
                found.add(canon(chosen))
            return
        for i in range(start, len(patch)):
            p = patch[i]
            nd = set(dset)
            ok = True
            for r in chosen:
                d = q(sub(p, r))
                if d > D2:                       # true diameter bound, every pair
                    ok = False
                    break
                nd.add(d)
                if len(nd) > k:
                    ok = False
                    break
            if ok:
                rec(chosen + [p], nd, i + 1)
    rec([(0, 0)], set(), 0)
    return found, cnt[0]


def describe(pts):
    ds = sorted({q(sub(p, r)) for p, r in combinations(pts, 2)})
    g = 0
    for d in ds:
        g = gcd(g, d)
    norm = tuple(sp.Rational(d, ds[0]) for d in ds)
    vals = [sp.sqrt(d) for d in ds]
    gaps = [sp.simplify(b - a) for a, b in zip(vals, vals[1:])]
    cand = [vals[0]] + gaps
    gmin = min(cand, key=lambda v: float(sp.N(v, 40)))
    delta = sp.simplify(vals[-1] / gmin)
    return dict(points=list(pts), sqdist=ds, values=[str(v) for v in vals],
                delta=str(delta), delta_num=str(sp.N(delta, 20)), norm=[str(x) for x in norm])


if __name__ == '__main__':
    n = int(sys.argv[1]); k = int(sys.argv[2])
    D2 = int(sys.argv[3]) if len(sys.argv) > 3 else 28
    t0 = time.time()
    found, leaves = search(n, k, D2)
    rows = [describe(p) for p in found]
    # merge sets related by a lattice similarity.  The similarities of the lattice into
    # itself that shrink it are compositions of the point group with the index-2 map
    # (all coordinates even: halve) and the index-3 map (a = b mod 3: (a,b) -> (b+t, t),
    # t = (a-b)/3, which is the inverse of the sqrt3-scaled 30-degree rotation).  A set is
    # reduced to primitive form by applying these while they apply, then canonicalised;
    # two sets are merged only when their primitive canonical forms coincide.  Sets that
    # are merely homometric (same distance multiset, different shape) stay separate, and
    # the count is therefore a count of shapes, comparable with a published figure.
    def primitive(pts):
        pts = list(pts)
        while True:
            if all(a % 2 == 0 and b % 2 == 0 for a, b in pts):
                pts = [(a // 2, b // 2) for a, b in pts]
                continue
            if all((a - b) % 3 == 0 for a, b in pts):
                pts = [(b + (a - b) // 3, (a - b) // 3) for a, b in pts]
                continue
            # the two index-7 sublattices, generated by (2,1),(-1,3) and by (1,2),(3,-1);
            # (a,b) = s(2,1) + t(-1,3) gives s = (3a+b)/7, t = (2b-a)/7, and the mirror
            # image likewise; both are sqrt7-scaled rotated copies of the lattice
            if all((3 * a + b) % 7 == 0 for a, b in pts):
                pts = [((3 * a + b) // 7, (2 * b - a) // 7) for a, b in pts]
                continue
            if all((a + 3 * b) % 7 == 0 for a, b in pts):
                pts = [((2 * a - b) // 7, (a + 3 * b) // 7) for a, b in pts]
                continue
            # scale by a prime p = 2 mod 3 (all coordinates divisible by p), and the two
            # index-13 sublattices generated by (3,1),(-1,4) and by (1,3),(-3,4)
            if all(a % 5 == 0 and b % 5 == 0 for a, b in pts):
                pts = [(a // 5, b // 5) for a, b in pts]
                continue
            if all((4 * a + b) % 13 == 0 for a, b in pts):
                pts = [((4 * a + b) // 13, (3 * b - a) // 13) for a, b in pts]
                continue
            if all((4 * a + 3 * b) % 13 == 0 for a, b in pts):
                pts = [((4 * a + 3 * b) // 13, (b - 3 * a) // 13) for a, b in pts]
                continue
            return canon(pts)
    merged = {}
    for r in rows:
        merged.setdefault(primitive(r['points']), r)
    rows = sorted(merged.values(), key=lambda r: float(sp.N(sp.sympify(r['delta']), 30)))
    print('n=%d k=%d D2<=%d : %d lattice sets up to congruence, %d up to similarity (%.0fs)'
          % (n, k, D2, len(found), len(rows), time.time() - t0))
    for r in rows:
        print('  delta = %-22s %s   %s' % (r['delta_num'][:14], r['values'], r['points']))
    json.dump(dict(n=n, k=k, D2=D2, congruence_classes=len(found), similarity_classes=len(rows),
                   sets=rows, seconds=round(time.time() - t0, 1), completed=True),
              open('results/lat_n%d_k%d.json' % (n, k), 'w'), indent=1)
