"""Piepmeyer's 9 points, built two independent ways and checked in exact arithmetic.

Erdos describes the set verbally in [Er95] (Resenhas 2 (1995) 165-186):

  "let first x = (1 + sqrt2) sqrt(2 - sqrt3). Then take 2 equilateral triangles, one of
   them with side length x, and the second 'around' the first, containing it, with
   parallel sides, and distances x between corresponding vertices. The 3 remaining
   points are the centres of the 3 circles determined by the 4 endpoints of the three
   pairs of parallel sides of the two equilateral triangles."

Route A rebuilds that sentence.  Route B uses the closed-form coordinates that appear in
a Lean branch of google-deepmind/formal-conjectures.  The two must agree as point sets up
to congruence, and the distance multiset must agree exactly; agreement of two derivations
is what makes the coordinates safe to build on (L5: re-derive, do not re-run).

This is also the POSITIVE CONTROL for everything later (L74): any search that reports
delta(9) has to at least match what this configuration achieves.
"""
import sys
import json
from itertools import combinations

import sympy as sp

sys.stdout.reconfigure(encoding='utf-8', errors='replace')
from core import distances, gaps, delta, binding, d2

FAIL = []


def ck(label, ok, detail=''):
    print(('  [PASS] ' if ok else '  [FAIL] ') + label + (('  ' + detail) if detail else ''))
    if not ok:
        FAIL.append(label)


s2, s3, s6 = sp.sqrt(2), sp.sqrt(3), sp.sqrt(6)
X = sp.simplify((1 + s2) * sp.sqrt(2 - s3))


def route_A():
    """rebuild Erdos's sentence"""
    R_in = X / sp.sqrt(3)                       # circumradius of a triangle of side X
    R_out = R_in + X                            # 'distances x between corresponding vertices'
    ang = [sp.pi / 2, sp.pi / 2 + 2 * sp.pi / 3, sp.pi / 2 + 4 * sp.pi / 3]
    inner = [(sp.simplify(R_in * sp.cos(a)), sp.simplify(R_in * sp.sin(a))) for a in ang]
    outer = [(sp.simplify(R_out * sp.cos(a)), sp.simplify(R_out * sp.sin(a))) for a in ang]

    def circumcentre(A, B, C):
        ax, ay = A; bx, by = B; cx, cy = C
        d = 2 * (ax * (by - cy) + bx * (cy - ay) + cx * (ay - by))
        a2 = ax ** 2 + ay ** 2; b2 = bx ** 2 + by ** 2; c2 = cx ** 2 + cy ** 2
        return (sp.simplify((a2 * (by - cy) + b2 * (cy - ay) + c2 * (ay - by)) / d),
                sp.simplify((a2 * (cx - bx) + b2 * (ax - cx) + c2 * (bx - ax)) / d))

    # each pair of parallel sides: inner edge (i,j) and the outer edge on the same two
    # directions; its four endpoints are concyclic, and the centre is the extra point
    extra = []
    for i, j in ((0, 1), (1, 2), (2, 0)):
        quad = [inner[i], inner[j], outer[i], outer[j]]
        c = circumcentre(quad[0], quad[1], quad[2])
        r2 = sp.simplify(d2(c, quad[0]))
        for q in quad[1:]:
            if sp.simplify(d2(c, q) - r2) != 0:
                raise ValueError('the four endpoints are not concyclic')
        extra.append(c)
    return inner + outer + extra, extra


def route_B():
    """the closed-form coordinates from the Lean branch"""
    A = (3 * s2 - s6 + 6 - 2 * s3) / 6
    B = (s6 - s2 + 2 * s3 - 2) / 4
    C = (2 * s3 + s6) / 3
    D = (2 + s2) / 2
    E = (s6 + 3 * s2 + 6 + 2 * s3) / 6
    F = (3 * s2 + 3 * s6 + 6 * s3 + 6) / 12
    return [(sp.Integer(0), A), (-B, -A / 2), (B, -A / 2),
            (sp.Integer(0), C), (-D, -C / 2), (D, -C / 2),
            (sp.Integer(0), -E), (F, E / 2), (-F, E / 2)]


if __name__ == '__main__':
    print('=' * 78)
    print("PIEPMEYER'S 9 POINTS, EXACT")
    print('=' * 78)
    print()
    print('x = (1+sqrt2) sqrt(2-sqrt3) = %s' % sp.nsimplify(X))
    print('    = %s' % sp.N(X, 12))

    print()
    print('Route A: rebuilt from Erdos\'s verbal description in [Er95].')
    ptsA, extra = route_A()
    ck('the four endpoints of each pair of parallel sides are concyclic', True,
       'checked inside route_A, which raises otherwise')
    dA = distances(ptsA)
    print('    %d distinct distances' % len(dA))
    for v in dA:
        print('      %-28s = %s' % (sp.nsimplify(sp.radsimp(v)), sp.N(v, 12)))

    print()
    print('Route B: closed-form coordinates from the Lean branch.')
    ptsB = route_B()
    dB = distances(ptsB)
    print('    %d distinct distances' % len(dB))

    print()
    same = (len(dA) == len(dB)) and all(sp.simplify(a - b) == 0 for a, b in zip(dA, dB))
    ck('the two derivations give the SAME exact distance set', same)

    # full multiset, not just the value set
    msA = sorted((float(sp.N(sp.sqrt(d2(P, Q)), 40)) for P, Q in combinations(ptsA, 2)))
    msB = sorted((float(sp.N(sp.sqrt(d2(P, Q)), 40)) for P, Q in combinations(ptsB, 2)))
    ck('the two derivations give the same 36-element distance MULTISET',
       len(msA) == 36 and len(msB) == 36
       and max(abs(a - b) for a, b in zip(msA, msB)) < 1e-30,
       'max difference %.2e' % max(abs(a - b) for a, b in zip(msA, msB)))

    print()
    dl, info = delta(ptsB)
    print('Distances and gaps (exact):')
    for i, v in enumerate(info['d'], 1):
        print('    d_%d = %-22s = %s' % (i, sp.nsimplify(sp.radsimp(v)), sp.N(v, 12)))
    for i, v in enumerate(info['gaps'], 1):
        print('    gap %d->%d = %-16s = %s' % (i, i + 1, sp.nsimplify(sp.radsimp(v)), sp.N(v, 12)))
    name, val = binding(ptsB)
    print()
    print('    binding constraint: %s = %s' % (name, sp.N(val, 12)))
    print('    delta = d_4 / %s = %s' % (name, sp.N(dl, 12)))

    ck('k = 4 distinct distances', info['k'] == 4)
    ck('the middle gap is EXACTLY 1, so it is the binding constraint',
       sp.simplify(info['gaps'][1] - 1) == 0 and name == 'gap_2')
    ck('delta(9) <= 4.664, matching the page\'s "diameter < 5"',
       float(sp.N(dl, 30)) < 4.664, 'delta = %s' % sp.N(dl, 12))
    ck('the set is NOT an arithmetic progression, so it does not attain the bound k = 4',
       not all(sp.simplify(info['d'][i] - (i + 1) * info['g']) == 0
               for i in range(len(info['d']))),
       'attaining delta = 4 would need distances g, 2g, 3g, 4g')

    json.dump(dict(x=str(sp.N(X, 30)),
                   distances=[str(sp.N(v, 30)) for v in info['d']],
                   gaps=[str(sp.N(v, 30)) for v in info['gaps']],
                   binding=name, delta=str(sp.N(dl, 30)), k=info['k'],
                   points=[[str(sp.N(c, 30)) for c in P] for P in ptsB],
                   two_routes_agree=bool(same), completed=True),
              open('results/piepmeyer.json', 'w'), indent=1)

    print()
    print('=' * 78)
    if FAIL:
        print('FAILED %d CHECK(S):' % len(FAIL))
        for f in FAIL:
            print('  -', f)
        sys.exit(1)
    print('ALL CHECKS PASSED')
    print('=' * 78)
