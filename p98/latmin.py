"""Upper bounds on D_gen(n) by exhaustive lattice search.

D_gen(n) = minimum number of distinct distances among n points in the plane with no
three collinear and no four cocircular (Erdos #98; notation from Sheffer's survey).

A lattice search proves nothing about the true minimum, because the optimal set need not
be lattice-realisable.  What it DOES give is an upper-bound CERTIFICATE: an explicit
point set in general position with k distinct distances proves D_gen(n) <= k, and the
certificate is valid however it was found.  All arithmetic here is exact integer.

Two lattices are supported:
  z2  square lattice,      squared distance dx^2 + dy^2
  a2  triangular lattice,  squared distance da^2 + da*db + db^2  (Eisenstein integers)

For a2 the embedding X = 2a+b, Y = b makes collinearity and cocircularity integer
determinants under the metric x^2 + 3y^2.

Usage:  python latmin.py <n> <radius2> <z2|a2> [target]
"""
import sys, itertools, json, time

sys.stdout.reconfigure(encoding='utf-8', errors='replace')


class Lat:
    def __init__(self, kind):
        self.kind = kind

    def norm(self, da, db):
        return da * da + db * db if self.kind == 'z2' else da * da + da * db + db * db

    def emb(self, p):
        return (p[0], p[1]) if self.kind == 'z2' else (2 * p[0] + p[1], p[1])

    def q(self, p):
        x, y = self.emb(p)
        return x * x + y * y if self.kind == 'z2' else x * x + 3 * y * y


def collinear(L, p, q, r):
    (x1, y1), (x2, y2), (x3, y3) = L.emb(p), L.emb(q), L.emb(r)
    return (x2 - x1) * (y3 - y1) - (x3 - x1) * (y2 - y1) == 0


def cocircular(L, pts):
    M = []
    for t in pts:
        x, y = L.emb(t)
        M.append((L.q(t), x, y, 1))
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


def search(n, R2, kind, target=None):
    L = Lat(kind)
    pool = [(a, b) for a in range(-R2, R2 + 1) for b in range(-R2, R2 + 1)
            if L.norm(a, b) <= R2]
    pool.sort(key=lambda p: (L.norm(*p), p))
    # translate so the first chosen point is the origin; require the rest to follow it
    origin = (0, 0)
    assert origin in pool
    rest = [p for p in pool if p != origin]
    print('  lattice %s, R2=%d, pool %d points (origin fixed, %d others)'
          % (kind, R2, len(pool), len(rest)))

    best = [target if target else 10 ** 9]
    bestset = [None]
    nodes = [0]

    def rec(chosen, dists, start):
        nodes[0] += 1
        if len(chosen) == n:
            if len(dists) < best[0]:
                best[0] = len(dists)
                bestset[0] = list(chosen)
                print('     new best: %d distinct distances  %s' % (len(dists), chosen))
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
            # the distance set only grows, so this bound is monotone and sound
            if len(nd) >= best[0]:
                continue
            chosen.append(p)
            rec(chosen, nd, idx + 1)
            chosen.pop()

    t0 = time.time()
    rec([origin], set(), 0)
    dt = time.time() - t0
    return best[0], bestset[0], nodes[0], dt, len(pool)


if __name__ == '__main__':
    n = int(sys.argv[1])
    R2 = int(sys.argv[2])
    kind = sys.argv[3] if len(sys.argv) > 3 else 'a2'
    target = int(sys.argv[4]) if len(sys.argv) > 4 else None
    print('=' * 74)
    print('LATTICE UPPER BOUND on D_gen(%d)   (no 3 collinear, no 4 cocircular)' % n)
    print('=' * 74)
    b, s, nd, dt, npool = search(n, R2, kind, target)
    print()
    if s:
        print('  BEST FOUND: %d distinct distances' % b)
        print('  witness   : %s' % (s,))
        L = Lat(kind)
        ds = sorted({L.norm(s[i][0] - s[j][0], s[i][1] - s[j][1])
                     for i, j in itertools.combinations(range(n), 2)})
        print('  squared distances: %s' % ds)
        print('  => D_gen(%d) <= %d' % (n, b))
        json.dump({'n': n, 'R2': R2, 'lattice': kind, 'distinct': b,
                   'points': s, 'squared_distances': ds, 'nodes': nd,
                   'seconds': round(dt, 2), 'pool': npool},
                  open('latmin_n%d_%s_R%d.json' % (n, kind, R2), 'w'), indent=1)
        print('  written: latmin_n%d_%s_R%d.json' % (n, kind, R2))
    else:
        print('  nothing found at or below the target within this radius')
    print('  nodes %d, %.1fs' % (nd, dt))
