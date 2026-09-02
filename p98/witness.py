"""Find a realisable pattern (an upper-bound witness) fast, stopping at the first SAT.

Complements hdecide.py: that script proves lower bounds by deciding EVERY pattern; this
one only wants one SAT, so it exits the moment it finds a realisable configuration.

Applies the vertex prune before calling the solver: no four points are cocircular, so at
most three points are equidistant from any given point, hence in any realisable pattern
each distance class appears AT MOST THREE TIMES at each vertex.  This is a purely
combinatorial filter and is sound for exactly that reason.

Usage:  python witness.py <n> <k> [timeout_ms]
"""
import sys, itertools, json, time

sys.stdout.reconfigure(encoding='utf-8', errors='replace')
import z3
from hdecide import pairs, enumerate_patterns, det4


def vertex_ok(pat, n):
    """each class at most 3 times at each vertex (no 4 cocircular)"""
    P = pairs(n)
    for v in range(n):
        cnt = {}
        for idx, (i, j) in enumerate(P):
            if i == v or j == v:
                cnt[pat[idx]] = cnt.get(pat[idx], 0) + 1
        if any(c > 3 for c in cnt.values()):
            return False
    return True


def solve(pat, n, tmo):
    P = pairs(n)
    m = max(pat) + 1
    X = [z3.Real('x%d' % i) for i in range(n)]
    Y = [z3.Real('y%d' % i) for i in range(n)]
    D = [z3.Real('d%d' % c) for c in range(m)]
    s = z3.Solver()
    s.set('timeout', tmo)
    s.add(X[0] == 0, Y[0] == 0, Y[1] == 0, X[1] > 0)
    if n > 2:
        s.add(Y[2] >= 0)
    s.add(D[0] > 0)
    for c in range(m - 1):
        s.add(D[c] < D[c + 1])
    for idx, (i, j) in enumerate(P):
        s.add((X[i] - X[j]) ** 2 + (Y[i] - Y[j]) ** 2 == D[pat[idx]])
    for (i, j, l) in itertools.combinations(range(n), 3):
        s.add((X[j] - X[i]) * (Y[l] - Y[i]) - (X[l] - X[i]) * (Y[j] - Y[i]) != 0)
    for quad in itertools.combinations(range(n), 4):
        rows = [[X[t] ** 2 + Y[t] ** 2, X[t], Y[t], 1] for t in quad]
        s.add(det4(rows) != 0)
    r = s.check()
    if r == z3.sat:
        return 'sat', s.model()
    return ('unsat' if r == z3.unsat else 'unknown'), None


if __name__ == '__main__':
    n = int(sys.argv[1])
    k = int(sys.argv[2])
    tmo = int(sys.argv[3]) if len(sys.argv) > 3 else 30000
    print('=' * 74)
    print('WITNESS SEARCH  n=%d  k=%d  (stop at first SAT)' % (n, k))
    print('=' * 74)
    t0 = time.time()
    allp = list(enumerate_patterns(n, k))
    kept = [p for p in allp if vertex_ok(p, n)]
    print('  %d patterns mod symmetry; %d survive the "at most 3 per vertex" prune'
          % (len(allp), len(kept)))
    nu = nunk = 0
    for i, pat in enumerate(kept):
        r, mdl = solve(pat, n, tmo)
        if r == 'sat':
            print()
            print('  SAT at pattern %d/%d: %s' % (i + 1, len(kept), (pat,)))
            print('  MODEL: %s' % mdl)
            print()
            print('  => D_gen(%d) <= %d' % (n, k))
            json.dump({'n': n, 'k': k, 'pattern': list(pat), 'model': str(mdl),
                       'seconds': round(time.time() - t0, 1)},
                      open('witness_n%d_k%d.json' % (n, k), 'w'), indent=1)
            sys.exit(0)
        if r == 'unsat':
            nu += 1
        else:
            nunk += 1
    print()
    print('  no SAT found: %d unsat, %d unknown, %.1fs' % (nu, nunk, time.time() - t0))
    if nunk == 0:
        print('  => every pattern is UNSAT, so D_gen(%d) > %d' % (n, k))
    else:
        print('  => INCONCLUSIVE, %d patterns undecided' % nunk)
