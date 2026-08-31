"""Confirm the two Phase 1 classes are the SAME set up to similarity.

Multiplication by (1+zeta), zeta = e^{i pi/3}, is a similarity of the triangular
lattice scaling lengths by sqrt3 and rotating by 30 degrees.  In Eisenstein
coordinates (i,j) <-> i + j*zeta, with zeta^2 = zeta - 1, it is the integer map

    (i, j)  ->  (i - j,  i + 2j).

Apply it to class 1 and canonicalise; the result must equal class 2.
"""
from geo import distance_set, collinear_triples

S1 = [(0, 0), (0, 1), (0, 2), (1, -1), (1, 0), (1, 1), (1, 2),
      (2, -1), (2, 0), (2, 1), (3, -1), (3, 0)]
S2 = [(0, 0), (1, -2), (1, 1), (2, -4), (2, -1), (3, -3), (3, 0),
      (4, -5), (4, -2), (5, -4), (5, -1), (6, -3)]


def canon(S):
    reps = []
    for rot in range(6):
        for refl in (0, 1):
            Q = []
            for (x, y) in S:
                a, b = x, y
                for _ in range(rot):
                    a, b = -b, a + b          # rotation by 60 degrees
                if refl:
                    a, b = b, a               # reflection
                Q.append((a, b))
            mx = min(Q)
            reps.append(tuple(sorted((u - mx[0], v - mx[1]) for (u, v) in Q)))
    return min(reps)


img = [(i - j, i + 2 * j) for (i, j) in S1]
print("class 1 distances      :", sorted(distance_set(S1, 'A2')))
print("class 2 distances      :", sorted(distance_set(S2, 'A2')))
print("image of class 1       :", sorted(distance_set(img, 'A2')))
print("collinear triples      : class1", len(collinear_triples(S1)),
      " class2", len(collinear_triples(S2)), " image", len(collinear_triples(img)))
print()
print("canon(image of class 1) == canon(class 2) ?", canon(img) == canon(S2))
assert canon(img) == canon(S2)
print("\nCONFIRMED: the two classes the enumeration returned are one set up to")
print("similarity -- the sqrt3-scaling 30-degree rotation maps one to the other.")
print("Consistent with Shinohara's uniqueness theorem.")
