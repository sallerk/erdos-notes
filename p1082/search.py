"""Exact branch-and-bound for maximum few-distance sets over a lattice pool.

Computes, over a chosen finite pool of lattice points:

    G_pool(k)  = max |S|,  S subset of pool, |dist(S)| <= k
    H_pool(k)  = max |S|,  S subset of pool, |dist(S)| <= k, no 3 of S collinear

All arithmetic is integer.  Squared distances are integers; collinearity is the
vanishing of an integer 3x3 determinant.

Pool convention
---------------
The pool is a ball of squared radius D about the origin, and the origin is
FORCED into S.  Every point of a set of squared diameter <= D lies within
squared distance D of every other point of the set, so after translating one
of its points to the origin the whole set lies in that ball.  The search is
therefore complete for all lattice sets of squared diameter <= D, up to
translation.  Pairs at squared distance > D are never both selected.
"""

import numpy as np
from numba import njit

from geo import D2, cross

# ---------------------------------------------------------------- popcount
POP16 = np.array([bin(i).count('1') for i in range(1 << 16)], dtype=np.uint8)


@njit(cache=False, inline="always")
def _pc(x, POP16):
    return (np.int64(POP16[np.int64(x & np.uint64(0xFFFF))])
            + np.int64(POP16[np.int64((x >> np.uint64(16)) & np.uint64(0xFFFF))])
            + np.int64(POP16[np.int64((x >> np.uint64(32)) & np.uint64(0xFFFF))])
            + np.int64(POP16[np.int64((x >> np.uint64(48)) & np.uint64(0xFFFF))]))


@njit(cache=False, parallel=False)
def _build_coll(P, collmask):
    """collmask[i,j] = bitset of pool points collinear with the pair (i,j).

    Exact: the 2x2 integer determinant (b-a) x (c-a) vanishes iff a,b,c are
    collinear.  The lattice basis map is linear and invertible, so this test is
    valid in the plane for both Z2 and A2 coordinates.
    """
    m = P.shape[0]
    for i in range(m):
        for j in range(i + 1, m):
            bx = P[j, 0] - P[i, 0]
            by = P[j, 1] - P[i, 1]
            for t in range(m):
                if t == i or t == j:
                    continue
                cx = P[t, 0] - P[i, 0]
                cy = P[t, 1] - P[i, 1]
                if bx * cy - by * cx == 0:
                    w = t >> 6
                    bit = np.uint64(1) << np.uint64(t & 63)
                    collmask[i, j, w] |= bit
                    collmask[j, i, w] |= bit


# ---------------------------------------------------------------- pool build
def build_pool(D, basis='A2'):
    """All lattice points p with |p|^2 <= D, origin first."""
    f = D2[basis]
    R = int(D ** 0.5) + 2
    pts = []
    for x in range(-2 * R, 2 * R + 1):
        for y in range(-2 * R, 2 * R + 1):
            if f((x, y), (0, 0)) <= D:
                pts.append((x, y))
    pts.sort(key=lambda p: (f(p, (0, 0)), p))
    assert pts[0] == (0, 0)
    return pts


def prepare(pts, D, basis='A2', with_collinear=False):
    """Build the integer tables the kernel needs."""
    f = D2[basis]
    m = len(pts)
    d2 = np.zeros((m, m), dtype=np.int64)
    for i in range(m):
        for j in range(m):
            d2[i, j] = f(pts[i], pts[j])

    vals = sorted({int(d2[i, j]) for i in range(m) for j in range(i + 1, m)
                   if d2[i, j] <= D})
    vid = {v: t for t, v in enumerate(vals)}
    V = len(vals)
    DW = (V + 63) // 64
    MW = (m + 63) // 64

    # dmask[i,j] : bit of the distance value of pair (i,j); adj[i,j] : usable pair
    dmask = np.zeros((m, m, DW), dtype=np.uint64)
    adj = np.zeros((m, m), dtype=np.uint8)
    for i in range(m):
        for j in range(m):
            if i == j:
                continue
            v = int(d2[i, j])
            if v <= D:
                adj[i, j] = 1
                t = vid[v]
                dmask[i, j, t >> 6] |= np.uint64(1) << np.uint64(t & 63)

    collmask = np.zeros((m, m, MW), dtype=np.uint64) if with_collinear else \
        np.zeros((1, 1, 1), dtype=np.uint64)
    if with_collinear:
        P = np.array(pts, dtype=np.int64)
        _build_coll(P, collmask)
    return dict(m=m, V=V, DW=DW, MW=MW, vals=np.array(vals, dtype=np.int64),
                dmask=dmask, adj=adj, collmask=collmask, d2=d2)


# ---------------------------------------------------------------- kernel
@njit(cache=False)
def _dfs(k, target, m, DW, MW, dmask, adj, collmask, use_coll, POP16,
         S, cand, cmask, fbd,
         curmask, forb, depth, best, bestset, stop_at_target, count_all,
         found_store, found_n, max_store):
    """Iterative-free recursive DFS.  Returns updated best."""
    nc = cand[depth, 0]  # number of candidates stored in cand[depth,1:]

    if depth > best[0]:
        best[0] = depth
        for i in range(depth):
            bestset[i] = S[i]
    if count_all and depth == target:
        if found_n[0] < max_store:
            for i in range(depth):
                found_store[found_n[0], i] = S[i]
        found_n[0] += 1
        return best[0]
    if stop_at_target and best[0] >= target:
        return best[0]
    if depth + nc <= best[0] and not count_all:
        return best[0]
    if count_all and depth + nc < target:
        return best[0]

    for t in range(nc):
        if not count_all and depth + (nc - t) <= best[0]:
            break
        if count_all and depth + (nc - t) < target:
            break
        c = cand[depth, 1 + t]

        # new distance mask
        for w in range(DW):
            curmask[depth + 1, w] = curmask[depth, w] | cmask[depth, t, w]
        nd = 0
        for w in range(DW):
            nd += _pc(curmask[depth + 1, w], POP16)
        if nd > k:
            continue

        # new forbidden (collinear) mask
        if use_coll:
            bad = False
            for w in range(MW):
                forb[depth + 1, w] = forb[depth, w] | fbd[depth, t, w]
            wi = c >> 6
            if (forb[depth, wi] >> np.uint64(c & 63)) & np.uint64(1):
                bad = True
            if bad:
                continue

        S[depth] = c
        # build child candidate list from cand[depth, 1+t+1 : ]
        cnt = 0
        for u in range(t + 1, nc):
            x = cand[depth, 1 + u]
            if adj[x, c] == 0:
                continue
            if use_coll:
                if (forb[depth + 1, x >> 6] >> np.uint64(x & 63)) & np.uint64(1):
                    continue
            ok = True
            acc = 0
            for w in range(DW):
                v = curmask[depth + 1, w] | cmask[depth, u, w] | dmask[x, c, w]
                cmask[depth + 1, cnt, w] = v
                acc += _pc(v, POP16)
            if acc > k:
                ok = False
            if not ok:
                continue
            if use_coll:
                for w in range(MW):
                    fbd[depth + 1, cnt, w] = fbd[depth, u, w] | collmask[x, c, w]
            cand[depth + 1, 1 + cnt] = x
            cnt += 1
        cand[depth + 1, 0] = cnt

        best[0] = _dfs(k, target, m, DW, MW, dmask, adj, collmask, use_coll,
                       POP16, S, cand, cmask, fbd, curmask, forb, depth + 1,
                       best, bestset, stop_at_target, count_all,
                       found_store, found_n, max_store)
        if stop_at_target and best[0] >= target and not count_all:
            return best[0]
    return best[0]


def run(tab, k, target=99, with_collinear=False, stop_at_target=False,
        count_all=False, max_store=20000, maxlevels=None):
    """Search the prepared pool.  Returns (best_size, best_set_indices, found)."""
    m, DW, MW = tab['m'], tab['DW'], tab['MW']
    L = (maxlevels or min(m, 40)) + 2
    S = np.zeros(L, dtype=np.int32)
    cand = np.zeros((L, m + 1), dtype=np.int32)
    cmask = np.zeros((L, m, DW), dtype=np.uint64)
    fbd = np.zeros((L, m, MW), dtype=np.uint64) if with_collinear else \
        np.zeros((L, 1, 1), dtype=np.uint64)
    curmask = np.zeros((L, DW), dtype=np.uint64)
    forb = np.zeros((L, MW), dtype=np.uint64)
    best = np.zeros(1, dtype=np.int64)
    bestset = np.zeros(L, dtype=np.int32)
    found_store = np.zeros((max_store if count_all else 1, L), dtype=np.int32)
    found_n = np.zeros(1, dtype=np.int64)

    # The origin (pool index 0) is forced into S by _dfs_entry.  Any lattice set
    # of squared diameter <= D is a translate of one containing the origin, so
    # this loses nothing.
    _dfs_entry(k, target, m, DW, MW, tab['dmask'], tab['adj'],
                     tab['collmask'], with_collinear, POP16, S, cand, cmask,
                     fbd, curmask, forb, best, bestset, stop_at_target,
                     count_all, found_store, found_n, max_store)
    nf = int(found_n[0])
    found = found_store[:min(nf, max_store), :].copy() if count_all else None
    return int(best[0]), bestset[:int(best[0])].copy(), found, nf


@njit(cache=False)
def _dfs_entry(k, target, m, DW, MW, dmask, adj, collmask, use_coll, POP16,
               S, cand, cmask, fbd, curmask, forb, best, bestset,
               stop_at_target, count_all, found_store, found_n, max_store):
    """Pick the origin (index 0) at level 0, then recurse."""
    c = 0
    S[0] = 0
    for w in range(DW):
        curmask[1, w] = 0
    for w in range(MW):
        forb[1, w] = 0
    cnt = 0
    for x in range(1, m):
        if adj[x, 0] == 0:
            continue
        for w in range(DW):
            cmask[1, cnt, w] = dmask[x, 0, w]
        if use_coll:
            for w in range(MW):
                fbd[1, cnt, w] = collmask[x, 0, w]
        cand[1, 1 + cnt] = x
        cnt += 1
    cand[1, 0] = cnt
    return _dfs(k, target, m, DW, MW, dmask, adj, collmask, use_coll, POP16,
                S, cand, cmask, fbd, curmask, forb, 1, best, bestset,
                stop_at_target, count_all, found_store, found_n, max_store)
