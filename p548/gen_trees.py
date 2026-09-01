"""Generate all free trees (up to isomorphism) on m vertices, m = 1..12.

Method: leaf-augmentation with canonical-form dedup.
  Every tree on m>=2 vertices has a leaf; deleting it gives a tree on m-1
  vertices.  So {T on m vertices} = dedup{ T' + new leaf attached to v :
  T' on m-1 vertices, v in V(T') }.  This is complete by that observation.

Canonical form: AHU (Aho-Hopcroft-Ullman) string, rooted at the tree's
center.  A tree has 1 or 2 centers; with 2 centers we take the two rooted
canonical strings of the two halves obtained by deleting the central edge,
sort them, and concatenate.  This is a complete isomorphism invariant for
free trees.

Verification: the produced counts must match OEIS A000055 (number of trees
on n unlabeled nodes): n=1..12 -> 1,1,1,2,3,6,11,23,47,106,235,551.

Usage:  python gen_trees.py            (writes trees_<m>.json for m=9,10,11)
"""
import json
import sys
from itertools import combinations


# ---------------------------------------------------------------- canonical
def adj_of(m, edges):
    a = [[] for _ in range(m)]
    for u, v in edges:
        a[u].append(v)
        a[v].append(u)
    return a


def rooted_canon(adj, root, banned):
    """AHU canonical string of the tree rooted at `root`, not crossing to
    `banned` (use -1 for none)."""
    def rec(v, parent):
        subs = sorted(rec(w, v) for w in adj[v] if w != parent and w != banned)
        return "(" + "".join(subs) + ")"
    return rec(root, -1)


def centers(m, adj):
    if m == 1:
        return [0]
    deg = [len(adj[v]) for v in range(m)]
    alive = [True] * m
    remaining = m
    leaves = [v for v in range(m) if deg[v] == 1]
    while remaining > 2:
        nxt = []
        for v in leaves:
            alive[v] = False
            remaining -= 1
            for w in adj[v]:
                if alive[w]:
                    deg[w] -= 1
                    if deg[w] == 1:
                        nxt.append(w)
        leaves = nxt
    return [v for v in range(m) if alive[v]]


def canonical(m, edges):
    adj = adj_of(m, edges)
    c = centers(m, adj)
    if len(c) == 1:
        return "1|" + rooted_canon(adj, c[0], -1)
    a, b = c
    sa = rooted_canon(adj, a, b)
    sb = rooted_canon(adj, b, a)
    if sa > sb:
        sa, sb = sb, sa
    return "2|" + sa + sb


# ---------------------------------------------------------------- generation
def gen(max_m):
    """Return dict m -> list of edge lists (one per iso class)."""
    out = {1: [[]]}
    for m in range(2, max_m + 1):
        seen = {}
        for edges in out[m - 1]:
            for v in range(m - 1):
                new = edges + [(v, m - 1)]
                key = canonical(m, new)
                if key not in seen:
                    seen[key] = new
        out[m] = list(seen.values())
    return out


# ---------------------------------------------------------------- properties
def tree_props(m, edges):
    adj = adj_of(m, edges)
    deg = [len(adj[v]) for v in range(m)]
    # all-pairs distance by BFS
    INF = 10 ** 6
    diam = 0
    for s in range(m):
        dist = [INF] * m
        dist[s] = 0
        q = [s]
        while q:
            nq = []
            for v in q:
                for w in adj[v]:
                    if dist[w] == INF:
                        dist[w] = dist[v] + 1
                        nq.append(w)
            q = nq
        diam = max(diam, max(dist))
    nbranch = sum(1 for v in range(m) if deg[v] >= 3)
    leaves = [v for v in range(m) if deg[v] == 1]
    max_leaf_nb = 0
    for v in range(m):
        c = sum(1 for w in adj[v] if deg[w] == 1)
        max_leaf_nb = max(max_leaf_nb, c)
    return {
        "diameter": diam,
        "degrees": sorted(deg, reverse=True),
        "max_degree": max(deg),
        "n_leaves": len(leaves),
        "n_branch_vertices": nbranch,          # vertices of degree >= 3
        "is_path": max(deg) <= 2,
        "is_spider": nbranch <= 1,             # <=1 vertex of degree > 2
        "is_star": max(deg) == m - 1,
        "max_leaf_neighbours": max_leaf_nb,
    }


def main():
    max_m = 12
    trees = gen(max_m)
    expected = {1: 1, 2: 1, 3: 1, 4: 2, 5: 3, 6: 6, 7: 11, 8: 23,
                9: 47, 10: 106, 11: 235, 12: 551}
    ok = True
    for m in range(1, max_m + 1):
        got = len(trees[m])
        exp = expected[m]
        flag = "OK " if got == exp else "BAD"
        if got != exp:
            ok = False
        print(f"  m={m:2d}  trees={got:4d}  expected(A000055)={exp:4d}  {flag}")
    if not ok:
        print("COUNT MISMATCH -- aborting")
        sys.exit(1)
    print("All counts match OEIS A000055.")

    for m in (9, 10, 11):
        recs = []
        for i, e in enumerate(sorted(trees[m], key=lambda x: canonical(m, x))):
            recs.append({
                "id": i,
                "n_vertices": m,
                "n_edges": len(e),
                "edges": [list(x) for x in sorted(tuple(sorted(p)) for p in e)],
                "canonical_ahu": canonical(m, e),
                **tree_props(m, e),
            })
        # sanity: all canonical forms distinct, all have m-1 edges & connected
        assert len({r["canonical_ahu"] for r in recs}) == len(recs)
        assert all(r["n_edges"] == m - 1 for r in recs)
        fn = f"trees_{m}.json"
        with open(fn, "w") as f:
            json.dump({"n_vertices": m, "count": len(recs),
                       "oeis": "A000055", "trees": recs}, f, indent=1)
        print(f"  wrote {fn}: {len(recs)} trees")


if __name__ == "__main__":
    main()
