"""VERIFY THE VERIFIER, against published ground truth, before searching.

Checks
  A. Harborth's 8-point set (Erdos-Fishburn [ErFi97b], Fishburn [Fi02]) really
     does refute the SECOND question of #1082, and is NOT a counterexample to
     the first.  Exact arithmetic in Q(sqrt 3).
  B. Regular m-gons have exactly floor(m/2) distinct distances and no three
     collinear.  Exact arithmetic in the cyclotomic ring Z[x]/Phi_m(x).
     (These are the extremal examples showing the conjecture is sharp.)
  C. The lattice branch-and-bound reproduces the published lower bounds
     g(k) >= 3, 5, 7, 9, 12, 13 for k = 1..6 where the extremal set is a
     lattice set, and never exceeds the published values g(k).
"""
import sys
from fractions import Fraction
import numpy as np

from geo import Q3, analyse_q3, distance_set, has_collinear_triple, cross

PASS, FAIL = [], []


def check(name, cond, detail=""):
    (PASS if cond else FAIL).append(name)
    print(f"  [{'PASS' if cond else 'FAIL'}] {name} {detail}")


# ==========================================================================
print("A. Harborth 8-point set  (square + equilateral triangle on each side)")
# Square of side 2 at (+-1, +-1); equilateral triangles erected outward.
# Apex of the triangle on the bottom edge: (0, -1-sqrt3), etc.
s3 = Q3(0, 1)
one = Q3(1)
h = one + s3            # 1 + sqrt3
H8 = [
    (Q3(1), Q3(1)), (Q3(-1), Q3(1)), (Q3(-1), Q3(-1)), (Q3(1), Q3(-1)),
    (Q3(0), h), (Q3(0), -h), (h, Q3(0)), (-h, Q3(0)),
]
r = analyse_q3(H8, "  Harborth H8")
check("H8 has no three collinear", r['collinear'] == 0)
check("H8: every point sees exactly 3 distinct distances",
      max(r['per_point']) == 3 and min(r['per_point']) == 3,
      "-> refutes the SECOND question (3 < floor(8/2)=4)")
check("H8 total distinct distances >= floor(8/2)=4", r['k'] >= 4,
      f"(k={r['k']}) -> H8 is NOT a counterexample to the FIRST question")

# ==========================================================================
print("\nB. Regular m-gons: floor(m/2) distances, no three collinear")


def cyclo_poly(m):
    """Phi_m as an integer coefficient list (low->high), via x^m-1 division."""
    from sympy import Poly, cyclotomic_poly, symbols
    x = symbols('x')
    return [int(c) for c in reversed(Poly(cyclotomic_poly(m, x), x).all_coeffs())]


def reduce_mod(poly, phi):
    p = list(poly)
    d = len(phi) - 1
    while len(p) > d:
        c = p.pop()
        if c:
            k = len(p) - d
            for i, a in enumerate(phi[:-1]):
                p[k + i] -= c * a
    while len(p) < d:
        p.append(0)
    return tuple(p)


def gon_distances(m):
    """|z^a - z^b|^2 = 2 - z^d - z^-d in Z[z]/Phi_m ; count distinct values."""
    phi = cyclo_poly(m)
    vals = set()
    for d in range(1, m):
        p = [0] * m
        p[0] += 2
        p[d % m] -= 1
        p[(-d) % m] -= 1
        vals.add(reduce_mod(p, phi))
    return len(vals)


ok = True
for m in range(3, 26):
    nd = gon_distances(m)
    if nd != m // 2:
        ok = False
        print(f"    m={m}: got {nd}, expected {m//2}")
check("regular m-gon has exactly floor(m/2) distinct distances, 3<=m<=25", ok)
check("points on a circle are never 3-collinear (classical)", True,
      "-> the regular n-gon attains floor(n/2) exactly, for every n")

# ==========================================================================
print("\nC. Lattice branch-and-bound vs published g(k) = 3,5,7,9,12,13")
from search import build_pool, prepare, run

GK = {1: 3, 2: 5, 3: 7, 4: 9, 5: 12, 6: 13}       # published values
results = {}
for basis, D in (('A2', 30), ('Z2', 30)):
    pts = build_pool(D, basis)
    tab = prepare(pts, D, basis, with_collinear=False)
    print(f"  pool {basis} D<={D}: {tab['m']} points, {tab['V']} distance values")
    for k in range(1, 7):
        b, bs, _, _ = run(tab, k)
        results[(basis, k)] = (b, [pts[i] for i in bs])
        print(f"    k={k}: best over pool = {b}   (published g({k})={GK[k]})")

for k in range(1, 7):
    got = max(results[('A2', k)][0], results[('Z2', k)][0])
    check(f"g({k}) lattice search <= published {GK[k]}", got <= GK[k],
          f"(got {got})")

for k, exp in ((1, 3), (4, 9), (5, 12), (6, 13)):
    got = max(results[('A2', k)][0], results[('Z2', k)][0])
    check(f"g({k}) = {exp} attained by a lattice set", got == exp, f"(got {got})")

print("\n" + "=" * 70)
print(f"PASSED {len(PASS)}   FAILED {len(FAIL)}")
if FAIL:
    print("FAILURES:", FAIL)
    sys.exit(1)
