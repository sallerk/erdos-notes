"""Exhaustive search for #982 counterexamples among convex polygons whose
vertices are LATTICE points in a bounded region.

SCOPE WARNING (stated here so it cannot be lost downstream): this certifies
nothing about general real convex n-gons.  It is exhaustive only over the
stated finite pool.

Pool:  P(R, lattice) = all lattice points p with |p| <= R.
       lattice 'Z2' = the square lattice
       lattice 'A2' = the triangular lattice, embedded as x*(1,0)+y*(1/2,sqrt3/2);
                      squared distance = dx^2+dx*dy+dy^2 (Eisenstein norm), and
                      orientation determinants are the same up to the positive
                      factor sqrt3/2, so both are exact integer computations.

Enumeration: a strictly convex polygon is enumerated by its vertices in ccw
order starting from its lexicographically smallest vertex p0.  Every later
vertex must keep all triples positively oriented.  We add points in increasing
angle around p0 and check the left-turn condition on the chain, plus the two
closing turns.

Prune: as soon as ANY already-placed vertex sees more than k = floor(n/2)-1
distinct distances the branch dies, because per-vertex distinct-distance counts
only ever increase when more points are added.  (n is fixed for a run.)
"""

import sys, json, time, math, os
import multiprocessing as mp
from itertools import combinations


def make_pool(R, lattice):
    pts = []
    for x in range(-R, R + 1):
        for y in range(-R, R + 1):
            if lattice == 'Z2':
                if x * x + y * y <= R * R:
                    pts.append((x, y))
            else:
                if x * x + x * y + y * y <= R * R:
                    pts.append((x, y))
    return pts


def d2f(lattice):
    if lattice == 'Z2':
        return lambda p, q: (p[0]-q[0])**2 + (p[1]-q[1])**2
    return lambda p, q: (p[0]-q[0])**2 + (p[0]-q[0])*(p[1]-q[1]) + (p[1]-q[1])**2


def cross(a, b, c):
    return (b[0]-a[0])*(c[1]-a[1]) - (b[1]-a[1])*(c[0]-a[0])


_G = {}


def _init(pool, n, lattice, k, keep_near):
    """k here is the SEARCH BUDGET: branches die as soon as some vertex sees
    more than k distinct distances.  Setting k = floor(n/2)-1 searches exactly
    for counterexamples; setting it higher also collects near-misses."""
    _G.update(pool=pool, n=n, lattice=lattice, k=k, D2=d2f(lattice),
              keep_near=keep_near)


def _search_from(i0):
    """All strictly convex n-gons whose lexicographically smallest vertex is
    pool[i0]."""
    pool, n, k, D2 = _G['pool'], _G['n'], _G['k'], _G['D2']
    keep_near = _G['keep_near']
    p0 = pool[i0]
    # candidates: strictly lexicographically greater than p0
    cand = [p for p in pool if (p[1], p[0]) > (p0[1], p0[0])]
    # sort by angle around p0 (ccw), then by distance
    cand.sort(key=lambda p: (math.atan2(p[1]-p0[1], p[0]-p0[0]),
                             D2(p0, p)))
    m = len(cand)
    chain = [p0]
    dsets = [set()]          # dsets[t] = distinct squared distances seen by chain[t]
    best = []                # (maxcount, points)
    found = []
    stats = {'nodes': 0}

    def add_point(p):
        """returns per-point 'undo' info, or None if the prune fires"""
        newd = []
        for t, q in enumerate(chain):
            d = D2(q, p)
            newd.append(d)
        # tentatively update
        for t, d in enumerate(newd):
            dsets[t].add(d)
        ds = set(newd)
        dsets.append(ds)
        chain.append(p)
        for t in range(len(chain)):
            if len(dsets[t]) > k:
                return False
        return True

    def undo(saved):
        chain.pop()
        dsets.pop()
        for t, s in enumerate(saved):
            dsets[t] = s

    def rec(start):
        stats['nodes'] += 1
        L = len(chain)
        if L == n:
            # closing turns: p0 must be a strict vertex too
            if cross(chain[-2], chain[-1], p0) > 0 and cross(chain[-1], p0, chain[1]) > 0:
                mx = max(len(s) for s in dsets)
                if mx <= n // 2 - 1:
                    found.append([mx, [list(p) for p in chain]])
                if keep_near:
                    best.append((mx, [list(p) for p in chain]))
            return
        if m - start < n - L:
            return
        for i in range(start, m):
            p = cand[i]
            if L >= 2 and cross(chain[-2], chain[-1], p) <= 0:
                continue
            if L >= 1 and cross(chain[-1], p, p0) <= 0 and L >= 2:
                # would make p0 non-convex later; cheap partial test only when L>=2
                pass
            saved = [set(s) for s in dsets]
            if add_point(p):
                rec(i + 1)
            else:
                chain.pop(); dsets.pop()
                for t, s in enumerate(saved):
                    dsets[t] = s
                continue
            chain.pop(); dsets.pop()
            for t, s in enumerate(saved):
                dsets[t] = s

    rec(0)
    best.sort(key=lambda x: x[0])
    return found, best[:5], stats['nodes']


def run(n, R, lattice='Z2', workers=16, budget=None, keep_near=True, tag=''):
    t0 = time.time()
    pool = make_pool(R, lattice)
    k = n // 2 - 1
    b = k if budget is None else budget
    print(f"lattice={lattice} R={R} pool={len(pool)} points, n={n}, "
          f"counterexample needs max-per-vertex <= floor(n/2)-1 = {k}; "
          f"SEARCH BUDGET = {b}; workers={workers}", flush=True)
    idxs = list(range(len(pool)))
    allfound, allbest, nodes = [], [], 0
    ncomplete = 0
    with mp.Pool(workers, initializer=_init,
                 initargs=(pool, n, lattice, b, keep_near)) as P:
        for cnt, (f, bb, nd) in enumerate(P.imap_unordered(_search_from, idxs, chunksize=1), 1):
            allfound += f
            allbest += bb
            nodes += nd
            if f:
                print(f"*** FOUND {len(f)} COUNTEREXAMPLE candidate(s)", flush=True)
            if cnt % 100 == 0:
                allbest.sort(key=lambda x: x[0]); allbest = allbest[:40]
                print(f"  {cnt}/{len(idxs)} starts  {time.time()-t0:.0f}s  "
                      f"nodes={nodes}  cex={len(allfound)}  "
                      f"best_max={allbest[0][0] if allbest else '-'}", flush=True)
    allbest.sort(key=lambda x: x[0])
    # keep only distinct best-value polygons
    seen, near = set(), []
    for mx, pts in allbest:
        key = tuple(map(tuple, pts))
        if key in seen:
            continue
        seen.add(key); near.append({'max_per_vertex': mx, 'points': pts})
        if len(near) >= 20:
            break
    res = {'n': n, 'R': R, 'lattice': lattice, 'pool_size': len(pool),
           'counterexample_threshold': k, 'search_budget': b,
           'counterexamples': allfound, 'best_near_misses': near, 'nodes': nodes,
           'workers': workers, 'elapsed_s': round(time.time()-t0, 1),
           'status': 'COMPLETED',
           'exhaustive_over': f'all strictly convex {n}-gons with vertices in '
                              f'{{p in {lattice} : |p| <= {R}}} whose per-vertex '
                              f'distinct-distance counts never exceed {b}'}
    fn = f'lattice_{lattice}_n{n}_R{R}{tag}.json'
    json.dump(res, open(fn, 'w'), indent=1)
    print(f"n={n} {lattice} R={R}: COMPLETED {res['elapsed_s']}s, nodes={nodes}, "
          f"counterexamples={len(allfound)}, best max-per-vertex found="
          f"{near[0]['max_per_vertex'] if near else '-'} (counterexample needs "
          f"<= {k}) -> {fn}", flush=True)
    return res


if __name__ == '__main__':
    mp.freeze_support()
    n = int(sys.argv[1]); R = int(sys.argv[2])
    lat = sys.argv[3] if len(sys.argv) > 3 else 'Z2'
    w = int(sys.argv[4]) if len(sys.argv) > 4 else 16
    bud = int(sys.argv[5]) if len(sys.argv) > 5 else None
    run(n, R, lat, w, bud, tag=('_b%d' % bud if bud is not None else ''))
