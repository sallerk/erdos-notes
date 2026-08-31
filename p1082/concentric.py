"""PHASE 2, part 3: numeric screen of concentric regular polygons.

Both known extremal configurations for this problem that are NOT lattice sets
live in this family:
  * Harborth's 8-point set = two concentric squares (radii sqrt2 and 1+sqrt3,
    relative rotation 45 degrees) -- refutes the SECOND question;
  * eigensolver's 42-point set = two concentric regular 21-gons -- also the
    second question.
So it is the natural place to look for a counterexample to the FIRST question.

This is a FLOATING POINT SCREEN ONLY.  Nothing here is a certificate: any hit
would be re-derived and certified in exact arithmetic.  Its job is to say
whether anything in the family even gets close.

t rings of N points each, ring i at radius r_i and angular offset phi_i
(r_0 = 1, phi_0 = 0 by similarity).  n = t*N points.
"""
import sys
import numpy as np
import itertools

TOL = 1e-9


def config(N, t, radii, phis):
    pts = []
    for i in range(t):
        for j in range(N):
            a = phis[i] + 2 * np.pi * j / N
            pts.append((radii[i] * np.cos(a), radii[i] * np.sin(a)))
    return np.array(pts)


def ndist(P):
    """Number of distinct distances, or None if two points coincide.

    Coincident points must be rejected: otherwise the scan happily reports the
    degenerate radius ratio r = 1 with zero rotation, where the two rings are
    the same N points listed twice.
    """
    d = np.sqrt(((P[:, None, :] - P[None, :, :]) ** 2).sum(-1))
    iu = np.triu_indices(len(P), 1)
    v = np.sort(d[iu])
    if v[0] < 1e-7:
        return None, v                      # duplicate points -- not n points
    k = 1
    for a in range(1, len(v)):
        if v[a] - v[a - 1] > TOL * max(1.0, v[a]):
            k += 1
    return k, v


def has_collinear(P, tol=1e-9):
    n = len(P)
    for i in range(n):
        for j in range(i + 1, n):
            ux, uy = P[j] - P[i]
            L = np.hypot(ux, uy)
            for k in range(j + 1, n):
                vx, vy = P[k] - P[i]
                if abs(ux * vy - uy * vx) < tol * L * np.hypot(vx, vy):
                    return True
    return False


best_overall = []
GRID = int(sys.argv[1]) if len(sys.argv) > 1 else 4001

print("t=2 rings, offsets 0 and pi/N (the H8 pattern) plus offset 0;"
      " radius scanned on a fine grid")
print(f"{'N':>3} {'n':>4} {'need<':>6} {'best #distances':>16}  {'at r':>10}")
for N in range(3, 16):
    t = 2
    n = t * N
    need = n // 2
    best = (10 ** 9, None, None)
    for off in (0.0, np.pi / N):
        for r in np.linspace(0.02, 1.0, GRID):
            P = config(N, 2, [1.0, r], [0.0, off])
            k, _ = ndist(P)
            if k is not None and k < best[0]:
                best = (k, r, off)
    k, r, off = best
    flag = ""
    if k < need:
        P = config(N, 2, [1.0, r], [0.0, off])
        flag = " <-- CHECK" if not has_collinear(P) else " (collinear)"
    print(f"{N:>3} {n:>4} {need:>6} {k:>16}  {r:>10.5f}{flag}")
    best_overall.append((N, n, need, k))

print("\nt=3 rings, coarse 2-parameter scan (radii), offsets in {0, pi/N}")
G3 = 121
for N in range(3, 11):
    t = 3
    n = t * N
    need = n // 2
    best = (10 ** 9, None)
    for o1 in (0.0, np.pi / N):
        for o2 in (0.0, np.pi / N):
            for r1 in np.linspace(0.05, 0.98, G3):
                for r2 in np.linspace(0.05, 0.98, G3):
                    if r2 >= r1 - 1e-12:
                        continue
                    P = config(N, 3, [1.0, r1, r2], [0.0, o1, o2])
                    k, _ = ndist(P)
                    if k is not None and k < best[0]:
                        best = (k, (r1, r2, o1, o2))
    print(f"N={N:>3} n={n:>4} need<{need:>4}  best #distances = {best[0]:>4}"
          f"   {'*** BELOW ***' if best[0] < need else ''}")

print("\nSummary: the minimum over the whole scan of "
      "(distinct distances) - floor(n/2):")
print("  ", [(N, k - need) for (N, n, need, k) in best_overall])
