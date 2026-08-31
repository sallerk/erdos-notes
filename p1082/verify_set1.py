"""Three independent verifications of the Phase 1 conclusion.

The set S (the unique maximum planar 5-distance set, found in the triangular
lattice) is checked with three separate arithmetic implementations:
  (1) integer Eisenstein arithmetic  (geo.py)
  (2) exact symbolic Cartesian arithmetic with sympy sqrt(3)
  (3) exact rational arithmetic on the doubled Cartesian coordinates
      (2x, 2y/sqrt3) which are integers -- an independent integral model
"""
from fractions import Fraction
import sympy as sp
from geo import distance_set, collinear_triples, cross, d2_A2

S = [(0, 0), (0, 1), (0, 2), (1, -1), (1, 0), (1, 1), (1, 2),
     (2, -1), (2, 0), (2, 1), (3, -1), (3, 0)]
n = len(S)
print(f"S has {n} points (Eisenstein coordinates)\n")

# ---- (1) integer Eisenstein ------------------------------------------------
ds1 = sorted(distance_set(S, 'A2'))
tri1 = collinear_triples(S)
print(f"(1) Eisenstein integers : {len(ds1)} distances {ds1}, "
      f"{len(tri1)} collinear triples")

# ---- (2) sympy exact Cartesian --------------------------------------------
r3 = sp.sqrt(3)
C = [(sp.Rational(i) + sp.Rational(j, 2), sp.Rational(j, 2) * r3) for (i, j) in S]
ds2 = set()
for a in range(n):
    for b in range(a + 1, n):
        v = sp.expand((C[a][0] - C[b][0]) ** 2 + (C[a][1] - C[b][1]) ** 2)
        ds2.add(sp.nsimplify(sp.simplify(v)))
tri2 = []
for a in range(n):
    for b in range(a + 1, n):
        for c in range(b + 1, n):
            det = sp.expand((C[b][0] - C[a][0]) * (C[c][1] - C[a][1])
                            - (C[b][1] - C[a][1]) * (C[c][0] - C[a][0]))
            if sp.simplify(det) == 0:
                tri2.append((a, b, c))
print(f"(2) sympy exact Cartesian: {len(ds2)} distances "
      f"{sorted(ds2, key=float)}, {len(tri2)} collinear triples")

# ---- (3) integral model on doubled coordinates -----------------------------
# x' = 2x = 2i + j  and  y' = 2y/sqrt3 = j.  Squared distance is
# ((dx')^2 + 3(dy')^2)/4 ; collinearity is unaffected by the linear change.
E = [(2 * i + j, j) for (i, j) in S]
ds3 = sorted({((E[a][0] - E[b][0]) ** 2 + 3 * (E[a][1] - E[b][1]) ** 2)
              for a in range(n) for b in range(a + 1, n)})
tri3 = [(a, b, c) for a in range(n) for b in range(a + 1, n)
        for c in range(b + 1, n)
        if (E[b][0] - E[a][0]) * (E[c][1] - E[a][1])
        - (E[b][1] - E[a][1]) * (E[c][0] - E[a][0]) == 0]
print(f"(3) doubled integer model: {len(ds3)} distances {ds3} (= 4x the "
      f"Eisenstein values), {len(tri3)} collinear triples")

assert len(ds1) == len(ds2) == len(ds3) == 5
assert len(tri1) == len(tri2) == len(tri3) == 18
assert [4 * v for v in ds1] == ds3
print("\nALL THREE AGREE: 12 points, exactly 5 distinct distances, "
      "18 collinear triples.")
print("floor(12/2) = 6 > 5, so WITHOUT the collinearity condition this set "
      "already\nrefutes the inequality -- the 18 collinear triples are the "
      "only thing saving it.")
print("\nThe 18 collinear triples:")
for (a, b, c) in tri1:
    print(f"   {S[a]}  {S[b]}  {S[c]}")
