"""Beam search for admissible lattice configurations with few distinct circumradii.

Upper bounds only.  Exact integer arithmetic throughout (circumradius squared kept as
a reduced fraction), so any configuration reported is genuinely admissible and its
radius count is exact.  Not a proof of anything about h(n): the lattice is a
restriction and the beam is a heuristic (A12/L74).

Usage: python beam.py <nmax> <grid W> <grid H> <beam width> [seedfile]
Writes results/beam_<W>x<H>_w<width>.json
"""
import sys, json, os, time
from math import gcd
from itertools import combinations

sys.stdout.reconfigure(encoding='utf-8', errors='replace')


def circ2(P, Q, R):
    a2 = (Q[0]-R[0])**2 + (Q[1]-R[1])**2
    b2 = (R[0]-P[0])**2 + (R[1]-P[1])**2
    c2 = (P[0]-Q[0])**2 + (P[1]-Q[1])**2
    S = 2*(a2*b2 + b2*c2 + c2*a2) - (a2*a2 + b2*b2 + c2*c2)
    if S == 0:
        return None
    num = a2*b2*c2
    g = gcd(num, S)
    return (num//g, S//g)


def det4(P, Q, R, T):
    def row(X):
        return (X[0]*X[0] + X[1]*X[1], X[0], X[1])
    r = [row(P), row(Q), row(R), row(T)]
    def d3(a, b, c):
        return (a[0]*(b[1]*c[2]-b[2]*c[1]) - a[1]*(b[0]*c[2]-b[2]*c[0])
                + a[2]*(b[0]*c[1]-b[1]*c[0]))
    return (-d3(r[1], r[2], r[3]) + d3(r[0], r[2], r[3])
            - d3(r[0], r[1], r[3]) + d3(r[0], r[1], r[2]))


def run(nmax, W, H, width):
    pts = [(x, y) for x in range(W) for y in range(H)]
    t0 = time.time()
    # Seeds are restricted to triples containing the grid corner (0,0).  The earlier
    # comment justified this "by translation invariance", which is wrong: translating a
    # set so that min x = min y = 0 does not put any POINT at the origin.  This is a
    # real narrowing of the beam, stated rather than justified.  It is sound for the use
    # made of it, since a beam yields upper bounds only.
    beam = []
    seen = set()
    for i in range(len(pts)):
        for j in range(i+1, len(pts)):
            for k in range(j+1, len(pts)):
                if pts[i] != (0, 0):
                    continue
                c = circ2(pts[i], pts[j], pts[k])
                if c is None:
                    continue
                beam.append((1, (pts[i], pts[j], pts[k]), frozenset([c])))
    beam = beam[:width*4]
    print('seeded %d triples' % len(beam), flush=True)
    best_by_n = {3: 1}
    out = {3: beam[0][1] if beam else None}
    for n in range(4, nmax+1):
        nxt = {}
        for score, cfg, radii in beam:
            cs = set(cfg)
            for P in pts:
                if P in cs:
                    continue
                new = set()
                ok = True
                for a, b in combinations(cfg, 2):
                    c = circ2(a, b, P)
                    if c is None:
                        ok = False
                        break
                    new.add(c)
                if not ok:
                    continue
                for q in combinations(cfg, 3):
                    if det4(q[0], q[1], q[2], P) == 0:
                        ok = False
                        break
                if not ok:
                    continue
                merged = radii | new
                key = tuple(sorted(cfg + (P,)))
                if key in nxt and nxt[key][0] <= len(merged):
                    continue
                nxt[key] = (len(merged), key, frozenset(merged))
        if not nxt:
            print('n=%d : no admissible extension' % n, flush=True)
            break
        beam = sorted(nxt.values(), key=lambda z: z[0])[:width]
        best_by_n[n] = beam[0][0]
        out[n] = list(map(list, beam[0][1]))
        print('n=%2d : best %d distinct circumradii  %s   (%d kept, %.0fs)'
              % (n, beam[0][0], out[n], len(beam), time.time()-t0), flush=True)
        os.makedirs('results', exist_ok=True)
        json.dump(dict(W=W, H=H, width=width, best=best_by_n, witness=out,
                       elapsed_s=round(time.time()-t0, 1), completed=(n == nmax)),
                  open('results/beam_%dx%d_w%d.json' % (W, H, width), 'w'), indent=1)
    return best_by_n, out


if __name__ == '__main__':
    run(int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4]))
