"""
Numba-accelerated exhaustive search for cubic counterexamples to Erdos-Gyarfas.

This is a re-implementation of gen.py's search in flat arrays.  gen.py (pure Python)
is validated against published enumeration counts in test_gen.py; test_fastgen.py
checks that this file reproduces gen.py's tree/solution counts exactly, so the
validation transfers.

SEARCH SPACE
------------
Connected cubic graphs on n vertices, enumerated in BFS-canonical labelling:
  * vertex 0 is the BFS root;
  * we repeatedly take i = the least vertex of degree < 3 and give it its next
    neighbour j, where j runs in INCREASING order over
        {j : lastnbr(i) < j < nused, deg(j) < 3}   u   {nused}  (a brand-new vertex),
    and a brand-new vertex always takes the next free label.
Every connected cubic graph on n vertices admits such a labelling (label by BFS
discovery order from any root), so the enumeration is COMPLETE.  Isomorphic copies
appear more than once; that costs time, never correctness of a non-existence claim.

BIPARTITE MODE
--------------
With `bipartite=True` each vertex carries its BFS parity (par[new] = 1 - par[i]) and an
edge between two existing vertices is allowed only when their parities differ.  This
enumerates exactly the connected cubic BIPARTITE graphs: in a connected bipartite graph
the 2-colouring is unique up to swapping colours and equals parity-of-BFS-distance from
the root, so every such graph still admits a labelling of the form above, and no
non-bipartite graph can be produced.  Validated against A006823 (1,1,2,5,13,38) and
cross-checked against the general search filtered by networkx.is_bipartite.

PRUNING (all sound)
-------------------
  * the partial graph is a subgraph of every completion, so if it already contains a
    cycle of a forbidden length, the subtree is cut;
  * if undiscovered vertices remain but no open degree slot exists, the subtree is cut.
No other pruning is applied.  In particular NOTHING from the literature is assumed.

PARALLEL SPLIT
--------------
At a fixed depth `split_depth` the k-th node encountered is expanded only by task
k mod ntasks.  Unioned over tasks = the whole tree, with no overlap.
"""

import numpy as np
from numba import njit

MAXST = 256


@njit(cache=True, nogil=True)
def _path_exists(nbr, deg, u, v, k, seen, sv, si):
    """Simple path from u to v with exactly k edges (k >= 1), in the CURRENT graph
    (call BEFORE inserting edge uv, so uv is not available and needs no banning).
    Iterative DFS; max degree 3 so the tree has <= 3*2^(k-1) leaves."""
    if k == 1:
        for t in range(deg[u]):
            if nbr[3 * u + t] == v:
                return True
        return False
    for x in range(seen.shape[0]):
        seen[x] = False
    seen[u] = True
    top = 0
    sv[0] = u
    si[0] = 0
    while top >= 0:
        x = sv[top]
        if si[top] >= deg[x]:
            seen[x] = False
            top -= 1
            continue
        y = nbr[3 * x + si[top]]
        si[top] += 1
        rem = k - top - 1  # edges still needed after stepping to y
        if y == v:
            if rem == 0:
                # unwind
                for t in range(top + 1):
                    seen[sv[t]] = False
                return True
            continue
        if rem == 0:
            continue
        if seen[y]:
            continue
        seen[y] = True
        top += 1
        sv[top] = y
        si[top] = 0
    return False


@njit(cache=True, nogil=True)
def _path_exists_d(nbr, deg, n, u, v, k, seen, sv, si, dist, q):
    """Same as _path_exists but with an extra SOUND prune: precompute BFS distances
    from v, and cut any branch whose current endpoint y satisfies dist[y] > rem,
    since a path of `rem` further edges from y to v cannot then exist.
    (dist[y] <= rem is necessary, not sufficient -- so this only prunes dead branches.)
    """
    if k == 1:
        for t in range(deg[u]):
            if nbr[3 * u + t] == v:
                return True
        return False
    # BFS from v
    for x in range(n):
        dist[x] = 127
    dist[v] = 0
    head = 0
    tail = 0
    q[tail] = v
    tail += 1
    while head < tail:
        x = q[head]
        head += 1
        if dist[x] >= k:
            continue
        for t in range(deg[x]):
            y = nbr[3 * x + t]
            if dist[y] == 127:
                dist[y] = dist[x] + 1
                q[tail] = y
                tail += 1
    if dist[u] > k:
        return False
    for x in range(n):
        seen[x] = False
    seen[u] = True
    top = 0
    sv[0] = u
    si[0] = 0
    while top >= 0:
        x = sv[top]
        if si[top] >= deg[x]:
            seen[x] = False
            top -= 1
            continue
        y = nbr[3 * x + si[top]]
        si[top] += 1
        rem = k - top - 1
        if y == v:
            if rem == 0:
                return True
            continue
        if rem == 0:
            continue
        if seen[y]:
            continue
        if dist[y] > rem:
            continue
        seen[y] = True
        top += 1
        sv[top] = y
        si[top] = 0
    return False


@njit(cache=True, nogil=True)
def _creates_forbidden(nbr, deg, n, i, j, forb, seen, sv, si, dist, q):
    """Would adding edge (i,j) create a cycle of one of the forbidden lengths?

    NOTE: measured -- the BFS distance prune in _path_exists_d never reduced the tree
    (identical node counts) and cost ~25% in speed, because in a small-diameter cubic
    graph dist[y] <= rem is almost always satisfied.  So we use the plain version.
    _path_exists_d is retained only as a cross-check in the tests.
    """
    for t in range(forb.shape[0]):
        L = forb[t]
        if _path_exists(nbr, deg, i, j, L - 1, seen, sv, si):
            return True
    return False


@njit(cache=True, nogil=True)
def search(n, forb, split_depth, taskid, ntasks, node_cap, out_sols, max_sols,
           bipartite=False):
    """Returns (nodes_visited, n_solutions, aborted_flag).

    `forb` = sorted int64 array of forbidden cycle lengths checked INCREMENTALLY.
    Complete graphs surviving those are written to out_sols (flattened adjacency,
    3n int32 per solution) for the caller to test the remaining lengths exactly.
    """
    nbr = np.full(3 * n, -1, np.int32)
    deg = np.zeros(n, np.int32)
    seen = np.zeros(n, np.bool_)
    sv = np.zeros(MAXST, np.int32)
    si = np.zeros(MAXST, np.int32)
    dist = np.zeros(n, np.int8)
    q = np.zeros(n, np.int32)
    par = np.zeros(n, np.int8)      # BFS 2-colouring, only meaningful if bipartite

    st_i = np.zeros(MAXST, np.int32)   # vertex being extended at this depth
    st_j = np.zeros(MAXST, np.int32)   # neighbour chosen at this depth
    st_new = np.zeros(MAXST, np.bool_)  # was j a brand-new vertex?

    nused = 1
    depth = 0
    nodes = 0
    nsol = 0
    split_count = 0
    aborted = 0

    # resume_from < 0  => entering a fresh level; otherwise continue scanning after it
    resume = -1

    while True:
        if resume < 0:
            nodes += 1
            if node_cap > 0 and nodes > node_cap:
                aborted = 1
                break
            # pick i = least vertex with deg < 3
            i = -1
            for v in range(nused):
                if deg[v] < 3:
                    i = v
                    break
            if i == -1:
                if nused == n:
                    if nsol < max_sols:
                        for v in range(n):
                            for t in range(3):
                                out_sols[nsol * 3 * n + 3 * v + t] = nbr[3 * v + t]
                    nsol += 1
                # backtrack
                resume = -2
            else:
                # open-slot prune
                if nused < n:
                    D = 0
                    for v in range(nused):
                        D += 3 - deg[v]
                    if D == 0:
                        resume = -2
                if resume != -2:
                    # split control
                    if depth == split_depth:
                        mine = (split_count % ntasks) == taskid
                        split_count += 1
                        if not mine:
                            resume = -2
                    if resume != -2:
                        st_i[depth] = i
                        # start scanning just after i's largest neighbour that is > i
                        start = i + 1
                        for t in range(deg[i]):
                            w = nbr[3 * i + t]
                            if w > i and w >= start:
                                start = w + 1
                        resume = start - 1

        if resume == -2:
            # unwind one level
            depth -= 1
            if depth < 0:
                break
            i = st_i[depth]
            j = st_j[depth]
            deg[i] -= 1
            deg[j] -= 1
            nbr[3 * i + deg[i]] = -1
            nbr[3 * j + deg[j]] = -1
            if st_new[depth]:
                nused -= 1
            resume = j
            continue

        # scan candidates j > resume
        i = st_i[depth]
        placed = False
        j = resume + 1
        while j <= nused:
            if j == nused:
                if nused >= n:
                    break
                # brand-new vertex: cannot close any cycle
                par[j] = 1 - par[i]
                nbr[3 * i + deg[i]] = j
                deg[i] += 1
                nbr[3 * j + deg[j]] = i
                deg[j] += 1
                st_j[depth] = j
                st_new[depth] = True
                nused += 1
                depth += 1
                placed = True
                break
            if deg[j] < 3 and ((not bipartite) or par[j] != par[i]):
                if not _creates_forbidden(nbr, deg, n, i, j, forb, seen, sv, si, dist, q):
                    nbr[3 * i + deg[i]] = j
                    deg[i] += 1
                    nbr[3 * j + deg[j]] = i
                    deg[j] += 1
                    st_j[depth] = j
                    st_new[depth] = False
                    depth += 1
                    placed = True
                    break
            j += 1
        if placed:
            resume = -1
        else:
            resume = -2

    return nodes, nsol, aborted
