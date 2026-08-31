"""Branch-and-bound search for point sets with FEW distinct circles (Erdos #506).

Upper-bound side: exhaustively search all n-subsets of a small integer grid and
report the fewest distinct circles achievable.  Everything is exact -- the points
are integers, so the circle key (A,B,C,D) is an integer 4-tuple and two triples
are cocircular exactly when their keys match.  No tolerance anywhere.

Method: iterative depth-first over grid points in increasing index order,
carrying the set of circle ids already forced.  Choosing point p at depth d marks
the circle of every triple (a,b,p) with a<b already chosen; the ids newly marked
are recorded in a per-depth list so the undo is exact.  If the running count
reaches the incumbent best, the subtree is pruned.

Collinear triples determine a line, not a circle, and are ignored (the convention
settled in the problem's forum thread).  The problem forbids all-collinear (0
circles) and all-concyclic (1 circle), so a leaf is accepted only with >= 2
circles; the winner is then re-validated by the independent exact checker in
circles.py.
"""
import numpy as np, sys, json, time
from itertools import combinations
from math import gcd
from numba import njit


def build_grid(w, h):
    return [(x, y) for x in range(w) for y in range(h)]


def circle_key_int(p, q, r):
    """integer (A,B,C,D) up to scale; A == 0 means the three points are collinear"""
    rows = [(x * x + y * y, x, y, 1) for (x, y) in (p, q, r)]

    def det3(m):
        return (m[0][0] * (m[1][1] * m[2][2] - m[1][2] * m[2][1])
                - m[0][1] * (m[1][0] * m[2][2] - m[1][2] * m[2][0])
                + m[0][2] * (m[1][0] * m[2][1] - m[1][1] * m[2][0]))

    cof = []
    for j in range(4):
        sub = [[rows[i][k] for k in range(4) if k != j] for i in range(3)]
        c = det3(sub)
        cof.append(c if j % 2 == 0 else -c)
    g = 0
    for v in cof:
        g = gcd(g, abs(v))
    if g:
        cof = [v // g for v in cof]
    for v in cof:
        if v != 0:
            if v < 0:
                cof = [-t for t in cof]
            break
    return tuple(cof)


def precompute(P):
    N = len(P)
    cid = -np.ones((N, N, N), np.int32)
    table = {}
    for i, j, k in combinations(range(N), 3):
        key = circle_key_int(P[i], P[j], P[k])
        if key[0] == 0:
            continue
        c = table.setdefault(key, len(table))
        for a, b, d in ((i, j, k), (i, k, j), (j, i, k), (j, k, i), (k, i, j), (k, j, i)):
            cid[a, b, d] = c
    return cid, len(table)


@njit(cache=True)
def _dfs(cid, N, n, used, best, bestset):
    chosen = np.zeros(n + 1, np.int32)
    nxt = np.zeros(n + 1, np.int32)
    addbuf = np.zeros((n + 1, 128), np.int32)
    naddb = np.zeros(n + 1, np.int32)
    cnt = np.zeros(n + 1, np.int64)
    nodes = 0
    d = 0
    nxt[0] = 0
    cnt[0] = 0
    while d >= 0:
        p = nxt[d]
        if p >= N or (N - p) < (n - d):
            # exhausted this level: undo the choice that led here
            d -= 1
            if d >= 0:
                for t in range(naddb[d]):
                    used[addbuf[d, t]] = 0
                nxt[d] += 1
            continue
        # tentatively take point p at depth d
        added = 0
        # circles forced by each pair already chosen, together with p
        for a in range(d):
            for b in range(a + 1, d):
                c = cid[chosen[a], chosen[b], p]
                if c >= 0 and used[c] == 0:
                    used[c] = 1
                    addbuf[d, added] = c
                    added += 1
        c_new = cnt[d] + added
        naddb[d] = added
        if c_new >= best[0]:
            for t in range(added):
                used[addbuf[d, t]] = 0
            naddb[d] = 0
            nxt[d] += 1
            continue
        chosen[d] = p
        nodes += 1
        if d == n - 1:
            if c_new >= 2:
                best[0] = c_new
                for t in range(n):
                    bestset[t] = chosen[t]
            for t in range(added):
                used[addbuf[d, t]] = 0
            naddb[d] = 0
            nxt[d] += 1
            continue
        cnt[d + 1] = c_new
        d += 1
        nxt[d] = p + 1
        naddb[d] = 0
    return nodes


def search(w, h, n, cap=None, verbose=True):
    P = build_grid(w, h)
    cid, ncirc = precompute(P)
    N = len(P)
    if verbose:
        print('grid %dx%d = %d points, %d distinct circles among all triples'
              % (w, h, N, ncirc), flush=True)
    used = np.zeros(ncirc, np.int8)
    best = np.array([cap if cap else 10 ** 9], np.int64)
    bestset = -np.ones(n, np.int32)
    t0 = time.time()
    nodes = _dfs(cid, N, n, used, best, bestset)
    dt = time.time() - t0
    pts = [P[i] for i in bestset] if bestset[0] >= 0 else None
    if verbose:
        if bestset[0] < 0:
            print('n=%d on %dx%d: NOTHING FOUND below cap %s  (%d nodes, %.1fs)'
                  % (n, w, h, cap, nodes, dt), flush=True)
        else:
            print('n=%d on %dx%d: best = %d circles  (%d nodes, %.1fs)'
                  % (n, w, h, best[0], nodes, dt), flush=True)
            print('   points:', pts, flush=True)
    return int(best[0]), pts, int(nodes), dt


if __name__ == '__main__':
    n = int(sys.argv[1]); w = int(sys.argv[2]); h = int(sys.argv[3])
    cap = int(sys.argv[4]) if len(sys.argv) > 4 else None
    b, pts, nodes, dt = search(w, h, n, cap)
    rec = {'n': n, 'grid': [w, h], 'best_circles': b, 'points': pts,
           'nodes': nodes, 'seconds': round(dt, 1), 'cap': cap,
           'exhaustive_over': 'all %d-subsets of the %dx%d integer grid' % (n, w, h),
           'status': 'COMPLETED'}
    # independent re-validation with the exact checker
    if pts:
        sys.path.insert(0, '.')
        from circles import count_circles, valid
        rec['recheck_circles'] = count_circles(pts)
        rec['recheck_valid'] = valid(pts)
        print('   independent recheck: circles=%d valid=%s'
              % (rec['recheck_circles'], rec['recheck_valid']))
    json.dump(rec, open('grid_n%d_%dx%d.json' % (n, w, h), 'w'), indent=1)
