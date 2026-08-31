"""
Exact cycle-length machinery for the Erdos-Gyarfas search.

CORRECTNESS NOTES (read before trusting anything downstream)
-----------------------------------------------------------
All routines here are EXACT and DETERMINISTIC.  No color-coding, no randomisation,
so there is no error probability to bound.

Core primitive: `has_cycle_len(adj, L)`.
  Algorithm: for every vertex s, enumerate simple paths that start at s and use only
  vertices with label > s, of length exactly L-1 edges; report success if the final
  vertex is adjacent to s.
  Completeness: every cycle C of length L has a unique minimum-labelled vertex s, and
  traversing C from s in either direction gives such a path.  So the enumeration sees
  every L-cycle.  Soundness: any path found is a simple path v0=s, v1, ..., v_{L-1}
  with all v_i distinct and v_{L-1}v_0 an edge, i.e. a genuine L-cycle.
  Complexity: O(n * Dmax * (Dmax-1)^(L-2)).  For subcubic graphs that is O(n * 3*2^(L-2)).

For L equal to the number of vertices this degenerates to Hamiltonicity, so a separate
pruned routine `has_hamiltonian_cycle` is provided; it is still exact (plain DFS with
sound prunings only).

`cycle_spectrum_bruteforce` enumerates EVERY cycle (exponential) and is used only to
validate the fast routines on small graphs.
"""

from itertools import combinations

# ---------------------------------------------------------------------------
# Graph representation: adj = list of sorted lists (or tuples) of neighbours,
# vertices labelled 0..n-1, simple undirected graph.
# ---------------------------------------------------------------------------


def adj_from_edges(n, edges):
    adj = [[] for _ in range(n)]
    for u, v in edges:
        assert u != v, "no loops"
        assert v not in adj[u], "no multi-edges"
        adj[u].append(v)
        adj[v].append(u)
    return [sorted(a) for a in adj]


def edges_from_adj(adj):
    return [(u, v) for u in range(len(adj)) for v in adj[u] if u < v]


# ---------------------------------------------------------------------------
# 1. Brute-force full cycle spectrum (ground truth for tests)
# ---------------------------------------------------------------------------


def cycle_spectrum_bruteforce(adj):
    """Return the set of lengths of all simple cycles.  Exponential; small graphs only.

    Each cycle is found from its minimum-labelled vertex s.  We walk simple paths
    s = v0, v1, ..., vk using only vertices > s, and whenever v_k is adjacent to s and
    k >= 2 we have a cycle of length k+1.
    """
    n = len(adj)
    lengths = set()

    for s in range(n):
        # iterative DFS over simple paths rooted at s using vertices > s
        stack = [(s, [s], {s})]
        while stack:
            v, path, seen = stack.pop()
            for w in adj[v]:
                if w == s and len(path) >= 3:
                    lengths.add(len(path))
                elif w > s and w not in seen:
                    stack.append((w, path + [w], seen | {w}))
    return lengths


# ---------------------------------------------------------------------------
# 2. Exact "is there a cycle of length exactly L" (fast path)
# ---------------------------------------------------------------------------


def has_cycle_len(adj, L):
    """Exact test for a simple cycle of length exactly L.  L >= 3."""
    n = len(adj)
    if L < 3 or L > n:
        return False
    if L == 3:
        for u in range(n):
            for v in adj[u]:
                if v > u:
                    su = set(adj[u])
                    for w in adj[v]:
                        if w > v and w in su:
                            return True
        return False
    if L == 4:
        # C4 <=> some pair of distinct vertices has two common neighbours
        for u in range(n):
            su = set(adj[u])
            for v in range(u + 1, n):
                c = 0
                for w in adj[v]:
                    if w in su:
                        c += 1
                        if c >= 2:
                            return True
        return False

    seen = [False] * n
    adjset = [set(a) for a in adj]

    def dfs(v, s, depth):
        """v = current end of a simple path from s of `depth` edges, all vertices > s
        except s itself.  Return True if it extends to an L-cycle through s."""
        if depth == L - 1:
            return s in adjset[v]
        for w in adj[v]:
            if w > s and not seen[w]:
                seen[w] = True
                if dfs(w, s, depth + 1):
                    seen[w] = False
                    return True
                seen[w] = False
        return False

    for s in range(n):
        seen[s] = True
        if dfs(s, s, 0):
            return True
        seen[s] = False
    return False


def has_hamiltonian_cycle(adj):
    """Exact Hamiltonicity test.  Plain DFS with two sound prunings.

    Prunings used (both are implications of Hamiltonicity, so no solutions are lost):
      P1: every not-yet-visited vertex must retain >= 2 usable incidences
          (usable = to another unvisited vertex, or to the current path end, or to
           the start vertex);
      P2: the unvisited vertices together with the current endpoint must be connected.
    """
    n = len(adj)
    if n < 3:
        return False
    start = 0
    visited = [False] * n
    visited[start] = True

    adjset = [set(a) for a in adj]

    def usable_deg(v, cur):
        """Number of incidences at an UNVISITED vertex v that could still be used.

        Write the completed cycle as start = p0, p1, ..., p_{n-1}, start, with
        p0..p_{cnt-1} the currently visited prefix and cur = p_{cnt-1}.  An unvisited
        v equals p_j for some j >= cnt, and its two cycle-neighbours are p_{j-1} and
        p_{j+1 mod n}.  p_{j-1} is unvisited unless j == cnt (then it is cur);
        p_{j+1 mod n} is unvisited unless j == n-1 (then it is start).  So the only
        visited vertices v may still attach to are `cur` and `start`.
        """
        d = 0
        for w in adj[v]:
            if (not visited[w]) or w == cur or w == start:
                d += 1
        return d

    def connected_ok(cur):
        # BFS over unvisited vertices starting from any unvisited neighbour of cur
        un = [v for v in range(n) if not visited[v]]
        if not un:
            return True
        seeds = [w for w in adj[cur] if not visited[w]]
        if not seeds:
            return False
        stack = [seeds[0]]
        seen = {seeds[0]}
        while stack:
            v = stack.pop()
            for w in adj[v]:
                if not visited[w] and w not in seen:
                    seen.add(w)
                    stack.append(w)
        return len(seen) == len(un)

    def dfs(cur, cnt):
        if cnt == n:
            return start in adjset[cur]
        # prunings
        for v in range(n):
            if not visited[v] and usable_deg(v, cur) < 2:
                return False
        if not connected_ok(cur):
            return False
        for w in adj[cur]:
            if not visited[w]:
                visited[w] = True
                if dfs(w, cnt + 1):
                    visited[w] = False
                    return True
                visited[w] = False
        return False

    return dfs(start, 1)


# ---------------------------------------------------------------------------
# 3. The conjecture predicate
# ---------------------------------------------------------------------------


def pow2_lengths_upto(n):
    """Cycle lengths that are powers of 2 and could fit in an n-vertex simple graph."""
    out = []
    L = 4
    while L <= n:
        out.append(L)
        L *= 2
    return out


def has_pow2_cycle(adj):
    """True iff the graph has a cycle whose length is a power of 2."""
    n = len(adj)
    for L in pow2_lengths_upto(n):
        if L == n:
            if has_hamiltonian_cycle(adj):
                return True
        elif has_cycle_len(adj, L):
            return True
    return False


def min_degree(adj):
    return min((len(a) for a in adj), default=0)


def is_counterexample(adj):
    return min_degree(adj) >= 3 and not has_pow2_cycle(adj)
