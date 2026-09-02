"""Decide D_gen(n) <= k with a SINGLE formula, no pattern enumeration.

hdecide.py enumerates every distance pattern up to symmetry and calls the solver once
per pattern.  That is sound but the pattern count is k^C(n,2) before symmetry reduction,
which stops being viable around n=6.

This script asks the question directly:

    exist points p_0..p_{n-1} in R^2 and reals 0 < D_0 < ... < D_{k-1} such that
      every pairwise squared distance equals SOME D_c,
      no three points are collinear,
      no four points are cocircular.

SAT   => D_gen(n) <= k, with an explicit witness.
UNSAT => D_gen(n) >  k.

The per-pair disjunction replaces the whole enumeration.  Symmetry is cut by pinning the
isometry (p_0 at the origin, p_1 on the positive x-axis, p_2 in the upper half-plane) and
by the strict ordering of the distance classes.

Usage:  python direct.py <n> <k> [timeout_s] [--nlsat]
        python direct.py controls
"""
import sys, itertools, time, json

sys.stdout.reconfigure(encoding='utf-8', errors='replace')
import z3


def det4(m):
    def det3(a):
        return (a[0][0] * (a[1][1] * a[2][2] - a[1][2] * a[2][1])
                - a[0][1] * (a[1][0] * a[2][2] - a[1][2] * a[2][0])
                + a[0][2] * (a[1][0] * a[2][1] - a[1][1] * a[2][0]))
    tot = 0
    for c in range(4):
        minor = [[m[r][cc] for cc in range(4) if cc != c] for r in range(1, 4)]
        term = m[0][c] * det3(minor)
        tot = tot + term if c % 2 == 0 else tot - term
    return tot


def build(n, k):
    X = [z3.Real('x%d' % i) for i in range(n)]
    Y = [z3.Real('y%d' % i) for i in range(n)]
    D = [z3.Real('D%d' % c) for c in range(k)]
    C = [X[0] == 0, Y[0] == 0, Y[1] == 0, X[1] > 0, D[0] > 0]
    if n > 2:
        C.append(Y[2] >= 0)
    for c in range(k - 1):
        C.append(D[c] < D[c + 1])
    for (i, j) in itertools.combinations(range(n), 2):
        d2 = (X[i] - X[j]) ** 2 + (Y[i] - Y[j]) ** 2
        C.append(z3.Or([d2 == D[c] for c in range(k)]))
    for (i, j, l) in itertools.combinations(range(n), 3):
        C.append((X[j] - X[i]) * (Y[l] - Y[i]) - (X[l] - X[i]) * (Y[j] - Y[i]) != 0)
    for quad in itertools.combinations(range(n), 4):
        rows = [[X[t] ** 2 + Y[t] ** 2, X[t], Y[t], 1] for t in quad]
        C.append(det4(rows) != 0)
    return C, X, Y, D


def run(n, k, timeout_s=600, nlsat=False):
    C, X, Y, D = build(n, k)
    s = z3.Tactic('qfnra-nlsat').solver() if nlsat else z3.Solver()
    s.set('timeout', int(timeout_s * 1000))
    s.add(C)
    t0 = time.time()
    r = s.check()
    dt = time.time() - t0
    if r == z3.sat:
        m = s.model()
        pts = []
        for i in range(n):
            pts.append((str(m.eval(X[i])), str(m.eval(Y[i]))))
        return 'sat', dt, pts
    return ('unsat' if r == z3.unsat else 'unknown'), dt, None


if __name__ == '__main__':
    if sys.argv[1] == 'controls':
        print('=' * 74)
        print('CONTROLS for the single-formula encoding')
        print('=' * 74)
        exp = [(3, 1, 'sat', 'equilateral triangle'),
               (4, 1, 'unsat', 'no 4 mutually equidistant points in the plane'),
               (4, 2, 'sat', 'diamond / triangle-plus-centre, verified on the lattice'),
               (5, 4, 'sat', 'lattice witness found with 4 distances')]
        bad = 0
        for n, k, want, why in exp:
            got, dt, pts = run(n, k, 300)
            ok = (got == want)
            bad += (not ok)
            print('  [%s] n=%d k=%d  expected %-5s got %-7s %6.1fs  %s'
                  % ('PASS' if ok else 'FAIL', n, k, want, got, dt, why))
        print()
        print('CONTROLS FAILED' if bad else 'ALL CONTROLS PASSED')
        sys.exit(1 if bad else 0)

    n = int(sys.argv[1]); k = int(sys.argv[2])
    tmo = int(sys.argv[3]) if len(sys.argv) > 3 else 600
    nl = '--nlsat' in sys.argv
    print('D_gen(%d) <= %d ?   (timeout %ds, tactic %s)'
          % (n, k, tmo, 'qfnra-nlsat' if nl else 'default'))
    got, dt, pts = run(n, k, tmo, nl)
    print('  %s in %.1fs' % (got.upper(), dt))
    if got == 'sat':
        print('  witness:')
        for p in pts:
            print('     ', p)
        print('  => D_gen(%d) <= %d' % (n, k))
    elif got == 'unsat':
        print('  => D_gen(%d) > %d' % (n, k))
    json.dump({'n': n, 'k': k, 'result': got, 'seconds': round(dt, 1),
               'witness': pts, 'tactic': 'nlsat' if nl else 'default'},
              open('direct_n%d_k%d.json' % (n, k), 'w'), indent=1)
