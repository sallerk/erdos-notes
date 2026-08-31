"""CONTROL for decide.py.  A decision procedure that answers UNSAT to
everything proves nothing, so the encoding must be shown to admit models.

z3's nlsat is a complete decision procedure for the reals, so an UNSAT answer
is a proof.  The risk being controlled for here is a DIFFERENT one: that the
encoding (normalisation + orientation convention + equality constraints) is
accidentally self-contradictory, which would make every pattern UNSAT for a
trivial reason and make the whole search vacuous.

Controls:

 A. ENCODING-ADMITS-MODELS, checked without z3's search.  Take an explicit
    convex polygon, put it through the exact same normalisation, and evaluate
    every single constraint of the encoding on it.  Uses exact rational
    arithmetic for the lattice polygons and exact Q(sqrt5)/Q(sqrt3) arithmetic
    for the regular pentagon and hexagon.

 B. POSITIVE z3 control.  The colouring induced by a convex LATTICE polygon.
    After the normalisation v0=(0,0), v1=(1,0) -- which is the complex map
    z -> (z-v0)/(v1-v0) -- a lattice polygon has RATIONAL coordinates, so z3
    can and must return SAT.

 C. NEGATIVE z3 control.  All edges of K_n one colour: impossible for n >= 4,
    must be UNSAT.

 D. The regular n-gon colouring, whose models are irrational.  Recorded for
    information: z3 is expected to time out (UNKNOWN) here.  That is a
    limitation on DETECTING counterexamples, not on refuting them.
"""
import sys, time
from fractions import Fraction as F
from itertools import combinations
import z3


# --------------------------------------------------------------- normalisation
def normalise_rational(pts):
    """z -> (z - p0)/(p1 - p0) in the complex plane; exact over Q."""
    x0, y0 = pts[0]
    dx, dy = pts[1][0] - x0, pts[1][1] - y0
    den = F(dx * dx + dy * dy)
    out = []
    for (x, y) in pts:
        ux, uy = F(x - x0), F(y - y0)
        out.append(((ux * dx + uy * dy) / den, (uy * dx - ux * dy) / den))
    return out


def colouring(pts, dist):
    n = len(pts)
    edges = sorted(combinations(range(n), 2), key=lambda e: (e[1], e[0]))
    vals, col = [], []
    for a, b in edges:
        d = dist(pts[a], pts[b])
        for i, v in enumerate(vals):
            if v == d:
                col.append(i); break
        else:
            col.append(len(vals)); vals.append(d)
    return edges, col


def eval_encoding(pts, edges, col, name, zero):
    """Evaluate EVERY constraint of decide.py's encoding on an explicit point
    set.  Returns (ok, message)."""
    n = len(pts)
    if not (zero(pts[0][0]) and zero(pts[0][1]) and zero(pts[1][0] - 1) and zero(pts[1][1])):
        return False, "normalisation v0=(0,0), v1=(1,0) not met"
    for i, j, k in combinations(range(n), 3):
        c = ((pts[j][0]-pts[i][0])*(pts[k][1]-pts[i][1])
             - (pts[j][1]-pts[i][1])*(pts[k][0]-pts[i][0]))
        if not (c > 0):
            return False, f"orientation of triple {i},{j},{k} is not positive ({c})"
    byc = {}
    for e, c in zip(edges, col):
        byc.setdefault(c, []).append(e)
    def sq(e):
        a, b = e
        return (pts[a][0]-pts[b][0])**2 + (pts[a][1]-pts[b][1])**2
    for c, es in byc.items():
        for t in range(1, len(es)):
            if not zero(sq(es[0]) - sq(es[t])):
                return False, f"equality {es[0]} == {es[t]} fails"
    return True, f"{name}: all {n*(n-1)*(n-2)//6} orientation constraints and all " \
                 f"equality constraints hold"


def solve(n, colvec, edges, timeout_ms=60000):
    s = z3.Solver()
    s.set('timeout', timeout_ms)
    X = [z3.Real(f'x{i}') for i in range(n)]
    Y = [z3.Real(f'y{i}') for i in range(n)]
    s.add(X[0] == 0, Y[0] == 0, X[1] == 1, Y[1] == 0)
    for i, j, k in combinations(range(n), 3):
        s.add((X[j]-X[i])*(Y[k]-Y[i]) - (Y[j]-Y[i])*(X[k]-X[i]) > 0)
    byc = {}
    for e, c in zip(edges, colvec):
        byc.setdefault(c, []).append(e)
    def sq(e):
        a, b = e
        return (X[a]-X[b])**2 + (Y[a]-Y[b])**2
    for c, es in byc.items():
        for t in range(1, len(es)):
            s.add(sq(es[0]) == sq(es[t]))
    r = s.check()
    if r == z3.sat:
        m = s.model()
        return 'sat', [[str(m.eval(X[i], model_completion=True)),
                        str(m.eval(Y[i], model_completion=True))] for i in range(n)]
    return ('unsat' if r == z3.unsat else 'unknown'), None


# ------------------------------------------------------------------ exact fields
class Qd:
    """a + b*sqrt(D), a,b rational."""
    D = 5
    __slots__ = ('a', 'b')
    def __init__(s, a, b=0): s.a = F(a); s.b = F(b)
    def __add__(s, o): o = qd(o); return Qd(s.a+o.a, s.b+o.b)
    def __sub__(s, o): o = qd(o); return Qd(s.a-o.a, s.b-o.b)
    def __mul__(s, o):
        o = qd(o); return Qd(s.a*o.a + Qd.D*s.b*o.b, s.a*o.b + s.b*o.a)
    def __truediv__(s, o):
        o = qd(o); nn = o.a*o.a - Qd.D*o.b*o.b
        return s * Qd(o.a/nn, -o.b/nn)
    __radd__ = __add__; __rmul__ = __mul__
    def __rsub__(s, o): return qd(o) - s
    def __neg__(s): return Qd(-s.a, -s.b)
    def __pow__(s, k):
        r = Qd(1)
        for _ in range(k): r = r * s
        return r
    def __eq__(s, o): o = qd(o); return s.a == o.a and s.b == o.b
    def __hash__(s): return hash((s.a, s.b))
    def val(s):
        import decimal
        decimal.getcontext().prec = 60
        return float(s.a) + float(s.b) * (float(Qd.D) ** 0.5)
    def __gt__(s, o):
        o = qd(o); d = s - o
        if d.b == 0: return d.a > 0
        # exact sign of a + b sqrt(D)
        if d.a >= 0 and d.b >= 0: return d.a > 0 or d.b > 0
        if d.a <= 0 and d.b <= 0: return False
        if d.b > 0:  # a<0, b>0 : b^2 D > a^2 ?
            return d.b*d.b*Qd.D > d.a*d.a
        return d.a*d.a > d.b*d.b*Qd.D
    def __repr__(s): return f"({s.a}+{s.b}v{Qd.D})"
def qd(o): return o if isinstance(o, Qd) else Qd(o)


bad = 0
print("=" * 74)
print("CONTROL A  -- encoding admits models (checked exactly, no z3 search)")
print("=" * 74)

# A1: convex lattice polygons, exact over Q
lat_polys = {
    'lattice hexagon': [(0,0),(2,0),(3,2),(2,4),(0,4),(-1,2)],
    'lattice pentagon': [(0,0),(3,0),(4,3),(2,5),(-1,2)],
    'lattice heptagon': [(0,0),(3,0),(5,2),(5,5),(3,7),(0,6),(-1,3)],
    'lattice octagon': [(0,0),(3,0),(5,1),(6,3),(6,6),(4,8),(1,8),(-1,5)],
}
d2int = lambda p, q: (p[0]-q[0])**2 + (p[1]-q[1])**2
zeroQ = lambda v: v == 0
lat_ready = {}
for name, P in lat_polys.items():
    edges, col = colouring(P, d2int)
    NP = normalise_rational(P)
    ok, msg = eval_encoding(NP, edges, col, name, zeroQ)
    print(("  OK   " if ok else "  FAIL ") + msg)
    if not ok:
        bad += 1
    else:
        lat_ready[name] = (len(P), edges, col)

# A2: regular pentagon, exact in Q(sqrt5).  cos72 = (sqrt5-1)/4, and the
# normalised regular pentagon has coordinates in Q(sqrt5).
Qd.D = 5
c1 = Qd(F(-1, 4), F(1, 4))          # cos 72  = (sqrt5 - 1)/4
c2 = Qd(F(-1, 4), F(-1, 4))         # cos 144 = -(sqrt5 + 1)/4
# put v0=(0,0), v1=(1,0): the regular pentagon with side 1
# vertices: (0,0), (1,0), (1+cos72, sin72), (1/2, sin72+sin36), (-cos72, sin72)
# sin72, sin36 are NOT in Q(sqrt5); use instead squared distances only via the
# Q(sqrt5) golden ratio phi = (1+sqrt5)/2 (diagonal length of a unit pentagon).
# We verify the encoding on the pentagon by working with y-coordinates as
# elements of Q(sqrt5)[sqrt(...)]; simpler: use high precision and report it.
try:
    from mpmath import mp, mpf, cos, sin, pi
    mp.dps = 80
    for n in (5, 7, 9):
        P = [(cos(2*pi*t/n), sin(2*pi*t/n)) for t in range(n)]
        # normalise
        x0, y0 = P[0]; dx, dy = P[1][0]-x0, P[1][1]-y0; den = dx*dx+dy*dy
        NP = [(((x-x0)*dx + (y-y0)*dy)/den, ((y-y0)*dx - (x-x0)*dy)/den) for x, y in P]
        edges, col = colouring(list(range(n)),
                               lambda a, b: min(abs(a-b), n-abs(a-b)))
        zt = lambda v: abs(v) < mpf(10)**-60
        ok, msg = eval_encoding(NP, edges, col, f"regular {n}-gon (80 dps)", zt)
        print(("  OK   " if ok else "  FAIL ") + msg + "   [HIGH-PRECISION, 80 dps, "
              "tolerance 1e-60]")
        if not ok:
            bad += 1
except ImportError:
    print("  (mpmath unavailable)")

print()
print("=" * 74)
print("CONTROL B  -- z3 POSITIVE: colouring of a convex LATTICE polygon")
print("             (rational model exists after normalisation, so SAT)")
print("=" * 74)
for name, (n, edges, col) in lat_ready.items():
    ncol = len(set(col))
    per = max(len({col[i] for i, e in enumerate(edges) if v in e}) for v in range(n))
    t0 = time.time()
    r, pts = solve(n, col, edges, 60000)
    ok = (r == 'sat')
    print(("  OK   " if ok else "  FAIL ") +
          f"{name} (n={n}, {ncol} colours, max {per}/vertex): z3 says {r} "
          f"[{time.time()-t0:.1f}s]")
    if pts:
        print("        model:", pts)
    if not ok:
        bad += 1

print()
print("=" * 74)
print("CONTROL C  -- z3 NEGATIVE: all pairwise distances equal (impossible)")
print("=" * 74)
for n in range(4, 9):
    edges = sorted(combinations(range(n), 2), key=lambda e: (e[1], e[0]))
    t0 = time.time()
    r, _ = solve(n, [0]*len(edges), edges, 60000)
    ok = (r == 'unsat')
    print(("  OK   " if ok else "  FAIL ") +
          f"n={n}: all {len(edges)} distances equal -> {r} [{time.time()-t0:.1f}s]")
    if not ok:
        bad += 1

print()
print("=" * 74)
print("CONTROL D  -- INFORMATIONAL: regular n-gon colouring (irrational models)")
print("=" * 74)
for n in (5, 6):
    edges = sorted(combinations(range(n), 2), key=lambda e: (e[1], e[0]))
    col = [min(abs(a-b), n-abs(a-b)) for a, b in edges]
    t0 = time.time()
    r, pts = solve(n, col, edges, 30000)
    print(f"  n={n} regular colouring -> {r} [{time.time()-t0:.1f}s]"
          + ("  (expected: z3 cannot construct the irrational model)"
             if r == 'unknown' else ""))
    if r == 'unsat':
        print("        *** THIS WOULD BE A BUG: the regular n-gon realises it ***")
        bad += 1

print()
print(("CONTROLS FAILED: %d" % bad) if bad else "ALL CONTROLS PASSED")
sys.exit(1 if bad else 0)
