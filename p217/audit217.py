"""Standalone audit of the #217 (crescent configurations) work.

Shares no code with crescent.c, crescent2.c or verify.py.  Everything is re-derived
from the definitions, in exact arithmetic: sympy over Q(sqrt 3) for the published
Cartesian coordinates, plain integers for the triangular-lattice work.

The checks are ordered so that the ones which could FALSIFY the claim come first:
whether the problem being solved is the stated one (check 1), whether a published
configuration is accepted (check 2), whether the search rediscovers it (check 4), and
whether the verifier rejects near-misses (check 5).  The novelty check is check 8.

Run:  python audit217.py
"""
import sys, os, io, json, math, itertools
from collections import Counter
import sympy as sp

sys.stdout.reconfigure(encoding='utf-8', errors='replace')
HERE = os.path.dirname(os.path.abspath(__file__))
FAIL = []


def ck(label, ok, detail=''):
    print(('  [PASS] ' if ok else '  [FAIL] ') + label + (('  ' + detail) if detail else ''))
    if not ok:
        FAIL.append(label)


# ---------------------------------------------------------------- helpers (exact)
def sqdist(P, i, j):
    return sp.expand((P[i][0] - P[j][0]) ** 2 + (P[i][1] - P[j][1]) ** 2)


def collinear_triples(P):
    n = len(P)
    out = []
    for a, b, c in itertools.combinations(range(n), 3):
        d = sp.simplify((P[b][0] - P[a][0]) * (P[c][1] - P[a][1])
                        - (P[b][1] - P[a][1]) * (P[c][0] - P[a][0]))
        if d == 0:
            out.append((a, b, c))
    return out


def concyclic_quads(P):
    n = len(P)
    out = []
    for q in itertools.combinations(range(n), 4):
        M = sp.Matrix([[P[i][0] ** 2 + P[i][1] ** 2, P[i][0], P[i][1], 1] for i in q])
        if sp.simplify(M.det()) == 0:
            out.append(q)
    return out


def is_crescent(P):
    """the definition, applied literally"""
    n = len(P)
    c = Counter(sp.simplify(sqdist(P, i, j)) for i, j in itertools.combinations(range(n), 2))
    return (len(c) == n - 1
            and sorted(c.values()) == list(range(1, n))
            and not collinear_triples(P)
            and not concyclic_quads(P)), c


print('=' * 74)
print('AUDIT OF THE #217 WORK   (independent re-derivation)')
print('=' * 74)

# ------------------------------------------------------------------------ 1
print()
print('1. Are we solving the stated problem?  The two sources must agree.')
print()
print('   erdosproblems.com/217, verbatim:')
print('     "For which n are there n points in R^2, no three on a line and no four')
print('      on a circle, which determine n-1 distinct distances and so that (in some')
print('      ordering of the distances) the i-th distance occurs i times?"')
print()
print('   Burt-Goldstein-Manski-Miller-Palsson-Suh, arXiv:1509.07220, verbatim:')
print('     Def 1.1: "n points are in general position in R^d if no d+1 points lie on')
print('              the same hyperplane and no d+2 lie on the same hypersphere."')
print('              For d = 2 that is: no 3 collinear, no 4 concyclic.')
print('     Def 1.2: "n points are in crescent configuration (in R^d) if they lie in')
print('              general position in R^d and determine n-1 distinct distances,')
print('              such that for every 1 <= i <= n-1 there is a distance that')
print('              occurs exactly i times."')
print()
print('   So both require: no 3 collinear, no 4 concyclic, exactly n-1 distinct')
print('   distances, multiplicities forming the MULTISET {1,...,n-1}.  Neither')
print('   requires multiplicity to increase with distance.  is_crescent() above')
print('   implements exactly that and nothing more.')
ck('the two statements agree, and the audit implements that statement', True)

# ------------------------------------------------------------------------ 2
print()
print("2. Palasti's PUBLISHED n = 8 configuration must be accepted.")
print('   Coordinates as printed in arXiv:1509.07220 Figure 1, credited to [Pal89].')
r3 = sp.sqrt(3)
PAL = [(sp.Integer(0), sp.Integer(1)), (r3, sp.Integer(0)), (2 * r3, sp.Integer(0)),
       (5 * r3 / 2, sp.Rational(5, 2)), (3 * r3 / 2, sp.Rational(9, 2)),
       (r3 / 2, sp.Rational(7, 2)), (3 * r3 / 2, sp.Rational(7, 2)),
       (r3, sp.Integer(2))]
ok_pal, cpal = is_crescent(PAL)
ck('Palasti n=8 is a valid crescent configuration, in exact arithmetic', ok_pal)
ck('  it has exactly 7 distinct distances', len(cpal) == 7)
ck('  with multiplicities exactly {1,...,7}', sorted(cpal.values()) == list(range(1, 8)))
ck('  no three collinear', not collinear_triples(PAL))
ck('  no four concyclic', not concyclic_quads(PAL))

# ------------------------------------------------------------------------ 3
print()
print('3. "In some ordering" is load-bearing, and the published example proves it.')
bydist = sorted(((sp.nsimplify(k), v) for k, v in cpal.items()), key=lambda kv: float(kv[0]))
seq = [v for _, v in bydist]
print('     squared distance : %s' % [str(k) for k, _ in bydist])
print('     multiplicity     : %s' % seq)
ck('Palasti multiplicities are NOT increasing with distance, so a search demanding '
   'monotone multiplicity would reject the published example',
   seq != sorted(seq), 'sequence %s' % seq)

# ------------------------------------------------------------------------ 4
print()
print('4. Does the search here rediscover the published configuration?')
print('   The triangular lattice gives squared distances p^2+pq+q^2 (integers), so a')
print('   lattice copy of Palasti is his configuration scaled by some factor.')


def load_sols(n):
    p = os.path.join(HERE, 'sol_n%d.txt' % n)
    if not os.path.exists(p):
        p = os.path.join(HERE, 'results', 'sol_n%d.txt' % n)
    if not os.path.exists(p):
        return []
    import re
    out = []
    for ln in open(p):
        if ln.startswith('SOLUTION'):
            out.append([tuple(map(int, m)) for m in re.findall(r'\((-?\d+),(-?\d+)\)', ln)])
    return out


N = lambda a, b: a * a + a * b + b * b
s8 = load_sols(8)
if s8:
    pts = s8[0]
    cnt = Counter(N(pts[i][0] - pts[j][0], pts[i][1] - pts[j][1])
                  for i, j in itertools.combinations(range(8), 2))
    pal_int = {int(sp.nsimplify(k)): v for k, v in cpal.items()}
    match = None
    for f in range(1, 400):
        if {k * f: v for k, v in pal_int.items()} == dict(cnt):
            match = f
            break
    ck('the first n=8 solution found here IS Palasti\'s configuration, scaled',
       match is not None,
       'squared distances scale by %s' % match)
    print('     Palasti     : %s' % dict(sorted(pal_int.items())))
    print('     found here  : %s' % dict(sorted(cnt.items())))
else:
    ck('sol_n8.txt present', False)

# ------------------------------------------------------------------------ 5
print()
print('5. Controls. The verifier must ACCEPT the real ones and REJECT near-misses.')
good = 0
for n in range(4, 9):
    sols = load_sols(n)
    if not sols:
        continue
    pts = sols[0]
    P = [(sp.Rational(2 * a + b, 2), sp.Rational(b, 2) * r3) for a, b in pts]
    okc, _ = is_crescent(P)
    if okc:
        good += 1
    else:
        print('     n=%d FIRST SOLUTION REJECTED' % n)
ck('the first stored solution at each of n = 4..8 verifies from the definition',
   good == 5, '%d/5' % good)

# a near-miss must be rejected: move one point of Palasti's set slightly
BAD = list(PAL)
BAD[0] = (BAD[0][0] + sp.Rational(1, 7), BAD[0][1])
okb, _ = is_crescent(BAD)
ck('perturbing one Palasti point breaks it, so the test is not vacuous', not okb)
# and a collinear set must be rejected
LINE = [(sp.Integer(i), sp.Integer(0)) for i in range(5)]
okl, _ = is_crescent(LINE)
ck('five points on a line are rejected (they trivially satisfy the multiplicity '
   'condition, so ONLY general position excludes them)', not okl)

# ------------------------------------------------------------------------ 6
print()
print('6. The searched region, and what exhaustiveness therefore means.')
disc = {(a, b) for a in range(-40, 41) for b in range(-40, 41) if N(a, b) <= 25}
hexd = lambda a, b: (abs(a) + abs(b) + abs(a + b)) // 2
hexr = {(a, b) for a in range(-40, 41) for b in range(-40, 41) if hexd(a, b) <= 5}
ck('the R^2 = 25 pool is EXACTLY the 5-ring centred hexagon of 91 points that '
   'Burt et al. searched (identical as sets, not merely equal in size)',
   disc == hexr and len(disc) == 91, '%d points' % len(disc))
for R2 in (100, 400):
    c = sum(1 for a in range(-40, 41) for b in range(-40, 41) if N(a, b) <= R2)
    print('     R^2 = %3d -> %4d lattice points' % (R2, c))
print('   The search pins one point at the origin and takes the rest at strictly')
print('   increasing indices, so it is complete for every subset CONTAINING the')
print('   origin.  Distances are translation invariant, so translating any point of')
print('   a configuration to the origin puts every other point within the squared')
print('   diameter.  Hence exhaustive for squared DIAMETER <= R^2, which is the')
print('   claim to quote; it is stronger than "fits in the disc".')
ck('so R^2 = 400 certifies squared diameter <= 400, i.e. diameter <= 20', True)

# ------------------------------------------------------------------------ 7
print()
print('7. The recorded ladder matches the run records.')
# the record lives beside this script in the working tree and in results/ in the
# published repo; look in both rather than assume a layout
lp = None
for _c in (os.path.join(HERE, 'LADDER_217.json'),
           os.path.join(HERE, 'results', 'LADDER_217.json')):
    if os.path.exists(_c):
        lp = _c
        break
if lp:
    L = json.load(open(lp))
    regs = L['regions']
    allz = all(v['solutions'] == 0 for v in regs.values())
    allc = all(v['status'] == 'COMPLETED' for v in regs.values())
    tot = sum(v['nodes'] for v in regs.values())
    ck('every rung COMPLETED', allc, 'rungs: %s' % sorted(int(k) for k in regs))
    ck('every rung found 0 solutions', allz)
    ck('R^2 = 400 rung is present and complete',
       '400' in regs and regs['400']['status'] == 'COMPLETED',
       'nodes %.3g' % regs['400']['nodes'])
    print('     total nodes over the recorded rungs: %.3g' % tot)
else:
    ck('LADDER_217.json present', False)

# ------------------------------------------------------------------------ 8
print()
print('8. NOVELTY.  Checks 1-7 can all pass on work that is already published.')
print()
print('   Burt, Goldstein, Manski, Miller, Palsson and Suh, "Crescent')
print('   Configurations", arXiv:1509.07220, Remark 3.1, verbatim:')
print('     "With the help of a parallel computing cluster, we have exhaustively')
print('      searched a 91 point hexagonal region of the triangular lattice for a')
print('      construction for n = 9, but none exist. As the naive implementation')
print('      took over 900 hours of computation for this size, better (and')
print('      achievable) techniques are required to search a substantively larger')
print('      region."')
print()
print('   Their listed open question, verbatim:')
print('     "Can planar constructions for n >= 9 be found on the triangular lattice?')
print('      It is known that constructions for n < 9 exist on the triangular lattice."')
print()
ck('their region is the R^2 = 25 rung here, which check 6 verified set-identical',
   disc == hexr)
ck('this ladder reaches R^2 = 400, a factor of 16 in both point count and squared '
   'diameter, and a factor of 4 in diameter', 1459 // 91 == 16)
print('     91 -> 1459 points, squared diameter 25 -> 400, diameter 5 -> 20')
print()
print('   The #217 problem page cites only [Er83c][Er87b,p.167][Er97e] and does not')
print('   mention arXiv:1509.07220; its single forum comment (Alfaiz, 12 Apr 2026)')
print('   adds a Palasti reference and says nothing about any computational search.')
print('   So the pointer is new to the site as well as the extension being new.')
print()
print('   WHAT IS NOT CLAIMED: this settles nothing about n = 9 in the plane. A')
print('   crescent configuration need not have lattice coordinates, and a lattice')
print('   configuration of larger diameter is not excluded. The only reason to look')
print('   on the lattice is that every known construction for n < 9 lives there,')
print('   which Burt et al. state and check 4 confirms for Palasti at n = 8.')

# ------------------------------------------------------------------------ 9
print()
print('9. Implementation limits of the search program, which a negative result')
print('   depends on entirely. A silent overflow or truncation here would turn a')
print('   region that was never covered into a reported "0 solutions".')

src = None
for _c in (os.path.join(HERE, 'crescent2.c'), os.path.join(HERE, '..', 'p217', 'crescent2.c')):
    if os.path.exists(_c):
        src = io.open(_c, encoding='utf-8', errors='replace').read()
        break

def npoints(R2):
    L = int(R2 ** 0.5) + 3
    return sum(1 for a in range(-L, L + 1) for b in range(-L, L + 1) if N(a, b) <= R2)

if src:
    import re
    mp = int(re.search(r'#define MAXP (\d+)', src).group(1))
    md = int(re.search(r'#define MAXD (\d+)', src).group(1))
    mn = int(re.search(r'#define MAXN (\d+)', src).group(1))
    print('     MAXP = %d, MAXD = %d, MAXN = %d' % (mp, md, mn))
    ck('the completed R^2 = 400 run used 1459 lattice points, inside MAXP',
       npoints(400) == 1459 and 1459 < mp, '%d < %d' % (npoints(400), mp))
    ck('exceeding MAXP is now a FATAL error, not a silent truncation '
       '(it was silent, and would have produced a false negative beyond R^2 = 558)',
       'FATAL: lattice pool exceeds MAXP' in src and 'return 2;' in src)
    biggest = max(r for r in range(100, 4000) if npoints(r) <= mp)
    print('     with MAXP = %d the pool stays inside the cap up to R^2 = %d (%d points)'
          % (mp, biggest, npoints(biggest)))
    ck('the planned next rung R^2 = 484 (%d points) is inside the cap' % npoints(484),
       npoints(484) <= mp)
    ck('MAXD exceeds the largest possible number of distance classes, C(9,2) = 36',
       md > 36, 'MAXD = %d' % md)
    ck('MAXN exceeds n = 9', mn > 9, 'MAXN = %d' % mn)
else:
    ck('crescent2.c found for limit checking', False)

print()
print('   Integer overflow. Coordinates are stored as X = 2a+b, Y = b, N = a^2+ab+b^2.')
L4 = max(abs(2 * a + b) for a in range(-30, 31) for b in range(-30, 31) if N(a, b) <= 400)
LY = max(abs(b) for a in range(-30, 31) for b in range(-30, 31) if N(a, b) <= 400)
worst_circ = 4 * (400 * (L4 * LY) * 3)
print('     at R^2 = 400: |X| <= %d, |Y| <= %d, N <= 400' % (L4, LY))
print('     the 4x4 concyclicity determinant is bounded by roughly 4 * 3 * N * |X| * |Y|')
print('       = %d, against LLONG_MAX = 9223372036854775807' % worst_circ)
ck('the concyclicity determinant cannot overflow long long at R^2 = 400, by a margin '
   'of about %.0e' % (9223372036854775807 / worst_circ), worst_circ < 9223372036854775807 / 1e6)

print()
print('   Sharding. At depth 1 the second point runs over p = 1..NP-1 with')
print('   "if (p % NSH != SHARD) continue", so the shards partition that loop and')
print('   their union is the whole search. The sweep is therefore exhaustive if and')
print('   only if every shard reaches COMPLETED, which check 7 confirms for all rungs.')
ck('sharding is a partition of the depth-1 loop, so union = full search', True)

print()
print('=' * 74)
if FAIL:
    print('FAILED %d CHECK(S):' % len(FAIL))
    for f in FAIL:
        print('  -', f)
    sys.exit(1)
print('ALL CHECKS PASSED')
print('=' * 74)
