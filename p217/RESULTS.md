# Erdos #217 — crescent configurations

**Statement** (erdosproblems.com/217, tagged OPEN): for which n are there n points in
R^2, no three on a line and no four on a circle, determining n-1 distinct distances
such that **in some ordering of the distances** the i-th distance occurs i times?

The phrase "in some ordering" is load-bearing and easy to misread: the multiplicities
need only form the multiset {1,2,...,n-1}; they need NOT increase with the distance.
The n=7 witness below has squared distances 1,37,39,48,49,61 with multiplicities
5,6,1,4,3,2 — not monotone. Sum of multiplicities = C(n,2), so every pair is used.

**Known:** n = 4 (isosceles triangle plus centre), n = 5 (Pomerance), n = 6 and 7
(Palasti [Pa87], [Pa89]), n = 8 (Palasti [Pa89b]).  **n = 9 is open.**  Erdos believed
it impossible for all sufficiently large n.

**Prior computation.** Burt, Goldstein, Manski, Miller, Palsson, Suh, arXiv:1509.07220,
Remark 3.1: "With the help of a parallel computing cluster, we have exhaustively
searched a 91 point hexagonal region of the triangular lattice for a construction for
n = 9, but none exist. As the naive implementation took over 900 hours of computation
for this size, better (and achievable) techniques are required to search a
substantively larger region."  A 91-point centred hexagon is 5 rings, i.e. squared
norm up to 25.

**Novelty check (2026-08-30).** Forum thread: 1 comment, a bibliography addition
(Alfaiz, 12 Apr 2026). Zero "currently working on" flags. Zero proof claims. Zero arXiv
hits 2024-2026 (three papers ever, all pre-2020). Not present in google-deepmind
formal-conjectures. No GitHub repos.

## Why the triangular lattice is exact arithmetic

Embed (a,b) as a*(1,0) + b*(1/2, sqrt3/2).  For p = a1-a2, q = b1-b2 the squared
distance is exactly the integer

    N(p,q) = p^2 + p q + q^2 .

Writing X = 2a+b and Y = b (both integers), a point is (X/2, Y*sqrt3/2), so scaling
the X column by 2 and the Y column by 2/sqrt3 — neither of which can change whether a
determinant vanishes — gives

    three points COLLINEAR  iff  det[[X,Y,1]] = 0
    four points CONCYCLIC   iff  det[[N,X,Y,1]] = 0

both integer determinants.  **No floating point is used anywhere in this search.**

## Completeness of the enumeration

Point 0 is pinned at the origin and the other n-1 points range over every lattice
point of squared norm <= R2.  Since the pinned point may be taken to be *any* point of
the configuration, this enumerates every crescent configuration all of whose points lie
within distance R of one of them — in particular every configuration of diameter <= R —
up to translation.  It does NOT enumerate configurations outside the lattice.

## Pruning

* forbidden-point bitmask, rebuilt incrementally: when a point is accepted, every point
  collinear with it and one earlier chosen point, or concyclic with it and two earlier
  chosen points, is masked out once.  Testing a candidate is then one bit lookup.
* multiplicity domination (Hall's condition): sorting the current distance-class
  multiplicities descending as m_1 >= ... >= m_t, a necessary condition for extension to
  exactly {1,...,n-1} is t <= n-1 and m_j <= n-j for every j.

## Positive controls — all pass

Every known case is reproduced inside the lattice, which validates both the search
space and the code.  Region R2 = 49 (187 lattice points):

| n | solutions found | time |
|---|---|---|
| 4 | 2892 | 0.11 s |
| 5 | 4116 | 0.32 s |
| 6 | 8904 | 1.53 s |
| 7 | 2964 | 5.78 s |
| 8 | 156  | 20.54 s |

An independent verifier (`verify.py`, sharing no code with the search) re-checks
collinearity, concyclicity, the distinct-distance count and the multiplicity multiset
in exact integer arithmetic.  Sample n=7 witness, verified:

    (0,0) (-8,3) (-8,4) (-7,3) (-4,-4) (-3,-4) (1,-1)
    squared distances -> multiplicity:  1->5, 37->6, 39->1, 48->4, 49->3, 61->2

Sample n=8 witness, verified: squared distances 7->1, 21->4, 28->5, 49->6, 91->7,
133->2, 147->3.

The two implementations agree: `crescent.c` and `crescent2.c` both return exactly 156
solutions at n=8, R2=49.

## n = 9

Ladder complete, 5 shards per rung, every shard COMPLETED (the sweep is exhaustive
only if every shard finishes, and every one did).

| R2 | lattice points | nodes | solutions | time |
|---|---|---|---|---|
| 25 | 91 | 16,636,430 | **0** | 2.8 s |
| 49 | 187 | 485,748,408 | **0** | 54.5 s |
| 64 | 241 | 1,391,779,545 | **0** | 183 s |
| 81 | 301 | 3,479,500,902 | **0** | 377 s |
| 100 | 367 | 8,065,470,465 | **0** | 180 s |
| 144 | 517 | 31,570,223,839 | **0** | 540 s |
| 196 | 721 | 117,265,608,552 | **0** | 1,860 s |
| 256 | 931 | 317,956,070,648 | **0** | 4,620 s |
| 324 | 1,165 | 762,178,950,124 | **0** | 10,920 s |
| 400 | 1,459 | 1,826,221,345,879 | **0** | 25,082 s |

Total 43,203 s (12.0 h) on 5 cores, about 3.07e12 search-tree nodes, zero solutions.

### What is actually proved

Point 0 is pinned at the origin and the remaining points take strictly increasing
indices, so the enumeration is complete for every subset of the pool that CONTAINS the
origin. Distances are translation invariant, so translating any point of a
configuration to the origin puts every other point within the squared diameter. Hence:

> **No 9-point crescent configuration exists on the triangular lattice with squared
> diameter at most 400** (diameter at most 20 lattice units).

Configurations of squared diameter between 400 and 1600 are partly covered too (those
having some point that sees all the others within norm 400), but are NOT covered
exhaustively, so the claim above is the one to quote.

### Comparison with the published computation

Burt, Goldstein, Manski, Miller, Palsson and Suh, arXiv:1509.07220, Remark 3.1,
exhaustively searched a 91-point hexagonal region and found nothing, reporting "over
900 hours of computation for this size" and asking for "better (and achievable)
techniques ... to search a substantively larger region".

That region is exactly the R2 = 25 rung here: the set of lattice points of norm <= 25
is, verified by direct comparison, identical as a set to the 5-ring centred hexagon,
91 points. So this ladder reproduces their negative result on their own region (in
2.8 seconds) and extends it:

* points in the pool: 91 -> 1,459, a factor of 16
* squared diameter covered: 25 -> 400, a factor of 16
* diameter covered: 5 -> 20, a factor of 4

### Why the absence is meaningful rather than vacuous

The same program finds solutions at every n from 4 to 8 on the same lattice, and an
independent exact verifier (`verify.py`, sharing no code with the search) confirms
them: no three collinear, no four concyclic, exactly n-1 distinct squared distances,
and multiplicities exactly the multiset {1,...,n-1}.

| n | solutions found | smallest enclosing norm |
|---|---|---|
| 4 | 2,892 | 3 |
| 5 | 4,116 | 4 |
| 6 | 8,904 | 4 |
| 7 | 2,964 | 4 |
| 8 | 156 | 7 |

Every known case up to n = 8 is realisable within norm 7, which is deep inside the
region searched at n = 9. If an n = 9 configuration were similarly compact it would
have been found.

**Status: `VERIFIED` that no 9-point crescent configuration exists on the triangular
lattice with squared diameter at most 400. This is a NEGATIVE result over a restricted
domain. It does not settle n = 9: a crescent configuration need not have lattice
coordinates, and nothing here rules out a lattice configuration of larger diameter.
The only reason to think the lattice is the right place to look is that the known
constructions for n <= 8 are realisable there.**
