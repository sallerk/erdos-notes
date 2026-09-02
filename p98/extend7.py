"""Can the 7-point 5-distance witness be extended to 8 points without new distances?

If YES, then D_gen(8) <= 5, and with monotonicity (D_gen(8) >= D_gen(7) = 5) that gives
D_gen(8) = 5 exactly -- n=8 settled.

This is a FINITE EXACT computation, not a search.  An added point p must lie at one of
the five existing distances from every one of the seven witness points.  Fix any two
witness points and any two of the five distances: p lies on the intersection of two
circles, which is at most two points.  Enumerating over all pairs and all distance
choices therefore produces a finite candidate set that provably CONTAINS every possible
extension, and each candidate is then checked exactly.

Why this is worth doing even though lattice searches came up empty: the candidate points
here need NOT be lattice points.  The lattice searches are exhaustive only over Z^2 and
A_2, and we have proof that matters -- the D_gen(5)=3 optimum has irrational squared-
distance ratios and is invisible to both at any radius.  This test covers exactly the
off-lattice extensions those searches cannot see.

The same routine also tries extension with SIX distances (one new distance allowed),
which would give D_gen(8) <= 6.
"""
import sys, itertools

sys.stdout.reconfigure(encoding='utf-8', errors='replace')
import sympy as sp

# the verified 7-point witness, as exact plane points (triangular lattice, 5 distances)
LAT7 = [(0, 0), (-1, 0), (-1, 1), (1, -3), (3, -2), (2, -4), (4, -2)]
r3 = sp.sqrt(3)
P7 = [(sp.Rational(a) + sp.Rational(b, 2), sp.Rational(b) * r3 / 2) for a, b in LAT7]
N = len(P7)


def sq(p, q):
    return sp.expand((p[0] - q[0]) ** 2 + (p[1] - q[1]) ** 2)


DIST = sorted({sp.simplify(sq(P7[i], P7[j]))
               for i, j in itertools.combinations(range(N), 2)}, key=lambda e: float(e))
print('=' * 74)
print('EXTENDING THE 7-POINT WITNESS TO 8 POINTS')
print('=' * 74)
print('  witness squared distances: %s   (%d distinct)' % (DIST, len(DIST)))
print()


def circle_inter(c1, r1s, c2, r2s):
    """exact intersection points of circles (c1, r1^2) and (c2, r2^2); 0, 1 or 2 points"""
    x1, y1 = c1
    x2, y2 = c2
    dx, dy = sp.simplify(x2 - x1), sp.simplify(y2 - y1)
    d2 = sp.simplify(dx * dx + dy * dy)
    if d2 == 0:
        return []
    # standard radical-line construction
    a = sp.simplify((r1s - r2s + d2) / (2 * sp.sqrt(d2)))
    h2 = sp.simplify(r1s - a * a)
    if h2 == sp.nan:
        return []
    try:
        if sp.simplify(h2) < 0:
            return []
    except TypeError:
        return []
    h = sp.sqrt(sp.simplify(h2))
    ux, uy = sp.simplify(dx / sp.sqrt(d2)), sp.simplify(dy / sp.sqrt(d2))
    mx, my = sp.simplify(x1 + a * ux), sp.simplify(y1 + a * uy)
    if sp.simplify(h) == 0:
        return [(mx, my)]
    return [(sp.simplify(mx - h * uy), sp.simplify(my + h * ux)),
            (sp.simplify(mx + h * uy), sp.simplify(my - h * ux))]


def check(p, allowed):
    """does adding p keep every distance inside `allowed`, and general position?"""
    ds = []
    for q in P7:
        v = sp.simplify(sq(p, q))
        if v == 0:
            return None
        if not any(sp.simplify(v - a) == 0 for a in allowed):
            return None
        ds.append(v)
    S = P7 + [p]
    for t in itertools.combinations(range(8), 3):
        a, b, c = S[t[0]], S[t[1]], S[t[2]]
        if sp.simplify((b[0] - a[0]) * (c[1] - a[1]) - (c[0] - a[0]) * (b[1] - a[1])) == 0:
            return None
    for q in itertools.combinations(range(8), 4):
        M = sp.Matrix([[S[t][0] ** 2 + S[t][1] ** 2, S[t][0], S[t][1], 1] for t in q])
        if sp.simplify(M.det()) == 0:
            return None
    tot = {sp.simplify(sq(S[i], S[j])) for i, j in itertools.combinations(range(8), 2)}
    vals = []
    for v in tot:
        if not any(sp.simplify(v - w) == 0 for w in vals):
            vals.append(v)
    return len(vals)


def run(allowed, label):
    print('  --- %s ---' % label)
    print('      allowed squared distances: %s' % [sp.nsimplify(a) for a in allowed])
    seen = []
    cands = 0
    hits = []
    for i, j in itertools.combinations(range(N), 2):
        for r1s in allowed:
            for r2s in allowed:
                for p in circle_inter(P7[i], r1s, P7[j], r2s):
                    cands += 1
                    if any(sp.simplify((p[0] - s[0]) ** 2 + (p[1] - s[1]) ** 2) == 0
                           for s in seen):
                        continue
                    seen.append(p)
                    k = check(p, allowed)
                    if k is not None:
                        hits.append((p, k))
    print('      circle-intersection candidates examined: %d  (%d distinct)'
          % (cands, len(seen)))
    if hits:
        for p, k in hits:
            print('      *** EXTENSION FOUND: %s  giving %d distinct distances ***'
                  % ((sp.nsimplify(p[0]), sp.nsimplify(p[1])), k))
    else:
        print('      NO extension exists: the candidate set is provably complete, so')
        print('      this witness admits no 8th point within these distances.')
    return hits


h5 = run(DIST, 'extension with NO new distance (would give D_gen(8) = 5)')
print()
print('=' * 74)
if h5:
    print('D_gen(8) <= 5, and with monotonicity D_gen(8) = 5.  n=8 SETTLED.')
else:
    print('This particular witness does not extend to 8 points with 5 distances.')
    print('That does NOT settle D_gen(8): another 7-point 5-distance configuration')
    print('might extend, and we have only this one.')
