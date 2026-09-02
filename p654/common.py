"""Functions shared with the #98 work, vendored so that p654 stands alone.

Every p654 script originally did `sys.path.insert(0, '../p98')` and imported from there.
That made a clone of this directory alone unrunnable, which defeats the point of
publishing it.  The definitions below are lifted verbatim from the #98 sources named
against each block; they are not re-derived here, and any divergence between the two
copies is a bug in this file.

    pairs, canonical, det4      from p98/hdecide.py
    gram_sym, minors3,
    real_roots_num, solve_chain from p98/hard.py
    GM_A2, GM_Z2, Lat,
    collinear, cocircular       from p98/latmin2.py
"""
import sys, itertools

import sympy as sp
import mpmath as mp

mp.mp.dps = 50


# --------------------------------------------------------------- from p98/hdecide.py
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

# ------------------------------------------------------------------ from p98/hard.py
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

# --------------------------------------------------------------- from p98/latmin2.py
GM_A2 = [((1, 0), (0, 1)), ((0, -1), (1, 1)), ((-1, -1), (1, 0)), ((-1, 0), (0, -1)),
         ((0, 1), (-1, -1)), ((1, 1), (-1, 0)), ((0, 1), (1, 0)), ((1, 1), (0, -1)),
         ((1, 0), (-1, -1)), ((0, -1), (-1, 0)), ((-1, -1), (0, 1)), ((-1, 0), (1, 1))]
# the 8 elements of the point group of the square lattice
GM_Z2 = [((1, 0), (0, 1)), ((0, -1), (1, 0)), ((-1, 0), (0, -1)), ((0, 1), (-1, 0)),
         ((0, 1), (1, 0)), ((1, 0), (0, -1)), ((0, -1), (-1, 0)), ((-1, 0), (0, 1))]


class Lat:
    def __init__(self, kind):
        self.kind = kind
        self.G = GM_A2 if kind == 'a2' else GM_Z2

    def norm(self, da, db):
        return da * da + db * db if self.kind == 'z2' else da * da + da * db + db * db

    def emb(self, p):
        return (p[0], p[1]) if self.kind == 'z2' else (2 * p[0] + p[1], p[1])

    def q(self, p):
        x, y = self.emb(p)
        return x * x + y * y if self.kind == 'z2' else x * x + 3 * y * y

    def act(self, M, p):
        return (M[0][0] * p[0] + M[0][1] * p[1], M[1][0] * p[0] + M[1][1] * p[1])


def collinear(L, p, q, r):
    (x1, y1), (x2, y2), (x3, y3) = L.emb(p), L.emb(q), L.emb(r)
    return (x2 - x1) * (y3 - y1) - (x3 - x1) * (y2 - y1) == 0


def cocircular(L, pts):
    M = [(L.q(t),) + L.emb(t) + (1,) for t in pts]

    def det3(a):
        return (a[0][0] * (a[1][1] * a[2][2] - a[1][2] * a[2][1])
                - a[0][1] * (a[1][0] * a[2][2] - a[1][2] * a[2][0])
                + a[0][2] * (a[1][0] * a[2][1] - a[1][1] * a[2][0]))
    tot = 0
    for c in range(4):
        minor = [[M[r][cc] for cc in range(4) if cc != c] for r in range(1, 4)]
        term = M[0][c] * det3(minor)
        tot = tot + term if c % 2 == 0 else tot - term
    return tot == 0
