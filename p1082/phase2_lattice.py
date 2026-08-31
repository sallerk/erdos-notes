"""PHASE 2, part 1: exhaustive lattice search for a counterexample.

A counterexample to the first question of #1082 with k distinct distances needs
n >= 2k+2 points, no three collinear.  For each k we ask the pool:

    is there a subset of size 2k+2 with <= k distinct distances
    and no three collinear?

and separately (no collinearity constraint) what the largest k-distance subset
of the pool is, i.e. a lattice lower bound for g(k).

Motivation for using lattices: Erdos and Fishburn conjectured that for k >= 7
EVERY maximum planar k-distance set is similar to a subset of the triangular
lattice.  So this is exactly the pool their conjecture points at.

Completeness: the pool is a ball of squared radius D about the origin with the
origin forced into the set, which covers every lattice set of squared diameter
<= D up to translation.
"""
import sys, time
import numpy as np
from search import build_pool, prepare, run
from geo import distance_set, collinear_triples

BASIS = sys.argv[1] if len(sys.argv) > 1 else 'A2'
DLIST = [int(x) for x in sys.argv[2].split(',')] if len(sys.argv) > 2 else [30]
KLIST = [int(x) for x in sys.argv[3].split(',')] if len(sys.argv) > 3 else [5, 6, 7, 8]

for D in DLIST:
    pts = build_pool(D, BASIS)
    print(f"\n### pool {BASIS}, squared diameter <= {D}: {len(pts)} points",
          flush=True)
    tabG = prepare(pts, D, BASIS, with_collinear=False)
    print(f"    {tabG['V']} distinct distance values ({tabG['DW']} mask words)",
          flush=True)
    t0 = time.time()
    tabH = prepare(pts, D, BASIS, with_collinear=True)
    print(f"    collinearity table built in {time.time()-t0:.1f}s", flush=True)

    for k in KLIST:
        t0 = time.time()
        gb, gs, _, _ = run(tabG, k)
        t1 = time.time()
        # decisive question: any (2k+2)-point, k-distance, no-3-collinear set?
        hb, hs, _, _ = run(tabH, k, target=2 * k + 2, with_collinear=True,
                           stop_at_target=True)
        t2 = time.time()
        S = [pts[i] for i in hs]
        assert len(collinear_triples(S)) == 0
        assert len(distance_set(S, BASIS)) <= k
        verdict = "COUNTEREXAMPLE!!!" if hb >= 2 * k + 2 else "none"
        print(f"  k={k}: g_pool={gb:3d} (need {2*k+2} for any hope)   "
              f"h_pool={hb:3d} [target {2*k+2}] -> {verdict}   "
              f"[{t1-t0:.1f}s / {t2-t1:.1f}s]", flush=True)
        if hb >= 2 * k + 2:
            print("   !!! ", S)
