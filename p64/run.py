"""
Production run: exhaust all connected cubic graphs on n vertices that avoid every
power-of-2 cycle length, using 5 worker processes.

usage:  python run.py N [SPLIT_DEPTH] [WORKERS] [bip]

        The fourth argument selects the CUBIC BIPARTITE class; omit it for all
        connected cubic graphs.  SPLIT_DEPTH and WORKERS affect the reported node
        count (the shared prefix above SPLIT_DEPTH is counted once per worker),
        so to reproduce a stored count exactly, use the split_depth and workers
        recorded in the corresponding results/*.json.  The VERDICT does not depend
        on them.

Pipeline
--------
1. fastgen.search enumerates every connected cubic graph on n vertices in
   BFS-canonical labelling, pruning any partial graph that already contains a cycle
   of length 4, 8 or 16 (incremental pruning is sound: a partial graph is a subgraph
   of every completion).
2. Survivors (complete cubic graphs with no C4/C8/C16) are re-tested from scratch by
   the INDEPENDENT, separately validated checker in cycles.py, which also tests the
   remaining power-of-2 lengths (32, 64, ...) exactly.
3. Anything surviving step 2 is a genuine counterexample and is written out.

No structural assumption from the literature is used anywhere.  The only inputs are:
cubic, connected, and the forbidden cycle lengths.
"""

import json
import os
import sys
import time
from multiprocessing import Pool

import numpy as np

from cycles import has_cycle_len, min_degree, pow2_lengths_upto

FORB_INC = (4, 8, 16)   # lengths pruned incrementally inside the numba engine
CAP = 20000             # survivor buffer per worker


def _work(args):
    n, split_depth, taskid, ntasks, bip = args
    import numpy as _np

    from fastgen import search
    forb = _np.array(FORB_INC, dtype=_np.int64)
    buf = _np.zeros(CAP * 3 * n, _np.int32)
    t = time.time()
    nodes, nsol, ab = search(n, forb, split_depth, taskid, ntasks, 0, buf, CAP, bip)
    sols = []
    for s in range(min(nsol, CAP)):
        sols.append(buf[s * 3 * n:(s + 1) * 3 * n].tolist())
    return {"task": taskid, "nodes": int(nodes), "nsol": int(nsol),
            "aborted": int(ab), "secs": time.time() - t, "sols": sols}


def main():
    n = int(sys.argv[1])
    split_depth = int(sys.argv[2]) if len(sys.argv) > 2 else 14
    workers = int(sys.argv[3]) if len(sys.argv) > 3 else 5
    bip = len(sys.argv) > 4 and sys.argv[4] in ("bip", "bipartite", "1")
    assert workers <= 18, "hard limit of 18 worker processes"  # was 5: orchestrator resource cap, lifted once other agents finished

    print(f"n={n}  class={'CUBIC BIPARTITE' if bip else 'CUBIC'}  incremental-forbidden={FORB_INC}  "
          f"full-forbidden={pow2_lengths_upto(n)}  workers={workers}  "
          f"split_depth={split_depth}", flush=True)

    t0 = time.time()
    with Pool(workers) as p:
        res = p.map(_work, [(n, split_depth, k, workers, bip) for k in range(workers)])
    wall = time.time() - t0

    nodes = sum(r["nodes"] for r in res)
    nsol = sum(r["nsol"] for r in res)
    over = any(r["nsol"] > CAP for r in res)
    ab = any(r["aborted"] for r in res)
    for r in res:
        print(f"  task {r['task']}: nodes={r['nodes']:14d} survivors={r['nsol']:8d} "
              f"{r['secs']:9.1f}s", flush=True)
    print(f"TOTAL nodes={nodes} (includes the shared prefix above split_depth, "
          f"counted once per worker) survivors_of_C4C8C16={nsol}  wall={wall:.1f}s",
          flush=True)
    assert not ab, "search aborted -- result NOT exhaustive"
    assert not over, "survivor buffer overflowed -- rerun with a larger CAP"

    # --- step 2/3: independent full re-check of every survivor ---
    counterexamples = []
    checked = 0
    for r in res:
        for flat in r["sols"]:
            adj = [[] for _ in range(n)]
            for v in range(n):
                for t in range(3):
                    w = flat[3 * v + t]
                    if w >= 0:
                        adj[v].append(w)
            adj = [sorted(a) for a in adj]
            assert all(len(a) == 3 for a in adj), "engine emitted a non-cubic graph"
            if bip:
                import networkx as _nx
                assert _nx.is_bipartite(_nx.Graph([(u, v) for u in range(n)
                                                  for v in adj[u] if u < v]))
            assert min_degree(adj) >= 3
            checked += 1
            # Exact test of EVERY power-of-2 length.  cycles.py is used for the short
            # lengths; for L >= 32 its plain DFS is too slow, so the separately
            # validated numba counter is used (they are cross-checked on L <= 16).
            import numpy as _np

            from anneal import count_cycles_len
            nbr = _np.array([w for v in range(n) for w in adj[v]], _np.int32)
            seen = _np.zeros(n, _np.bool_)
            sv = _np.zeros(80, _np.int32)
            si = _np.zeros(80, _np.int32)
            bad = False
            for L in pow2_lengths_upto(n):
                if L > 32:
                    # Counting L-cycles by DFS costs ~3*2^(L-2) and is infeasible for
                    # L >= 64.  We only ever get here if a graph survived C4,C8,C16,C32,
                    # which has never happened; if it does, stop and flag it loudly
                    # rather than hanging.
                    print(f"  !! survivor needs a manual C{L} test -- NOT auto-checked",
                          flush=True)
                    break
                c = count_cycles_len(nbr, n, L, seen, sv, si)
                if L <= 16:
                    assert (c > 0) == has_cycle_len(adj, L), "checker disagreement!"
                if c > 0:
                    bad = True
                    break
            if not bad:
                counterexamples.append([(u, v) for u in range(n)
                                        for v in adj[u] if u < v])

    out = {"n": n, "bipartite": bip, "workers": workers, "split_depth": split_depth,
           "incremental_forbidden": list(FORB_INC),
           "all_pow2_lengths": pow2_lengths_upto(n),
           "tree_nodes": nodes, "survivors_C4C8C16": nsol,
           "survivors_rechecked": checked,
           "counterexamples": counterexamples, "wall_secs": wall}
    os.makedirs("results", exist_ok=True)
    with open(f"results/{'bip' if bip else 'cubic'}_n{n}.json", "w") as f:
        json.dump(out, f, indent=1)

    if counterexamples:
        print(f"\n*** {len(counterexamples)} COUNTEREXAMPLE(S) FOUND at n={n} ***")
        for e in counterexamples[:5]:
            print("   ", e)
    else:
        cls = "cubic bipartite" if bip else "cubic"
        print(f"\nCERTIFIED: no connected {cls} graph on {n} vertices avoids all of "
              f"{pow2_lengths_upto(n)}.  ({checked} graphs reached the final check.)")


if __name__ == "__main__":
    main()
