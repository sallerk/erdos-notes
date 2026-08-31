# Erdős problem #97 — attack report

**The question.** Does every convex polygon have a vertex with no other 4 vertices
equidistant from it? A counterexample would be a convex polygon in which *every*
vertex has 4 other vertices lying at one common distance from it (the distance is
allowed to differ from vertex to vertex). Status: open, $100, falsifiable.

**Bottom line: no counterexample was found, and none was expected.** What this run
did produce is (a) an exact, independently verified 9-point example for the known
k = 3 version, (b) a small exact theorem that empties one natural family
completely, and (c) a structural explanation of why k = 3 is easy and k = 4 is
hard, which then told the search where to look.

### Prior art that determines what is worth doing here `CITED`

AlphaEvolve was pointed at exactly this problem — Problem 6.53 of *Mathematical
exploration and discovery at scale* (arXiv:2511.02864, Georgiev–Gómez-Serrano–
Tao–Wagner). Its objective was, after normalising the polygon to diameter 1: for
each vertex, sort the distances to the other vertices, take the **four consecutive
distances with the smallest total gap**, and score max_i max{d̄/d_i, d_i/d̄}, divided
by the square of the minimum side length. It reached configurations where every
vertex has at least **3** equidistant vertices, and **did not find one for 4**.

That objective is, up to the ratio-versus-difference normalisation, identical to
the one I derived and used here (the "four consecutive order statistics" fact is
forced — the minimiser of the spread over 4-subsets is always a window of
consecutive sorted distances). So a stronger optimiser has already run this exact
attack and failed. **Free-form numerical optimisation of an equidistance objective
is covered ground and is not where the value is.** Everything in §2 below —
exact algebraic solution under imposed symmetry, and structural impossibility
results — is a different instrument, and it is what this report keeps. The
numerical runs in §3 are reported for completeness and as near-miss evidence, not
as novelty.

---

## 0. What "verified" means here

Every object below is stored as JSON with its coordinates and re-checked by
`verify_p97.py`, a standalone script sharing no code with any search or
construction script. It re-derives convex position from the definition (every turn
a strict left turn, total turning exactly 2π, decided by *exact* sign tests) and
re-derives equidistance by *exact* comparison of squared distances. For algebraic
coordinates, zero-testing uses sympy's `minimal_polynomial` (exact) and
sign-testing uses a Cauchy root bound together with a 200-digit evaluation (also
rigorous — the bound certifies which side of zero the value is on). Objects that
exist only in floating point (the near-misses) are labelled float64 with the
tolerance used; those are **not** proofs and the verifier says so on every line.

Verifier control tests: regular 5-, 6-, 7-, 8-gons come back with maximum
equidistant count 2 (correct — §2a), and a deliberately non-convex control is
rejected with the offending vertex named.

---

## 1. Calibration (Phase 1 gate)

### 1a. Danzer's theorem (k = 3, nine points) — REPRODUCED, EXACTLY. `VERIFIED`

I could not obtain Danzer's own coordinates from the literature (erdosproblems.com
returns 403 to the fetcher and the Fishburn–Reeds paper is paywalled), so the
project's own search found the structure and I then solved it exactly.

The mechanism found: with ω = e^{2πi/3} and three complex numbers p, q, r, take the
nine vertices p, ωp, ω²p, q, ωq, ω²q, r, ωr, ω²r. Each orbit is an **equilateral
triangle**, so every vertex already has its two orbit-mates at the common distance
√3·|point| — two equidistant vertices for free. Only one more is needed per orbit:
3 equations for 4 essential parameters, hence a **1-parameter family**. Normalising
p = 1 and imposing

    |p − ω²q| = √3|p|,   |q − ωr| = √3|q|,   |r − ω²p| = √3|r|

the first is exactly |q − ω| = √3 (a circle, so q can be taken with rational
parametrisation), and the second minus half the third is *linear* in r, so r is a
line meeting a circle. Every coordinate therefore lies in a field of degree ≤ 4
over ℚ.

**Object:** `artifact_danzer9_t0.json` — nine vertices, the first three being
(1,0), (−1/2, √3/2), (−1/2, −√3/2), the rest involving √3 and √(−116+67√3).
**Verified:** convex position, and **all nine per-vertex equidistant counts = 3**,
by exact arithmetic only (methods used: syntactic, `is_zero`,
`minimal_polynomial`, `minpoly+bound`; no floating-point step anywhere in the
certification). `artifact_danzer9_test.json` holds six such polygons from
different rational parameters (convexity margins 0.0072 … 0.2131).

Note this is *a* proof of Danzer's statement, not necessarily *his* polygon.

### 1b. Fishburn–Reeds (k = 3, twenty points, one common distance) — NOT reproduced. `ASSERTED (negative)`

I did not clear this half of the gate. Three independent attempts:

* **C_m-symmetric common-distance ansatz** (`orbit_solve.py`). For n = 20 as four
  orbits of five under C_5 with orbit graph K_4: all 15 625 offset assignments,
  12 pinned points along each solution family. Every system solved (residual
  < 1e-12) with minimum unit-degree 3 — and **every solution was non-convex**
  (0 convex hits). A short exact argument covers the sibling case of two orbits of
  ten: the own-circle unit pair pins the radius to 1/(2 sin(πj/10)) ∈ {1.618,
  0.851, 0.618, 0.526}, and the closest ratio of two of these is 0.851, far below
  the cos(π/10) = 0.951 that 20 points in convex position require.
* **Mirror ansatz** (`fr_mirror.py`): put the separating line on the y-axis and
  make B the mirror image of A, so |a_i − b_j| = 1 becomes
  (x_i+x_j)² + (y_i−y_j)² = 1, a *symmetric* relation, i.e. a cubic graph on 10
  indices. That is 15 equations in 19 unknowns — a 4-dimensional family — with
  convex position the only real obstacle. 300 random cubic graphs × 3 starts with
  a convexity homotopy (weights 0 → 3000): best result was a convex configuration
  with equation residual 1.5e-2, i.e. the unit distances were never achieved once
  convexity was enforced. `frmirror_h10_d3_s11.json`, COMPLETED, 609 s.
* **Unstructured optimisation** over all 40 coordinates: never converged (best
  worst |d − 1| ≈ 1.4e-3).

So the machinery reproduces Danzer exactly but does **not** reproduce
Fishburn–Reeds. Theirs is a minimality theorem (n = 20 is the smallest possible),
which suggests a delicate construction; I have no evidence against it and treat it
as `CITED`. This is a real gap in the calibration and it is why the k = 4
conclusions below are stated as "searched, not found" and never as "impossible".

---

## 2. Theory obtained

### 2a. One circle is never enough. `VERIFIED`

If all points lie on a circle of radius R about O then |v_α − v_β| =
2R|sin((α−β)/2)|, so two vertices are equidistant from v exactly when they are
symmetric about the diameter through v. Hence **every distance from a vertex of a
cyclic polygon has multiplicity at most 2** — even the k = 3 version needs at
least two "radii". (Cross-checked by the regular-polygon controls, all of which
return maximum count 2.)

### 2b. THEOREM — the alternating 2m-gon family is empty. `VERIFIED`

*Setup.* Suppose a counterexample has dihedral symmetry D_m (m ≥ 2) with every
vertex on a mirror line. A line through the symmetry centre meets a convex curve
twice, so each of the m mirror lines carries at most 2 vertices and n ≤ 2m; orbits
of mirror points have size m, so n ∈ {m, 2m}; n = m is a regular m-gon (dead by
2a); and n = 2m forces two orbits whose phases differ by π/m — the **alternating
2m-gon**

    v_l = ρ_l · e^{iπl/m},   ρ_l = 1 (l even), b (l odd),   l = 0 … 2m−1,

which is in convex position exactly when cos(π/m) < b < 1/cos(π/m).

*Theorem.* For every m ≥ 2 and every b in that window, the distances |v_0 − v_l|
for l = 0 … m−1 are **strictly increasing**. Hence each distance from v_0 is
attained at most twice among v_1 … v_{m−1} and their mirror images, plus at most
once by the antipodal v_m: the maximum equidistant count is ≤ 3, never 4.

*Proof.* Write c_i = cos(iπ/m). For l even the step needs
q(b) = b² − 2c_{l+1}b + 2c_l − 1 > 0 on b > cos(π/m); q is an upward parabola whose
larger root is below cos(π/m) precisely when
(c_1 − c_{l+1})² − (c_{l+1}² − 2c_l + 1) > 0, and that expression is *identically*
2 sin((l+1)π/m)·sin(π/m) − sin²(π/m), which is positive because
sin((l+1)π/m) ≥ sin(π/m) for 1 ≤ l+1 ≤ m−1. For l odd the corresponding quantity is
sin(π/m)·(2 sin((l+1)π/m)cos(π/m) − sin(π/m)), positive for l ≤ m−2. Both
identities were verified **symbolically and exactly** by sympy (`theorem_alt.py`
returns `A_identity: True`, `B_identity: True`), and the conclusion was
cross-checked numerically for m = 2 … 60 at 119 values of b each (7 021
configurations, mpmath 50 dps): maximum equidistant count seen anywhere = 2, zero
violations of monotonicity.

The l = m step is genuinely different — there the sequence *can* drop — and that
is exactly the loophole that lets multiplicity 3 exist while 4 does not.

*Corollary.* No counterexample to #97 has dihedral symmetry D_m, m ≥ 2, with all
of its vertices on mirror lines.

An independent 60-digit screen (`search_alt.py`, m = 2 … 200, i.e. n up to 400)
agrees: over all m and all (own-pair, cross-pair) index combinations, **zero** of
the quadratic conditions has a root inside the convexity window. For m ≤ 16 the
same combinations were also tested with an *exact* resultant in
ℤ[u]/(minpoly of 2cos(π/m)): 206 combinations do have a common root, but every one
of them lies outside the convexity window. (An earlier version of that screen
reported 214 spurious in-window roots; the theorem is what exposed the bug —
catastrophic cancellation in the quadratic formula when 1 − 2cos(2πk/m) = 0, i.e.
6 | m. The solver is now the numerically stable one and the count is 0.)

### 2c. Why k = 3 is easy and k = 4 is hard

A configuration symmetric under a finite group of plane isometries (necessarily
fixing the centroid, which is interior) gives a vertex v equidistant partners "for
free" from two sources: the stabiliser of v (a reflection, order ≤ 2, which pairs
up every vertex off v's mirror line) and v's own orbit (a regular m-gon, in which
the distances from one vertex have multiplicity 2 — or, when m = 3, both mates at
once). In every case:

> **A vertex of a symmetric convex configuration has at most 2 other vertices
> equidistant from it for free.**

So k = 3 costs 1 equation per orbit and k = 4 costs 2 — unless the two extra
vertices form a *pair*, which costs only 1 but requires the two orbits to be
phase-aligned. Counting parameters against equations:

| symmetry | free parameters | equations, k = 3 | equations, k = 4 |
|---|---|---|---|
| C_m (m ≥ 3), c orbits | 2c − 2 | c | 2c |
| D_m (m ≥ 3), a mirror + g generic orbits (a ≤ 2) | a + 2g − 1 | a + g | a + 2g |

(m = 2 is worse, not better: an orbit of size 2 gives a vertex only its antipode,
so there is no free pair and a generic D_2 vertex costs 3 equations, not 2.)

For k = 3 under C_3 the system is **under**determined as soon as c ≥ 3, which is
exactly Danzer's nine points (c = 3: three equations, four unknowns, a 1-parameter
family — found and solved exactly in §1a). For k = 4 *every* symmetric family is
overdetermined, by at least 1. Moreover the cheap "pair" option is blocked under
pure rotation:

> If orbits V and B of a C_m-symmetric convex polygon are phase-aligned (so that
> some pair of B is symmetric about v's ray), then V ∪ B is an alternating 2m-gon
> **in convex position** (a subset of a convex-position set is in convex
> position), so by 2b the distance from v to that B-pair never equals the distance
> to a V-pair. Hence a C_m-symmetric counterexample needs ≥ 2 equations per orbit,
> i.e. deficiency ≥ 2.

The least overdetermined surviving family is **D_m with generic orbits**
(deficiency exactly 1), in which a mirror-orbit vertex matches its own-orbit pair
against a mirror pair of a generic orbit. That is where the search went.

### 2d. LEMMA — the smallest surviving D_m family, reduced exactly. `VERIFIED`

Take the family that §2c identifies as least overdetermined: D_m with one mirror
orbit M = {e^{2πik/m}} and one generic orbit G = {ρ e^{i(±θ + 2πk/m)}},
0 < θ < π/m, so n = 3m. Its generic vertex w = ρe^{iθ} already has its two
same-chirality orbit-mates equidistant, and needs two further vertices at that same
distance.  A second same-chirality pair is impossible (sin(πk₁/m) = sin(πk₂/m)
gives back the same pair), so the two extras come from just two sources — the
mirror orbit M and the opposite-chirality half of G — and two of the three
resulting combinations die outright, **for every m**:

* *Both extras from the mirror orbit.* Two points of M are equidistant from w only
  if cos(θ − 2πk₁/m) = cos(θ − 2πk₂/m), i.e. 2θ = 2π(k₁+k₂)/m, i.e. θ ∈ (π/m)ℤ —
  which puts w on a mirror line. **Impossible.**
* *Both extras from the opposite-chirality half of G.* Equality forces
  4θ = 2π(k₁+k₂)/m, and with 0 < θ < π/m the only option is θ = π/(2m). Matching
  that distance to the same-chirality pair distance then requires
  sin(π/(2m)) = sin(πj/m), i.e. j = 1/2 or j = m − 1/2, neither an integer.
  **Impossible.**

So a generic vertex must take **one** extra from the mirror orbit and **one** from
the opposite-chirality half of its own orbit. Together with the mirror vertex's
single equation this leaves 3 equations in the 2 unknowns (ρ, θ) — overdetermined
by exactly 1, as §2c predicts — with only finitely many index choices. The dense
grid of §3 row 3 found no solution anywhere in the convex region of this family for
m = 3 … 8 (best worst-vertex spread ≈ 1.2e-2 at m = 5). Turning that last step into
an exact resultant computation over ℚ(e^{2πi/m}) is small (2 unknowns, ~m⁵/4 index
choices, degrees ≤ 4) and is the obvious next exact step; I did not run it.

### 2e. A conditional remark on the common-distance version

If all the radii are equal, each edge of the witness graph is *one* equation
serving *two* vertices. Then the unknowns are 2n − 3 and the equations are |E|
with min degree k, so |E| ≥ kn/2. For k = 3 that is 1.5n < 2n − 3 for n ≥ 6 —
underdetermined, which is exactly why Fishburn–Reeds exists. For k = 4 it is
|E| ≥ 2n, overdetermined by 3, and it would require 2n unit distances among n
points in convex position. The conjectured maximum there is 2n − 7
(Edelsbrunner–Hajnal lower bound, believed tight; the best proven upper bound is
only O(n log n)). So: **the common-distance k = 4 version is impossible if the
2n − 7 conjecture holds** — `CONDITIONAL` on that conjecture, which I did not
attempt to prove.

---

## 3. Searches run for k = 4

All numerical work is float64 unless stated. "Spread" below means, for a vertex,
the smallest possible max − min over any 4 of its distances to the other vertices,
in a polygon normalised to circumradius 1; a counterexample needs it to be 0 at
every vertex.

| # | what | scope | status | outcome |
|---|---|---|---|---|
| 1 | `search_alt.py --mmax 200 --k 4 --exact-all 16` | alternating 2m-gons, m = 2…200 (n ≤ 400); complete for the family | COMPLETED, 84 s, 1 worker | **0** conditions with a root in the convexity window; exact resultants for m ≤ 16 |
| 2 | `search_dm.py --sweep --k 4 --restarts 1200 --nfev 250 --workers 4 --seed 1 --nmax 30` | 52 D_m families, m = 2…8, a ≤ 2, g ≤ 3, n ≤ 30; 1200 restarts each | COMPLETED, ~25 min, 4 workers | best: 2 of 12 vertices reach 4; smallest worst-spread anywhere 7.5e-5 |
| 3 | `grid_dm.py --mmin 3 --mmax 8 --steps 120` | near-exhaustive grid over the 24 deficiency-1 D_m families of dimension ≤ 3, n ≤ 32 | COMPLETED, 73 s, 1 worker | global minimum of the worst-vertex spread = **1.96e-3** (0 would be a counterexample) |
| 4 | `enum_c3.py --c 3 --starts 4 --out enum_c3_c3.json` | **exhaustive** over all 3 375 combinatorial assignments in the C_3 family with 3 orbits (n = 9), both with all orbits required and with one orbit dropped | COMPLETED, 171 s, 1 worker | **0** convex exact solutions in either mode; best residual 3.13e-1 |
| 5 | `enum_c3.py --c 4 --starts 2 --maxcombos 30000` | C_3 family, 4 orbits (n = 12) | **KILLED** after ~40 min | contributes nothing; no result is claimed from it |
| 6 | `search_num.py --n 9 --k 4 --sym 1 --loss linear --nfev 250 --restarts 200 --workers 2 --seed 5` | unstructured, all 18 coordinates | COMPLETED, 101 s, 2 workers | 9 of 9 vertices short; best worst-spread 4.3e-3. (This is the AlphaEvolve-covered attack, run only for a baseline.) |
| 7 | `search_num.py --n 12/15 --k 4 --sym 3 --mask 0 --restarts 1200 --nfev 600 --workers 4 --seed 3` | C_3-symmetric with one orbit's requirement dropped — the structurally best near-miss shape | COMPLETED (252 s / 384 s, 4 workers); the n = 18 and n = 21 jobs were **KILLED** | n = 12: 12 of 12 short. n = 15: **3 of 15 vertices reach 4** — the best near-miss found |
| — | `search_num.py --n 9 --k 3 --restarts 200` (first attempt) | — | **KILLED** after ~13 min | contributes nothing |
| — | `search_dm.py --sweep --restarts 3000` (first attempt) | — | **KILLED** after ~30 min | contributes nothing; relaunched as row 2 |
| — | `run_nearmiss.sh` masked-orbit batch | — | **KILLED** after ~13 min on its first job | contributes nothing |

**Best near-miss.** Two different metrics, both worth stating:

* *By how many vertices reach 4:* the best found is **3 of 15** — a convex,
  C_3-symmetric 15-gon with per-vertex equidistant counts
  [2,4,2,2,2,2,4,2,2,2,2,4,2,2,2], so **12 of its 15 vertices fell short**
  (independently re-checked by `verify_p97.py` on its float path at tolerance
  1e-9). Runner-up: 2 of 12 in a D_2 family, counts [4,1,1,2,1,1,4,1,1,2,1,1].
  Both are in `artifact_nearmiss_k4.json` (25 objects) and
  `artifact_nearmiss_best.json` (the two above).
* *By the minimum count over all vertices:* the best is **3**, attained by the
  entire exact 9-point family of §1a — every one of its nine vertices has exactly
  three equidistant vertices and is exactly one short of a counterexample. That is
  the strongest near-miss in the sense that matters, and it is exact rather than
  numerical.

Within the deficiency-1 D_m families the near-exhaustive grid (row 3) never got
the worst-vertex spread below 2e-3 in a polygon of circumradius 1 — that is three
orders of magnitude away from a solution, not a whisker.

---

## 4. Answer, and what I would keep

**No counterexample to Erdős #97 was found.**

Solid results:

1. `VERIFIED` — an exact convex 9-gon in which every vertex has 3 other vertices
   equidistant from it, with the construction reduced to a circle, a line and one
   rational parameter (Danzer's theorem, reproved constructively).
2. `VERIFIED` — the theorem of §2b: the alternating 2m-gon family contains no
   counterexample for any m, with an exact proof and two independent checks.
3. `VERIFIED` — the corollary that no counterexample has D_m symmetry with all
   vertices on mirror lines, plus the derived obstruction of §2c that blocks the
   cheapest route under pure rotational symmetry.
4. `ASSERTED` — negative search evidence over the D_m and C_3 symmetric families
   described in §3. These are searches, not proofs; "I did not find an X" is all
   that is claimed.
5. `CONDITIONAL` — the common-distance k = 4 version is impossible if the 2n − 7
   unit-distance conjecture for convex position holds.
6. `ASSERTED (negative)` — Fishburn–Reeds' 20-point common-distance configuration
   was **not** reproduced. That is a genuine gap in the calibration.

### What is left, and my judgement on it

Given that AlphaEvolve already ran the numerical attack and stopped at k = 3, the
only routes I would spend more on are the ones it structurally cannot take:

1. **Finish §2d exactly.** The D_m family with one mirror and one generic orbit is
   now reduced to 3 equations in 2 unknowns with ~m⁵/4 index choices, over
   ℚ(e^{2πi/m}). Resultants of two low-degree bivariate polynomials — small, and it
   would upgrade "the grid found nothing" to "no counterexample of this shape
   exists, for every m". *Worth doing; I ran out of budget.*
2. **Push the same treatment to D_m with a = 2 or g = 2** (dimensions 3–5). Harder
   but still finite and still exact.
3. **The counting identity Σ_v d(v) = 4n** (TheAbandonedThinker's, where d(v) is
   the number of witness circles through v) combined with circle-incidence bounds.
   I looked at this and do not think it closes: a circle centred at a vertex can
   cross a convex boundary arbitrarily often (a convex polygon closely inscribed in
   a circle weaves in and out 2n times), so convexity alone puts no bound on how
   many vertices lie on one witness circle, and the counting is not obviously
   forced anywhere. *I would not lead with this.*
4. **Free-form numerical optimisation.** Covered by AlphaEvolve; do not repeat.

Honest summary of the state: a stronger system already ran the search attack and
failed, the exact/symmetric side is where an amateur instrument still has an edge,
and the concrete unfinished piece is item 1.
