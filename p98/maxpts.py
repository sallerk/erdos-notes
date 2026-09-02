"""G(k): the largest point set in general position with at most k distinct distances.

This is the inverse of D_gen, and it is the form that bears on Erdos #98.  The conjecture
D_gen(n)/n -> infinity is equivalent to G(k)/k -> 0.  Our exact values give

    G(1)=3, G(2)=4, G(3)=5, G(4)=6        i.e.  G(k) = k+2 so far,

and if that persisted for all k then G(k)/k -> 1 and the conjecture would be FALSE.  So
the interesting question is where, if anywhere, G(k) falls below k+2.

What this computes: the maximum over subsets of a LATTICE pool.  A lattice restriction
means the answer is a LOWER bound on the true G(k) -- the optimum need not be lattice
realisable -- and every configuration found is an exact certificate.  The best published
general construction gives n*2^{O(sqrt log n)} distances, i.e. superlinear, so any linear
family found here would beat the literature.

Search: depth-first over the pool in order, keeping the running distance set (which only
grows, so the bound is monotone and pruning is sound), rejecting any point that creates a
collinear triple or a cocircular quadruple.

Usage:  python maxpts.py <k> <R2> <z2|a2> [target_n]
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


def det4(M):
    def det3(a):
        return (a[0][0] * (a[1][1] * a[2][2] - a[1][2] * a[2][1])
                - a[0][1] * (a[1][0] * a[2][2] - a[1][2] * a[2][0])
                + a[0][2] * (a[1][0] * a[2][1] - a[1][1] * a[2][0]))
    t = 0
    for c in range(4):
        minor = [[M[r][cc] for cc in range(4) if cc != c] for r in range(1, 4)]
        term = M[0][c] * det3(minor)
        t = t + term if c % 2 == 0 else t - term
    return t


def cocircular(L, pts):
    M = []
    for t in pts:
        x, y = L.emb(t)
        M.append((L.q(t), x, y, 1))
    return det4(M) == 0


def search(k, R2, kind, target=None, report=None):
    L = Lat(kind)
    pool = [(a, b) for a in range(-R2, R2 + 1) for b in range(-R2, R2 + 1)
            if L.norm(a, b) <= R2]
    pool.sort(key=lambda p: (L.norm(*p), p))
    rest = [p for p in pool if p != (0, 0)]
    best = [1, [(0, 0)]]
    nodes = [0]
    t0 = time.time()

    def rec(chosen, dists, start):
        nodes[0] += 1
        if len(chosen) > best[0]:
            best[0] = len(chosen)
            best[1] = list(chosen)
            if report:
                report(len(chosen), list(chosen), sorted(dists))
        if target and best[0] >= target:
            return True
        for idx in range(start, len(rest)):
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
            if len(nd) > k:                       # the distance set only grows
                continue
            chosen.append(p)
            if rec(chosen, nd, idx + 1):
                chosen.pop()
                return True
            chosen.pop()
        return False

    rec([(0, 0)], set(), 0)
    return best[0], best[1], nodes[0], time.time() - t0, len(pool)


if __name__ == '__main__':
    k = int(sys.argv[1])
    R2 = int(sys.argv[2])
    kind = sys.argv[3] if len(sys.argv) > 3 else 'a2'
    target = int(sys.argv[4]) if len(sys.argv) > 4 else None
    print('=' * 74)
    print('G(%d): largest general-position set with at most %d distinct distances' % (k, k))
    print('=' * 74)

    def report(n, pts, ds):
        print('   n=%2d  distances %s' % (n, ds))
        print('         %s' % (pts,))
    n, pts, nodes, dt, npool = search(k, R2, kind, target, report)
    L = Lat(kind)
    ds = sorted({L.norm(pts[i][0] - pts[j][0], pts[i][1] - pts[j][1])
                 for i, j in itertools.combinations(range(len(pts)), 2)})
    print()
    print('  BEST: n = %d with %d distinct distances   (k+2 would be %d)'
          % (n, len(ds), k + 2))
    print('  points: %s' % (pts,))
    print('  squared distances: %s' % ds)
    print('  lattice %s, R2=%d, pool %d, nodes %d, %.1fs' % (kind, R2, npool, nodes, dt))
    json.dump({'k': k, 'R2': R2, 'lattice': kind, 'n': n, 'points': pts,
               'squared_distances': ds, 'nodes': nodes, 'seconds': round(dt, 1)},
              open('maxpts_k%d_%s_R%d.json' % (k, kind, R2), 'w'), indent=1)
    print('  written: maxpts_k%d_%s_R%d.json' % (k, kind, R2))
