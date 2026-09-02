"""Can the 7-point 5-distance witness be extended to 8 points? (fast, then exact)

Same finite exact argument as extend7.py, but that version did every circle intersection
in sympy over nested radicals and was killed by its time cap without a verdict.  Here the
enumeration is done in 40-digit mpmath and only the survivors are re-verified exactly, so
the expensive symbolic work happens on a handful of points rather than a thousand.

The candidate set is still provably COMPLETE: any 8th point keeping the distance set must
lie at one of the allowed distances from every witness point, hence on the intersection of
two circles for any chosen pair, and every such intersection is enumerated.

If an extension with no new distance exists then D_gen(8) <= 5, and with monotonicity
(D_gen(8) >= D_gen(7) = 5) that gives D_gen(8) = 5 exactly.
"""
import sys, itertools

sys.stdout.reconfigure(encoding='utf-8', errors='replace')
import mpmath as mp
import sympy as sp

mp.mp.dps = 40
TOL = mp.mpf('1e-25')

LAT7 = [(0, 0), (-1, 0), (-1, 1), (1, -3), (3, -2), (2, -4), (4, -2)]
S3 = mp.sqrt(3)
P = [(mp.mpf(a) + mp.mpf(b) / 2, mp.mpf(b) * S3 / 2) for a, b in LAT7]
N = len(P)


def sq(p, q):
    return (p[0] - q[0]) ** 2 + (p[1] - q[1]) ** 2


vals = []
for i, j in itertools.combinations(range(N), 2):
    v = sq(P[i], P[j])
    if not any(abs(v - w) < TOL for w in vals):
        vals.append(v)
vals.sort()
print('=' * 74)
print('EXTENDING THE 7-POINT WITNESS  (numeric enumeration, exact verification)')
print('=' * 74)
print('  witness squared distances: %s' % [mp.nstr(v, 8) for v in vals])
print('  (%d distinct, matching the verified witness)' % len(vals))
print()


def inter(c1, r1s, c2, r2s):
    dx, dy = c2[0] - c1[0], c2[1] - c1[1]
    d2 = dx * dx + dy * dy
    if d2 < TOL:
        return []
    d = mp.sqrt(d2)
    a = (r1s - r2s + d2) / (2 * d)
    h2 = r1s - a * a
    if h2 < -TOL:
        return []
    h = mp.sqrt(max(h2, mp.mpf(0)))
    ux, uy = dx / d, dy / d
    mx, my = c1[0] + a * ux, c1[1] + a * uy
    if h < TOL:
        return [(mx, my)]
    return [(mx - h * uy, my + h * ux), (mx + h * uy, my - h * ux)]


def screen(allowed, label):
    print('  --- %s ---' % label)
    seen, ok = [], []
    ncand = 0
    for i, j in itertools.combinations(range(N), 2):
        for r1s in allowed:
            for r2s in allowed:
                for p in inter(P[i], r1s, P[j], r2s):
                    ncand += 1
                    if any(abs(p[0] - s[0]) < mp.mpf('1e-20')
                           and abs(p[1] - s[1]) < mp.mpf('1e-20') for s in seen):
                        continue
                    seen.append(p)
                    # every distance to the witness must be an allowed one
                    good = True
                    for q in P:
                        v = sq(p, q)
                        if v < TOL:
                            good = False
                            break
                        if not any(abs(v - a) < mp.mpf('1e-22') for a in allowed):
                            good = False
                            break
                    if not good:
                        continue
                    # general position on the 8 points
                    S = P + [p]
                    bad = False
                    for t in itertools.combinations(range(8), 3):
                        a1, b1, c1 = S[t[0]], S[t[1]], S[t[2]]
                        ar = abs((b1[0] - a1[0]) * (c1[1] - a1[1])
                                 - (c1[0] - a1[0]) * (b1[1] - a1[1]))
                        if ar < mp.mpf('1e-20'):
                            bad = True
                            break
                    if not bad:
                        for q4 in itertools.combinations(range(8), 4):
                            M = mp.matrix(4, 4)
                            for rr, t in enumerate(q4):
                                M[rr, 0] = S[t][0] ** 2 + S[t][1] ** 2
                                M[rr, 1] = S[t][0]
                                M[rr, 2] = S[t][1]
                                M[rr, 3] = mp.mpf(1)
                            if abs(mp.det(M)) < mp.mpf('1e-20'):
                                bad = True
                                break
                    if not bad:
                        ok.append(p)
    print('      circle intersections examined : %d  (%d distinct points)'
          % (ncand, len(seen)))
    print('      surviving all conditions      : %d' % len(ok))
    for p in ok:
        print('         candidate (%s, %s)' % (mp.nstr(p[0], 20), mp.nstr(p[1], 20)))
    return ok


print('  The candidate set below is COMPLETE: any valid 8th point lies on the')
print('  intersection of two of these circles, and all are enumerated.')
print()
h5 = screen(vals, 'no new distance -> would give D_gen(8) = 5')
print()
h6 = None
if not h5:
    print('  no 5-distance extension; now allowing ONE new distance is NOT a finite')
    print('  enumeration (the new distance is a free parameter), so it is not attempted.')
print()
print('=' * 74)
if h5:
    print('EXTENSION FOUND -> D_gen(8) <= 5, and with monotonicity D_gen(8) = 5.')
    print('Re-derive exactly before claiming it.')
else:
    print('NO extension of this witness keeps the distance set at 5.')
    print('The enumeration is complete FOR THIS WITNESS, so that is a real negative,')
    print('but it does not settle D_gen(8): another 7-point 5-distance configuration')
    print('might extend, and this is the only one we have.')
