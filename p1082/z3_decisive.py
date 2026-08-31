"""Only the decisive question on the big Z[sqrt3]^2 pools:

    is there a subset of 2k+2 points with <= k distinct distances
    and no three collinear?

(The unrestricted maximum g_pool is much more expensive to compute and is not
needed to answer it, so it is skipped here.)
"""
import sys, time
from cyclo import build_pool_z3, prepare_z3, d2, cross3
from search import run

B = int(sys.argv[1]); DSQ = int(sys.argv[2])
KLIST = [int(x) for x in sys.argv[3].split(',')]

pts = build_pool_z3(B, DSQ)
print(f"pool Z[sqrt3]^2 |coeff|<={B}, |z|^2<={DSQ}: {len(pts)} points", flush=True)
t0 = time.time()
tab = prepare_z3(pts, DSQ)
print(f"  tables: {tab['V']} distance values, {tab['DW']} words "
      f"({time.time()-t0:.1f}s)", flush=True)

for k in KLIST:
    t0 = time.time()
    hb, hs, _, _ = run(tab, k, target=2 * k + 2, with_collinear=True,
                       stop_at_target=True)
    S = [pts[i] for i in hs]
    dd = {d2(S[i], S[j]) for i in range(len(S)) for j in range(i + 1, len(S))}
    cc = sum(1 for i in range(len(S)) for j in range(i + 1, len(S))
             for t in range(j + 1, len(S)) if cross3(S[i], S[j], S[t]) == (0, 0))
    assert len(dd) <= k and cc == 0
    tag = "*** COUNTEREXAMPLE ***" if hb >= 2 * k + 2 else "none"
    print(f"  k={k}: h_pool={hb:3d}  [target {2*k+2}, conjectured max {2*k+1}] "
          f"-> {tag}   [{time.time()-t0:.1f}s]", flush=True)
    if hb >= 2 * k + 2:
        print("   !!! ", S)
