"""
Exhaustive generation of connected cubic graphs in BFS-canonical labelling, with
sound incremental pruning on forbidden cycle lengths.

COMPLETENESS ARGUMENT (this is the whole point -- read it)
----------------------------------------------------------
Let G be any connected cubic graph on n vertices.  Run breadth-first search from any
vertex r and label the vertices 0,1,2,... in discovery order.  Then:

  (i)  vertex 0 = r;
  (ii) processing vertices in increasing label order, when we reach vertex i every
       edge from i to a vertex j < i has already been recorded;
  (iii) the neighbours of i that are not yet discovered receive the next consecutive
       unused labels.

The generator below explores exactly the tree of all such labellings:
  at each step it takes i = the least vertex with degree < 3 and chooses the set of
  its remaining neighbours from
        { j : i < j < nused, deg[j] < 3 }  u  { the next new labels nused, nused+1, ... }
  in increasing order.
Therefore EVERY connected cubic graph on n vertices is produced at least once.
(It is produced several times -- once per BFS labelling -- which costs time but never
correctness for a NON-EXISTENCE claim.)

SOUNDNESS OF THE CYCLE PRUNING
-------------------------------
At every point the partial graph is a subgraph of every completion of it.  A cycle in
a subgraph is a cycle in the supergraph.  So if the partial graph already contains a
cycle of forbidden length L, no completion can be a counterexample, and the whole
subtree may be cut.  This is the only pruning applied to the cycle structure.

DEGREE/COUNTING PRUNE
---------------------
Let D = sum over discovered vertices of (3 - deg).  Every one of the (n - nused) still
undiscovered vertices must be attached by an edge that consumes one open slot, so we
need D >= n - nused.  Also nused <= n.  Both are necessary conditions, hence sound.
"""

import sys

# ---------------------------------------------------------------------------


def _path_exists_len(adj, u, v, k, banned_edge):
    """Is there a simple path from u to v with exactly k edges, not using banned_edge?
    adj is a list of lists.  Used to detect a cycle of length k+1 through banned_edge."""
    n = len(adj)
    seen = [False] * n
    seen[u] = True
    bu, bv = banned_edge

    def dfs(x, d):
        if d == k:
            return x == v
        rem = k - d
        for y in adj[x]:
            if (x == bu and y == bv) or (x == bv and y == bu):
                continue
            if y == v:
                if rem == 1:
                    return True
                continue
            if seen[y]:
                continue
            if rem <= 1:
                continue
            seen[y] = True
            if dfs(y, d + 1):
                seen[y] = False
                return True
            seen[y] = False
        return False

    return dfs(u, 0)


def creates_cycle(adj, u, v, L):
    """Does the edge uv (already present in adj) lie on a cycle of length exactly L?"""
    return _path_exists_len(adj, u, v, L - 1, (u, v))


# ---------------------------------------------------------------------------


def generate_cubic(n, forbidden=(), on_complete=None, forbid_check_limit=8,
                   node_budget=None, stats=None):
    """Enumerate connected cubic graphs on n vertices in BFS-canonical labelling.

    forbidden           : cycle lengths that must NOT appear (pruned incrementally)
    forbid_check_limit  : only cycle lengths <= this are checked incrementally at every
                          edge insertion (longer ones are checked once the graph is
                          complete, by the caller).  Purely a speed/pruning tradeoff;
                          correctness does not depend on it.
    on_complete(adj)    : called with the finished adjacency list (a fresh copy)
    node_budget         : abort (raise Budget) after this many search-tree nodes
    """
    adj = [[] for _ in range(n)]
    deg = [0] * n
    inc = [f for f in forbidden if f <= forbid_check_limit]
    late = [f for f in forbidden if f > forbid_check_limit]
    counters = {"nodes": 0, "complete": 0}

    class Budget(Exception):
        pass

    def add_edge(i, j):
        adj[i].append(j)
        adj[j].append(i)
        deg[i] += 1
        deg[j] += 1

    def del_edge(i, j):
        adj[i].pop()
        adj[j].pop()
        deg[i] -= 1
        deg[j] -= 1

    def rec(nused):
        counters["nodes"] += 1
        if node_budget is not None and counters["nodes"] > node_budget:
            raise Budget()
        # find least vertex with deg < 3 among discovered
        i = -1
        for v in range(nused):
            if deg[v] < 3:
                i = v
                break
        if i == -1:
            if nused == n:
                counters["complete"] += 1
                if on_complete is not None:
                    on_complete([sorted(a) for a in adj])
            return
        need = 3 - deg[i]
        # counting prune: if there are still undiscovered vertices they must be
        # attachable, i.e. at least one open slot must exist among discovered vertices.
        if nused < n:
            D = 0
            for v in range(nused):
                D += 3 - deg[v]
            if D == 0:
                return
        cand = [j for j in range(i + 1, nused) if deg[j] < 3]
        maxnew = min(need, n - nused)

        # choose `need` neighbours: some existing (a subset of cand, increasing) and
        # then `t` brand-new vertices (which necessarily get labels nused..nused+t-1)
        def choose(picked, start, t_new):
            """picked = chosen existing neighbours so far; start = index into cand;
            t_new = number of new vertices this call will use at the end."""
            if len(picked) + t_new == need:
                # commit
                added = []
                ok = True
                for j in picked:
                    add_edge(i, j)
                    added.append((i, j))
                    for L in inc:
                        if creates_cycle(adj, i, j, L):
                            ok = False
                            break
                    if not ok:
                        break
                if ok:
                    for k in range(t_new):
                        j = nused + k
                        add_edge(i, j)
                        added.append((i, j))
                        # a brand-new vertex is a leaf, cannot close any cycle
                    rec(nused + t_new)
                for (a, b) in reversed(added):
                    del_edge(a, b)
                return
            if start < len(cand):
                for s in range(start, len(cand)):
                    choose(picked + [cand[s]], s + 1, t_new)

        for t_new in range(0, maxnew + 1):
            if need - t_new <= len(cand):
                choose([], 0, t_new)

    try:
        rec(0) if n == 0 else _start(rec, adj, deg, n)
    except Budget:
        counters["aborted"] = True
    if stats is not None:
        stats.update(counters)
    return counters


def _start(rec, adj, deg, n):
    """Seed: vertex 0 exists, nothing else.  rec will give it 3 new neighbours."""
    return rec(1)


# ---------------------------------------------------------------------------
# convenience: finish-check of the long forbidden lengths
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import time

    for n in [4, 6, 8, 10, 12, 14, 16]:
        t = time.time()
        st = {}
        generate_cubic(n, forbidden=(), stats=st)
        print(f"n={n:3d}  labelled-complete={st['complete']:12d}  "
              f"nodes={st['nodes']:12d}  {time.time()-t:.2f}s")
        sys.stdout.flush()
