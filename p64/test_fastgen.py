"""
Check the numba engine reproduces the (validated) pure-Python generator EXACTLY.

We compare, for many (n, forbidden) pairs:
  * the number of complete cubic graphs produced (with BFS-labelling multiplicity)
  * the multiset of produced graphs themselves (as canonical edge-sets)
  * that the parallel split partitions the tree exactly (sum over tasks == serial)
"""

import sys

import numpy as np

from cycles import has_cycle_len
from fastgen import search
from gen import generate_cubic

FAIL = []


def check(cond, msg):
    print(("  ok   " if cond else "  FAIL ") + msg)
    if not cond:
        FAIL.append(msg)


def py_graphs(n, forb):
    out = []

    def oc(adj):
        out.append(tuple(sorted((u, v) for u in range(n) for v in adj[u] if u < v)))

    generate_cubic(n, forbidden=forb, on_complete=oc,
                   forbid_check_limit=max(forb) if forb else 0)
    return sorted(out)


def nb_graphs(n, forb, taskid=0, ntasks=1, split_depth=-1):
    f = np.array(sorted(forb), dtype=np.int64) if forb else np.zeros(0, np.int64)
    cap = 400000
    buf = np.zeros(cap * 3 * n, np.int32)
    nodes, nsol, ab = search(n, f, split_depth, taskid, ntasks, 0, buf, cap)
    assert ab == 0 and nsol <= cap, (nsol, ab)
    out = []
    for s in range(nsol):
        es = set()
        for v in range(n):
            for t in range(3):
                w = buf[s * 3 * n + 3 * v + t]
                if w >= 0:
                    es.add((min(v, w), max(v, w)))
        out.append(tuple(sorted(es)))
    return sorted(out), nodes, nsol


print("numba engine vs pure-Python generator (identical output required)")
for n, forb in [(4, ()), (6, ()), (8, ()), (10, ()), (12, ()),
                (10, (3, 4)), (12, (3, 4)), (14, (3, 4)), (16, (3, 4)),
                (14, (3, 4, 5)), (16, (3, 4, 5)), (18, (3, 4, 5)),
                (10, (4, 8)), (14, (4, 8)), (16, (4, 8)), (18, (4, 8)),
                (12, (4,)), (14, (4,)), (16, (4,)),
                (14, (4, 8, 16)), (16, (4, 8, 16)), (18, (4, 8, 16))]:
    p = py_graphs(n, forb)
    q, nodes, nsol = nb_graphs(n, forb)
    check(p == q, f"n={n:2d} forbidden={forb}: {len(p)} labelled graphs, identical")

print("\nparallel split partitions the tree exactly")
for n, forb, sd in [(12, (), 6), (14, (3, 4), 6), (16, (4,), 8), (18, (4, 8), 6)]:
    serial, _, ns = nb_graphs(n, forb)
    merged = []
    for t in range(5):
        g, _, _ = nb_graphs(n, forb, taskid=t, ntasks=5, split_depth=sd)
        merged.extend(g)
    check(sorted(merged) == serial,
          f"n={n} forbidden={forb} split_depth={sd}: 5 tasks reunite to {ns} graphs")

print("\nforbidden lengths really are absent from the output")
bad = 0
for n, forb in [(16, (3, 4)), (16, (4,)), (18, (3, 4, 5))]:
    g, _, _ = nb_graphs(n, forb)
    for es in g[:400]:
        adj = [[] for _ in range(n)]
        for u, v in es:
            adj[u].append(v)
            adj[v].append(u)
        adj = [sorted(a) for a in adj]
        if any(len(a) != 3 for a in adj):
            bad += 1
        for L in forb:
            if has_cycle_len(adj, L):
                bad += 1
check(bad == 0, "every emitted graph is cubic and free of the forbidden lengths")

print()
if FAIL:
    print(f"*** {len(FAIL)} FAILURES ***")
    sys.exit(1)
print("NUMBA ENGINE VALIDATED")
