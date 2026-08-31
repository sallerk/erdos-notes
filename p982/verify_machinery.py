"""HARD RULE: verify the verifier against known ground truth BEFORE searching."""
import sys, math
from fractions import Fraction
from core import (cross, d2, convex_hull, in_strict_convex_position,
                  per_vertex_counts, per_vertex_class_sizes, check982,
                  regular_ngon_per_vertex, subset_of_regular_mgon_per_vertex,
                  circdiff)

FAIL = []
def chk(cond, msg):
    print(("  OK   " if cond else "  FAIL ") + msg)
    if not cond:
        FAIL.append(msg)

print("=" * 72)
print("TEST 1  regular n-gon: every vertex must see exactly floor(n/2) distances")
print("        (exact index arithmetic in Z_n -- the regular n-gon is NOT a")
print("         lattice polygon, so this is done symbolically, not numerically)")
print("=" * 72)
for n in range(3, 41):
    pv = regular_ngon_per_vertex(n)
    chk(set(pv) == {n // 2}, f"n={n:3d}: per-vertex counts all == floor(n/2) = {n//2}"
                             f"  (got {sorted(set(pv))})")

print()
print("=" * 72)
print("TEST 1b independent HIGH-PRECISION cross-check of the regular n-gon")
print("        (mpmath, 60 digits; used only as a cross-check, never to certify)")
print("=" * 72)
try:
    from mpmath import mp, mpf, cos, sin, pi
    mp.dps = 60
    for n in [5, 7, 8, 9, 12, 13, 20, 21]:
        P = [(cos(2 * pi * k / n), sin(2 * pi * k / n)) for k in range(n)]
        cnt = []
        for i in range(n):
            vals = []
            for j in range(n):
                if i == j:
                    continue
                dd = (P[i][0] - P[j][0]) ** 2 + (P[i][1] - P[j][1]) ** 2
                if not any(abs(dd - v) < mpf(10) ** (-40) for v in vals):
                    vals.append(dd)
            cnt.append(len(vals))
        chk(set(cnt) == {n // 2}, f"n={n:3d}: mpmath 60-digit agrees, all == {n//2}")
except ImportError:
    print("  (mpmath unavailable, skipped)")

print()
print("=" * 72)
print("TEST 2  convex-position test: accept convex, reject an interior point")
print("=" * 72)
# integer approximations to regular polygons are NOT reliable, so use exact
# convex lattice polygons instead.
sq = [(0, 0), (1, 0), (1, 1), (0, 1)]
chk(in_strict_convex_position(sq), "unit square is in strict convex position")
hexa = [(0, 0), (2, 0), (3, 2), (2, 4), (0, 4), (-1, 2)]
chk(in_strict_convex_position(hexa), "a convex lattice hexagon accepted")
chk(not in_strict_convex_position(sq + [(0, 0)]), "duplicate point rejected")
# interior point
big = [(0, 0), (10, 0), (10, 10), (0, 10), (5, 4)]
chk(not in_strict_convex_position(big), "square + INTERIOR point rejected")
# collinear boundary point (a 180-degree 'vertex') must be rejected
coll = [(0, 0), (1, 0), (2, 0), (1, 3)]
chk(not in_strict_convex_position(coll), "collinear boundary point rejected")
# a genuine convex 20-gon from the lattice
import itertools
def lattice_convex_polygon(k):
    """primitive-vector convex polygon: sort primitive vectors by angle."""
    vs = [(a, b) for a in range(-k, k + 1) for b in range(-k, k + 1)
          if (a, b) != (0, 0) and math.gcd(abs(a), abs(b)) == 1]
    vs.sort(key=lambda v: math.atan2(v[1], v[0]))
    pts, x, y = [], 0, 0
    for a, b in vs:
        pts.append((x, y)); x += a; y += b
    return pts
p = lattice_convex_polygon(2)
chk(in_strict_convex_position(p), f"primitive-vector convex {len(p)}-gon accepted")

print()
print("=" * 72)
print("TEST 3  the counterexample predicate must NOT fire on the regular n-gon")
print("=" * 72)
for n in [6, 7, 8, 9, 12, 21]:
    pv = regular_ngon_per_vertex(n)
    chk(max(pv) > n // 2 - 1,
        f"n={n}: regular n-gon max per-vertex {max(pv)} > floor(n/2)-1 = {n//2-1}")

print()
print("=" * 72)
print("TEST 4  keep #982 (per-vertex) separate from Altman (TOTAL) and from")
print("        #1082 (no-3-collinear, not convex).  Harborth H_8 must have")
print("        per-point count 3 (= counterexample to #1082 q2) but must NOT")
print("        be convex, so it must NOT register as a #982 counterexample.")
print("=" * 72)
# H_8 exactly in Q(sqrt 3): square (+-1,+-1) with equilateral triangles outward
s3 = None
class Q3:
    __slots__ = ('a', 'b')
    def __init__(self, a, b=0): self.a = Fraction(a); self.b = Fraction(b)
    def __add__(s, o): o = q3(o); return Q3(s.a + o.a, s.b + o.b)
    def __sub__(s, o): o = q3(o); return Q3(s.a - o.a, s.b - o.b)
    def __mul__(s, o): o = q3(o); return Q3(s.a*o.a + 3*s.b*o.b, s.a*o.b + s.b*o.a)
    __radd__ = __add__; __rmul__ = __mul__
    def __rsub__(s, o): return q3(o) - s
    def __neg__(s): return Q3(-s.a, -s.b)
    def __eq__(s, o): o = q3(o); return s.a == o.a and s.b == o.b
    def __hash__(s): return hash((s.a, s.b))
    def __lt__(s, o):  # sqrt3 = 1.7320508...
        o = q3(o); d = (s.a - o.a) + (s.b - o.b) * Fraction(17320508075688772935, 10**19)
        return d < 0
    def __repr__(s): return f"({s.a}+{s.b}r3)"
def q3(o): return o if isinstance(o, Q3) else Q3(o)

one, zero = Q3(1), Q3(0)
r3 = Q3(0, 1)
H8 = [(Q3(1), Q3(1)), (Q3(-1), Q3(1)), (Q3(-1), Q3(-1)), (Q3(1), Q3(-1)),
      (Q3(0), one + r3), (Q3(0), -(one + r3)),
      (one + r3, Q3(0)), (-(one + r3), Q3(0))]
def d2q(p, q_): return (p[0]-q_[0])*(p[0]-q_[0]) + (p[1]-q_[1])*(p[1]-q_[1])
per = [len({d2q(H8[i], H8[j]) for j in range(8) if j != i}) for i in range(8)]
tot = len({d2q(H8[i], H8[j]) for i in range(8) for j in range(i+1, 8)})
chk(per == [3]*8, f"H_8: every point sees exactly 3 distances (got {per})")
chk(tot == 4, f"H_8: 4 distinct distances in TOTAL (got {tot}) -- so it is NOT a "
              f"counterexample to Altman/#1082-q1 (needs < floor(8/2)=4)")
# convexity of H_8: the 4 square corners are inside the hull of the other 4
def crossq(a, b, c): return (b[0]-a[0])*(c[1]-a[1]) - (b[1]-a[1])*(c[0]-a[0])
outer = [H8[4], H8[6], H8[5], H8[7]]  # (0,1+r3),(1+r3,0),(0,-1-r3),(-1-r3,0)
def inside(pt, poly):
    n = len(poly); s = []
    for i in range(n):
        s.append(crossq(poly[i], poly[(i+1) % n], pt))
    return all(x < zero for x in s) or all(zero < x for x in s)
chk(all(inside(H8[i], outer) for i in range(4)),
    "H_8: the 4 square corners lie strictly INSIDE the hull of the other 4")
chk(per[0] == 3 and 3 <= 8//2 - 1,
    "H_8 would meet the #982 per-vertex bound (3 <= 3) -- it fails only on CONVEXITY. "
    "This is exactly why #1082's refutation does not touch #982.")

print()
print("=" * 72)
print("TEST 5  n points on a COMMON CIRCLE can never be a counterexample.")
print("        Reason (exact): for concyclic points, two chords from a vertex v")
print("        are equal iff the far endpoints are mirror images in the diameter")
print("        through v.  So every distance class at v has size <= 2, hence")
print("        #classes >= ceil((n-1)/2) = floor(n/2).  Verified below on")
print("        subsets of regular m-gons via exact Z_m index arithmetic.")
print("=" * 72)
import random
random.seed(7)
bad = 0; tested = 0
for m in range(5, 60):
    for n in range(4, min(m, 16) + 1):
        for _ in range(30):
            S = sorted(random.sample(range(m), n))
            pv = subset_of_regular_mgon_per_vertex(S, m)
            tested += 1
            if max(pv) < n // 2:
                bad += 1
                print("   COUNTEREXAMPLE?!", m, S, pv)
chk(bad == 0, f"{tested} random subsets of regular m-gons (5<=m<60): none has "
              f"max per-vertex < floor(n/2)")
# and the max class size claim
bad2 = 0
for m in range(5, 40):
    for _ in range(200):
        n = random.randint(4, min(m, 14))
        S = sorted(random.sample(range(m), n))
        for i in S:
            c = {}
            for j in S:
                if j != i:
                    d = circdiff(i, j, m); c[d] = c.get(d, 0) + 1
            if max(c.values()) > 2:
                bad2 += 1
chk(bad2 == 0, "concyclic: no distance class at a vertex ever exceeds size 2")

print()
print("=" * 72)
print("TEST 6  pigeonhole necessary condition (this is ERDOS'S OWN remark,")
print("        restated; not new).  A counterexample needs, at every vertex,")
print("        'excess' E_v = sum over classes of max(0, size-2) >= 1 (n even),")
print("        >= 2 (n odd).  In particular >= 3 vertices equidistant from EVERY")
print("        vertex.  Check the arithmetic exhaustively for n <= 200.")
print("=" * 72)
ok = True
for n in range(4, 201):
    k = n // 2 - 1           # allowed classes
    need = (n - 1) - 2 * k   # minimum total excess
    want = 1 if n % 2 == 0 else 2
    if k <= 0:
        continue
    if need != want:
        ok = False; print("   mismatch at n =", n, need, want)
chk(ok, "excess >= 1 for even n and >= 2 for odd n, for all 4 <= n <= 200")

print()
print("=" * 72)
print("TEST 7  a hand-built convex lattice polygon: sanity of per-vertex counts")
print("=" * 72)
ok_, rep = check982(hexa, verbose=True)
chk(not ok_, "convex lattice hexagon is not a counterexample")
chk(rep['per_vertex'] == per_vertex_counts(hexa), "per_vertex_counts consistent")

print()
print("=" * 72)
if FAIL:
    print(f"VERIFIER FAILED {len(FAIL)} CHECK(S):")
    for m in FAIL:
        print("   -", m)
    sys.exit(1)
print("ALL VERIFIER CHECKS PASSED")
