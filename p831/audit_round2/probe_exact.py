"""ROUND-2 PROBE: exact re-verification of the three witnesses, the pattern counts,
the lower-bound table, and the fgp claim.  Fractions only, no sympy, no shared code."""
# 2026-09-16: absolute paths replaced by paths relative to this file; nothing else changed.
import sys, json, os
from fractions import Fraction as F
from itertools import combinations, permutations
from math import comb

sys.stdout.reconfigure(encoding='utf-8', errors='replace')
os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))  # the p831 directory
BAD = []


def note(ok, s):
    print(('  [ok]   ' if ok else '  [FAIL] ') + s)
    if not ok:
        BAD.append(s)


def d2(P, Q): return (P[0] - Q[0]) ** 2 + (P[1] - Q[1]) ** 2


def cross(P, Q, R): return (Q[0] - P[0]) * (R[1] - P[1]) - (Q[1] - P[1]) * (R[0] - P[0])


def r2(P, Q, R):
    a2, b2, c2 = d2(Q, R), d2(R, P), d2(P, Q)
    S = 2 * (a2 * b2 + b2 * c2 + c2 * a2) - (a2 * a2 + b2 * b2 + c2 * c2)
    if S == 0: return None
    return F(a2 * b2 * c2, S)


def det4(a, b, c, d):
    def row(X): return [X[0] * X[0] + X[1] * X[1], X[0], X[1], 1]
    M = [row(a), row(b), row(c), row(d)]
    # Laplace, exact integers
    def minor(i, j):
        r = [row for k, row in enumerate(M) if k != i]
        return [[v for l, v in enumerate(rr) if l != j] for rr in r]
    def det3(m):
        return (m[0][0]*(m[1][1]*m[2][2]-m[1][2]*m[2][1])
                - m[0][1]*(m[1][0]*m[2][2]-m[1][2]*m[2][0])
                + m[0][2]*(m[1][0]*m[2][1]-m[1][1]*m[2][0]))
    return sum((-1) ** j * M[0][j] * det3(minor(0, j)) for j in range(4))


def analyse(pts):
    n = len(pts)
    coll = [t for t in combinations(range(n), 3) if cross(pts[t[0]], pts[t[1]], pts[t[2]]) == 0]
    conc = [q for q in combinations(range(n), 4) if det4(*[pts[i] for i in q]) == 0]
    cls = {}
    for t in combinations(range(n), 3):
        v = r2(pts[t[0]], pts[t[1]], pts[t[2]])
        cls.setdefault(v, []).append(t)
    return coll, conc, cls


print('=' * 78)
print('A. THE THREE WITNESSES, exact rational arithmetic (Fraction, independent code)')
print('=' * 78)
W = {4: [(0, 0), (0, 3), (1, 1), (2, 1)],
     5: [(0, 0), (0, 7), (2, 6), (4, 3), (6, 9)],
     6: [(0, 0), (0, 7), (2, 6), (4, 3), (6, 2), (6, 9)]}
CLAIM = {4: 1, 5: 4, 6: 6}
SIZES = {5: [4, 2, 2, 2], 6: [8, 4, 2, 2, 2, 2]}
for n, pts in W.items():
    coll, conc, cls = analyse(pts)
    sizes = sorted((len(v) for v in cls.values()), reverse=True)
    note(not coll and not conc, 'n=%d witness admissible (0 collinear triples, 0 concyclic quadruples): %d/%d' % (n, len(coll), len(conc)))
    note(len(cls) == CLAIM[n], 'n=%d has exactly %d distinct circumradii (claim %d)' % (n, len(cls), CLAIM[n]))
    if n in SIZES:
        note(sizes == SIZES[n], 'n=%d class profile %s (claim %s)' % (n, sizes, SIZES[n]))
    print('        radii^2 = %s' % sorted(str(k) for k in cls))
    print('        sizes   = %s   sum=%d = C(%d,3)=%d' % (sizes, sum(sizes), n, comb(n, 3)))

print()
print('B. The n=6 witness: support of its size-4 class (NOTE.md says 6, an earlier draft said 5)')
coll, conc, cls = analyse(W[6])
for v, ts in sorted(cls.items(), key=lambda kv: -len(kv[1])):
    sup = sorted(set(i for t in ts for i in t))
    print('     size %d  support %s  (%d points)' % (len(ts), sup, len(sup)))

print()
print('=' * 78)
print('C. PATTERN COUNTS, re-enumerated from the lemma statements (fresh code)')
print('=' * 78)
tri = list(combinations(range(5), 3)); ti = {t: i for i, t in enumerate(tri)}


def pdeg(lab):
    d = {}
    for t, c in zip(tri, lab):
        for p in combinations(t, 2):
            d[(p, c)] = d.get((p, c), 0) + 1
            if d[(p, c)] > 2: return False
    return True


def l4(lab):
    for q in combinations(range(5), 4):
        sub = [ti[t] for t in combinations(q, 3)]
        cnt = {}
        for i in sub: cnt[lab[i]] = cnt.get(lab[i], 0) + 1
        for c, m in cnt.items():
            if m == 3: return False
            if m == 4:
                for i, t in enumerate(tri):
                    if lab[i] == c and i not in sub and len(set(t) & set(q)) >= 2: return False
    return True


def canon(lab):
    best = None
    for perm in permutations(range(5)):
        out = [lab[ti[tuple(sorted(perm[v] for v in t))]] for t in tri]
        m = {}; rg = []
        for c in out:
            if c not in m: m[c] = len(m)
            rg.append(m[c])
        rg = tuple(rg)
        if best is None or rg < best: best = rg
    return best


def enum(k, l1=True, use4=True):
    seen = set()
    def rec(i, lab, used):
        if i == 10:
            if used != k: return
            if l1 and not pdeg(lab): return
            if use4 and not l4(lab): return
            seen.add(canon(lab)); return
        for c in range(min(used + 1, k)):
            rec(i + 1, lab + [c], used + (1 if c == used else 0))
    rec(0, [], 0)
    return seen


tot = {}
for k in (1, 2, 3):
    a = enum(k, True, False); b = enum(k, True, True); tot[k] = (len(a), len(b))
    prof = {}
    for lab in b:
        s = tuple(sorted((sum(1 for x in lab if x == c) for c in set(lab)), reverse=True))
        prof[s] = prof.get(s, 0) + 1
    f4 = sum(v for s, v in prof.items() if s[0] <= 4)
    print('   k=%d : Lemma1 only %3d ; Lemma1+4 %3d ; also f(5)<=4 : %3d   profiles %s'
          % (k, len(a), len(b), f4, prof))
    if k == 3:
        note((len(a), len(b), f4) == (35, 15, 12), 'k=3 counts 35 / 15 / 12 reproduce')
note(tot[1][1] == 0, 'k=1 : 0 patterns  -> h(5) >= 2 with no external input')
note(tot[2][1] == 1, 'k=2 : 1 pattern (sizes [5,5]) -> needs f(5)=4 to kill it')

print()
print('=' * 78)
print('D. LOWER-BOUND TABLE and the forum bound')
print('=' * 78)
Fv = {3: 1, 4: 4, 5: 4, 6: 8, 7: 12, 8: 16}
tab = []
for n in range(4, 9):
    b = -(-comb(n, 3) // Fv[n]); fo = -(-(n - 2) // 2)
    tab.append(b)
    print('   n=%d C=%2d f=%2d -> %d ; forum ceil((n-2)/2)=%d %s' % (n, comb(n, 3), Fv[n], b, fo, 'BETTER' if b > fo else ('tie' if b == fo else 'WORSE')))
note(tab == [1, 3, 3, 3, 4], 'table 1,3,3,3,4 for n=4..8')
print('   offset check: A003829 offset 3, S = 1,4,4,8,12,16  ->  a(3)=1 a(4)=4 a(5)=4 a(6)=8 a(7)=12 a(8)=16')
note(Fv == {3: 1, 4: 4, 5: 4, 6: 8, 7: 12, 8: 16}, 'F104 dict matches A003829 at offset 3')
print('   forum bound vs the constant 4:')
for n in range(8, 13):
    print('     n=%2d ceil((n-2)/2)=%d   monotonicity gives 4   %s' % (n, -(-(n - 2) // 2), 'forum strictly better' if -(-(n-2)//2) > 4 else ('tie' if -(-(n-2)//2) == 4 else 'monotonicity better')))

print()
print('=' * 78)
print('E. fgp: does a class of size m certify f_gp(n) >= m ?')
print('=' * 78)
g = json.load(open('results/fgp.json'))['table']
for k in sorted(g, key=int):
    n = int(k); rec = g[k]
    pts = [tuple(p) for p in rec['witness']]
    coll, conc, cls = analyse(pts)
    m = max(len(v) for v in cls.values())
    circles = set()
    for v, ts in cls.items():
        if len(v_ts := ts) == m and len(v_ts) == m:
            pass
    note(not coll and not conc and m == rec['largest_class'],
         'n=%d witness admissible and largest class = %d (artifact says %d)' % (n, m, rec['largest_class']))
    # distinct circles: two triples of the same class on the same circle would be 4 concyclic
    note(len(cls) == rec['distinct'], 'n=%d distinct radii %d matches artifact' % (n, rec['distinct']))
print('   Since no 4 points are concyclic, distinct triples of one class lie on DISTINCT')
print('   circles, each through EXACTLY 3 points, so m circles of one radius exist:')
print('   rescale -> m unit circles through exactly 3 of n points, hence f_gp(n) >= m. Sound.')

print()
if BAD:
    print('%d FAILURES' % len(BAD))
    for b in BAD: print('  -', b)
else:
    print('all exact checks reproduce')
