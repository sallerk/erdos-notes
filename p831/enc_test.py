"""Compare three encodings of the same realisability question on one pattern."""
import sys, json, time
from itertools import combinations
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
import z3

n, k = 5, 3
pats = json.load(open('results/penum_n5_k3.json'))['patterns']
lab = pats[0]['labels']
tri = list(combinations(range(n), 3))


def frame():
    X = [z3.RealVal(0), z3.RealVal(1)] + [z3.Real('x%d' % i) for i in range(2, n)]
    Y = [z3.RealVal(0), z3.RealVal(0)] + [z3.Real('y%d' % i) for i in range(2, n)]
    return X, Y


def d2(X, Y, i, j):
    return (X[i]-X[j])**2 + (Y[i]-Y[j])**2


def SS(X, Y, t):
    i, j, l = t
    a2, b2, c2 = d2(X, Y, j, l), d2(X, Y, l, i), d2(X, Y, i, j)
    return 2*(a2*b2 + b2*c2 + c2*a2) - (a2*a2 + b2*b2 + c2*c2), a2*b2*c2


def det4(X, Y, q):
    m = [[X[v]**2 + Y[v]**2, X[v], Y[v], z3.RealVal(1)] for v in q]
    r = [row[:3] for row in m]
    def d3(a, b, c):
        return (a[0]*(b[1]*c[2]-b[2]*c[1]) - a[1]*(b[0]*c[2]-b[2]*c[0])
                + a[2]*(b[0]*c[1]-b[1]*c[0]))
    return -d3(r[1], r[2], r[3]) + d3(r[0], r[2], r[3]) - d3(r[0], r[1], r[3]) + d3(r[0], r[1], r[2])


def common(X, Y, cons):
    cons.append(Y[2] > 0)
    for t in tri:
        S, _ = SS(X, Y, t)
        cons.append(S > 0)
    for q in combinations(range(n), 4):
        cons.append(det4(X, Y, q) != 0)


def encA():
    """9 vars, s_c explicit, degree 6"""
    X, Y = frame(); S = [z3.Real('s%d' % c) for c in range(k)]
    cons = []; common(X, Y, cons)
    for idx, t in enumerate(tri):
        s, p = SS(X, Y, t)
        cons.append(p == S[lab[idx]]*s)
    for a in range(k):
        cons.append(S[a] > 0)
        for b in range(a+1, k):
            cons.append(S[a] != S[b])
    return cons


def encB():
    """6 vars, cross-multiplied within class, degree 10"""
    X, Y = frame()
    cons = []; common(X, Y, cons)
    byc = {}
    for idx, t in enumerate(tri):
        byc.setdefault(lab[idx], []).append(t)
    reps = {}
    for c, ts in byc.items():
        s0, p0 = SS(X, Y, ts[0]); reps[c] = (s0, p0)
        for t in ts[1:]:
            s, p = SS(X, Y, t)
            cons.append(p*s0 == p0*s)
    cs = sorted(byc)
    for i in range(len(cs)):
        for j in range(i+1, len(cs)):
            s1, p1 = reps[cs[i]]; s2, p2 = reps[cs[j]]
            cons.append(p1*s2 != p2*s1)
    return cons


def encC():
    """centres as variables: all equations degree <= 2"""
    X, Y = frame(); S = [z3.Real('s%d' % c) for c in range(k)]
    cons = []; common(X, Y, cons)
    for idx, t in enumerate(tri):
        u = z3.Real('u%d' % idx); v = z3.Real('v%d' % idx)
        c = lab[idx]
        for w in t:
            cons.append((X[w]-u)**2 + (Y[w]-v)**2 == S[c])
    for a in range(k):
        cons.append(S[a] > 0)
        for b in range(a+1, k):
            cons.append(S[a] != S[b])
    return cons


import os
BUDGET = int(sys.argv[1]) if len(sys.argv) > 1 else 30000
rows = []
for name, fn in [('A 9var deg6', encA), ('B 6var deg10', encB), ('C centres deg2', encC)]:
    s = z3.SolverFor('QF_NRA'); s.set('timeout', BUDGET)
    for c in fn():
        s.add(c)
    t0 = time.time(); r = s.check(); el = time.time()-t0
    rows.append(dict(encoding=name, verdict=str(r), seconds=round(el, 2)))
    print('%-16s %-8s %6.2fs' % (name, r, el), flush=True)
os.makedirs('results', exist_ok=True)
json.dump(dict(budget_ms=BUDGET, pattern=0, rows=rows, completed=True,
               note=('A budget this short cannot distinguish "the algebra is hard" from '
                     '"the budget is short". The 1800 s run in pdecide_n5_k3.json is the '
                     'evidence; this is only a record of which encodings were tried.')),
          open('results/enc_test.json', 'w'), indent=1)
