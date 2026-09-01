"""Core kernels for the Erdos-Sos counterexample search.

Containment test = complete depth-first backtracking search for an injective
homomorphism (= subgraph embedding) of a tree T into a graph G, with

  * degree pruning   (tree vertex of degree d needs a host of G-degree >= d)
  * free-neighbour pruning (host must retain >= #children free neighbours)
  * a node cap so the caller can distinguish "proved absent" from "gave up".

Return status:
   1  embedding FOUND      (f[] holds it; T is a subgraph of G)
   0  search EXHAUSTED     (proof that T is NOT a subgraph of G)
  -1  node cap hit         (undecided)

Everything is exact integer/bitmask arithmetic.  No floating point, no
randomised approximation, in any decision path.
"""
import numpy as np
from numba import njit

MAXN = 32


# --------------------------------------------------------------- tree order
def tree_search_order(m, edges):
    """Return (order, parent_pos, tdeg, childcnt) for backtracking.

    Vertices are emitted parent-before-child; among available vertices we
    always take the one of largest degree in T (strongest pruning first).
    Root = a maximum-degree vertex.
    """
    adj = [[] for _ in range(m)]
    for u, v in edges:
        adj[u].append(v)
        adj[v].append(u)
    deg = [len(adj[v]) for v in range(m)]
    root = max(range(m), key=lambda v: deg[v])
    order = [root]
    pos = {root: 0}
    parent_pos = [-1]
    frontier = list(adj[root])
    par_of = {w: root for w in adj[root]}
    while frontier:
        w = max(frontier, key=lambda x: deg[x])
        frontier.remove(w)
        pos[w] = len(order)
        parent_pos.append(pos[par_of[w]])
        order.append(w)
        for z in adj[w]:
            if z not in pos and z not in par_of:
                par_of[z] = w
                frontier.append(z)
    assert len(order) == m
    tdeg = [deg[v] for v in order]
    childcnt = [0] * m
    for i in range(1, m):
        childcnt[parent_pos[i]] += 1
    return (np.array(order, np.int32), np.array(parent_pos, np.int32),
            np.array(tdeg, np.int32), np.array(childcnt, np.int32))


def pack_trees(tree_records):
    """Pack a list of tree JSON records into flat numpy arrays."""
    k = len(tree_records)
    m = tree_records[0]["n_vertices"]
    PAR = np.zeros((k, m), np.int32)
    TDEG = np.zeros((k, m), np.int32)
    CHILD = np.zeros((k, m), np.int32)
    for i, r in enumerate(tree_records):
        assert r["n_vertices"] == m
        _, par, td, cc = tree_search_order(m, [tuple(e) for e in r["edges"]])
        PAR[i], TDEG[i], CHILD[i] = par, td, cc
    return PAR, TDEG, CHILD


# --------------------------------------------------------------- kernels
@njit(cache=True, inline="always")
def _popcount(x):
    c = 0
    while x:
        x &= x - 1
        c += 1
    return c


@njit(cache=True)
def embed_tree(nbr, n, par, tdeg, child, t, node_cap, f, cand):
    """Complete backtracking.  nbr[v] = neighbour bitmask of v in G.

    Returns (status, nodes).  On status==1, f[0:t] is the embedding:
    tree vertex i (in search order) -> graph vertex f[i].
    """
    # allowed[i]: graph vertices whose degree is at least tdeg[i]
    full = (np.int64(1) << n) - 1
    allowed = np.zeros(t, np.int64)
    for i in range(t):
        m = np.int64(0)
        for v in range(n):
            if _popcount(nbr[v]) >= tdeg[i]:
                m |= np.int64(1) << v
        allowed[i] = m
        if m == 0:
            return 0, 0                      # no host possible: not contained

    nodes = 0
    used = np.int64(0)
    cand[0] = allowed[0]
    i = 0
    while i >= 0:
        c = cand[i]
        if c == 0:
            i -= 1
            if i >= 0:
                used &= ~(np.int64(1) << f[i])
            continue
        b = c & (-c)                          # lowest set bit
        cand[i] = c ^ b
        v = 0
        bb = b
        while bb > 1:
            bb >>= 1
            v += 1
        nodes += 1
        if node_cap > 0 and nodes > node_cap:
            return -1, nodes
        # free-neighbour prune
        nu = used | b
        if _popcount(nbr[v] & ~nu & full) < child[i]:
            continue
        f[i] = v
        used = nu
        if i == t - 1:
            return 1, nodes
        i += 1
        cand[i] = nbr[f[par[i]]] & allowed[i] & ~used & full
    return 0, nodes


@njit(cache=True)
def score_graph(nbr, n, PAR, TDEG, CHILD, t, ntrees, node_cap,
                out_status, out_nodes, f, cand):
    """Test every tree.  Returns (n_missing, n_undecided, difficulty_sum)."""
    miss = 0
    undec = 0
    diff = 0
    for j in range(ntrees):
        st, nd = embed_tree(nbr, n, PAR[j], TDEG[j], CHILD[j], t,
                            node_cap, f, cand)
        out_status[j] = st
        out_nodes[j] = nd
        if st == 0:
            miss += 1
        elif st == -1:
            undec += 1
        diff += nd
    return miss, undec, diff


@njit(cache=True)
def count_embeddings(nbr, n, par, tdeg, child, t, count_cap, node_cap,
                     f, cand):
    """Exact number of embeddings of T in G, capped at count_cap.

    Returns (count, nodes, status):
      status 0  search exhausted, count is EXACT
      status -2 count_cap reached (count == count_cap)
      status -1 node_cap hit, count is a lower bound
    count == 0 with status 0 is a proof that T is not a subgraph of G.
    """
    full = (np.int64(1) << n) - 1
    allowed = np.zeros(t, np.int64)
    for i in range(t):
        m = np.int64(0)
        for v in range(n):
            if _popcount(nbr[v]) >= tdeg[i]:
                m |= np.int64(1) << v
        allowed[i] = m
        if m == 0:
            return 0, 0, 0
    nodes = 0
    count = 0
    used = np.int64(0)
    cand[0] = allowed[0]
    i = 0
    while i >= 0:
        c = cand[i]
        if c == 0:
            i -= 1
            if i >= 0:
                used &= ~(np.int64(1) << f[i])
            continue
        b = c & (-c)
        cand[i] = c ^ b
        v = 0
        bb = b
        while bb > 1:
            bb >>= 1
            v += 1
        nodes += 1
        if node_cap > 0 and nodes > node_cap:
            return count, nodes, -1
        nu = used | b
        if i == t - 1:
            count += 1
            if count >= count_cap:
                return count, nodes, -2
            continue
        if _popcount(nbr[v] & ~nu & full) < child[i]:
            continue
        f[i] = v
        used = nu
        i += 1
        cand[i] = nbr[f[par[i]]] & allowed[i] & ~used & full
    return count, nodes, 0


@njit(cache=True)
def knuth_estimate(nbr, n, par, tdeg, t, trials, rng, f):
    """Knuth's unbiased backtrack-tree estimator for the NUMBER of embeddings
    of T in G.  Each trial walks one random root-to-leaf path, multiplying the
    number of choices available at each level; the mean over trials is an
    unbiased estimate of the number of embeddings.  Wide dynamic range, so it
    gives the annealer a gradient even where embeddings are abundant.
    Returns (mean_estimate, n_dead_ends, new_rng_state)."""
    full = (np.int64(1) << n) - 1
    allowed = np.zeros(t, np.int64)
    for i in range(t):
        m = np.int64(0)
        for v in range(n):
            if _popcount(nbr[v]) >= tdeg[i]:
                m |= np.int64(1) << v
        allowed[i] = m
    tot = 0.0
    dead = 0
    for _ in range(trials):
        used = np.int64(0)
        prod = 1.0
        ok = True
        for i in range(t):
            if i == 0:
                c = allowed[0]
            else:
                c = nbr[f[par[i]]] & allowed[i] & ~used & full
            k = _popcount(c)
            if k == 0:
                ok = False
                break
            prod *= k
            rng = _xs(rng)
            pick = np.int64(rng % np.uint64(k))
            v = -1
            cc = c
            for _j in range(pick + 1):
                b = cc & (-cc)
                cc ^= b
                v = 0
                bb = b
                while bb > 1:
                    bb >>= 1
                    v += 1
            f[i] = v
            used |= np.int64(1) << v
        if ok:
            tot += prod
        else:
            dead += 1
    return tot / trials, dead, rng



@njit(cache=True)
def hom_log2(nbr, n, par, t, val):
    """log2 of the number of HOMOMORPHISMS of T into G (not injective).

    Exact tree DP, fully deterministic: no randomness, so the annealer sees a
    noise-free landscape.  It is a smooth surrogate for the number of
    embeddings with a huge dynamic range, which is what the long-range part of
    the search needs; the exact backtracking test still decides containment.
    """
    for i in range(t):
        for v in range(n):
            val[i, v] = 1.0
    for i in range(t - 1, 0, -1):
        p = par[i]
        for v in range(n):
            acc = 0.0
            m = nbr[v]
            while m:
                b = m & (-m)
                m ^= b
                w = 0
                bb = b
                while bb > 1:
                    bb >>= 1
                    w += 1
                acc += val[i, w]
            val[p, v] *= acc
    tot = 0.0
    for v in range(n):
        tot += val[0, v]
    return np.log2(1.0 + tot)


@njit(cache=True)
def _xs(state):
    state ^= (state << np.uint64(13)) & np.uint64(0xFFFFFFFFFFFFFFFF)
    state ^= state >> np.uint64(7)
    state ^= (state << np.uint64(17)) & np.uint64(0xFFFFFFFFFFFFFFFF)
    return state


@njit(cache=True)
def anneal(nbr0, n, PAR, TDEG, CHILD, t, ntrees, node_cap,
           n_steps, seed, T0, T1, mindeg_pen, best_nbr):
    """Simulated annealing over graphs with a FIXED edge count.

    Move = remove one existing edge, insert one non-edge (edge count fixed).
    Objective (maximised):
        1e9 * (#trees proved absent)
      + 1e5 * (#trees undecided at the node cap)
      + total backtracking nodes needed to embed the rest   (scarcity proxy)
      + mindeg_pen * max(0, 6 - min_degree)                  (steering, see
        Eaton-Tiner: delta(G) >= t-4 forces every tree of order t)
    Returns (best_score, best_miss, best_undec, steps_done).
    """
    full = (np.int64(1) << n) - 1
    nbr = nbr0.copy()
    st = np.zeros(ntrees, np.int64)
    nd = np.zeros(ntrees, np.int64)
    f = np.zeros(t, np.int64)
    cand = np.zeros(t + 1, np.int64)
    rng = np.uint64(seed * np.uint64(2654435761) + np.uint64(12345))
    if rng == np.uint64(0):
        rng = np.uint64(88172645463325252)

    def _sc(nb):
        miss, undec, diff = score_graph(nb, n, PAR, TDEG, CHILD, t, ntrees,
                                        node_cap, st, nd, f, cand)
        md = n
        for vv in range(n):
            dd = _popcount(nb[vv])
            if dd < md:
                md = dd
        bonus = 0
        if md < t - 4:
            bonus = mindeg_pen * (t - 4 - md)
        return (miss * 1000000000 + undec * 100000 + diff + bonus,
                miss, undec)

    cur, cmiss, cundec = _sc(nbr)
    best = cur
    bmiss = cmiss
    bundec = cundec
    for v in range(n):
        best_nbr[v] = nbr[v]

    for step in range(n_steps):
        frac = step / n_steps
        temp = T0 * (T1 / T0) ** frac
        # pick a random existing edge
        while True:
            rng = _xs(rng)
            u = np.int64(rng % np.uint64(n))
            rng = _xs(rng)
            v = np.int64(rng % np.uint64(n))
            if u != v and (nbr[u] >> v) & 1:
                break
        # pick a random non-edge
        while True:
            rng = _xs(rng)
            x = np.int64(rng % np.uint64(n))
            rng = _xs(rng)
            y = np.int64(rng % np.uint64(n))
            if x != y and not ((nbr[x] >> y) & 1):
                break
        nbr[u] &= ~(np.int64(1) << v)
        nbr[v] &= ~(np.int64(1) << u)
        nbr[x] |= np.int64(1) << y
        nbr[y] |= np.int64(1) << x
        new, nmiss, nundec = _sc(nbr)
        d = new - cur
        accept = False
        if d >= 0:
            accept = True
        else:
            rng = _xs(rng)
            r = (rng >> np.uint64(11)) * (1.0 / 9007199254740992.0)
            if r < np.exp(d / temp):
                accept = True
        if accept:
            cur = new
            cmiss = nmiss
            cundec = nundec
            if new > best:
                best = new
                bmiss = nmiss
                bundec = nundec
                for w in range(n):
                    best_nbr[w] = nbr[w]
        else:
            nbr[x] &= ~(np.int64(1) << y)
            nbr[y] &= ~(np.int64(1) << x)
            nbr[u] |= np.int64(1) << v
            nbr[v] |= np.int64(1) << u
    return best, bmiss, bundec, n_steps


@njit(cache=True)
def anneal2(nbr0, n, PAR, TDEG, CHILD, t, ntrees, node_cap, count_cap,
            n_steps, seed, T0, T1, mindeg_pen, trials, best_nbr):
    """Annealing with a scarcity objective that has a gradient everywhere.

    For each target tree T:
        est   = Knuth estimate of the number of embeddings of T in G
        cnt   = exact number of embeddings, capped (only computed when the
                estimate is already small, so it is cheap)
    Maximised objective:
        1e15 * (#trees PROVED absent)
      + 1e11 * (#trees whose exact count could not be finished)
      + sum over T of  1e6 * max(0, 50 - log2(1+est))     <- long-range
      + sum over T of  1e6 * max(0, 22 - log2(1+cnt))     <- short-range
      + mindeg bonus  (Eaton-Tiner: delta >= t-4 forces containment)
    Returns (best_score, best_missing, best_undecided).
    """
    nbr = nbr0.copy()
    f = np.zeros(t, np.int64)
    cand = np.zeros(t + 1, np.int64)
    rng = np.uint64(seed) * np.uint64(2654435761) + np.uint64(12345)
    if rng == np.uint64(0):
        rng = np.uint64(88172645463325252)

    cur = -1.0e30
    best = -1.0e30
    bmiss = 0
    bundec = 0
    first = True
    for step in range(n_steps + 1):
        if not first:
            frac = step / n_steps
            temp = T0 * (T1 / T0) ** frac
            while True:
                rng = _xs(rng)
                u = np.int64(rng % np.uint64(n))
                rng = _xs(rng)
                v = np.int64(rng % np.uint64(n))
                if u != v and (nbr[u] >> v) & 1:
                    break
            while True:
                rng = _xs(rng)
                x = np.int64(rng % np.uint64(n))
                rng = _xs(rng)
                y = np.int64(rng % np.uint64(n))
                if x != y and not ((nbr[x] >> y) & 1):
                    break
            nbr[u] &= ~(np.int64(1) << v)
            nbr[v] &= ~(np.int64(1) << u)
            nbr[x] |= np.int64(1) << y
            nbr[y] |= np.int64(1) << x

        sc = 0.0
        miss = 0
        undec = 0
        for j in range(ntrees):
            est, dead, rng = knuth_estimate(nbr, n, PAR[j], TDEG[j], t,
                                            trials, rng, f)
            le = np.log2(1.0 + est)
            if le < 50.0:
                sc += 1.0e6 * (50.0 - le)
            # est > 0 already PROVES containment (a Knuth trial that does not
            # dead-end has walked a genuine embedding), so the exact count is
            # only run in the scarce regime, where it is also cheap.
            if est < 2000.0:
                cnt, nd, stt = count_embeddings(nbr, n, PAR[j], TDEG[j],
                                                CHILD[j], t, count_cap,
                                                node_cap, f, cand)
                if stt == 0 and cnt == 0:
                    miss += 1
                elif stt == -1:
                    undec += 1
                lc = np.log2(1.0 + cnt)
                if lc < 22.0:
                    sc += 1.0e6 * (22.0 - lc)
        md = n
        for vv in range(n):
            dd = _popcount(nbr[vv])
            if dd < md:
                md = dd
        # Eaton-Tiner: delta(G) >= t-4 forces every tree of order t, so any
        # counterexample has delta <= t-5.  Flat reward for being in that
        # region (not a gradient toward delta=0, which would just thin G).
        if md <= t - 5:
            sc += mindeg_pen
        sc += miss * 1.0e15 + undec * 1.0e11

        if first:
            cur = sc
            best = sc
            bmiss = miss
            bundec = undec
            for w in range(n):
                best_nbr[w] = nbr[w]
            first = False
            continue

        d = sc - cur
        accept = False
        if d >= 0:
            accept = True
        else:
            rng = _xs(rng)
            r = (rng >> np.uint64(11)) * (1.0 / 9007199254740992.0)
            if r < np.exp(d / temp):
                accept = True
        if accept:
            cur = sc
            if sc > best:
                best = sc
                bmiss = miss
                bundec = undec
                for w in range(n):
                    best_nbr[w] = nbr[w]
        else:
            nbr[x] &= ~(np.int64(1) << y)
            nbr[y] &= ~(np.int64(1) << x)
            nbr[u] |= np.int64(1) << v
            nbr[v] |= np.int64(1) << u
    return best, bmiss, bundec



@njit(cache=True)
def anneal3(nbr0, n, PAR, TDEG, CHILD, t, ntrees, node_cap, count_cap,
            n_steps, seed, T0, T1, mindeg_pen, best_nbr):
    """Deterministic-objective annealing (see hom_log2).

    Maximised objective:
        1e15 * (#target trees PROVED absent)
      + 1e11 * (#target trees undecided at the node cap)
      + 1e6  * sum over targets of (60 - log2(1+hom(T,G)))   <- smooth, exact
      + 1e2  * sum over targets of (backtracking nodes to find one embedding)
      + mindeg_pen if delta(G) <= t-5   (Eaton-Tiner region)
    """
    nbr = nbr0.copy()
    f = np.zeros(t, np.int64)
    cand = np.zeros(t + 1, np.int64)
    val = np.zeros((t, n), np.float64)
    rng = np.uint64(seed) * np.uint64(2654435761) + np.uint64(12345)
    if rng == np.uint64(0):
        rng = np.uint64(88172645463325252)
    cur = -1.0e30
    best = -1.0e30
    bmiss = 0
    bundec = 0
    u = np.int64(0); v = np.int64(0); x = np.int64(0); y = np.int64(0)
    for step in range(n_steps + 1):
        if step > 0:
            frac = step / n_steps
            temp = T0 * (T1 / T0) ** frac
            while True:
                rng = _xs(rng)
                u = np.int64(rng % np.uint64(n))
                rng = _xs(rng)
                v = np.int64(rng % np.uint64(n))
                if u != v and (nbr[u] >> v) & 1:
                    break
            while True:
                rng = _xs(rng)
                x = np.int64(rng % np.uint64(n))
                rng = _xs(rng)
                y = np.int64(rng % np.uint64(n))
                if x != y and not ((nbr[x] >> y) & 1):
                    break
            nbr[u] &= ~(np.int64(1) << v)
            nbr[v] &= ~(np.int64(1) << u)
            nbr[x] |= np.int64(1) << y
            nbr[y] |= np.int64(1) << x

        sc = 0.0
        miss = 0
        undec = 0
        for j in range(ntrees):
            lh = hom_log2(nbr, n, PAR[j], t, val)
            if lh < 60.0:
                sc += 1.0e6 * (60.0 - lh)
            st, nd = embed_tree(nbr, n, PAR[j], TDEG[j], CHILD[j], t,
                                node_cap, f, cand)
            if st == 0:
                miss += 1
            elif st == -1:
                undec += 1
            sc += 1.0e2 * nd
        md = n
        for vv in range(n):
            dd = _popcount(nbr[vv])
            if dd < md:
                md = dd
        if md <= t - 5:
            sc += mindeg_pen
        sc += miss * 1.0e15 + undec * 1.0e11

        if step == 0:
            cur = sc
            best = sc
            bmiss = miss
            bundec = undec
            for w in range(n):
                best_nbr[w] = nbr[w]
            continue
        d = sc - cur
        accept = False
        if d >= 0:
            accept = True
        else:
            rng = _xs(rng)
            r = (rng >> np.uint64(11)) * (1.0 / 9007199254740992.0)
            if r < np.exp(d / temp):
                accept = True
        if accept:
            cur = sc
            if sc > best:
                best = sc
                bmiss = miss
                bundec = undec
                for w in range(n):
                    best_nbr[w] = nbr[w]
        else:
            nbr[x] &= ~(np.int64(1) << y)
            nbr[y] &= ~(np.int64(1) << x)
            nbr[u] |= np.int64(1) << v
            nbr[v] |= np.int64(1) << u
    return best, bmiss, bundec


# --------------------------------------------------------------- helpers
def nbr_from_edges(n, edges):
    nbr = np.zeros(n, np.int64)
    for u, v in edges:
        nbr[u] |= np.int64(1) << v
        nbr[v] |= np.int64(1) << u
    return nbr


def edges_from_nbr(n, nbr):
    return [(u, v) for u in range(n) for v in range(u + 1, n)
            if (int(nbr[u]) >> v) & 1]


def threshold_edges(n, t):
    """Erdos-Sos threshold for graph order n and TREE ORDER t (t vertices,
    t-1 edges).  Conjecture: e(G) > n(t-2)/2  ==>  every tree of order t
    embeds.  Smallest integer edge count at or above that is
    floor(n(t-2)/2) + 1."""
    return (n * (t - 2)) // 2 + 1
