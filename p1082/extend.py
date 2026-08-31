"""Can the known tight configuration be extended?

A counterexample with n = 2k+2 points and k distances contains, after deleting
any one point, a set of 2k+1 points with at most k distances and no three
collinear -- i.e. a set meeting the conjectured bound exactly.  The only such
family we know is the regular (2k+1)-gon.  So a natural complete question is:

    can a regular (2k+1)-gon be extended by ONE point without introducing a
    new distance (and without putting three points on a line)?

This is finite and pool-free.  If p is such a point then |p - v_0| and
|p - v_1| both lie in the k-element distance set D, so p is one of at most
2k^2 intersection points of two circles.  Enumerate those, test against all
the other vertices.

High-precision (mpmath, 60 digits) SCREEN.  Any hit would be certified exactly
in the cyclotomic field afterwards; nothing here is by itself a certificate.
"""
import mpmath as mp

mp.mp.dps = 60
TOL = mp.mpf(10) ** -40


def run(m):
    k = m // 2
    V = [(mp.cos(2 * mp.pi * j / m), mp.sin(2 * mp.pi * j / m)) for j in range(m)]
    D = sorted({mp.sqrt((V[0][0] - V[d][0]) ** 2 + (V[0][1] - V[d][1]) ** 2)
                for d in range(1, m)}, key=float)
    # de-duplicate at tolerance
    Du = []
    for d in D:
        if not Du or abs(d - Du[-1]) > TOL:
            Du.append(d)
    hits = []
    a, b = V[0], V[1]
    dx, dy = b[0] - a[0], b[1] - a[1]
    L = mp.sqrt(dx * dx + dy * dy)
    for r1 in Du:
        for r2 in Du:
            # circle(a,r1) cap circle(b,r2)
            t = (r1 * r1 - r2 * r2 + L * L) / (2 * L)
            h2 = r1 * r1 - t * t
            if h2 < -TOL:
                continue
            h = mp.sqrt(max(h2, mp.mpf(0)))
            mx, my = a[0] + t * dx / L, a[1] + t * dy / L
            for s in (1, -1):
                p = (mx + s * h * (-dy) / L, my + s * h * dx / L)
                # must be a NEW point
                if any(mp.sqrt((p[0] - v[0]) ** 2 + (p[1] - v[1]) ** 2) < TOL
                       for v in V):
                    continue
                ok = True
                for v in V:
                    dd = mp.sqrt((p[0] - v[0]) ** 2 + (p[1] - v[1]) ** 2)
                    if min(abs(dd - u) for u in Du) > TOL:
                        ok = False
                        break
                if ok:
                    hits.append(p)
    # collinearity of the extended set
    clean = []
    for p in hits:
        W = V + [p]
        bad = False
        for i in range(len(W)):
            for j in range(i + 1, len(W)):
                for t2 in range(j + 1, len(W)):
                    cr = ((W[j][0] - W[i][0]) * (W[t2][1] - W[i][1])
                          - (W[j][1] - W[i][1]) * (W[t2][0] - W[i][0]))
                    if abs(cr) < TOL:
                        bad = True
                        break
                if bad:
                    break
            if bad:
                break
        if not bad:
            clean.append(p)
    return k, len(Du), len(hits), len(clean)


print("regular m-gon, m = 2k+1: extend by one point keeping only k distances?")
print(f"{'m':>4} {'k':>3} {'|D|':>4} {'extensions':>11} {'general position':>17}")
for m in range(5, 42, 2):
    k, nd, nh, nc = run(m)
    flag = "  *** COUNTEREXAMPLE CANDIDATE ***" if nc else ""
    print(f"{m:>4} {k:>3} {nd:>4} {nh:>11} {nc:>17}{flag}", flush=True)

print("""
Reading: an "extension" is a point at one of the k polygon distances from every
one of the m vertices.  Zero everywhere means the regular odd polygon -- the one
configuration known to meet the bound exactly -- is rigid: it admits no
(2k+2)-nd point at all, let alone one in general position.
""")
