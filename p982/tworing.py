"""Structured family: the CONVEX analogue of the concentric-regular-polygon
constructions that refute #1082's second question.

Configuration T(m, r), n = 2m points:
    A_j = ( cos(2*pi*j/m),  sin(2*pi*j/m) )                 j = 0..m-1
    B_j = r*( cos(pi*(2j+1)/m), sin(pi*(2j+1)/m) )          j = 0..m-1
i.e. two concentric regular m-gons, the inner/outer one STAGGERED by half a
step.  (The radially ALIGNED version -- which is what eigensolver used for
#1082 -- is never convex: the smaller ring lies inside the hull.)

Convex position  <=>  cos(pi/m) < r < 1/cos(pi/m).

The whole configuration is invariant under the dihedral group D_m, and every
vertex lies on a mirror axis.  Hence:
    from A_0:  A-A distances give floor(m/2) values, A-B distances ceil(m/2)
               values, so the count is  m - |I_A|  where I_A is the set of
               coincidences between the two lists;
    from B_0:  likewise  m - |I_B|.
The counterexample condition  max per-vertex <= floor(2m/2) - 1 = m-1  is
therefore EXACTLY

        |I_A| >= 1   and   |I_B| >= 1.

Each single coincidence is a quadratic in r, so we solve for r and test the
other side.  Screen in float64, refine in mpmath, certify with sympy.
"""

import sys, json, math
import numpy as np


def convex_range(m):
    c = math.cos(math.pi / m)
    return c, 1.0 / c


def per_vertex_counts_ring(m, r, tol=1e-9):
    """Exact-in-structure count of distinct distances from A_0 and from B_0,
    computed in float64 with a relative tolerance.  Screening only."""
    j = np.arange(1, m)
    dAA = 2.0 - 2.0 * np.cos(2 * np.pi * j / m)
    j2 = np.arange(0, m)
    dAB = 1.0 + r * r - 2.0 * r * np.cos(np.pi * (2 * j2 + 1) / m)
    dBB = r * r * (2.0 - 2.0 * np.cos(2 * np.pi * j / m))

    def ndist(arr):
        a = np.sort(arr)
        keep = 1
        for i in range(1, len(a)):
            if a[i] - a[keep - 1] > tol * max(1.0, abs(a[i])):
                a[keep] = a[i]; keep += 1
        return keep, a[:keep]

    nA, _ = ndist(np.concatenate([dAA, dAB]))
    nB, _ = ndist(np.concatenate([dBB, dAB]))
    return nA, nB


def candidate_radii(m):
    """All r solving one A-side coincidence  4 sin^2(pi a/m) = 1+r^2-2 r cos(pi(2b+1)/m),
    within the convex range."""
    lo, hi = convex_range(m)
    out = []
    for a in range(1, m // 2 + 1):
        alpha = math.cos(2 * math.pi * a / m)
        for b in range(0, m):
            beta = math.cos(math.pi * (2 * b + 1) / m)
            # r^2 - 2 beta r + (2 alpha - 1) = 0
            disc = beta * beta - (2 * alpha - 1)
            if disc < 0:
                continue
            s = math.sqrt(disc)
            for r in (beta + s, beta - s):
                if lo + 1e-12 < r < hi - 1e-12:
                    out.append((r, ('A', a, b)))
    # and the B-side quadratics, in case the A-side coincidence is the derived one
    for a in range(1, m // 2 + 1):
        alpha = math.cos(2 * math.pi * a / m)
        for b in range(0, m):
            beta = math.cos(math.pi * (2 * b + 1) / m)
            # r^2(2-2alpha) = 1 + r^2 - 2 beta r  ->  r^2(1-2alpha) + 2 beta r - 1 = 0
            A2 = 1.0 - 2.0 * alpha
            if abs(A2) < 1e-14:
                if abs(beta) > 1e-14:
                    r = 1.0 / (2 * beta)
                    if lo < r < hi:
                        out.append((r, ('B', a, b)))
                continue
            disc = beta * beta + A2
            if disc < 0:
                continue
            s = math.sqrt(disc)
            for r in ((-beta + s) / A2, (-beta - s) / A2):
                if lo + 1e-12 < r < hi - 1e-12:
                    out.append((r, ('B', a, b)))
    return out


def scan(mlo, mhi, tol=1e-9, report=None):
    best = []
    hits = []
    for m in range(mlo, mhi + 1):
        n = 2 * m
        target = n // 2 - 1          # = m-1
        bm = None
        for r, tag in candidate_radii(m):
            nA, nB = per_vertex_counts_ring(m, r, tol)
            mx = max(nA, nB)
            if bm is None or mx < bm[0]:
                bm = (mx, r, tag, nA, nB)
            if mx <= target:
                hits.append(dict(m=m, n=n, r=r, tag=list(tag), nA=nA, nB=nB,
                                 target=target))
                print(f"  *** HIT m={m} n={n} r={r!r} nA={nA} nB={nB} "
                      f"target={target} tag={tag}", flush=True)
        if bm:
            best.append(dict(m=m, n=n, target=target, best_max=bm[0], r=bm[1],
                             tag=list(bm[2]), nA=bm[3], nB=bm[4]))
            if m % 25 == 0:
                print(f"  m={m} n={n}: best max-per-vertex {bm[0]} (need <= {target})",
                      flush=True)
    if report:
        json.dump({'best': best, 'hits': hits}, open(report, 'w'), indent=1)
    return best, hits


if __name__ == '__main__':
    lo = int(sys.argv[1]) if len(sys.argv) > 1 else 3
    hi = int(sys.argv[2]) if len(sys.argv) > 2 else 300
    print(f"two-ring staggered scan, m = {lo}..{hi}  (n = 2m)")
    best, hits = scan(lo, hi, report='tworing_scan.json')
    print()
    print(f"total hits: {len(hits)}")
    # summary of how close we get
    gaps = [(b['best_max'] - b['target'], b['m']) for b in best]
    gaps.sort()
    print("closest (excess over floor(n/2)-1, m):", gaps[:12])
