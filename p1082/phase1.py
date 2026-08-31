"""PHASE 1.  g(5) = 12 (Erdos-Fishburn / Shinohara).  Since 12 = 2*5+2, a
12-point 5-distance set with no three collinear WOULD be a counterexample to
the first question of #1082 (5 < floor(12/2) = 6).

Shinohara proved the maximum planar 5-distance set is unique up to similarity.
Our machinery finds a 12-point 5-distance set inside the triangular lattice.
Here we enumerate EVERY 12-point 5-distance subset of the lattice pool and test
each one, exactly, for collinear triples.
"""
import sys
import numpy as np
from search import build_pool, prepare, run
from geo import distance_set, collinear_triples, D2

BASIS, D = 'A2', 30
pts = build_pool(D, BASIS)
tab = prepare(pts, D, BASIS, with_collinear=False)
print(f"pool {BASIS}, squared diameter <= {D}: {tab['m']} points, "
      f"{tab['V']} distance values\n")

# ---------------------------------------------------------------- enumerate
b, bs, found, nf = run(tab, k=5, target=12, count_all=True, max_store=200000)
print(f"12-point 5-distance sets in pool (containing the origin): {nf}")

canon = {}
for row in found:
    S = [pts[i] for i in row[:12]]
    ds = distance_set(S, BASIS)
    assert len(ds) <= 5, ds
    # canonical form under the 12-element point group of A2 + translation
    key = _k = None
    reps = []
    for rot in range(6):
        for refl in (0, 1):
            Q = []
            for (x, y) in S:
                # A2 rotation by 60 deg: (x,y) -> (-y, x+y) in Eisenstein coords
                a, bb = x, y
                for _ in range(rot):
                    a, bb = -bb, a + bb
                if refl:                       # reflection (x,y) -> (y,x)
                    a, bb = bb, a
                Q.append((a, bb))
            mx = min(Q)
            Q = tuple(sorted(((u - mx[0], v - mx[1]) for (u, v) in Q)))
            reps.append(Q)
    key = min(reps)
    canon.setdefault(key, S)

print(f"distinct up to the A2 symmetry group + translation: {len(canon)}\n")

# ---------------------------------------------------------------- test them
any_clean = False
for idx, (key, S) in enumerate(sorted(canon.items())):
    ds = sorted(distance_set(S, BASIS))
    tri = collinear_triples(S)
    clean = (len(tri) == 0)
    any_clean |= clean
    print(f"SET #{idx+1}  (Eisenstein coords, distance = sqrt(dx^2+dx*dy+dy^2))")
    print(f"   points   : {sorted(key)}")
    print(f"   squared distances : {ds}   ({len(ds)} distinct)")
    print(f"   collinear triples : {len(tri)}  -> "
          f"{'NO THREE COLLINEAR *** COUNTEREXAMPLE ***' if clean else 'has 3 on a line'}")
    if tri:
        ex = tri[0]
        print(f"   e.g. {S[ex[0]]}, {S[ex[1]]}, {S[ex[2]]} are collinear")
    print()

print("=" * 72)
print("PHASE 1 VERDICT:",
      "COUNTEREXAMPLE FOUND" if any_clean else
      "every 12-point 5-distance set in the pool contains three collinear points")

# ---------------------------------------------------------------- H_pool(5)
print("\nNow the collinearity-constrained maximum H_pool(5):")
tab2 = prepare(pts, D, BASIS, with_collinear=True)
b2, bs2, _, _ = run(tab2, k=5, with_collinear=True)
S2 = [pts[i] for i in bs2]
print(f"  max no-3-collinear 5-distance subset of the pool: {b2} points")
print(f"  {S2}")
print(f"  distances {sorted(distance_set(S2, BASIS))}, "
      f"collinear triples {len(collinear_triples(S2))}")
print(f"  need >= 12 for a counterexample; 2k+1 = 11 is the conjectured max")
