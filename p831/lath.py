"""Exhaustive integer-lattice search for admissible n-point sets with few distinct
circumradii.  All arithmetic is exact integer / Fraction; no floating point anywhere.

Upper bounds only: a hit is a genuine admissible configuration and certifies
h(n) <= value.  A miss over a lattice is NOT a proof of anything (A12/L74), because
lattice circumradii are constrained; the search is reported as a search.

Usage:  python lath.py <n> <grid W> <grid H> [target]
        target = prune as soon as the running radius count reaches it (default n).
Writes results/lath_n<n>_<W>x<H>.json
"""
import sys, json, os, time
from math import gcd
from itertools import combinations

sys.stdout.reconfigure(encoding='utf-8', errors='replace')


def build(W, H):
    return [(x, y) for x in range(W) for y in range(H)]


def cross2(P, Q, R):
    return (Q[0]-P[0])*(R[1]-P[1]) - (Q[1]-P[1])*(R[0]-P[0])


def d2(P, Q):
    return (P[0]-Q[0])**2 + (P[1]-Q[1])**2


def circ2(P, Q, R):
    """exact R^2 as a reduced (num, den) pair, or None if collinear"""
    a2, b2, c2 = d2(Q, R), d2(R, P), d2(P, Q)
    S = 2*(a2*b2 + b2*c2 + c2*a2) - (a2*a2 + b2*b2 + c2*c2)   # = 16 K^2
    if S == 0:
        return None
    num = a2*b2*c2
    g = gcd(num, S)
    return (num//g, S//g)


def det4(P, Q, R, S):
    def row(X):
        return (X[0]*X[0] + X[1]*X[1], X[0], X[1], 1)
    m = [row(P), row(Q), row(R), row(S)]
    # 4x4 determinant by cofactor on the last column (all ones)
    def det3(a, b, c):
        return (a[0]*(b[1]*c[2]-b[2]*c[1])
                - a[1]*(b[0]*c[2]-b[2]*c[0])
                + a[2]*(b[0]*c[1]-b[1]*c[0]))
    r = [row[:3] for row in m]
    return (-det3(r[1], r[2], r[3]) + det3(r[0], r[2], r[3])
            - det3(r[0], r[1], r[3]) + det3(r[0], r[1], r[2]))


def search(n, W, H, target):
    pts = build(W, H)
    N = len(pts)
    best = [target]
    bestset = [None]
    nodes = [0]
    t0 = time.time()
    hb = [time.time()]
    # the target is part of the name: two runs at different targets are different
    # experiments and the audit found one silently overwriting the other
    ck = 'results/lath_n%d_%dx%d_t%d.ck.json' % (n, W, H, target)

    def beat():
        # heartbeat BEFORE more work, carrying a counter that must INCREASE (L32)
        now = time.time()
        if now - hb[0] > 30:
            hb[0] = now
            json.dump(dict(n=n, W=W, H=H, nodes=nodes[0], best=best[0],
                           witness=bestset[0], elapsed_s=round(now - t0, 1),
                           completed=False), open(ck, 'w'), indent=1)
            print('   [hb] nodes=%d best=%s t=%.0fs' % (nodes[0], best[0], now - t0),
                  flush=True)

    def rec(chosen, radii):
        nodes[0] += 1
        if nodes[0] % 200000 == 0:
            beat()
        k = len(chosen)
        if k == n:
            if len(radii) < best[0]:
                best[0] = len(radii)
                bestset[0] = [pts[i] for i in chosen]
                print('  new best %d : %s' % (len(radii), bestset[0]), flush=True)
            return
        start = chosen[-1] + 1 if chosen else 0
        for p in range(start, N):
            P = pts[p]
            new = set()
            ok = True
            # new triples: every pair already chosen, plus P
            for i, j in combinations(chosen, 2):
                c = circ2(pts[i], pts[j], P)
                if c is None:          # three collinear -> inadmissible
                    ok = False
                    break
                new.add(c)
            if not ok:
                continue
            merged = radii | new
            if len(merged) >= best[0]:      # cannot beat the incumbent
                continue
            # new quadruples: every triple already chosen, plus P
            for a, b, c in combinations(chosen, 3):
                if det4(pts[a], pts[b], pts[c], P) == 0:
                    ok = False
                    break
            if not ok:
                continue
            rec(chosen + [p], merged)

    rec([], frozenset())
    return best[0], bestset[0], nodes[0], time.time() - t0


if __name__ == '__main__':
    n = int(sys.argv[1]); W = int(sys.argv[2]); H = int(sys.argv[3])
    target = int(sys.argv[4]) if len(sys.argv) > 4 else n
    print('n=%d grid %dx%d  prune at %d' % (n, W, H, target))
    b, s, nodes, el = search(n, W, H, target)
    os.makedirs('results', exist_ok=True)
    out = dict(n=n, W=W, H=H, target=target, best=(b if s else None),
               witness=s, nodes=nodes, seconds=round(el, 2), completed=True)
    fn = 'results/lath_n%d_%dx%d_t%d.json' % (n, W, H, target)
    json.dump(out, open(fn, 'w'), indent=1)
    print('best=%s nodes=%d  %.1fs -> %s' % (b if s else 'none', nodes, el, fn))
