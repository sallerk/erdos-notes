"""Robust exact decider: Groebner elimination + guaranteed-real roots.

gram.py calls sympy.solve on the rank-<=2 Gram minors.  That is fast when it works but
leaves branches unevaluated (52 'inconclusive' of 449 at n=5,k=4) and sometimes hangs
(39 timeouts).  The method that actually settled the hard cases by hand -- the pentagon
at n=5 and the heptagon pattern at n=6 -- was different:

    1. Groebner basis of the vanishing 3x3 minors, LEX order.
    2. If the basis is [1] the ideal is empty: UNSAT outright.
    3. Otherwise the basis is triangular.  Take the univariate eliminant, get its roots
       with real_roots / CRootOf (guaranteed real, unlike radical forms whose `is_real`
       does not resolve -- the bug that made six_pattern.py announce an unearned verdict).
    4. Back-substitute level by level at high precision, taking EVERY real root at each
       level so nothing is lost.
    5. For each full solution: positivity, distinct classes, PSD, then reconstruct
       coordinates and test no-three-collinear / no-four-cocircular exactly.

Anything that cannot be evaluated is reported 'inconclusive', never 'unsat'.

Usage:  python hard.py <n> <k> <pattern>        one pattern
        python hard.py selftest
"""
import sys, itertools, json

sys.stdout.reconfigure(encoding='utf-8', errors='replace')
import sympy as sp
import mpmath as mp

mp.mp.dps = 50


def gram_sym(pat, n, vals):
    P = list(itertools.combinations(range(n), 2))
    idx = {p: i for i, p in enumerate(P)}

    def d(i, j):
        if i == j:
            return sp.Integer(0)
        a, b = (i, j) if i < j else (j, i)
        return vals[pat[idx[(a, b)]]]
    m = n - 1
    return sp.Matrix(m, m, lambda i, j: sp.Rational(1, 2) *
                     (d(0, i + 1) + d(0, j + 1) - d(i + 1, j + 1)))


def minors3(G, m):
    out = set()
    for r in itertools.combinations(range(m), 3):
        for c in itertools.combinations(range(m), 3):
            e = sp.expand(G[list(r), list(c)].det())
            if e != 0:
                out.add(sp.factor(e))
    return sorted(out, key=sp.count_ops)


def real_roots_num(poly_coeffs):
    """all real roots of a polynomial given as mpmath coefficients, high precision"""
    cs = [c for c in poly_coeffs]
    while cs and abs(cs[0]) < mp.mpf('1e-40'):
        cs = cs[1:]
    if len(cs) <= 1:
        return None if not cs else []
    try:
        rts = mp.polyroots(cs, maxsteps=200, extraprec=200)
    except Exception:
        return None
    out = []
    for r in rts:
        if abs(mp.im(r)) < mp.mpf('1e-30'):
            out.append(mp.re(r))
    return out


def solve_chain(basis, uvars):
    """Solve the triangular lex basis, returning every real assignment.

    uvars are ordered so that uvars[0] is the most-eliminated (appears alone).
    """
    assigns = [{}]
    for level, var in enumerate(uvars):
        nxt = []
        for a in assigns:
            polys = []
            for g in basis:
                gs = g
                for v, val in a.items():
                    gs = gs.subs(v, sp.Float(str(val), 40))
                fs = gs.free_symbols
                if fs == {var}:
                    polys.append(sp.Poly(sp.expand(gs), var))
            if not polys:
                return None                      # not triangular; bail out honestly
            polys.sort(key=lambda p: p.degree())
            p0 = polys[0]
            cs = [mp.mpf(str(sp.N(c, 40))) for c in p0.all_coeffs()]
            rts = real_roots_num(cs)
            if rts is None:
                return None
            for r in rts:
                b = dict(a)
                b[var] = r
                # must satisfy EVERY basis polynomial at this level
                ok = True
                for g in basis:
                    gs = g
                    for v, val in b.items():
                        gs = gs.subs(v, sp.Float(str(val), 40))
                    if not gs.free_symbols:
                        if abs(complex(sp.N(gs, 40))) > 1e-22:
                            ok = False
                            break
                if ok:
                    nxt.append(b)
        assigns = nxt
        if not assigns:
            return []
    return assigns


def geom_check(pat, n, vals):
    """reconstruct at high precision and test general position; also validates distances"""
    P = list(itertools.combinations(range(n), 2))
    idx = {p: i for i, p in enumerate(P)}
    D = [[mp.mpf(0)] * n for _ in range(n)]
    for (i, j) in P:
        D[i][j] = D[j][i] = vals[pat[idx[(i, j)]]]
    m = n - 1
    G = mp.matrix(m, m)
    for a in range(m):
        for b in range(m):
            G[a, b] = (D[0][a + 1] + D[0][b + 1] - D[a + 1][b + 1]) / 2
    try:
        E, V = mp.eigsy(G)
    except Exception:
        return None, 'eigendecomposition failed'
    order = sorted(range(m), key=lambda i: -E[i])
    if any(E[i] < mp.mpf('-1e-25') for i in range(m)):
        return False, 'Gram not PSD'
    if len(order) > 2 and E[order[2]] > mp.mpf('1e-25'):
        return False, 'Gram rank > 2, not planar'
    pts = [(mp.mpf(0), mp.mpf(0))]
    for i in range(m):
        pts.append(tuple(mp.sqrt(max(E[order[k]], mp.mpf(0))) * V[i, order[k]]
                         for k in (0, 1)))
    worst = mp.mpf(0)
    for (i, j) in P:
        got = (pts[i][0] - pts[j][0]) ** 2 + (pts[i][1] - pts[j][1]) ** 2
        worst = max(worst, abs(got - D[i][j]))
    if worst > mp.mpf('1e-25'):
        return None, 'reconstruction error %s' % mp.nstr(worst, 5)
    for (a, b, c) in itertools.combinations(range(n), 3):
        dd = ((pts[b][0] - pts[a][0]) * (pts[c][1] - pts[a][1])
              - (pts[c][0] - pts[a][0]) * (pts[b][1] - pts[a][1]))
        if abs(dd) < mp.mpf('1e-25'):
            return False, 'collinear %s' % ((a, b, c),)
    for q in itertools.combinations(range(n), 4):
        M = mp.matrix(4, 4)
        for rr, t in enumerate(q):
            M[rr, 0] = pts[t][0] ** 2 + pts[t][1] ** 2
            M[rr, 1] = pts[t][0]
            M[rr, 2] = pts[t][1]
            M[rr, 3] = mp.mpf(1)
        if abs(mp.det(M)) < mp.mpf('1e-25'):
            return False, 'cocircular %s' % (q,)
    return True, pts


def decide(pat, n, k):
    u = list(sp.symbols('u1:%d' % k, real=True))
    vals = [sp.Integer(1)] + u
    G = gram_sym(pat, n, vals)
    eqs = minors3(G, n - 1)
    if not eqs:
        return 'inconclusive', 'no rank conditions', None
    try:
        GB = sp.groebner(eqs, *list(reversed(u)), order='lex')
    except Exception as ex:
        return 'inconclusive', 'groebner failed: %r' % ex, None
    if list(GB.exprs) == [sp.Integer(1)]:
        return 'unsat', 'ideal is trivial: no complex solutions at all', None
    # sympy's groebner(eqs, x, y, lex) eliminates x FIRST, so the univariate eliminant is
    # in the LAST variable passed.  We pass reversed(u), hence the eliminant is in u[0]
    # and the chain must be solved in FORWARD order u1, u2, ...  Solving it reversed finds
    # no univariate polynomial at the first level and bails out as 'not triangular'.
    chain = solve_chain(list(GB.exprs), list(u))
    if chain is None:
        return 'inconclusive', 'basis not triangular / root-finding failed', None
    if not chain:
        return 'unsat', 'no real solutions', None
    for a in chain:
        vv = [mp.mpf(1)] + [a[x] for x in u]
        if any(v <= mp.mpf('1e-25') for v in vv):
            continue
        if len(set(round(float(v), 18) for v in vv)) != k:
            continue
        ok, info = geom_check(pat, n, vv)
        if ok is None:
            return 'inconclusive', info, None
        if ok:
            return 'sat', [mp.nstr(v, 20) for v in vv], [[mp.nstr(c, 20) for c in p]
                                                         for p in info]
    return 'unsat', 'every real branch fails positivity, distinctness or general position', None


if __name__ == '__main__':
    if sys.argv[1] == 'selftest':
        print('=' * 74)
        print('SELFTEST -- must reproduce results proved by other means')
        print('=' * 74)
        cases = [
            ((0, 0, 1, 1, 1, 0, 1, 1, 0, 0), 5, 2, 'unsat', 'pentagon, proved by pentagon.py'),
            ((0, 0, 0, 1, 0, 1, 1, 1, 2, 1), 5, 3, 'sat', 'the n=5 witness'),
            ((0, 0, 1, 1, 2, 1, 0, 2, 1, 2, 0, 2, 2, 0, 1), 6, 3, 'unsat',
             'heptagon minus a vertex, proved by six_pattern4.py'),
        ]
        bad = 0
        for pat, n, k, want, why in cases:
            r, info, pts = decide(pat, n, k)
            ok = (r == want)
            bad += (not ok)
            print('  [%s] n=%d k=%d  expected %-5s got %-12s  %s'
                  % ('PASS' if ok else 'FAIL', n, k, want, r, why))
            if r != want:
                print('        info: %s' % (info,))
        print()
        print('SELFTEST FAILED' if bad else 'SELFTEST PASSED')
        sys.exit(1 if bad else 0)

    n, k = int(sys.argv[1]), int(sys.argv[2])
    pat = tuple(int(x) for x in sys.argv[3].split(','))
    r, info, pts = decide(pat, n, k)
    print(json.dumps({'r': r, 'info': str(info)[:400],
                      'pts': pts if r == 'sat' else None}))
