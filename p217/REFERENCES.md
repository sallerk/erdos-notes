# References for the #217 note

## The problem statement

* **erdosproblems.com/217**, read 2026-08-31, verbatim:

  > "For which n are there n points in R^2, no three on a line and no four on a circle,
  > which determine n-1 distinct distances and so that (in some ordering of the
  > distances) the i-th distance occurs i times?"

  Page citations are `#217: [Er83c][Er87b,p.167][Er97e]`. Status OPEN. The page records
  n = 4 (isosceles triangle plus centre), n = 5 (Pomerance, described in [Er83c]),
  n = 7 (Palasti [Pa87]), n = 6 with no equilateral triangles (Palasti [Pa89]), and
  n = 8 (Palasti [Pa89b]); and that "Erdos believed this is impossible for all
  sufficiently large n."
  *[VERIFIED AT SOURCE]*

## The paper this note extends

* **David Burt, Eli Goldstein, Sarah Manski, Steven J. Miller, Eyvindur Ari Palsson and
  Hong Suh**, "Crescent Configurations", arXiv:1509.07220v1 [math.CO], 24 Sep 2015.

  Definition 1.1, verbatim:

  > "We say that n points are in general position in R^d if no d + 1 points lie on the
  > same hyperplane and no d + 2 lie on the same hypersphere."

  Definition 1.2, verbatim:

  > "We say n points are in crescent configuration (in R^d) if they lie in general
  > position in R^d and determine n - 1 distinct distances, such that for every
  > 1 <= i <= n - 1 there is a distance that occurs exactly i times."

  In the plane those two are exactly the problem-page statement, which is why the work
  here is on the right problem. Note that Definition 1.2 imposes NO monotonicity of
  multiplicity in distance; the sentence before it ("The multiplicities of the distances
  are in an increasing order") motivates the name "crescent" and is not part of the
  definition. Palasti's own published example has non-monotone multiplicities, which
  settles the reading; see `audit217.py` check 3.

  Remark 3.1, verbatim:

  > "With the help of a parallel computing cluster, we have exhaustively searched a 91
  > point hexagonal region of the triangular lattice for a construction for n = 9, but
  > none exist. As the naive implementation took over 900 hours of computation for this
  > size, better (and achievable) techniques are required to search a substantively
  > larger region."

  Among the paper's open problems, verbatim:

  > "Can planar constructions for n >= 9 be found on the triangular lattice? It is known
  > that constructions for n < 9 exist on the triangular lattice."

  *[VERIFIED AT SOURCE: PDF fetched from arXiv and read 2026-08-31]*

* **I. Palasti**, n = 8 construction. Not obtained at source. The coordinates used in
  `audit217.py` check 2 are those printed in arXiv:1509.07220 Figure 1, credited there
  to [Pal89]:

      (0,1), (sqrt3,0), (2 sqrt3,0), (5 sqrt3/2, 5/2),
      (3 sqrt3/2, 9/2), (sqrt3/2, 7/2), (3 sqrt3/2, 7/2), (sqrt3, 2)

  Verified here in exact arithmetic to be a crescent configuration: 7 distinct squared
  distances 1, 3, 4, 7, 13, 19, 21 with multiplicities 1, 4, 5, 6, 7, 2, 3, no three
  collinear, no four concyclic.
  *[coordinates SECONDARY, taken from Burt et al.; their correctness VERIFIED here]*

## Novelty

The arithmetic-style check does not apply here (there is no numerical bound to
substitute into), so the check is bibliographic and is recorded as `audit217.py`
check 8:

* The #217 problem page cites only [Er83c][Er87b,p.167][Er97e] and **does not mention
  arXiv:1509.07220 or any computational search**.
* The single forum comment on the thread (Alfaiz, 19:44 on 12 Apr 2026) says only "The
  reference [Pa89] of I. Palasti can be added here as well" and mentions no computation,
  no lattice, and not Burt et al.
* Burt et al. themselves state that their 91-point search is the extent of what had been
  done and ask for a substantively larger region.

So both halves of the contribution are new relative to the site: the pointer to
arXiv:1509.07220, and the extension of its search from 91 to 1,459 lattice points.

**What is not claimed.** No statement about n = 9 in the plane, and no lower bound. A
crescent configuration need not have lattice coordinates, and a lattice configuration
of larger diameter is not excluded by this. The search is exhaustive only over what
`audit217.py` check 6 defines: configurations of squared diameter at most 400 on the
triangular lattice.

## Why the triangular lattice is exact arithmetic

Embed (a,b) as a*(1,0) + b*(1/2, sqrt3/2). For p = a1-a2, q = b1-b2 the squared
distance is exactly the integer N(p,q) = p^2 + pq + q^2. Writing X = 2a+b and Y = b,
a point is (X/2, Y*sqrt3/2), so scaling the X column by 2 and the Y column by 2/sqrt3,
neither of which can change whether a determinant vanishes, gives

    three points COLLINEAR   iff  det[[X, Y, 1]] = 0
    four points CONCYCLIC    iff  det[[N, X, Y, 1]] = 0

with every entry an integer. No floating point enters the search or either verifier.
