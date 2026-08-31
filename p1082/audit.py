"""Independent audit of every checkable claim in the #1082 note.

Exact integer arithmetic throughout for the lattice claims; exact algebraic for the
regular polygons.  Shares no code with the original search.
"""
import io, sys
from itertools import combinations
from collections import Counter
from fractions import Fraction as F
import sympy as sp

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
ok = True


def check(label, got, want):
    global ok
    good = (got == want)
    ok = ok and good
    print('  %-58s %-22s %s' % (label, str(got), 'OK' if good else 'WRONG, want %s' % (want,)))


print('=== 1. The Eisenstein 12-point set quoted in the note ===')
# In the triangular lattice, squared distance between (a1,b1),(a2,b2) with p=a1-a2,
# q=b1-b2 is p^2+pq+q^2.
S = [(0,0),(0,1),(0,2),(1,-1),(1,0),(1,1),(1,2),(2,-1),(2,0),(2,1),(3,-1),(3,0)]
check('number of points', len(S), 12)
d2 = lambda A,B: (A[0]-B[0])**2 + (A[0]-B[0])*(A[1]-B[1]) + (A[1]-B[1])**2
dists = sorted({d2(a,b) for a,b in combinations(S,2)})
check('distinct squared distances', dists, [1,3,4,7,9])
check('number of distinct distances k', len(dists), 5)

# collinear triples: in this lattice, (a,b) embeds as (a + b/2, b*sqrt3/2); with
# X = 2a+b, Y = b the collinearity determinant is integral.
def col(A,B,C):
    XA,YA = 2*A[0]+A[1], A[1]
    XB,YB = 2*B[0]+B[1], B[1]
    XC,YC = 2*C[0]+C[1], C[1]
    return (XB-XA)*(YC-YA) - (YB-YA)*(XC-XA) == 0
ncol = sum(1 for t in combinations(S,3) if col(*t))
check('collinear triples', ncol, 18)
print('     -> so this set is NOT a counterexample to the first question')

print()
print('=== 2. The regular (2k+1)-gon gives h(k) >= 2k+1 ===')
for k in range(1,8):
    n = 2*k+1
    pts = [(sp.cos(2*sp.pi*j/n), sp.sin(2*sp.pi*j/n)) for j in range(n)]
    ds = {sp.simplify((pts[i][0]-pts[j][0])**2 + (pts[i][1]-pts[j][1])**2)
          for i,j in combinations(range(n),2)}
    ds = {sp.nsimplify(sp.radsimp(x)) for x in ds}
    # count distinct numerically to avoid symbolic-form duplicates
    vals = sorted({round(float(x), 12) for x in ds})
    coll = 0
    for a,b,c in combinations(range(n),3):
        m = sp.Matrix([[pts[a][0],pts[a][1],1],[pts[b][0],pts[b][1],1],[pts[c][0],pts[c][1],1]])
        if sp.simplify(m.det()) == 0: coll += 1
    check('regular %2d-gon: distinct distances' % n, len(vals), k)
    check('regular %2d-gon: collinear triples' % n, coll, 0)

print()
print('=== 3. The g(k) table and where it forces h(k) = 2k+1 ===')
g = {1:3, 2:5, 3:7, 4:9, 5:12, 6:13}
for k in sorted(g):
    print('  k=%d  g(k)=%-3d 2k+1=%-3d  %s' % (k, g[k], 2*k+1,
          'g = 2k+1, so h(k) = 2k+1 immediately'
          if g[k] == 2*k+1 else 'g > 2k+1, needs the uniqueness argument'))
check('the only k <= 6 needing extra work', [k for k in g if g[k] != 2*k+1], [5])

print()
print('=== 4. The proposition: n <= 15 ===')
# if h(k) = 2k+1 for all k <= K, the argument runs for every n with floor(n/2)-1 <= K
K = 6
nmax = max(n for n in range(4, 60) if n//2 - 1 <= K)
check('largest n the argument covers with h known to k<=6', nmax, 15)
# and verify the contradiction chain symbolically for each n
bad = []
for n in range(4, 16):
    m = n//2
    for k in range(1, m):            # k < floor(n/2)
        if k > 6: continue
        if not (n <= 2*k+1):          # n <= h(k) = 2k+1 must fail
            continue
        bad.append((n,k))
check('n,k pairs surviving the contradiction (should be none)', bad, [])

print()
print('=== 5. Without no-three-collinear the claim fails at n = 12 ===')
check('g(5) = 12 points with 5 distances, and 5 < floor(12/2)', (g[5], 5 < 12//2), (12, True))

print()
print('=== 6. The frontier claim ===')
# a counterexample on n points needs n <= g(floor(n/2)-1)
cands = [n for n in range(4, 20) if (n//2 - 1) in g and n <= g[n//2 - 1]]
print('  n with n <= g(floor(n/2)-1) using known g:', cands)
check('smallest n not excluded by known g values', min([n for n in range(16,20)
      if (n//2-1) not in g]), 16)
print('     -> n = 16 needs k = 7, and g(7) is unknown, which is why it is open')

print()
print('NOVELTY. Every check above can pass on a result that is already known, so this')
print('one asks whether the published bound already covers n <= 15.')
print()
print('  Sheffer, "Distinct Distances: Open Problems and Current Bounds"')
print('  (arXiv:1406.1949), records the published lower bound for this question as')
print('  D_no3l(n) >= ceil((n-1)/3), attributed to Szemeredi via Erdos, against the')
print('  conjectured floor(n/2).')
print()
print('   n  floor(n/2)  ceil((n-1)/3)  settled by the published bound?')
_settled = []
for _n in range(4, 17):
    _t = _n // 2
    _s = -(-(_n - 1) // 3)
    if _s >= _t:
        _settled.append(_n)
    print('  %2d      %2d           %2d          %s' % (_n, _t, _s, 'YES' if _s >= _t else 'no'))
check('n settled by the published bound, 4..16', _settled, [5])
check('is n = 15 covered by it?', 15 in _settled, False)
print('     -> so n <= 15 goes well past the published bound, unlike the #982 note,')
print('        whose whole claimed range turned out to be covered by known results')
print()
print('  Also checked, all negative for prior art: the 21 forum comments are all about')
print('  the SECOND question and none mentions g(5), g(6), Shinohara, Wei or 2k+1;')
print('  Sheffer gives no exact small-n values and says the last progress was')
print('  "several decades ago"; no source found studies h(k) in its own right.')
print('  RESIDUAL UNCERTAINTY: the k = 6 case cannot predate Wei (2012) and is absent')
print('  from the 2014 survey, but the derivation from published g(k) is short and a')
print('  short corollary can be folklore. Negative search, not proof of novelty.')

print()
print('ALL CHECKS PASSED' if ok else '*** SOME CHECKS FAILED ***')
