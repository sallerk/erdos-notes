"""PHASE 2, part 2: search the richer non-lattice pool Z[sqrt3] x Z[sqrt3].

Step 0 cross-checks the pool machinery on Harborth's 8-point set, which lives
in this pool, against the independent Q(sqrt3) implementation in geo.py.
Then searches for a counterexample: 2k+2 points, <= k distances, no 3 collinear.

NOTE ON COMPLETENESS.  Unlike the lattice runs, this is NOT an exhaustive sweep
of a similarity class of configurations: the pool is truncated by a bound B on
the integer coefficients as well as by the squared radius, and translating a
configuration can push coefficients outside the box.  Treat it as a broad
heuristic sweep over a pool that contains both lattices and H8.
"""
import sys, time
import numpy as np
from cyclo import build_pool_z3, prepare_z3, d2, cross3, sign3
from search import run
from geo import analyse_q3, Q3

B = int(sys.argv[1]) if len(sys.argv) > 1 else 2
DSQ = int(sys.argv[2]) if len(sys.argv) > 2 else 20
KLIST = [int(x) for x in sys.argv[3].split(',')] if len(sys.argv) > 3 else [3, 4, 5, 6, 7]

# ---------------------------------------------------------------- step 0
print("step 0: cross-check on Harborth H8 inside this pool", flush=True)
H8 = [(1, 0, 1, 0), (-1, 0, 1, 0), (-1, 0, -1, 0), (1, 0, -1, 0),
      (0, 0, 1, 1), (0, 0, -1, -1), (1, 1, 0, 0), (-1, -1, 0, 0)]
ds = {d2(H8[i], H8[j]) for i in range(8) for j in range(i + 1, 8)}
coll = sum(1 for i in range(8) for j in range(i + 1, 8) for t in range(j + 1, 8)
           if cross3(H8[i], H8[j], H8[t]) == (0, 0))
per = [len({d2(H8[i], H8[j]) for j in range(8) if j != i}) for i in range(8)]
print(f"  Z[sqrt3] module: distances={len(ds)} collinear={coll} per-point={per}")
s3 = Q3(0, 1); h = Q3(1) + s3
r = analyse_q3([(Q3(1), Q3(1)), (Q3(-1), Q3(1)), (Q3(-1), Q3(-1)), (Q3(1), Q3(-1)),
                (Q3(0), h), (Q3(0), -h), (h, Q3(0)), (-h, Q3(0))], "  geo.Q3 module")
assert len(ds) == r['k'] and coll == r['collinear'] and per == r['per_point'], \
    "the two independent implementations disagree"
print("  -> the two independent exact implementations AGREE\n", flush=True)

# ---------------------------------------------------------------- pool
t0 = time.time()
pts = build_pool_z3(B, DSQ)
print(f"pool Z[sqrt3]^2, |coeff| <= {B}, squared norm <= {DSQ}: "
      f"{len(pts)} points  ({time.time()-t0:.1f}s)", flush=True)
missing = [p for p in H8 if p not in set(pts)]
print(f"  H8 points present in pool: {8-len(missing)}/8", flush=True)

t0 = time.time()
tab = prepare_z3(pts, DSQ)
print(f"  tables: {tab['V']} distance values, {tab['DW']} mask words "
      f"({time.time()-t0:.1f}s)", flush=True)

# ---------------------------------------------------------------- search
for k in KLIST:
    t0 = time.time()
    gb, gs, _, _ = run(tab, k)
    t1 = time.time()
    hb, hs, _, _ = run(tab, k, target=2 * k + 2, with_collinear=True,
                       stop_at_target=True)
    t2 = time.time()
    S = [pts[i] for i in hs]
    # independent re-verification of whatever the search returned
    dd = {d2(S[i], S[j]) for i in range(len(S)) for j in range(i + 1, len(S))}
    cc = sum(1 for i in range(len(S)) for j in range(i + 1, len(S))
             for t in range(j + 1, len(S)) if cross3(S[i], S[j], S[t]) == (0, 0))
    assert len(dd) <= k and cc == 0, (len(dd), cc)
    tag = "*** COUNTEREXAMPLE ***" if hb >= 2 * k + 2 else "none"
    print(f"  k={k}: g_pool={gb:3d}   h_pool={hb:3d} [target {2*k+2}] -> {tag}"
          f"   [{t1-t0:.1f}s / {t2-t1:.1f}s]", flush=True)
    if hb >= 2 * k + 2:
        print("   !!! ", S)
