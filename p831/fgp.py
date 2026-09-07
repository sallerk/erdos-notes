"""Can the lower bound be sharpened by restricting f(n) to general position?

The bound h(n) >= ceil(C(n,3)/f(n)) uses f(n), the maximum number of unit circles
through three of n points, maximised over ALL n-point sets.  Our sets are restricted to
no three collinear and no four concyclic, so the relevant quantity is really

    f_gp(n) = the same maximum over ADMISSIBLE sets,      f_gp(n) <= f(n),

and any strict inequality would improve the bound on h(n).  A literature agent reported
that the published extremal configurations are degenerate at n = 7 and n = 8 but not at
n = 4, 5, 6.  This checks the n = 5 and n = 6 half of that claim from our OWN artifacts,
which is independent of the agent: the witnesses this directory already found contain a
radius class of size 4 at n = 5 and of size 8 at n = 6, and those witnesses are verified
admissible in exact integer arithmetic.  A class of size m in an admissible set IS m
circles of one radius through three points each, so it certifies f_gp >= m.
"""
import sys
import json
import glob
from itertools import combinations
from math import gcd

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

F104 = {3: 1, 4: 4, 5: 4, 6: 8, 7: 12, 8: 16}       # OEIS A003829, offset 3


def circ2(P, Q, R):
    a2 = (Q[0] - R[0]) ** 2 + (Q[1] - R[1]) ** 2
    b2 = (R[0] - P[0]) ** 2 + (R[1] - P[1]) ** 2
    c2 = (P[0] - Q[0]) ** 2 + (P[1] - Q[1]) ** 2
    S = 2 * (a2 * b2 + b2 * c2 + c2 * a2) - (a2 * a2 + b2 * b2 + c2 * c2)
    if S == 0:
        return None
    num = a2 * b2 * c2
    g = gcd(num, S)
    return (num // g, S // g)


def det4(P, Q, R, T):
    def row(X):
        return (X[0] * X[0] + X[1] * X[1], X[0], X[1])
    r = [row(P), row(Q), row(R), row(T)]

    def d3(a, b, c):
        return (a[0] * (b[1] * c[2] - b[2] * c[1]) - a[1] * (b[0] * c[2] - b[2] * c[0])
                + a[2] * (b[0] * c[1] - b[1] * c[0]))
    return (-d3(r[1], r[2], r[3]) + d3(r[0], r[2], r[3])
            - d3(r[0], r[1], r[3]) + d3(r[0], r[1], r[2]))


def analyse(pts):
    n = len(pts)
    for t in combinations(pts, 3):
        if circ2(*t) is None:
            return None, 'three collinear'
    for q in combinations(pts, 4):
        if det4(*q) == 0:
            return None, 'four concyclic'
    cls = {}
    for t in combinations(range(n), 3):
        c = circ2(pts[t[0]], pts[t[1]], pts[t[2]])
        cls.setdefault(c, []).append(t)
    return cls, 'admissible'


if __name__ == '__main__':
    best = {}
    for fn in [p for p in glob.glob('results/lath_n*.json') if not p.endswith('.ck.json')] + glob.glob('results/beam_*.json'):
        d = json.load(open(fn))
        cands = []
        if isinstance(d.get('witness'), dict):
            for k, v in d['witness'].items():
                if v:
                    cands.append((int(k), v))
        elif d.get('witness'):
            cands.append((d['n'], d['witness']))
        for n, w in cands:
            pts = [tuple(map(int, p)) for p in w]
            cls, status = analyse(pts)
            if cls is None:
                continue
            m = max(len(v) for v in cls.values())
            if n not in best or m > best[n][0]:
                best[n] = (m, pts, len(cls))

    print('=' * 76)
    print('LARGEST RADIUS CLASS IN AN ADMISSIBLE WITNESS, versus f(n) = A003829')
    print('=' * 76)
    print(' n   largest class   f(n)   f_gp(n) is then   witness')
    out = {}
    for n in sorted(best):
        m, pts, hh = best[n]
        f = F104.get(n)
        if f is None:
            verdict = 'f(n) unknown'
        elif m == f:
            verdict = 'EXACTLY f(n) = %d, so the bound CANNOT be sharpened here' % f
        else:
            verdict = 'at least %d, at most %d' % (m, f)
        print(' %d   %11d   %4s   %s' % (n, m, f, verdict))
        print('       %s' % (pts,))
        out[n] = dict(largest_class=m, f=f, witness=pts, distinct=hh,
                      tight=(f is not None and m == f))
    print()
    print('Reading: a class of size m inside an ADMISSIBLE set is m circles of one radius')
    print('through exactly three points each, so it certifies f_gp(n) >= m directly.')
    print('Where that equals the published f(n), general position costs nothing and the')
    print('bound h(n) >= ceil(C(n,3)/f(n)) is already the best this route can give.')
    json.dump(dict(table=out, completed=True), open('results/fgp.json', 'w'), indent=1)
