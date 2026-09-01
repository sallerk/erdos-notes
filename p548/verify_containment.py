"""INDEPENDENT VERIFIER for the Erdos-Sos search artifacts.

Shares no code with the search.  The search decides "tree T embeds in G"
with a backtracking subgraph-isomorphism DFS (es_core.embed_tree).  This
file decides the same question by a completely different route:

    inj(T,G) = sum over U subset of V(G) of
                  (-1)^(t-|U|) * C(n-|U|, t-|U|) * hom(T, G[U])

    (Mobius inversion: hom(T,G[U]) = sum over W subset of U of s_W, where
     s_W = #homomorphisms with image exactly W; homomorphisms with image of
     size t = |V(T)| are exactly the injective ones.)

hom(T, G[U]) is counted by an ordinary tree dynamic program with no
injectivity constraint.  All arithmetic is done in uint64, i.e. exactly
modulo 2^64; since inj(T,G) <= n!/(n-t)! < 2^64 for every size used here,
the residue IS the exact value.  T embeds in G iff inj(T,G) > 0.

The tree catalogue is also re-verified from scratch, by Cayley's formula:
sum over iso classes of t!/|Aut(T)| must equal t^(t-2), the number of
labelled trees.  |Aut| is counted by definition-level backtracking.  This
certifies simultaneously that the catalogue is complete and that no two
entries are isomorphic.

Usage
    python verify_containment.py selftest
    python verify_containment.py <artifact.json> [<artifact.json> ...]
"""
import json
import math
import sys

import numpy as np

# The inclusion-exclusion sum is deliberately evaluated modulo 2^64: unsigned
# wraparound IS the arithmetic we want, and the true value is far below 2^64,
# so the residue is exact.  numpy's overflow warning is therefore expected.
np.seterr(over="ignore")


# ---------------------------------------------------- tree structure (local)
def _root_and_order(t, tedges):
    adj = [[] for _ in range(t)]
    for u, v in tedges:
        adj[int(u)].append(int(v))
        adj[int(v)].append(int(u))
    root = 0
    order = [root]
    parent = [-1] * t
    seen = [False] * t
    seen[root] = True
    i = 0
    while i < len(order):
        v = order[i]
        i += 1
        for w in adj[v]:
            if not seen[w]:
                seen[w] = True
                parent[w] = v
                order.append(w)
    if len(order) != t:
        raise ValueError("tree edge list is not connected")
    children = [[] for _ in range(t)]
    for v in order[1:]:
        children[parent[v]].append(v)
    return root, order, children


def inj_count(n, gedges, t, tedges, block=1 << 14):
    """Exact number of injective homomorphisms T -> G (subgraph copies with
    labelled tree vertices).  Exact: uint64 arithmetic is exact mod 2^64 and
    the true value is far below 2^64."""
    A = np.zeros((n, n), np.uint64)
    for u, v in gedges:
        A[int(u), int(v)] = 1
        A[int(v), int(u)] = 1
    root, order, children = _root_and_order(t, tedges)

    # coefficient by subset size
    coef = np.zeros(n + 1, np.uint64)
    for u in range(n + 1):
        if u > t:
            c = 0
        else:
            c = math.comb(n - u, t - u)
        if (t - u) % 2:
            c = (-c) % (1 << 64)
        coef[u] = np.uint64(c)

    bitpos = np.arange(n, dtype=np.uint64)
    total = np.uint64(0)
    nsub = 1 << n
    for start in range(0, nsub, block):
        stop = min(start + block, nsub)
        U = np.arange(start, stop, dtype=np.uint64)
        inU = ((U[:, None] >> bitpos[None, :]) & np.uint64(1)).astype(np.uint64)
        B = inU.shape[0]
        f = [None] * t
        for x in reversed(order):                     # children before parent
            val = np.ones((B, n), np.uint64)
            for c in children[x]:
                fc = f[c] * inU                       # zero outside U
                s = np.zeros((B, n), np.uint64)
                for w in range(n):
                    nz = A[w]
                    if nz.any():
                        s += fc[:, w][:, None] * nz[None, :]
                val = val * s
                f[c] = None
            f[x] = val * inU
        homU = f[root].sum(axis=1, dtype=np.uint64)
        size = inU.sum(axis=1, dtype=np.uint64).astype(np.int64)
        total = total + (coef[size] * homU).sum(dtype=np.uint64)
    return int(total)


def contains_tree_incl_excl(n, gedges, t, tedges):
    return inj_count(n, gedges, t, tedges) > 0


# ------------------------------------------------------- tree set validation
def count_automorphisms(t, tedges):
    """|Aut(T)| by definition: count bijections V->V preserving adjacency."""
    E = set()
    adj = [set() for _ in range(t)]
    for u, v in tedges:
        u, v = int(u), int(v)
        E.add((min(u, v), max(u, v)))
        adj[u].add(v)
        adj[v].add(u)
    deg = [len(adj[v]) for v in range(t)]
    img = [-1] * t
    used = [False] * t
    cnt = 0

    def rec(i):
        nonlocal cnt
        if i == t:
            cnt += 1
            return
        for j in range(t):
            if used[j] or deg[j] != deg[i]:
                continue
            ok = True
            for p in range(i):
                a = (img[p] in adj[j])
                b = (p in adj[i])
                if a != b:
                    ok = False
                    break
            if ok:
                used[j] = True
                img[i] = j
                rec(i + 1)
                used[j] = False
        return

    rec(0)
    return cnt


def verify_tree_set(path):
    d = json.load(open(path))
    t = d["n_vertices"]
    trees = d["trees"]
    a000055 = {9: 47, 10: 106, 11: 235}
    print(f"  {path}: {len(trees)} trees on {t} vertices")
    ok = True
    if t in a000055 and len(trees) != a000055[t]:
        print(f"    FAIL count {len(trees)} != A000055 {a000055[t]}")
        ok = False
    tot = 0
    for r in trees:
        e = [tuple(map(int, x)) for x in r["edges"]]
        if len(e) != t - 1:
            print(f"    FAIL tree {r['id']} has {len(e)} edges")
            ok = False
            continue
        try:
            _root_and_order(t, e)                    # connected?  (t-1 edges
        except ValueError:                           #  + connected => tree)
            print(f"    FAIL tree {r['id']} not connected")
            ok = False
            continue
        tot += math.factorial(t) // count_automorphisms(t, e)
    cayley = t ** (t - 2)
    print(f"    sum t!/|Aut| = {tot}   Cayley t^(t-2) = {cayley}   "
          f"{'PASS' if tot == cayley else 'FAIL'}")
    print(f"    (equality certifies the catalogue is COMPLETE and its "
          f"members PAIRWISE NON-ISOMORPHIC)")
    return ok and tot == cayley


# ------------------------------------------------------------- artifact check
def verify_artifact(path, max_trees=None):
    d = json.load(open(path))
    n = d["n_vertices"]
    t = d["tree_order"]
    edges = [tuple(map(int, e)) for e in d["edges"]]
    print(f"\n=== {path}")
    print(f"  graph on n={n} vertices, tree order t={t}")

    ok = True
    es = {(min(u, v), max(u, v)) for u, v in edges}
    if len(es) != len(edges):
        print("  FAIL duplicate edges")
        ok = False
    if any(u == v for u, v in edges):
        print("  FAIL loop")
        ok = False
    m = len(es)
    thr = (n * (t - 2)) // 2 + 1
    print(f"  edge count            : {m}  (claimed {d['n_edges']})  "
          f"{'PASS' if m == d['n_edges'] else 'FAIL'}")
    ok &= (m == d["n_edges"])
    print(f"  Erdos-Sos threshold   : floor({n}*{t-2}/2)+1 = {thr} "
          f"(claimed {d['threshold_edges']})  "
          f"{'PASS' if thr == d['threshold_edges'] else 'FAIL'}")
    ok &= (thr == d["threshold_edges"])
    at_threshold = m >= thr
    if at_threshold:
        print(f"  m >= threshold        : {m} >= {thr}  PASS")
    else:
        print(f"  m >= threshold        : {m} < {thr}  BELOW THRESHOLD -- this "
              f"artifact is an extremal/near-extremal example, not a "
              f"candidate counterexample")

    deg = [0] * n
    for u, v in es:
        deg[u] += 1
        deg[v] += 1
    print(f"  degrees               : min {min(deg)}  max {max(deg)}  "
          f"sum {sum(deg)} = 2m {'PASS' if sum(deg) == 2 * m else 'FAIL'}")

    trees = json.load(open(d["tree_file"]))["trees"]
    claimed_missing = set(d["missing_tree_ids"])
    partial = False
    if max_trees is not None and max_trees < len(trees):
        trees = trees[:max_trees]
        partial = True
        print(f"  PARTIAL verification: re-deciding the first {max_trees} of "
              f"{d['tree_file']} only (n={n} makes the full pass costly)")
    else:
        print(f"  re-deciding all {len(trees)} trees by inclusion-exclusion "
              f"(independent algorithm) ...")
    missing = []
    counts_all = []
    for r in trees:
        te = [tuple(map(int, x)) for x in r["edges"]]
        c = inj_count(n, sorted(es), t, te)
        counts_all.append(c)
        if c == 0:
            missing.append(r["id"])
    print(f"  trees NOT contained   : {missing}")
    print(f"  claimed               : {sorted(claimed_missing)}"
          + ("  (comparison restricted to the trees checked)" if partial
             else ""))
    if partial:
        checked = {int(r["id"]) for r in trees}
        agree = set(missing) == (claimed_missing & checked)
    else:
        agree = set(missing) == claimed_missing
    print(f"  {'PASS - agrees with the search' if agree else 'FAIL - DISAGREES'}")
    ok &= agree
    if missing and at_threshold:
        print(f"  *** COUNTEREXAMPLE TO ERDOS-SOS: {m} edges >= {thr} on "
              f"{n} vertices, misses {len(missing)} tree(s) of order {t} ***")
    elif missing:
        print(f"  not a counterexample: {m} < {thr} edges.  It misses "
              f"{len(missing)} tree(s), which is what makes it EXTREMAL.")
    else:
        print(f"  no counterexample: this graph contains all {len(trees)} "
              f"trees of order {t}.")
        nz = [c for c in counts_all if c > 0]
        if nz:
            print(f"  closest miss: the scarcest tree has {min(nz)} "
                  f"embeddings (0 would be a counterexample)")
    return ok


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return
    if sys.argv[1] == "selftest":
        good = True
        for f in ("trees_9.json", "trees_10.json", "trees_11.json"):
            good &= verify_tree_set(f)
        print("\nTREE CATALOGUE:", "PASS" if good else "FAIL")
        return
    mt = None
    args = list(sys.argv[1:])
    if "--max-trees" in args:
        i = args.index("--max-trees")
        mt = int(args[i + 1])
        del args[i:i + 2]
    allok = True
    for p in args:
        allok &= verify_artifact(p, mt)
    print("\nOVERALL:", "PASS" if allok else "FAIL")
    sys.exit(0 if allok else 1)


if __name__ == "__main__":
    main()
