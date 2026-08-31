"""Exhaustive enumeration of the COMBINATORIAL patterns a #982 counterexample
could have, for a fixed n.

A convex n-gon has vertices v_0..v_{n-1} in ccw order (WLOG).  Its distance
function induces a colouring c of the edges of K_n: c(uv) = the value |uv|,
so equal colour <=> equal length, different colour <=> different length.
Let S_v = { c(uv) : u != v }.  The #982 counterexample condition is exactly

        |S_v| <= k := floor(n/2) - 1     for every vertex v.

Two immediate consequences, both used as prunes:

 (1) For any u,v the edge uv is coloured by an element of S_u AND of S_v, so
     the family { S_v } is PAIRWISE INTERSECTING.
 (2) (Erdos's own remark, restated.)  |S_v| <= k and sum of class sizes = n-1
     forces total excess  sum_classes max(0, size-2) >= (n-1) - 2k, i.e. >= 1
     for even n and >= 2 for odd n.  In particular EVERY vertex must have
     three other vertices equidistant from it.

 (3) (Altman 1963.)  A convex n-gon determines >= floor(n/2) distinct distances
     in TOTAL, so the number of colours t >= floor(n/2) = k+1.

This module enumerates every such colouring up to (a) renaming colours and
(b) the dihedral symmetry of the ccw vertex order.  Each surviving pattern is
then a system of polynomial equalities to be decided over the reals.
"""

import sys
from itertools import combinations


def enumerate_patterns(n, verbose=True, cap=None, use_altman=True):
    """use_altman=False drops the (cited) Altman total-distance filter, so the
    enumeration rests on nothing but the definition of the problem."""
    k = n // 2 - 1
    if k <= 0:
        return []
    edges = list(combinations(range(n), 2))
    m = len(edges)
    # order edges so that vertices complete early -> prune early
    edges.sort(key=lambda e: (e[1], e[0]))
    eidx = {e: i for i, e in enumerate(edges)}
    # for each vertex, index of the last edge (in this order) incident to it
    last_edge_of = [max(i for i, e in enumerate(edges) if v in e) for v in range(n)]
    deg_needed = n - 1

    col = [-1] * m
    vcolors = [0] * n          # bitmask of colours used at v
    vcount = [0] * n
    # class sizes at each vertex: dict colour -> count
    vsize = [dict() for _ in range(n)]
    out = []
    stats = {'nodes': 0}

    def vertex_ok_complete(v):
        """called once every edge at v is coloured"""
        sizes = sorted(vsize[v].values(), reverse=True)
        if len(sizes) > k:
            return False
        excess = sum(max(0, s - 2) for s in sizes)
        return excess >= (n - 1) - 2 * k

    def rec(i, ncol):
        stats['nodes'] += 1
        if cap and len(out) >= cap:
            return
        if i == m:
            if (not use_altman) or ncol >= n // 2:      # Altman 1963 (CITED)
                out.append(tuple(col))
            return
        a, b = edges[i]
        # candidate colours: any existing colour that keeps both endpoints legal,
        # or a brand new colour (canonical: exactly ncol)
        for c in range(ncol + 1):
            newa = not (vcolors[a] >> c) & 1
            newb = not (vcolors[b] >> c) & 1
            if newa and vcount[a] + 1 > k:
                continue
            if newb and vcount[b] + 1 > k:
                continue
            col[i] = c
            if newa:
                vcolors[a] |= 1 << c; vcount[a] += 1
            if newb:
                vcolors[b] |= 1 << c; vcount[b] += 1
            vsize[a][c] = vsize[a].get(c, 0) + 1
            vsize[b][c] = vsize[b].get(c, 0) + 1
            good = True
            for v in (a, b):
                if last_edge_of[v] == i and not vertex_ok_complete(v):
                    good = False
                    break
            if good:
                rec(i + 1, ncol + (1 if c == ncol else 0))
            vsize[a][c] -= 1
            if vsize[a][c] == 0: del vsize[a][c]
            vsize[b][c] -= 1
            if vsize[b][c] == 0: del vsize[b][c]
            if newa:
                vcolors[a] &= ~(1 << c); vcount[a] -= 1
            if newb:
                vcolors[b] &= ~(1 << c); vcount[b] -= 1
            col[i] = -1

    rec(0, 0)
    if verbose:
        print(f"n={n} k={k}: {len(out)} raw colourings ({stats['nodes']} search nodes)")
    return [(edges, c) for c in out]


# --------------------------------------------------------- symmetry reduction

def canonical(n, edges, colvec):
    """Canonical form of a colouring under the dihedral group on the ccw order
    and under colour renaming."""
    eidx = {e: i for i, e in enumerate(edges)}
    best = None
    for r in range(n):
        for s in (1, -1):
            perm = [(s * i + r) % n for i in range(n)]
            # relabel colours in order of first appearance
            ren = {}
            vec = []
            for (a, b) in edges:
                pa, pb = perm[a], perm[b]
                e = (pa, pb) if pa < pb else (pb, pa)
                c = colvec[eidx[e]]
                if c not in ren:
                    ren[c] = len(ren)
                vec.append(ren[c])
            t = tuple(vec)
            if best is None or t < best:
                best = t
    return best


def reduce_patterns(n, pats, verbose=True):
    seen = {}
    for edges, c in pats:
        key = canonical(n, edges, c)
        if key not in seen:
            seen[key] = (edges, c)
    if verbose:
        print(f"n={n}: {len(seen)} colourings up to dihedral symmetry + colour renaming")
    return list(seen.values())


if __name__ == '__main__':
    for n in [int(x) for x in (sys.argv[1:] or ['6', '7', '8'])]:
        pats = enumerate_patterns(n)
        if pats and len(pats) < 400000:
            reduce_patterns(n, pats)
