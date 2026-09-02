"""Lattice witness hunt, with symmetry reduction and sharding.

latmin.py ran out of time at n=8 without completing, so it produced nothing usable -- not
even a lattice-exhaustive negative.  Two changes make the search feasible.

SYMMETRY.  The origin is fixed by translation, so the remaining freedom is the point group
about the origin: for the triangular lattice, 12 elements (6 rotations x reflection).  For
any configuration S containing 0, consider the 12 images gS and take the one minimising
min(gS \\ {0}) in pool order.  In that image the smallest point is ORBIT-MINIMAL, so it is
sound to require the first chosen point after the origin to be an orbit-minimal
representative.  This is the same argument validated in the p217 work (where a two-phase
check confirmed no solutions are lost across 17,196 cases).

SHARDING.  The choice of that first point partitions the search space, so shards can be
run independently and their results combined.  A witness found by any shard is a witness;
"no witness" requires every shard to complete.

Usage:  python latmin2.py <n> <R2> <z2|a2> <target> [shard] [nshards]
        python latmin2.py controls
"""
import sys, itertools, json, time

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

# the 12 elements of the point group of the triangular lattice, in (a,b) coordinates
GM_A2 = [((1, 0), (0, 1)), ((0, -1), (1, 1)), ((-1, -1), (1, 0)), ((-1, 0), (0, -1)),
         ((0, 1), (-1, -1)), ((1, 1), (-1, 0)), ((0, 1), (1, 0)), ((1, 1), (0, -1)),
         ((1, 0), (-1, -1)), ((0, -1), (-1, 0)), ((-1, -1), (0, 1)), ((-1, 0), (1, 1))]
# the 8 elements of the point group of the square lattice
GM_Z2 = [((1, 0), (0, 1)), ((0, -1), (1, 0)), ((-1, 0), (0, -1)), ((0, 1), (-1, 0)),
         ((0, 1), (1, 0)), ((1, 0), (0, -1)), ((0, -1), (-1, 0)), ((-1, 0), (0, 1))]


class Lat:
    def __init__(self, kind):
        self.kind = kind
        self.G = GM_A2 if kind == 'a2' else GM_Z2

    def norm(self, da, db):
        return da * da + db * db if self.kind == 'z2' else da * da + da * db + db * db

    def emb(self, p):
        return (p[0], p[1]) if self.kind == 'z2' else (2 * p[0] + p[1], p[1])

    def q(self, p):
        x, y = self.emb(p)
        return x * x + y * y if self.kind == 'z2' else x * x + 3 * y * y

    def act(self, M, p):
        return (M[0][0] * p[0] + M[0][1] * p[1], M[1][0] * p[0] + M[1][1] * p[1])


def collinear(L, p, q, r):
    (x1, y1), (x2, y2), (x3, y3) = L.emb(p), L.emb(q), L.emb(r)
    return (x2 - x1) * (y3 - y1) - (x3 - x1) * (y2 - y1) == 0


def cocircular(L, pts):
    M = [(L.q(t),) + L.emb(t) + (1,) for t in pts]

    def det3(a):
        return (a[0][0] * (a[1][1] * a[2][2] - a[1][2] * a[2][1])
                - a[0][1] * (a[1][0] * a[2][2] - a[1][2] * a[2][0])
                + a[0][2] * (a[1][0] * a[2][1] - a[1][1] * a[2][0]))
    tot = 0
    for c in range(4):
        minor = [[M[r][cc] for cc in range(4) if cc != c] for r in range(1, 4)]
        term = M[0][c] * det3(minor)
        tot = tot + term if c % 2 == 0 else tot - term
    return tot == 0


def search(n, R2, kind, target, shard=0, nsh=1, quiet=False):
    L = Lat(kind)
    pool = [(a, b) for a in range(-R2, R2 + 1) for b in range(-R2, R2 + 1)
            if L.norm(a, b) <= R2]
    pool.sort(key=lambda p: (L.norm(*p), p))
    rank = {p: i for i, p in enumerate(pool)}
    rest = [p for p in pool if p != (0, 0)]

    # orbit-minimal representatives for the FIRST chosen point after the origin
    orbmin = []
    for p in rest:
        if all(rank.get(L.act(M, p), 10 ** 9) >= rank[p] for M in L.G):
            orbmin.append(p)
    firsts = [p for i, p in enumerate(orbmin) if i % nsh == shard]
    if not quiet:
        print('  pool %d, orbit-minimal firsts %d of %d, this shard %d'
              % (len(pool), len(orbmin), len(rest), len(firsts)))

    best = [target, None]
    nodes = [0]

    def rec(chosen, dists, start):
        nodes[0] += 1
        if len(chosen) == n:
            if len(dists) < best[0]:
                best[0] = len(dists)
                best[1] = list(chosen)
                if not quiet:
                    print('   HIT: %d distances  %s' % (len(dists), chosen))
            return
        need = n - len(chosen)
        for idx in range(start, len(rest) - need + 1):
            p = rest[idx]
            ok = True
            for i in range(len(chosen)):
                for j in range(i + 1, len(chosen)):
                    if collinear(L, chosen[i], chosen[j], p):
                        ok = False
                        break
                if not ok:
                    break
            if not ok:
                continue
            for tri in itertools.combinations(range(len(chosen)), 3):
                if cocircular(L, [chosen[t] for t in tri] + [p]):
                    ok = False
                    break
            if not ok:
                continue
            nd = set(dists)
            for c in chosen:
                nd.add(L.norm(p[0] - c[0], p[1] - c[1]))
            if len(nd) >= best[0]:
                continue
            chosen.append(p)
            rec(chosen, nd, idx + 1)
            chosen.pop()

    t0 = time.time()
    for p in firsts:
        d = {L.norm(p[0], p[1])}
        if len(d) >= best[0]:
            continue
        rec([(0, 0), p], d, rank[p])
    return best[0], best[1], nodes[0], time.time() - t0


if __name__ == '__main__':
    if sys.argv[1] == 'controls':
        print('=' * 74)
        print('CONTROLS -- must reproduce the known witnesses')
        print('=' * 74)
        bad = 0
        for n, R2, tgt, want in ((4, 13, 3, 2), (6, 49, 5, 4), (7, 49, 6, 5)):
            b, s, nd, dt = search(n, R2, 'a2', tgt, quiet=True)
            ok = (b == want and s is not None)
            bad += (not ok)
            print('  [%s] n=%d target<=%d: found %s distances (expected %d)  %.1fs'
                  % ('PASS' if ok else 'FAIL', n, tgt - 1,
                     b if s else 'none', want, dt))
        print()
        print('CONTROLS FAILED' if bad else 'CONTROLS PASSED')
        sys.exit(1 if bad else 0)

    n, R2 = int(sys.argv[1]), int(sys.argv[2])
    kind = sys.argv[3]
    target = int(sys.argv[4])
    shard = int(sys.argv[5]) if len(sys.argv) > 5 else 0
    nsh = int(sys.argv[6]) if len(sys.argv) > 6 else 1
    print('n=%d R2=%d %s target<=%d shard %d/%d' % (n, R2, kind, target - 1, shard, nsh))
    b, s, nd, dt = search(n, R2, kind, target, shard, nsh)
    out = {'n': n, 'R2': R2, 'lattice': kind, 'target': target, 'shard': shard,
           'nshards': nsh, 'best': (b if s else None), 'points': s,
           'nodes': nd, 'seconds': round(dt, 1), 'completed': True}
    fn = 'lat2_n%d_%s_R%d_t%d_s%d.json' % (n, kind, R2, target, shard)
    json.dump(out, open(fn, 'w'), indent=1)
    print('  shard COMPLETE: best %s, nodes %d, %.1fs'
          % ((b if s else 'none found'), nd, dt))
    print('  written: %s' % fn)
