"""Exact realisability decider for #831 radius patterns, via z3 nlsat.

A pattern assigns each triple of an n-point set a class; the question is whether some
admissible configuration realises exactly that pattern.  Formulated over the reals:

  variables  : x_i, y_i (points, with a similarity frame fixed) and s_c = r_c^2
  equalities : for every triple T in class c,   a2*b2*c2 == s_c * S_T
               where a2,b2,c2 are the squared side lengths and
               S_T = 2*(a2*b2+b2*c2+c2*a2) - (a2^2+b2^2+c2^2) = 16*(area)^2
  strict     : S_T > 0             (no three collinear; S_T >= 0 always, = 0 iff collinear)
               det4(quad) != 0     (no four concyclic)
               s_c != s_d          (the classes really are DIFFERENT radii, L73)

Frame: p0 = (0,0), p1 = (1,0) (similarity), y2 > 0 (reflection).  Legitimate because
the pattern is invariant under similarities, which do not permute the labels.

nlsat is a decision procedure for real closed fields, so an `unsat` here is a proof,
provided the encoding is right; `unknown` (timeout) is recorded as undecided, never as
a negative.  Every unsat is meant to be cross-checked by a second method (L64/L65).

Usage: python pdecide.py <n> <k> [timeout_ms] [limit]
"""
import sys, json, os, time
from itertools import combinations

sys.stdout.reconfigure(encoding='utf-8', errors='replace')
import z3


def build(n, labels, nclass):
    tri = list(combinations(range(n), 3))
    X = [z3.RealVal(0), z3.RealVal(1)] + [z3.Real('x%d' % i) for i in range(2, n)]
    Y = [z3.RealVal(0), z3.RealVal(0)] + [z3.Real('y%d' % i) for i in range(2, n)]
    S = [z3.Real('s%d' % c) for c in range(nclass)]
    cons = [Y[2] > 0]

    def d2(i, j):
        return (X[i]-X[j])**2 + (Y[i]-Y[j])**2

    for idx, t in enumerate(tri):
        i, j, k = t
        a2, b2, c2 = d2(j, k), d2(k, i), d2(i, j)
        SS = 2*(a2*b2 + b2*c2 + c2*a2) - (a2*a2 + b2*b2 + c2*c2)
        cons.append(SS > 0)                       # non-collinear
        cons.append(a2*b2*c2 == S[labels[idx]]*SS)

    for q in combinations(range(n), 4):
        m = [[X[v]**2 + Y[v]**2, X[v], Y[v], z3.RealVal(1)] for v in q]
        det = z3_det4(m)
        cons.append(det != 0)                     # non-concyclic

    for a in range(nclass):
        for b in range(a+1, nclass):
            cons.append(S[a] != S[b])             # classes are distinct radii
        cons.append(S[a] > 0)
    return cons


def z3_det4(m):
    def det3(r):
        (a, b, c), (d, e, f), (g, h, i) = r
        return a*(e*i - f*h) - b*(d*i - f*g) + c*(d*h - e*g)
    r = [row[:3] for row in m]
    return (-det3([r[1], r[2], r[3]]) + det3([r[0], r[2], r[3]])
            - det3([r[0], r[1], r[3]]) + det3([r[0], r[1], r[2]]))


def decide(n, labels, nclass, timeout_ms):
    s = z3.SolverFor('QF_NRA')
    s.set('timeout', timeout_ms)
    for c in build(n, labels, nclass):
        s.add(c)
    t0 = time.time()
    r = s.check()
    el = time.time() - t0
    model = None
    if r == z3.sat:
        m = s.model()
        model = {str(v): str(m[v]) for v in m.decls()}
    return str(r), round(el, 2), model


if __name__ == '__main__':
    n = int(sys.argv[1]); k = int(sys.argv[2])
    tmo = int(sys.argv[3]) if len(sys.argv) > 3 else 60000
    limit = int(sys.argv[4]) if len(sys.argv) > 4 else 10**9
    src = 'results/penum_n%d_k%d.json' % (n, k)
    data = json.load(open(src))
    pats = [p for p in data['patterns']][:limit]
    out = 'results/pdecide_n%d_k%d.json' % (n, k)
    res = []
    for idx, p in enumerate(pats):
        v, el, model = decide(n, p['labels'], k, tmo)
        res.append(dict(i=idx, sizes=p['sizes'], f104_ok=p['f104_ok'],
                        verdict=v, seconds=el, model=model))
        json.dump(dict(n=n, k=k, timeout_ms=tmo, results=res,
                       completed=(idx == len(pats) - 1),
                       timeout_note=('z3 timeout is ADVISORY: nlsat does not poll for '
                                     'cancellation inside deep real-algebraic work, and '
                                     'three patterns overran by up to 30%. See L70.')),
                  open(out, 'w'), indent=1)
        print('  [%3d/%3d] sizes=%-12s f104=%-5s %-7s %6.2fs'
              % (idx+1, len(pats), p['sizes'], p['f104_ok'], v, el), flush=True)
    from collections import Counter
    print(Counter(r['verdict'] for r in res))
    print('->', out)
