"""How large can the isosceles count Z(P) actually get in general position?

THIS IS THE ANGLE WITH LEVERAGE ON THE CONJECTURE.  Szemeredi's bound comes from

    Z(P) <= 2*C(n,2) = n(n-1)          (a perpendicular bisector holds <= 2 points)

combined with a convexity lower bound on Z in terms of the number of distances seen per
vertex.  Any bound Z <= c*n^2 with c < 1 improves the constant from 1/3 to about
1/(2c+1); Dumitrescu got c = 11/12 in CONVEX position, lifting 1/3 to 6/17.  Nivasch,
Pach, Pinchasi and Zerbib pose determining the maximum of Z as their Problem 2, open with
only the trivial bound, and they work under no-three-collinear ONLY.

So: measure the true maximum of Z under BOTH hypotheses (no three collinear, no four
cocircular) at small n, and see how far below n(n-1) it sits.  A search gives a LOWER
bound on the maximum, so this is evidence about where the truth lies, not a proof of an
upper bound.  But if the achievable ratio stays well under 1, that is exactly the signal
that the trivial bound is loose and says by how much.

Z(P) = sum over points p of sum over distances d of C(m(p,d), 2), where m(p,d) is the
number of points at distance d from p.  Equivalently: the number of (apex, unordered
pair) triples with the apex equidistant from the pair.

Usage:  python maxiso.py <n> <R2> <z2|a2>
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


def isocount(L, pts):
    """Z(P): apex-equidistant-from-pair triples"""
    z = 0
    for i in range(len(pts)):
        cnt = {}
        for j in range(len(pts)):
            if i == j:
                continue
            d = L.norm(pts[i][0] - pts[j][0], pts[i][1] - pts[j][1])
            cnt[d] = cnt.get(d, 0) + 1
        for m in cnt.values():
            z += m * (m - 1) // 2
    return z


def search(n, R2, kind):
    L = Lat(kind)
    pool = [(a, b) for a in range(-R2, R2 + 1) for b in range(-R2, R2 + 1)
            if L.norm(a, b) <= R2]
    pool.sort(key=lambda p: (L.norm(*p), p))
    rest = [p for p in pool if p != (0, 0)]
    best = [-1, None]
    nodes = [0]

    def rec(chosen, start):
        nodes[0] += 1
        if len(chosen) == n:
            z = isocount(L, chosen)
            if z > best[0]:
                best[0] = z
                best[1] = list(chosen)
                print('   Z = %4d   ratio %.4f   %s'
                      % (z, z / float(n * (n - 1)), chosen))
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
            chosen.append(p)
            rec(chosen, idx + 1)
            chosen.pop()

    t0 = time.time()
    rec([(0, 0)], 0)
    return best[0], best[1], nodes[0], time.time() - t0, len(pool)


if __name__ == '__main__':
    n = int(sys.argv[1])
    R2 = int(sys.argv[2])
    kind = sys.argv[3] if len(sys.argv) > 3 else 'a2'
    triv = n * (n - 1)
    print('=' * 74)
    print('MAX ISOSCELES COUNT Z(P), n = %d, general position' % n)
    print('=' * 74)
    print('  trivial upper bound 2*C(n,2) = n(n-1) = %d' % triv)
    print('  any c < 1 with Z <= c*n^2 improves the constant 1/3 to about 1/(2c+1)')
    print()
    z, pts, nodes, dt, npool = search(n, R2, kind)
    print()
    print('  BEST Z FOUND      : %d' % z)
    print('  trivial bound     : %d' % triv)
    print('  ratio Z / n(n-1)  : %.4f' % (z / float(triv)))
    print('  implied constant if this ratio were the true max: %.4f'
          % (1.0 / (2.0 * z / float(triv) + 1)))
    print('  points: %s' % (pts,))
    print('  lattice %s R2=%d pool %d, nodes %d, %.1fs' % (kind, R2, npool, nodes, dt))
    json.dump({'n': n, 'R2': R2, 'lattice': kind, 'Z': z, 'trivial': triv,
               'ratio': z / float(triv), 'points': pts, 'nodes': nodes,
               'seconds': round(dt, 1)},
              open('maxiso_n%d_%s_R%d.json' % (n, kind, R2), 'w'), indent=1)
    print('  written: maxiso_n%d_%s_R%d.json' % (n, kind, R2))
    print()
    print('  NOTE: a search gives a LOWER bound on the maximum of Z, so this is')
    print('  evidence about the truth, not a proof of an upper bound.')
