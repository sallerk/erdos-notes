"""Exact decider for pinned patterns, for Erdos #654.

Same algebra as p98/hard.py: realisability in the plane is equivalent to the Gram matrix
G_ij = (d_0i + d_0j - d_ij)/2 being PSD of rank <= 2, so every 3x3 minor vanishes; those
minors are polynomials in the k-1 unknown class values (class 0 is fixed to 1 to pin the
scale).  A lex Groebner basis triangulates them, real roots come from CRootOf, and each
surviving branch is reconstructed at high precision and tested geometrically.

WHAT IS DIFFERENT HERE, AND WHY IT MATTERS.

(a) NO ORDERING CONSTRAINT ON THE CLASS VALUES.  p98/z3run.py adds d_0 < d_1 < ... to its
    encoding, but canonical patterns number their classes by ORDER OF FIRST APPEARANCE
    along the edge list, which is unrelated to magnitude.  Imposing an order therefore
    tests only one of the k! value-orders of each pattern and can in principle report a
    realisable pattern as unsat.  Nothing here imposes an order; distinctness is required,
    order is not.

(b) TWO GEOMETRIC MODES.
        'g'  : no three collinear AND no four concyclic   (Sheffer's D-hat_gen)
        'n4' : no four concyclic only, collinear allowed   (the #654 page's f(n))
    The 4x4 determinant |x^2+y^2, x, y, 1| vanishes for concyclic AND for collinear
    quadruples.  Under 'n4' those must be told apart, or every configuration on a small
    number of lines (which is what Aletheia's construction is) would be wrongly rejected.

SOUNDNESS.  'unsat' from a trivial ideal is a proof (no solution even over C).  'unsat'
from an exhausted branch list is sound only if the chain enumeration is complete, which is
exactly p98 assumption A8; those verdicts must be cross-checked with z3 (pz3.py), whose
nlsat is a decision procedure for real closed fields.

Usage:  python pdecide.py <n> <m> <g|n4> [patternfile]
        python pdecide.py selftest
"""
import sys, itertools, json, time

sys.stdout.reconfigure(encoding='utf-8', errors='replace')
import sympy as sp
from mpmath import mp
from common import gram_sym, minors3, solve_chain

mp.dps = 40
EPS = mp.mpf('1e-25')


def reconstruct(pat, n, vals):
    """coordinates from class values, or (None, reason)"""
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
    if any(E[i] < -EPS for i in range(m)):
        return None, 'Gram not PSD'
    if len(order) > 2 and E[order[2]] > EPS:
        return None, 'Gram rank > 2, not planar'
    pts = [(mp.mpf(0), mp.mpf(0))]
    for i in range(m):
        pts.append(tuple(mp.sqrt(max(E[order[t]], mp.mpf(0))) * V[i, order[t]]
                         for t in (0, 1)))
    worst = mp.mpf(0)
    for (i, j) in P:
        got = (pts[i][0] - pts[j][0]) ** 2 + (pts[i][1] - pts[j][1]) ** 2
        worst = max(worst, abs(got - D[i][j]))
    if worst > EPS:
        return None, 'reconstruction error %s' % mp.nstr(worst, 5)
    return pts, 'ok'


def tri(pts, a, b, c):
    return ((pts[b][0] - pts[a][0]) * (pts[c][1] - pts[a][1])
            - (pts[c][0] - pts[a][0]) * (pts[b][1] - pts[a][1]))


def geom_ok(pts, n, mode):
    """True if the reconstruction satisfies the chosen hypothesis"""
    for (a, b, c) in itertools.combinations(range(n), 3):
        if abs(tri(pts, a, b, c)) < EPS and mode == 'g':
            return False, 'collinear %s' % ((a, b, c),)
    for q in itertools.combinations(range(n), 4):
        M = mp.matrix(4, 4)
        for rr, t in enumerate(q):
            M[rr, 0] = pts[t][0] ** 2 + pts[t][1] ** 2
            M[rr, 1] = pts[t][0]
            M[rr, 2] = pts[t][1]
            M[rr, 3] = mp.mpf(1)
        if abs(mp.det(M)) >= EPS:
            continue
        # determinant vanishes: concyclic OR collinear.  Only concyclic is forbidden.
        flat = (abs(tri(pts, q[0], q[1], q[2])) < EPS
                and abs(tri(pts, q[0], q[1], q[3])) < EPS)
        if not flat:
            return False, 'concyclic %s' % (q,)
    return True, 'ok'


def decide(pat, n, mode):
    k = max(pat) + 1
    if k == 1:
        return 'unsat', 'one class: all C(n,2) distances equal, impossible for n >= 4', None
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
    chain = solve_chain(list(GB.exprs), list(u))
    if chain is None:
        return 'inconclusive', 'basis not triangular / root-finding failed', None
    if not chain:
        return 'unsat', 'no real solutions', None
    for a in chain:
        vv = [mp.mpf(1)] + [a[x] for x in u]
        if any(v <= EPS for v in vv):
            continue
        if len(set(round(float(v), 18) for v in vv)) != k:
            continue                                    # classes must be DISTINCT
        pts, why = reconstruct(pat, n, vv)
        if pts is None:
            if why.startswith('Gram') or why.startswith('recon'):
                continue                                # this branch is simply not planar
            return 'inconclusive', why, None
        ok, info = geom_ok(pts, n, mode)
        if ok:
            sats = [mp.nstr(v, 20) for v in vv]
            return 'sat', sats, [[mp.nstr(c, 20) for c in p] for p in pts]
    why = 'general position' if mode == 'g' else 'the no-4-concyclic rule'
    return 'unsat', 'every real branch fails positivity, distinctness, planarity or ' + why, None


if __name__ == '__main__':
    if sys.argv[1] == 'selftest':
        print('=' * 74)
        print('SELFTEST -- must reproduce verdicts established in the #98 work')
        print('=' * 74)
        cases = [
            ((0, 0, 1, 1, 1, 0, 1, 1, 0, 0), 5, 'g', 'unsat', 'pentagon (p98/pentagon.py)'),
            ((0, 0, 0, 1, 0, 1, 1, 1, 2, 1), 5, 'g', 'sat', 'the n=5 D_gen witness'),
            ((0, 0, 1, 1, 2, 1, 0, 2, 1, 2, 0, 2, 2, 0, 1), 6, 'g', 'unsat',
             'heptagon minus a vertex (p98/six_pattern4.py)'),
            ((0, 0, 0, 1, 0, 1, 1, 1, 2, 1), 5, 'n4', 'sat',
             'the same witness must survive the weaker hypothesis too'),
        ]
        bad = 0
        for pat, n, mode, want, why in cases:
            r, info, pts = decide(pat, n, mode)
            ok = (r == want)
            bad += (not ok)
            print('  [%s] n=%d %-3s expected %-5s got %-12s  %s'
                  % ('PASS' if ok else 'FAIL', n, mode, want, r, why))
            if not ok:
                print('        info: %s' % (info,))
        print()
        print('SELFTEST FAILED' if bad else 'SELFTEST PASSED')
        sys.exit(1 if bad else 0)

    n, m, mode = int(sys.argv[1]), int(sys.argv[2]), sys.argv[3]
    pf = sys.argv[4] if len(sys.argv) > 4 else 'penum_n%d_m%d.json' % (n, m)
    pats = [tuple(p) for p in json.load(open(pf))['patterns']]
    print('n=%d m=%d mode=%s: deciding %d canonical patterns' % (n, m, mode, len(pats)))
    t0 = time.time()
    res = {'sat': [], 'unsat': [], 'inconclusive': []}
    detail = []
    for i, p in enumerate(pats):
        r, info, pts = decide(p, n, mode)
        res[r].append(list(p))
        detail.append({'pattern': list(p), 'verdict': r, 'info': info, 'points': pts})
        print('  [%2d/%2d] %-12s %s' % (i + 1, len(pats), r, list(p)))
        if r == 'sat':
            print('          class values %s' % (info,))
        # dump after EVERY pattern (lesson L72)
        json.dump({'n': n, 'm': m, 'mode': mode, 'done': i + 1, 'total': len(pats),
                   'counts': {kk: len(v) for kk, v in res.items()},
                   'detail': detail},
                  open('pdec_n%d_m%d_%s.json' % (n, m, mode), 'w'), indent=1)
    print()
    print('  sat %d  unsat %d  inconclusive %d   %.1fs'
          % (len(res['sat']), len(res['unsat']), len(res['inconclusive']),
             time.time() - t0))
    if res['sat']:
        print('  => a configuration with M <= %d EXISTS: f_%s(%d) <= %d'
              % (m, mode, n, m))
    elif not res['inconclusive']:
        print('  => NO configuration with M <= %d: f_%s(%d) > %d' % (m, mode, n, m))
    else:
        print('  => inconclusive: %d pattern(s) undecided' % len(res['inconclusive']))
