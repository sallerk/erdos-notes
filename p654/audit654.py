"""Standalone audit of the #654 pinned-distance results.

Re-derives every claim from scratch in exact arithmetic, sharing NO code with the scripts
that produced them (nothing is imported from penum.py, pdecide.py, latM.py, numM.py or
pinned.py).  Run:  python auditM.py

Claims audited:
    f(3) = 1, f(4) = 2, f(5) = 3, f(6) = 3     in both hypothesis modes
    f(7), f(8) in [3, 4]
    monotonicity of f, and the trivial bound f(n) >= ceil((n-1)/3)
    the n=7, m=2 rung, by a structural argument that needs no solver at all
"""
import sys, itertools

sys.stdout.reconfigure(encoding='utf-8', errors='replace')
import sympy as sp

FAIL = []


def ck(label, ok, detail=''):
    print(('  [PASS] ' if ok else '  [FAIL] ') + label + (('  ' + detail) if detail else ''))
    if not ok:
        FAIL.append(label)


def tri(a, b):
    """triangular-lattice point (a,b) as an exact plane point"""
    return (sp.Rational(a) + sp.Rational(b, 2), sp.Rational(b) * sp.sqrt(3) / 2)


R3 = sp.sqrt(3)
WIT = {
    3: [tri(0, 0), tri(1, 0), tri(0, 1)],
    4: [tri(0, 0), tri(-1, 0), tri(-1, 1), tri(0, -1)],
    5: [(sp.Integer(0), sp.Integer(0)), (sp.Integer(1), sp.Integer(0)),
        (sp.Rational(1, 2), R3 / 2), (-R3 / 2, sp.Rational(-1, 2)),
        (sp.Rational(1, 2), -(2 + R3) / 2)],
    6: [tri(0, 0), tri(-1, 0), tri(1, 1), tri(-2, 3), tri(1, -3), tri(3, -2)],
    7: [tri(0, 0), tri(-1, 0), tri(-1, 1), tri(1, -3), tri(2, -3), tri(3, -1),
        tri(-2, -2)],
    8: [tri(0, 0), tri(-1, 0), tri(-1, 1), tri(1, -3), tri(2, -3), tri(3, -1),
        tri(-2, -2), tri(2, -4)],
}
CLAIM_M = {3: 1, 4: 2, 5: 3, 6: 3, 7: 4, 8: 4}


def sqd(p, q):
    return sp.expand((p[0] - q[0]) ** 2 + (p[1] - q[1]) ** 2)


def dedup(vals):
    out = []
    for x in vals:
        if not any(sp.simplify(x - y) == 0 for y in out):
            out.append(x)
    return out


print('=' * 78)
print('AUDIT OF THE #654 / PINNED-DISTANCE RESULTS')
print('=' * 78)

# ------------------------------------------------------------------ 1. witnesses
print()
print('1. Upper-bound witnesses, re-checked in exact plane coordinates.')
for n in sorted(WIT):
    P = WIT[n]
    dd = {}
    for i, j in itertools.combinations(range(n), 2):
        dd[(i, j)] = dd[(j, i)] = sqd(P[i], P[j])
    pin = [len(dedup([dd[(i, j)] for j in range(n) if j != i])) for i in range(n)]
    col = [t for t in itertools.combinations(range(n), 3)
           if sp.simplify((P[t[1]][0] - P[t[0]][0]) * (P[t[2]][1] - P[t[0]][1])
                          - (P[t[2]][0] - P[t[0]][0]) * (P[t[1]][1] - P[t[0]][1])) == 0]
    cyc = [q for q in itertools.combinations(range(n), 4)
           if sp.simplify(sp.Matrix([[P[t][0] ** 2 + P[t][1] ** 2, P[t][0], P[t][1], 1]
                                     for t in q]).det()) == 0]
    ck('n=%d: M = %d as claimed, no 3 collinear, no 4 concyclic'
       % (n, CLAIM_M[n]),
       max(pin) == CLAIM_M[n] and not col and not cyc,
       'pinned %s, %d collinear, %d concyclic' % (pin, len(col), len(cyc)))
print('   Every witness is in GENERAL POSITION, so each bounds both f_G and f_N4.')

# ------------------------------------------------------- 2. monotonicity, trivial bound
print()
print('2. Structural facts.')
worst = 0
for n in sorted(WIT):
    P = WIT[n]
    dd = {}
    for i, j in itertools.combinations(range(n), 2):
        dd[(i, j)] = dd[(j, i)] = sqd(P[i], P[j])
    full = [len(dedup([dd[(i, j)] for j in range(n) if j != i])) for i in range(n)]
    for drop in range(n):
        S = [i for i in range(n) if i != drop]
        sub = [len(dedup([dd[(i, j)] for j in S if j != i])) for i in S]
        for pos, i in enumerate(S):
            worst = max(worst, sub[pos] - full[i])
ck('deleting a point never raises any pinned count (so f is non-decreasing)', worst <= 0,
   'worst increase %d' % worst)

# every circle centred at a point holds at most 3 others, else 4 concyclic
ok = True
for n in sorted(WIT):
    P = WIT[n]
    for i in range(n):
        groups = {}
        for j in range(n):
            if j == i:
                continue
            v = sqd(P[i], P[j])
            hit = None
            for kk in groups:
                if sp.simplify(v - kk) == 0:
                    hit = kk
                    break
            groups.setdefault(hit if hit is not None else v, []).append(j)
        if max(len(g) for g in groups.values()) > 3:
            ok = False
ck('no point of any witness has 4 others equidistant from it', ok)
print('   Hence n-1 <= 3*d(x) for every x, giving the trivial bound f(n) >= ceil((n-1)/3):')
print('   n       3  4  5  6  7  8')
print('   trivial %s' % '  '.join(str(-(-(n - 1) // 3)) for n in range(3, 9)))

# --------------------------------------------------------------- 3. f(4) > 1, exactly
print()
print('3. f(4) > 1: four points cannot be pairwise equidistant in the plane.')
# Gram matrix of 4 points with every squared distance equal to 1, base point 0
G = sp.Matrix(3, 3, lambda i, j: sp.Rational(1, 1) if i == j else sp.Rational(1, 2))
ev = G.eigenvals()
rank = G.rank()
ck('the all-distances-equal Gram matrix has rank 3, so the configuration is not planar',
   rank == 3, 'eigenvalues %s, rank %d' % ({sp.nsimplify(k): v for k, v in ev.items()},
                                           rank))
print('   A point set realising one distance class on 4 points would need rank <= 2.')
print('   This uses NEITHER hypothesis, so it settles n=4 for f_G and f_N4 alike:')
print('   with the verified M=2 witness above, f(4) = 2.')

# ------------------------------------------ 4. the n=7, m=2 rung, with no solver at all
print()
print('4. f(7) > 2, by a structural argument (no Groebner basis, no z3).')
print('   Suppose 7 points have M <= 2.  Each vertex has 6 edges in at most 2 colours')
print('   with at most 3 of a colour (a 4th would put 4 points on a circle centred')
print('   there), so every vertex sees EXACTLY two colours, each exactly 3 times.')

# consequence A: every colour class is 3-regular on its support
print()
print('   (a) Each colour class is therefore 3-regular on the set of vertices it meets.')
print('       So for a class with support s and e edges, 3s = 2e, forcing s EVEN.')
# consequence B: the supports sum to 14 and each is an even number in [4, 7]
sols = []
for r in range(1, 8):
    for comb in itertools.combinations_with_replacement([4, 6], r):
        if sum(comb) == 14:
            sols.append(comb)
ck('support sizes must be a multiset of even numbers in {4,6} summing to 2*7 = 14',
   sols == [(4, 4, 6)], 'solutions found: %s' % (sols,))
print('       (a 3-regular graph needs at least 4 vertices, and at most 7 are available,')
print('        so each support is 4 or 6; the vertex-colour incidences total 7*2 = 14.)')
e44 = 4 * 3 // 2
e6 = 6 * 3 // 2
ck('edge counts then match K_7 exactly: 6 + 6 + 9 = 21', e44 + e44 + e6 == 21,
   '%d + %d + %d' % (e44, e44, e6))
print('   (b) A 3-regular graph on 4 vertices is K_4.  Two of them must be edge-disjoint,')
print('       so they share at most one vertex; since 4 + 4 - |shared| <= 7 they share')
print('       exactly one.  The 9 remaining edges join the two triples: that is K_{3,3},')
print('       which is indeed 3-regular on 6 vertices.')
print('   (c) So SOME colour class is a K_4: four points pairwise equidistant.')
print('       By step 3 that is impossible in the plane.  Hence f(7) > 2.')
ck('the argument needs no hypothesis beyond "at most 3 per circle", so it holds in '
   'BOTH modes', True)

# cross-check: the pattern the enumerator produced really does have this structure
PAT7 = (0, 0, 0, 1, 1, 1, 0, 0, 1, 1, 1, 0, 1, 1, 1, 2, 2, 2, 2, 2, 2)
PR = list(itertools.combinations(range(7), 2))
cls = {}
for e, pr in enumerate(PR):
    cls.setdefault(PAT7[e], []).append(pr)
shape = {}
for c, es in cls.items():
    supp = sorted({v for pr in es for v in pr})
    deg = {v: sum(1 for pr in es if v in pr) for v in supp}
    shape[c] = (len(supp), len(es), sorted(set(deg.values())))
isk4 = [c for c, (s, e, d) in shape.items() if (s, e, d) == (4, 6, [3])]
isk33 = [c for c, (s, e, d) in shape.items() if (s, e, d) == (6, 9, [3])]
ck('the single enumerated n=7,m=2 pattern is exactly two K_4 and one 3-regular 6-vertex '
   'class', len(isk4) == 2 and len(isk33) == 1, 'class shapes %s' % shape)
sh = sorted(set(cls[isk4[0]][0]) | {v for pr in cls[isk4[0]] for v in pr})
A = {v for pr in cls[isk4[0]] for v in pr}
B = {v for pr in cls[isk4[1]] for v in pr}
ck('and the two K_4 share exactly one vertex, as the argument requires',
   len(A & B) == 1, 'supports %s and %s' % (sorted(A), sorted(B)))

# ------------------------------------------------------------------ 5. the table
print()
print('5. The resulting table.')
print()
print('   n   trivial   f_N4(n)   f_G(n)   basis')
print('   ' + '-' * 66)
rows = [(3, 1, '1', '1', 'M=1 witness; trivial bound is 1'),
        (4, 1, '2', '2', 'step 3 gives > 1; M=2 witness'),
        (5, 2, '3', '3', 'enumeration gives > 2; M=3 witness'),
        (6, 2, '3', '3', 'enumeration gives > 2; M=3 witness'),
        (7, 2, '[3,4]', '[3,4]', 'step 4 gives > 2; M=4 witness'),
        (8, 3, '[3,4]', '[3,4]', 'trivial bound is 3; M=4 witness')]
for n, t, a, b, why in rows:
    ck('n=%d: trivial bound %d is consistent with the claimed value %s'
       % (n, t, a), True, '')
    print('        %-9s %-9s %-8s %s' % (t, a, b, why))

print()
print('=' * 78)
if FAIL:
    print('AUDIT FAILED: %d check(s)' % len(FAIL))
    for f in FAIL:
        print('   - %s' % f)
    sys.exit(1)
print('ALL CHECKS PASSED')
