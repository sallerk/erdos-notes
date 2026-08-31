"""The best near-misses found: convex 2m-gons in which HALF the vertices already
meet the counterexample budget.

In the staggered two-ring family T(m, r) every vertex automatically sees exactly
m distinct distances; a counterexample needs every vertex at <= m-1.  Choosing r
to be a root of one of the outer-ring coincidence quadratics

    r^2 - 2*cos(pi(2b+1)/m)*r + (2*cos(2*pi*a/m) - 1) = 0

drives the m OUTER vertices down to m-1 -- exactly the counterexample budget --
while the m inner vertices stay at m.  So half of the polygon is already a
counterexample and the other half misses by one, for EVERY m.

This produces those polygons at 60 decimal digits, plus the exact Q(sqrt3)
version for m=3, and writes them as artifacts for verify_artifacts.py.
"""
import sys, json, math
from mpmath import mp, mpf, cos, sin, pi, sqrt
import artifact

mp.dps = 60


def counts(P, tol=None):
    if tol is None:
        tol = mpf(10) ** (-40)
    n = len(P)
    out = []
    gaps = []
    for i in range(n):
        vals = []
        for j in range(n):
            if i == j:
                continue
            d = (P[i][0]-P[j][0])**2 + (P[i][1]-P[j][1])**2
            if not any(abs(d - v) < tol for v in vals):
                vals.append(d)
        out.append(len(vals))
        sv = sorted(vals)
        if len(sv) > 1:
            gaps.append(min(sv[t+1]-sv[t] for t in range(len(sv)-1)))
    return out, (min(gaps) if gaps else None)


def build(m, r):
    P = []
    for j in range(m):
        P.append((cos(2*pi*j/m), sin(2*pi*j/m)))
        P.append((r*cos(pi*(2*j+1)/m), r*sin(pi*(2*j+1)/m)))
    return P


def best_r(m):
    """radius roots of the outer-ring coincidence quadratics inside the convex
    window, returned with the (a,b) that produced them"""
    lo, hi = cos(pi/m), 1/cos(pi/m)
    out = []
    for a in range(1, m//2 + 1):
        al = cos(2*pi*a/m)
        for b in range(0, m):
            be = cos(pi*(2*b+1)/m)
            disc = be*be - (2*al - 1)
            if disc < 0:
                continue
            s = sqrt(disc)
            for r in (be + s, be - s):
                if lo < r < hi:
                    out.append((r, a, b))
    return out


def main(mlo, mhi):
    recs = []
    for m in range(mlo, mhi + 1):
        n = 2*m
        best = None
        for r, a, b in best_r(m):
            P = build(m, r)
            c, gap = counts(P)
            nlow = sum(1 for x in c if x <= n//2 - 1)
            key = (-nlow, max(c))
            if best is None or key < best[0]:
                best = (key, r, a, b, c, gap, P)
        if best is None:
            print(f"m={m}: no candidate radius inside the convex window")
            continue
        _, r, a, b, c, gap, P = best
        nlow = sum(1 for x in c if x <= n//2 - 1)
        print(f"m={m:3d} n={n:3d}: r={mp.nstr(r,20)}  per-vertex counts "
              f"min={min(c)} max={max(c)}  budget={n//2-1}  "
              f"vertices already AT budget: {nlow}/{n}   min gap between distinct "
              f"squared distances = {mp.nstr(gap,6)}", flush=True)
        coords = [[mp.nstr(x, 50), mp.nstr(y, 50)] for x, y in P]
        artifact.write(f'nearmiss_tworing_m{m}', coords, coords_kind='mp',
                       claim='near_miss',
                       producer=f'python nearmiss.py {mlo} {mhi}',
                       notes=f'staggered two-ring T({m}, r) with '
                             f'r={mp.nstr(r,30)} (a root of the outer-ring '
                             f'coincidence quadratic a={a}, b={b}); {nlow} of the '
                             f'{n} vertices see only {min(c)} = floor(n/2)-1 '
                             f'distinct distances, i.e. they already meet the '
                             f'counterexample budget; the other {n-nlow} see '
                             f'{max(c)} = floor(n/2).  HIGH-PRECISION object '
                             f'(60 dps), not exact.',
                       convex=True, per_vertex=c,
                       extra={'precision_dps': 60,
                              'radius_ratio': mp.nstr(r, 40),
                              'vertices_at_budget': nlow,
                              'min_gap_distinct_sq_distances': mp.nstr(gap, 20)})
        recs.append({'m': m, 'n': n, 'r': mp.nstr(r, 40), 'a': a, 'b': b,
                     'per_vertex': c, 'vertices_at_budget': nlow,
                     'budget': n//2 - 1,
                     'min_gap': mp.nstr(gap, 20)})

    # exact Q(sqrt3) version of the m=3 case: r = sqrt(3) - 1
    exact3 = [['1', '0'],
              ['(sqrt(3)-1)/2', '(sqrt(3)-1)*sqrt(3)/2'],
              ['-1/2', 'sqrt(3)/2'],
              ['-(sqrt(3)-1)', '0'],
              ['-1/2', '-sqrt(3)/2'],
              ['(sqrt(3)-1)/2', '-(sqrt(3)-1)*sqrt(3)/2']]
    artifact.write('nearmiss_hexagon_exact', exact3, coords_kind='sympy',
                   claim='near_miss', producer=f'python nearmiss.py {mlo} {mhi}',
                   notes='EXACT (coordinates in Q(sqrt3)) convex hexagon: two '
                         'concentric equilateral triangles staggered by 60 deg, '
                         'radii 1 and sqrt(3)-1.  Three of the six vertices see '
                         'only 2 = floor(6/2)-1 distinct distances -- the '
                         'counterexample budget -- and the other three see 3.  '
                         'By the n=6 certification no hexagon can do better than '
                         'this, so it is extremal.',
                   convex=True)
    json.dump({'status': 'COMPLETED', 'records': recs},
              open(f'nearmiss_{mlo}_{mhi}.json', 'w'), indent=1)
    print(f"\n-> nearmiss_{mlo}_{mhi}.json and artifacts/nearmiss_*.json")


if __name__ == '__main__':
    main(int(sys.argv[1]) if len(sys.argv) > 1 else 3,
         int(sys.argv[2]) if len(sys.argv) > 2 else 20)
