"""Decide h(n) for small n.

h(n) = the minimum, over all n-point sets in R^2 with NO THREE COLLINEAR and NO FOUR
CONCYCLIC, of the number of distinct pairwise distances.  Erdos problem #98 asks whether
h(n)/n -> infinity; he could not even prove h(n) >= n.  This script computes exact small
values, which is a far weaker question but a decidable one.

METHOD.  h(n) > k iff NO n-point general-position set has at most k distinct distances.
Enumerate every "distance pattern" (an assignment of each of the C(n,2) pairs to one of
m <= k distance classes) up to relabelling of the points and of the classes, and ask z3
whether that pattern is realisable over the REALS subject to:

    - pairs in the same class have equal squared distance, different classes differ
    - every triple is non-collinear          (cross product nonzero)
    - every quadruple is non-concyclic       (4x4 determinant nonzero)

All patterns UNSAT  =>  h(n) > k, a genuine real-closed-field statement, not a lattice
or floating-point one.  A single SAT gives a witness, and an explicit witness found by
any means at all is an independent upper-bound certificate.

Usage:  python hdecide.py <n> <k> [timeout_ms]
        python hdecide.py controls
"""
import sys, itertools, json, time

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

try:
    import z3
except ImportError:
    sys.exit('z3 is required:  pip install z3-solver')


def pairs(n):
    return list(itertools.combinations(range(n), 2))


def canonical(pat, n, P, index):
    """Least representative of `pat` under relabelling of points and of classes."""
    best = None
    for sigma in itertools.permutations(range(n)):
        moved = []
        for (i, j) in P:
            a, b = sigma[i], sigma[j]
            moved.append(pat[index[(a, b) if a < b else (b, a)]])
        # renumber classes by order of first appearance
        seen, ren = {}, []
        for c in moved:
            if c not in seen:
                seen[c] = len(seen)
            ren.append(seen[c])
        t = tuple(ren)
        if best is None or t < best:
            best = t
    return best


def enumerate_patterns(n, k):
    """All distance patterns on n points using at most k classes, up to symmetry."""
    P = pairs(n)
    index = {p: i for i, p in enumerate(P)}
    seen = set()
    for raw in itertools.product(range(k), repeat=len(P)):
        # cheap pre-filter: classes must appear in order of first use
        s, ok = {}, True
        for c in raw:
            if c not in s:
                if len(s) != c:
                    ok = False
                    break
                s[c] = 1
        if not ok:
            continue
        c = canonical(raw, n, P, index)
        if c not in seen:
            seen.add(c)
            yield c


def realisable(pat, n, timeout_ms):
    """Ask z3 whether this pattern is realisable in general position over R^2."""
    P = pairs(n)
    m = max(pat) + 1
    X = [z3.Real('x%d' % i) for i in range(n)]
    Y = [z3.Real('y%d' % i) for i in range(n)]
    D = [z3.Real('d%d' % c) for c in range(m)]
    s = z3.Solver()
    s.set('timeout', timeout_ms)

    # fix the isometry: translation, rotation, reflection
    s.add(X[0] == 0, Y[0] == 0, Y[1] == 0, X[1] > 0)
    if n > 2:
        s.add(Y[2] >= 0)

    # distance classes: positive and strictly increasing (this also forces distinctness)
    s.add(D[0] > 0)
    for c in range(m - 1):
        s.add(D[c] < D[c + 1])

    for idx, (i, j) in enumerate(P):
        d2 = (X[i] - X[j]) ** 2 + (Y[i] - Y[j]) ** 2
        s.add(d2 == D[pat[idx]])

    # no three collinear
    for (i, j, l) in itertools.combinations(range(n), 3):
        s.add((X[j] - X[i]) * (Y[l] - Y[i]) - (X[l] - X[i]) * (Y[j] - Y[i]) != 0)

    # no four concyclic: the standard 4x4 determinant in (|p|^2, x, y, 1)
    for quad in itertools.combinations(range(n), 4):
        rows = [[X[t] ** 2 + Y[t] ** 2, X[t], Y[t], 1] for t in quad]
        s.add(det4(rows) != 0)

    r = s.check()
    if r == z3.sat:
        mdl = s.model()
        return 'sat', mdl
    if r == z3.unsat:
        return 'unsat', None
    return 'unknown', None


def det4(m):
    """Exact symbolic 4x4 determinant by cofactor expansion."""
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


def decide(n, k, timeout_ms=60000, verbose=True):
    t0 = time.time()
    pats = list(enumerate_patterns(n, k))
    nsat = nunsat = nunk = 0
    witness = None
    for pat in pats:
        res, mdl = realisable(pat, n, timeout_ms)
        if res == 'sat':
            nsat += 1
            if witness is None:
                witness = (pat, str(mdl))
        elif res == 'unsat':
            nunsat += 1
        else:
            nunk += 1
    dt = time.time() - t0
    if verbose:
        print('  n=%d, at most k=%d distances: %d patterns mod symmetry -> '
              'sat %d / unsat %d / unknown %d   (%.1fs)'
              % (n, k, len(pats), nsat, nunsat, nunk, dt))
    return dict(n=n, k=k, patterns=len(pats), sat=nsat, unsat=nunsat,
                unknown=nunk, seconds=round(dt, 2), witness=witness)


if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == 'controls':
        print('=' * 74)
        print('CONTROLS -- the decider must reproduce facts known independently.')
        print('=' * 74)
        exp = [(3, 1, 'sat', 'equilateral triangle realises 1 distance'),
               (4, 1, 'unsat', 'no 4 mutually equidistant points exist in the plane'),
               (4, 2, 'sat', 'the two-glued-equilateral-triangles diamond, verified '
                             'exactly on the lattice')]
        bad = 0
        for n, k, want, why in exp:
            r = decide(n, k, 60000, verbose=False)
            got = 'sat' if r['sat'] else ('unsat' if r['unknown'] == 0 else 'unknown')
            ok = got == want
            bad += (not ok)
            print('  [%s] n=%d k=%d  expected %-5s got %-5s  (%d patterns)  %s'
                  % ('PASS' if ok else 'FAIL', n, k, want, got, r['patterns'], why))
        print()
        print('CONTROLS FAILED' if bad else 'ALL CONTROLS PASSED')
        sys.exit(1 if bad else 0)

    n = int(sys.argv[1])
    k = int(sys.argv[2])
    tmo = int(sys.argv[3]) if len(sys.argv) > 3 else 60000
    r = decide(n, k, tmo)
    json.dump(r, open('h_n%d_k%d.json' % (n, k), 'w'), indent=1)
    print('  written: h_n%d_k%d.json' % (n, k))
    if r['sat'] == 0 and r['unknown'] == 0:
        print('  => NO general-position %d-point set has at most %d distinct '
              'distances, so h(%d) > %d' % (n, k, n, k))
    elif r['sat']:
        print('  => h(%d) <= %d, witness recorded' % (n, k))
