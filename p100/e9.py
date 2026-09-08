"""delta(9) from the classification of 9-point 4-distance sets, exactly.

Erdos and Fishburn (Discrete Math. 160 (1996) 115-125, Theorem 1): a 9-point set with
exactly four distances is R_9 or one of the three configurations at the top of their
Fig. 1: two subsets of the triangular lattice and "three equilateral triangles with the
same center and a horizontal edge" with the distance rules quoted in REFERENCES.md.
Since delta(9) <= 4.664 < 5, only 4-distance sets can attain delta(9), so delta(9) is
the minimum of delta over these four sets.  This file builds all four exactly, checks
each has exactly four distances, computes delta exactly, and shows that the
three-triangle set is Piepmeyer's set (equal distance multisets up to scale).
"""
import sys
import json
from itertools import combinations

import sympy as sp

sys.stdout.reconfigure(encoding='utf-8', errors='replace')
from piepmeyer import route_B


def distances(pts):
    """distinct distances, grouped at 80 digits and each group checked exactly (sympy's
    simplify does not always recognise two trigonometric forms of the same chord, so the
    grouping is numeric and the exactness check is per pair)"""
    groups = []
    for P, Q in combinations(pts, 2):
        v = sp.sqrt(sp.expand((P[0] - Q[0]) ** 2 + (P[1] - Q[1]) ** 2))
        x = sp.N(v, 80)
        for g in groups:
            if abs(g[1] - x) < sp.Float('1e-70', 80):
                assert sp.simplify(g[0] - v) == 0 or abs(sp.N(g[0] - v, 200)) < sp.Float('1e-190', 200)
                break
        else:
            groups.append((sp.simplify(v), x))
    groups.sort(key=lambda g: g[1])
    for a, b in zip(groups, groups[1:]):
        assert b[1] - a[1] > sp.Float('1e-70', 80)
    return [g[0] for g in groups]


def delta(pts):
    ds = distances(pts)
    gaps = [sp.simplify(b - a) for a, b in zip(ds, ds[1:])]
    cand = [ds[0]] + gaps
    g = min(cand, key=lambda v: float(sp.N(v, 50)))
    return sp.simplify(ds[-1] / g), dict(k=len(ds), d=ds, gaps=gaps, g=g)

s2, s3 = sp.sqrt(2), sp.sqrt(3)


def R(n):
    return [(sp.cos(2 * sp.pi * i / n), sp.sin(2 * sp.pi * i / n)) for i in range(n)]


def lattice(pts):
    return [(sp.Integer(a) + sp.Rational(b, 2), sp.Integer(b) * s3 / 2) for a, b in pts]


def three_triangles():
    """Erdos-Fishburn's description, radii forced by it: big circumradius 1 (apex up),
    intermediate inverted with circumradius sqrt3 - 1, inner inverted with 2 - sqrt3"""
    big = [(0, 1), (-s3 / 2, -sp.Rational(1, 2)), (s3 / 2, -sp.Rational(1, 2))]
    rm, ri = s3 - 1, 2 - s3
    mid = [(rm * s3 / 2, rm / 2), (-rm * s3 / 2, rm / 2), (0, -rm)]
    inn = [(ri * s3 / 2, ri / 2), (-ri * s3 / 2, ri / 2), (0, -ri)]
    return [(sp.sympify(x), sp.sympify(y)) for x, y in big + mid + inn]


def multiset(pts):
    out = []
    for P, Q in combinations(pts, 2):
        out.append(sp.simplify(sp.sqrt(sp.expand((P[0] - Q[0]) ** 2 + (P[1] - Q[1]) ** 2))))
    return sorted(out, key=lambda v: float(sp.N(v, 40)))


E9 = {
    'R9': R(9),
    'lattice (a)': lattice([(1, 0), (2, 0), (3, 0), (0, 1), (1, 1), (2, 1), (0, 2), (1, 2), (2, 2)]),
    'lattice (b)': lattice([(3, 0), (1, 1), (2, 1), (3, 1), (0, 2), (1, 2), (2, 2), (1, 3), (2, 3)]),
    'three triangles (c)': three_triangles(),
}

if __name__ == '__main__':
    out = {}
    for name, pts in E9.items():
        ds = distances(pts)
        d, info = delta(pts)
        out[name] = dict(k=len(ds), values=[str(v) for v in ds],
                         ratios=[str(sp.N(v / ds[0], 20)) for v in ds],
                         delta=str(d), delta_num=str(sp.N(d, 25)))
        print('%-22s k=%d  delta = %-16s  ratios %s' % (name, len(ds), str(sp.N(d, 12)),
              [str(sp.N(v / ds[0], 8)) for v in ds]))
        assert len(ds) == 4, name
    # the three-triangle set is Piepmeyer's: same 36-element multiset up to one scale factor
    mc = multiset(three_triangles())
    mpp = multiset(route_B())
    scale = sp.simplify(mpp[0] / mc[0])
    same = all(sp.simplify(a * scale - b) == 0 for a, b in zip(mc, mpp))
    print('three-triangle set scaled by %s equals Piepmeyer\'s multiset exactly: %s' % (sp.N(scale, 12), same))
    best = min(out, key=lambda n: float(out[n]['delta_num']))
    print('delta(9) = min over the four = %s from %s' % (out[best]['delta_num'][:16], best))
    json.dump(dict(sets=out, three_triangles_is_piepmeyer=bool(same), scale=str(scale),
                   best=best, delta9=out[best]['delta'], delta9_num=out[best]['delta_num'],
                   completed=True), open('results/e9_k4.json', 'w'), indent=1)
