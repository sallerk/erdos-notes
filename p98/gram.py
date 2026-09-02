"""UNSOUND FOR NEGATIVE VERDICTS -- DO NOT USE FOR LOWER BOUNDS. Use hard.py or z3run.py.

This decider calls sympy.solve on the rank conditions and reports `unsat` when nothing
usable comes back.  sympy.solve is NOT complete on polynomial systems: it can silently
omit branches.  Cross-checking against hard.py (Groebner plus guaranteed-real CRootOf
roots) found 17 patterns at n=5, k=4 that gram.py declared impossible and that are in
fact REALISABLE -- one was verified by hand, all ten distances matching their classes.

Its `sat` verdicts are fine (they come with a witness).  Its `unsat` verdicts mean only
"sympy found nothing" and are not proofs.  The file is kept because xcheck.py documents
the discrepancy, and because D_gen(6)=4 had to be re-derived (six2.py) once this was
discovered.
"""

"""Exact decider for distance patterns, via the Gram matrix instead of coordinates.

z3 on the coordinate encoding is unreliable here: it returned unknown on n=5,k=2 after
872 s (a case that is provably unsatisfiable) and unknown on 5-point 4-class patterns
that demonstrably ARE realisable.  The trouble is 2n coordinate unknowns with high-degree
cocircularity constraints.

Better variables: the distance classes themselves.  A pattern with k classes has only
k unknowns, and after fixing the scale (smallest class = 1) only k-1.

THE CRITERION.  Squared distances d_ij are realisable by points in R^2 exactly when the
Gram matrix
        G_ij = (d_0i + d_0j - d_ij) / 2          (i, j = 1 .. n-1, base point 0)
is positive semidefinite of rank at most 2.  Rank <= 2 means every 3x3 minor vanishes;
those minors are polynomials in the k-1 unknowns, so the realisable class values are the
real points of a variety in very few variables.  Solve it exactly, then for each solution
reconstruct actual coordinates and check the geometric side conditions directly.

This never needs a cocircularity constraint inside the algebra: once coordinates are in
hand, cocircularity is a 4x4 determinant evaluated exactly.

Usage:  python gram.py selftest
        python gram.py <n> <k>
"""
import sys, itertools, json, time

sys.stdout.reconfigure(encoding='utf-8', errors='replace')
import sympy as sp
from hdecide import pairs, enumerate_patterns
from witness import vertex_ok


def gram(pat, n, vals):
    """Gram matrix of the pattern with class c mapped to vals[c]; base point 0."""
    idx = {p: i for i, p in enumerate(pairs(n))}

    def d(i, j):
        if i == j:
            return sp.Integer(0)
        a, b = (i, j) if i < j else (j, i)
        return vals[pat[idx[(a, b)]]]
    m = n - 1
    return sp.Matrix(m, m, lambda i, j: sp.Rational(1, 2) *
                     (d(0, i + 1) + d(0, j + 1) - d(i + 1, j + 1)))


def realise(G, n):
    """Recover planar coordinates from a numeric PSD rank<=2 Gram matrix."""
    m = n - 1
    Gn = sp.Matrix(m, m, lambda i, j: sp.nsimplify(G[i, j]))
    # eigen-decomposition; keep the two positive directions
    P, D = Gn.diagonalize(normalize=True) if Gn.is_diagonalizable() else (None, None)
    if P is None:
        return None
    cols = []
    for i in range(m):
        lam = sp.simplify(D[i, i])
        if sp.simplify(lam) != 0:
            cols.append((lam, P[:, i]))
    if len(cols) > 2:
        return None
    pts = [(sp.Integer(0), sp.Integer(0))]
    coords = []
    for i in range(m):
        v = []
        for lam, col in cols:
            v.append(sp.simplify(sp.sqrt(lam) * col[i]))
        while len(v) < 2:
            v.append(sp.Integer(0))
        coords.append((sp.simplify(v[0]), sp.simplify(v[1])))
    return pts + coords


def geom_ok(pts):
    """no three collinear, no four cocircular, all points distinct -- exact"""
    n = len(pts)
    for i, j in itertools.combinations(range(n), 2):
        if sp.simplify((pts[i][0] - pts[j][0]) ** 2 + (pts[i][1] - pts[j][1]) ** 2) == 0:
            return False, 'coincident points'
    for t in itertools.combinations(range(n), 3):
        a, b, c = [pts[x] for x in t]
        if sp.simplify((b[0] - a[0]) * (c[1] - a[1]) - (c[0] - a[0]) * (b[1] - a[1])) == 0:
            return False, 'collinear %s' % (t,)
    for q in itertools.combinations(range(n), 4):
        M = sp.Matrix([[pts[t][0] ** 2 + pts[t][1] ** 2, pts[t][0], pts[t][1], 1]
                       for t in q])
        if sp.simplify(M.det()) == 0:
            return False, 'cocircular %s' % (q,)
    return True, 'ok'


def decide(pat, n, k, verbose=False):
    """Exact verdict for one pattern: 'sat' (with points) or 'unsat'."""
    u = sp.symbols('u1:%d' % k, positive=True)      # classes 1..k-1; class 0 fixed to 1
    vals = [sp.Integer(1)] + list(u)
    G = gram(pat, n, vals)
    m = n - 1
    minors = set()
    for rows in itertools.combinations(range(m), 3):
        for cols in itertools.combinations(range(m), 3):
            e = sp.expand(G[list(rows), list(cols)].det())
            if e != 0:
                minors.add(sp.factor(e))
    eqs = sorted(minors, key=lambda e: sp.count_ops(e))
    if not eqs:
        sols = [{}]
    else:
        try:
            sols = sp.solve(eqs, list(u), dict=True)
        except Exception as ex:
            return 'error', str(ex), None
    # A branch we cannot evaluate is NOT a rejection.  Skipping it silently would turn a
    # completeness hole into a confident 'unsat', so such branches are counted and
    # reported as 'inconclusive' instead.
    punt = 0
    for s in sols:
        vv = [sp.Integer(1)] + [sp.simplify(s.get(x, x)) for x in u]
        if any(v.free_symbols for v in vv):
            punt += 1                                  # positive-dimensional branch
            continue
        if any(v.is_real is None for v in vv):
            punt += 1                                  # could not determine reality
            continue
        if any(not v.is_real or v <= 0 for v in vv):
            continue
        if len(set(sp.simplify(v) for v in vv)) != k:   # classes must be distinct
            continue
        Gs = gram(pat, n, vv)
        if any(sp.simplify(Gs[list(r), list(c)].det()) != 0
               for r in itertools.combinations(range(m), 3)
               for c in itertools.combinations(range(m), 3)):
            continue
        if any(sp.simplify(Gs[list(r), list(r)].det()) < 0
               for rr in (1, 2) for r in itertools.combinations(range(m), rr)):
            continue                                   # not PSD
        pts = realise(Gs, n)
        if pts is None:
            punt += 1                                  # could not reconstruct
            continue
        ok, why = geom_ok(pts)
        if ok:
            return 'sat', vv, pts
    if punt:
        return 'inconclusive', '%d branch(es) not evaluated' % punt, None
    return 'unsat', None, None


if __name__ == '__main__':
    if sys.argv[1] == 'selftest':
        print('=' * 74)
        print('SELFTEST -- the Gram decider must reproduce what we already proved')
        print('=' * 74)
        bad = 0
        cases = [(4, 1, 'unsat', 'no 4 mutually equidistant points'),
                 (4, 2, 'sat', 'the diamond'),
                 (5, 2, 'unsat', 'D_gen(5) > 2, proved via pentagon.py'),
                 (5, 3, 'sat', 'D_gen(5) = 3, witness verified in Q(sqrt3)')]
        for n, k, want, why in cases:
            t0 = time.time()
            pats = [p for p in enumerate_patterns(n, k) if vertex_ok(p, n)]
            got = 'unsat'
            for p in pats:
                r, vv, pts = decide(p, n, k)
                if r == 'sat':
                    got = 'sat'
                    break
            ok = (got == want)
            bad += (not ok)
            print('  [%s] n=%d k=%d  %d patterns  expected %-5s got %-5s  %.1fs  %s'
                  % ('PASS' if ok else 'FAIL', n, k, len(pats), want, got,
                     time.time() - t0, why))
        print()
        print('SELFTEST FAILED' if bad else 'SELFTEST PASSED')
        sys.exit(1 if bad else 0)

    n, k = int(sys.argv[1]), int(sys.argv[2])
    pats = [p for p in enumerate_patterns(n, k) if vertex_ok(p, n)]
    print('n=%d k=%d: %d patterns after the vertex prune' % (n, k, len(pats)))
    t0 = time.time()
    nsat = 0
    for i, p in enumerate(pats):
        r, vv, pts = decide(p, n, k)
        if r == 'sat':
            nsat += 1
            print('  SAT: pattern %s' % (p,))
            print('       class values %s' % (vv,))
            print('       points %s' % (pts,))
            break
        if r == 'error':
            print('  ERROR on %s: %s' % (p, vv))
    print('  %d sat, %.1fs' % (nsat, time.time() - t0))
    print('  => D_gen(%d) %s %d' % (n, '<=' if nsat else '>', k))
