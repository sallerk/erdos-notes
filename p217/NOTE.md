# Erdos #217 (crescent configurations)

Problem page: https://www.erdosproblems.com/217

Full note. The forum comment is a summary of this page. Bibliography with provenance is
in `REFERENCES.md`; step-by-step reproduction with the output each command actually
printed is in `REPRODUCE.md`.

## The problem, and that it is the one being solved

The page asks, verbatim:

> "For which n are there n points in R^2, no three on a line and no four on a circle,
> which determine n-1 distinct distances and so that (in some ordering of the
> distances) the i-th distance occurs i times?"

These are Burt-Goldstein-Manski-Miller-Palsson-Suh's **crescent configurations**, and
their definitions match the page exactly. Definition 1.1: "n points are in general
position in R^d if no d+1 points lie on the same hyperplane and no d+2 lie on the same
hypersphere", which in the plane is no 3 collinear and no 4 concyclic. Definition 1.2:
"n points are in crescent configuration (in R^d) if they lie in general position in R^d
and determine n-1 distinct distances, such that for every 1 <= i <= n-1 there is a
distance that occurs exactly i times."

**"In some ordering" is load-bearing.** The multiplicities need only form the multiset
{1,...,n-1}; they need NOT increase with the distance. This is easy to misread, and the
published n = 8 example settles it: Palasti's configuration has squared distances
1, 3, 4, 7, 13, 19, 21 with multiplicities 1, 4, 5, 6, 7, 2, 3, which is not monotone.
A search demanding monotone multiplicity would reject the known example. `audit217.py`
check 3 prints this.

Known: n = 4 (isosceles triangle plus centre), n = 5 (Pomerance), n = 6 and 7 (Palasti
[Pa87], [Pa89]), n = 8 (Palasti [Pa89b]). **n = 9 is open.** Erdos believed it
impossible for all sufficiently large n.

## Result

**No 9-point crescent configuration exists on the triangular lattice with squared
diameter at most 400** (diameter at most 20 lattice units).

Ladder complete, 5 shards per rung, every shard COMPLETED; the sweep is exhaustive only
if every shard finishes, and every one did.

| R^2 | lattice points | nodes | solutions | time |
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

### Why the claim is about DIAMETER

Point 0 is pinned at the origin and the remaining points take strictly increasing
indices, so the enumeration is complete for every subset of the pool that CONTAINS the
origin. Distances are translation invariant, so translating any point of a
configuration to the origin puts every other point within the squared diameter of it.
Hence the sweep is exhaustive for every configuration of squared diameter <= R^2. That
is the statement to quote, and it is stronger than "fits inside the disc".
Configurations of squared diameter between 400 and 1600 are partly covered as well, but
not exhaustively, so no claim is made about them.

## Comparison with the published computation

Burt, Goldstein, Manski, Miller, Palsson and Suh, arXiv:1509.07220, Remark 3.1:

> "With the help of a parallel computing cluster, we have exhaustively searched a 91
> point hexagonal region of the triangular lattice for a construction for n = 9, but
> none exist. As the naive implementation took over 900 hours of computation for this
> size, better (and achievable) techniques are required to search a substantively
> larger region."

and among their open problems:

> "Can planar constructions for n >= 9 be found on the triangular lattice? It is known
> that constructions for n < 9 exist on the triangular lattice."

Their region is exactly the R^2 = 25 rung above: `audit217.py` check 6 confirms the set
of lattice points of norm <= 25 is **identical as a set** to the 5-ring centred hexagon,
91 points, not merely the same size. So this ladder reproduces their negative result on
their own region in 2.8 seconds and extends it:

* points in the pool: 91 -> 1,459, a factor of 16
* squared diameter covered: 25 -> 400, a factor of 16
* diameter covered: 5 -> 20, a factor of 4

## Why the absence is meaningful rather than vacuous

The same program finds solutions at every n from 4 to 8 on the same lattice, and an
independent exact verifier confirms them from the definition.

| n | solutions found | smallest enclosing norm |
|---|---|---|
| 4 | 2,892 | 3 |
| 5 | 4,116 | 4 |
| 6 | 8,904 | 4 |
| 7 | 2,964 | 4 |
| 8 | 156 | 7 |

Every known case up to n = 8 is realisable within norm 7, deep inside the region
searched at n = 9.

**The strongest control is that the search rediscovers the published construction.**
The first n = 8 solution it stores has squared distances 7, 21, 28, 49, 91, 133, 147
with multiplicities 1, 4, 5, 6, 7, 2, 3; Palasti's published set has 1, 3, 4, 7, 13,
19, 21 with the same multiplicities. The first is exactly the second scaled by 7, so
the two configurations are similar. `audit217.py` check 4 verifies this, having taken
Palasti's coordinates from arXiv:1509.07220 Figure 1 rather than from anything here.

## Scale: how big are the known configurations?

The multiplier against Burt et al.'s region is one way to size this; the more
informative comparison is against where the known constructions actually live. The
tightest realisation on the lattice at each n, by squared diameter:

| n | tightest known squared diameter |
|---|---|
| 4, 5 | 7 |
| 6, 7 | 13 |
| 8 | 21 (Palasti's, and the minimum over the 156 found here) |

So Burt et al.'s 91-point region covers squared diameter <= 25, only 1.2 times the
value at which the known n = 8 configuration sits. The ladder here covers <= 400,
about 19 times it. If a 9-point configuration existed at anything like the scale of
every known smaller one, this search would have found it many times over. That, rather
than the 16-fold multiplier, is the reason the negative result carries weight.

## A latent bug, found while costing the next rung

`crescent2.c` generated its lattice pool with `if (N <= R2 && NP < MAXP)`, where MAXP
was 2048. Beyond 2048 points the excess was dropped **silently**: no error, no warning,
and the search would then report "0 solutions" for a region it had never covered. For
a negative result that is the worst possible failure.

The completed ladder is unaffected: R^2 = 400 uses 1,459 points, well inside the cap,
and `audit217.py` check 9 verifies this. The threshold is R^2 = 559 (2,053 points), so
every rung run so far was safe, as is the next planned rung R^2 = 484 (1,765 points).

MAXP is now 8192 and exceeding it is a fatal error rather than a truncation. The fix
was verified to be behaviour-preserving: after it, R^2 = 25 still gives exactly
16,636,430 nodes and 0 solutions, and the n = 8 control still finds exactly 156
solutions in 161,595,043 nodes, matching the pre-fix runs digit for digit.

`audit217.py` check 9 also confirms the other implementation limits: MAXD = 64 exceeds
the largest possible number of distance classes C(9,2) = 36; MAXN = 12 exceeds n = 9;
the 4x4 concyclicity determinant at R^2 = 400 is bounded by about 4.4e6 against a
64-bit limit of 9.2e18, a margin of 2e12, so it cannot overflow; and the shards
partition the depth-1 loop, so their union is the whole search and exhaustiveness
follows from every shard reaching COMPLETED.

## What is NOT claimed

This settles nothing about n = 9 in the plane. A crescent configuration need not have
lattice coordinates, and a lattice configuration of larger diameter is not excluded.
The only reason to look on the lattice is that every known construction for n < 9 lives
there, which Burt et al. state and which check 4 confirms for Palasti at n = 8.

Disclosure: the searches, computations and the drafting of this note were done with AI
assistance.

## Files in this directory

Documentation: `REPRODUCE.md`, `REFERENCES.md`, `RESULTS.md`.

Verification: `audit217.py` (standalone, shares no code with the search; includes the
novelty check) and `verify.py` (the earlier independent verifier).

Search: `crescent.c` and `crescent2.c` (exact integer arithmetic on the triangular
lattice), with `super217.py` and `ladder.sh` as drivers.

Data: `sol_n4.txt` .. `sol_n8.txt` (the positive controls) and `results/` holding the
run records `LADDER_217.json`, `STATUS_217.json`, `ladder.log`, the per-shard
heartbeats, and the empty `c2_n9_R*.txt` solution files, whose emptiness is the n = 9
result.
