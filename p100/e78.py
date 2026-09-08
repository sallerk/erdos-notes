"""delta(7) and delta(8) from the classifications of 7-point and 8-point 4-distance sets.

Lan and Wei (Mat. Zametki 93 (2013) 492-508, Theorem 8): there are exactly 42 seven-point
4-distance sets, namely (their numbering) 701-703 and 708 = the four R_9 - 2, 704 =
R_7^+ - 1, 705 and 709-716 = nine 7-subsets of the three-triangle 9-set, 706 and
721-739 = twenty lattice sets, 707 = R_8 - 1, 717-718 = two subsets of the
square-with-four-apexes 8-set, 719-720 = two "R_5 plus two points" inside the
double R_5, and 740, 741, 742 with distance ratios 1 : sqrt2 : 2 : sqrt5,
1 : sqrt(2+sqrt3) : sqrt(4+2sqrt3) : sqrt(5+2sqrt3), 1 : sqrt2 : sqrt(2+sqrt3) : sqrt(4+sqrt3).

Shinohara (Discrete Math. 308 (2008) 3048-3055, Theorem 1.2(a)): every 8-point 4-distance
set is R_8, R_7^+, the square with four apexes, or an 8-subset of a 9-point 4-distance
set (R_9, the two lattice sets, the three-triangle set).

delta(7) <= 4.664 < 5 and delta(8) <= 4.664 < 5, and the 7-point 3-distance sets are R_7
(delta 5.049) and R_6^+ (7.464), so delta(7) and delta(8) are minima over these lists.
Everything below is built explicitly at 50 digits from the descriptions (the lattice
members from lat.py's own exhaustive enumeration, which found the same 20 and 8
classes), every family's class count is compared with the paper's, and the three sets
given only by their distance ratios are searched for as one-point extensions of
6-point subsets of the explicit sets; where found, they are used as point sets.
"""
import sys
import json
from itertools import combinations, product

import mpmath as mp
import sympy as sp

sys.stdout.reconfigure(encoding='utf-8', errors='replace')
mp.mp.dps = 50
TOL = mp.mpf('1e-35')
from ext2 import dist, values_of, circle_circle, bisector, circle_line, line_line, delta_of


def R(n, r=1, phase=0):
    return [(r * mp.cos(2 * mp.pi * i / n + phase), r * mp.sin(2 * mp.pi * i / n + phase)) for i in range(n)]


def lattice(pts):
    s3 = mp.sqrt(3)
    return [(mp.mpf(a) + mp.mpf(b) / 2, mp.mpf(b) * s3 / 2) for a, b in pts]


def piepmeyer():
    from piepmeyer import route_B
    return [(mp.mpf(str(sp.N(x, 60))), mp.mpf(str(sp.N(y, 60)))) for x, y in route_B()]


def square_apexes():
    """square of side 1 with an equilateral triangle erected outward on each side"""
    h = mp.sqrt(3) / 2
    sq = [(0, 0), (1, 0), (1, 1), (0, 1)]
    ap = [(mp.mpf('0.5'), -h), (1 + h, mp.mpf('0.5')), (mp.mpf('0.5'), 1 + h), (-h, mp.mpf('0.5'))]
    return [(mp.mpf(x), mp.mpf(y)) for x, y in sq] + ap


def pentagram():
    """R_5 with the five intersection points of its diagonals"""
    tau = (1 + mp.sqrt(5)) / 2
    return R(5) + R(5, 1 / tau ** 2, mp.pi / 5)


def grid740():
    pts = [(0, 0), (1, 0), (2, 0), (0, 1), (1, 1), (2, 1), (1, 2)]
    return [(mp.mpf(x), mp.mpf(y)) for x, y in pts]


def key(pts):
    ds = sorted(dist(P, Q) for P, Q in combinations(pts, 2))
    return tuple(mp.nstr(d / ds[0], 25) for d in ds)


def subsets_with_k(pts, m, k):
    """m-subsets with exactly k distinct distances, one representative per distance multiset"""
    out = {}
    for S in combinations(pts, m):
        S = list(S)
        if len(values_of(S, TOL)) == k:
            out.setdefault(key(S), S)
    return out


def extend_one_new(pts, K):
    """all one-point extensions with at most K distances in total (complete: ext3 argument)"""
    vals = values_of(pts, TOL)
    n = len(pts)
    circles = [(pts[i], v) for i in range(n) for v in vals]
    lines = [bisector(pts[i], pts[j]) for i, j in combinations(range(n), 2)]
    cands = []
    for (A, rA), (B, rB) in combinations(circles, 2):
        if A is not B:
            cands += circle_circle(A, rA, B, rB, TOL)
    for (C, r), L in product(circles, lines):
        cands += circle_line(C, r, L, TOL)
    for L1, L2 in combinations(lines, 2):
        cands += line_line(L1, L2, TOL)
    out = {}
    for P in cands:
        if any(dist(P, Q) < TOL for Q in pts):
            continue
        S = pts + [P]
        if len(values_of(S, TOL)) <= K:
            out.setdefault(key(S), S)
    return out


def ratios(pts):
    v = values_of(pts, TOL)
    return [mp.nstr(x / v[0], 12) for x in v]


def report(fam, classes, expect):
    print('  %-34s %2d classes (paper: %s)  delta: %s' % (fam, len(classes), expect,
          sorted(set(mp.nstr(delta_of(values_of(S, TOL)), 10) for S in classes.values()))), flush=True)


if __name__ == '__main__':
    P9 = piepmeyer()
    lat7 = json.load(open('results/lat_n7_k4.json'))
    lat8 = json.load(open('results/lat_n8_k4.json'))
    SA = square_apexes()
    PG = pentagram()
    assert len(values_of(SA, TOL)) == 4 and len(values_of(PG, TOL)) == 5

    print('E_7(4): the 42 sets of Lan-Wei, by family')
    fam7 = {}
    fam7['R9 minus 2'] = subsets_with_k(R(9), 7, 4)
    fam7['R7+ minus 1'] = subsets_with_k(R(7) + [(mp.mpf(0), mp.mpf(0))], 7, 4)
    fam7['R8 minus 1'] = subsets_with_k(R(8), 7, 4)
    fam7['three-triangle (Piepmeyer) 7-subsets'] = subsets_with_k(P9, 7, 4)
    # lattice classes keyed by lat.py's exact canonical form, not by the distance multiset:
    # two of the twenty are homometric (same multiset, different shape)
    fam7['lattice (lat.py)'] = {'lat7_%d' % i: lattice(r['points']) for i, r in enumerate(lat7['sets'])}
    fam7['square+apexes 7-subsets'] = subsets_with_k(SA, 7, 4)
    pg = subsets_with_k(PG, 7, 4)
    fam7['pentagram 7-subsets'] = pg
    g = grid740()
    fam7['740 (grid)'] = {key(g): g} if len(values_of(g, TOL)) == 4 else {}
    # 741, 742: search one-point extensions of 6-subsets of the explicit sets
    want = {'741': [1, mp.sqrt(2 + mp.sqrt(3)), mp.sqrt(4 + 2 * mp.sqrt(3)), mp.sqrt(5 + 2 * mp.sqrt(3))],
            '742': [1, mp.sqrt(2), mp.sqrt(2 + mp.sqrt(3)), mp.sqrt(4 + mp.sqrt(3))]}
    found = {}
    bases = []
    for base in (P9, SA, PG, R(9), R(8), R(7) + [(mp.mpf(0), mp.mpf(0))], g):
        for S in combinations(base, 6):
            S = list(S)
            if len(values_of(S, TOL)) <= 4:
                bases.append(S)
    seen = {}
    for S in bases:
        for kk, T in extend_one_new(S, 4).items():
            if len(values_of(T, TOL)) == 4:
                seen.setdefault(kk, T)
    for nm, w in want.items():
        w = sorted(w)
        for kk, T in seen.items():
            v = values_of(T, TOL)
            if all(abs(v[i] / v[0] - w[i] / w[0]) < mp.mpf('1e-30') for i in range(4)):
                found[nm] = T
                break
    for nm in ('741', '742'):
        if nm in found:
            fam7[nm + ' (found as extension)'] = {key(found[nm]): found[nm]}
        else:
            fam7[nm + ' (ratios only, from the paper)'] = {}
    expect7 = {'R9 minus 2': 4, 'R7+ minus 1': 1, 'R8 minus 1': 1, 'three-triangle (Piepmeyer) 7-subsets': 9,
               'lattice (lat.py)': 20, 'square+apexes 7-subsets': 2, 'pentagram 7-subsets': 2, '740 (grid)': 1}
    allkeys = {}
    for fam, cl in fam7.items():
        report(fam, cl, expect7.get(fam, 1))
        for kk, S in cl.items():
            allkeys.setdefault(kk, (fam, S))
    print('  7-subsets of the pentagram containing R5: %d' % sum(
        1 for S in pg.values() if all(any(dist(p, q) < TOL for q in S) for p in R(5))))
    # the ratio-only sets contribute their delta from the ratios
    d7 = {}
    for kk, (fam, S) in allkeys.items():
        d7[kk] = (fam, delta_of(values_of(S, TOL)))
    for nm, w in want.items():
        if nm not in found:
            d7['ratios ' + nm] = (nm + ' ratios', delta_of(sorted(w)))
    print('  distinct 7-point 4-distance classes assembled: %d explicit + %d ratio-only = %d (paper: 42)'
          % (len(allkeys), sum(1 for nm in want if nm not in found), len(allkeys) + sum(1 for nm in want if nm not in found)))
    homo = len(allkeys) - len({key(S) for fam, S in allkeys.values()})
    print('  homometric pairs among them (same distance multiset, different shape): %d' % homo)
    best7 = min(d7.items(), key=lambda t: t[1][1])
    print('  delta(7) = min over E_7(4) = %s  from %s' % (mp.nstr(best7[1][1], 20), best7[1][0]))
    print('  all values:', sorted(set(mp.nstr(v[1], 8) for v in d7.values())))

    print()
    print('E_8(4): Shinohara 2008 Theorem 1.2(a)')
    fam8 = {'R8': {key(R(8)): R(8)},
            'R7+': {key(R(7) + [(mp.mpf(0), mp.mpf(0))]): R(7) + [(mp.mpf(0), mp.mpf(0))]},
            'square+apexes': {key(SA): SA},
            'R9 minus 1': subsets_with_k(R(9), 8, 4),
            'lattice 8-subsets (lat.py)': {'lat8_%d' % i: lattice(r['points']) for i, r in enumerate(lat8['sets'])},
            'three-triangle (Piepmeyer) 8-subsets': subsets_with_k(P9, 8, 4)}
    expect8 = {'R8': 1, 'R7+': 1, 'square+apexes': 1, 'R9 minus 1': 1, 'lattice 8-subsets (lat.py)': 8,
               'three-triangle (Piepmeyer) 8-subsets': 3}
    all8 = {}
    for fam, cl in fam8.items():
        report(fam, cl, expect8[fam])
        for kk, S in cl.items():
            all8.setdefault(kk, (fam, S))
    print('  distinct 8-point 4-distance classes assembled: %d' % len(all8))
    best8 = min(all8.items(), key=lambda t: delta_of(values_of(t[1][1], TOL)))
    d8 = delta_of(values_of(best8[1][1], TOL))
    print('  delta(8) = min over E_8(4) = %s  from %s' % (mp.nstr(d8, 20), best8[1][0]))

    json.dump(dict(
        E7=[dict(family=fam, k=4, ratios=ratios(S), delta=mp.nstr(delta_of(values_of(S, TOL)), 25),
                 points=[[mp.nstr(x, 40), mp.nstr(y, 40)] for x, y in S]) for kk, (fam, S) in allkeys.items()],
        E7_ratio_only=[dict(name=nm, ratios=[mp.nstr(x, 25) for x in sorted(w)],
                            delta=mp.nstr(delta_of(sorted(w)), 25)) for nm, w in want.items() if nm not in found],
        E7_classes=len(allkeys), E7_expected=42,
        delta7=mp.nstr(best7[1][1], 25), delta7_from=best7[1][0],
        E8=[dict(family=fam, k=4, ratios=ratios(S), delta=mp.nstr(delta_of(values_of(S, TOL)), 25),
                 points=[[mp.nstr(x, 40), mp.nstr(y, 40)] for x, y in S]) for kk, (fam, S) in all8.items()],
        E8_classes=len(all8), delta8=mp.nstr(d8, 25), delta8_from=best8[1][0], completed=True),
        open('results/e78_k4.json', 'w'), indent=1)
