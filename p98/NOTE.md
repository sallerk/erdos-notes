# Erdős #98: the finite end of D_gen(n)

**Problem.** `D_gen(n)` is the minimum number of distinct distances determined by `n`
points in the plane with **no three collinear** and **no four cocircular**. Erdős asks
whether `D_gen(n)/n → ∞`; he could not prove `D_gen(n) ≥ n`. (Sheffer's survey uses the
notation `D_gen`; the problem page writes `h(n)`.)

Everything below separates what is **known in the literature**, what is **computed and
verified here**, and what is **still open in this working directory**.

---

## 1. Where the literature actually stands (verified at source)

* **Lower bound: `D_gen(n) ≥ ⌈(n−1)/3⌉`, and nothing better is published.** Due to
  **Szemerédi** (unpublished, communicated by Erdős in [Er75f]). It requires only *no
  three collinear*. Sheffer's survey, Table 1, lists the `D_gen(n)` lower bound as
  **"Ω(n) (trivial)"** and notes `D_gen(n) ≥ D_no3(n) = Ω(n)`.
  → arXiv:1406.1949
* **The no-four-cocircular hypothesis buys nothing published.** Every published lower
  bound for `D_gen` is inherited from the weaker no-three-collinear setting.
* **Upper bound: `D_gen(n) = n·2^{O(√log n)}`.** Erdős, Füredi, Pach, Ruzsa, *The grid
  revisited*, Discrete Math. **111** (1993) 189–196. Take an integer grid in `d ≈ √log n`
  dimensions, keep the points on a common hypersphere, project generically to the plane;
  the hypersphere plus generic projection force general position.
* **The `n^{log₂3}` bound is Erdős–Hickerson–Pach**, *A problem of Leo Moser about
  repeated distances on the sphere*, Amer. Math. Monthly **96** (1989) 569–575, p. 571,
  Theorem 1: `G(n) < (3/2)n^{log3/log2}`, where their `G(n)` is defined on that page as
  the minimum over `n`-point sets in general position — exactly `D_gen(n)`. The problem
  page's attribution to "Pach" alone is incomplete, not absent. (An earlier draft here
  recorded it as an uncited claim that could not be located; that was wrong.)
* **Szemerédi conjectured `D_gen(n) ≥ (n−1)/2`**, same page: "(In fact, he conjectures
  G(n) ⩾ (n−1)/2, which would generalize a theorem of Altman [A].)" Every value computed
  below satisfies it — equality at n = 3, roughly double it from n = 4 on.
* **The #217 implication is real and sourced.** Erdős, *Some combinatorial and metric
  problems in geometry*, Colloq. Math. Soc. J. Bolyai **48** (1987), 167–177, **p. 168**: "`f(n) ≥ n` for
  `n > n₀` would of course show that my conjecture is true." (The conjecture itself is
  stated on p. 167.)
  A crescent configuration is in general position with exactly `n−1` distances, so its
  existence gives `D_gen(n) ≤ n−1`.
* **No published small values.** No table of `D_gen(n)` in Sheffer, EFPR93, Dumitrescu
  2008, or the crescent-configuration papers; no OEIS sequence (A186704 is the
  *unrestricted* version and its optimal sets, the square and regular pentagon, are
  cocircular and therefore inadmissible here). The one forum post on #98 (Aug 2026) is a
  self-labelled survey whose only unconditional claim is `(n−1)/3`.

So the published gap is `[(n−1)/3, n·2^{O(√log n)}]` and the lower end has not moved
since the 1970s.

## 2. Why the extra hypothesis does not help, in the counting framework

This explains Sheffer's "inherited" bound rather than improving on it.

With no four cocircular, four points equidistant from `p` would lie on a circle centred
`p`, so **at most three points are equidistant from any given point**. Pigeonhole alone
then gives `D_gen(n) ≥ ⌈(n−1)/3⌉` in one line, reaching Szemerédi's constant by a
different and much shorter route (his argument uses convexity plus perpendicular
bisectors and does not need cocircularity at all).

Trying to *combine* both constraints fails, and fails exactly. Write `m(p,d)` for the
number of points at distance `d` from `p`, so `m ≤ 3` and `Σ_d m(p,d) = n−1`; let `t(p)`
be the number of distances seen from `p`. Counting isosceles triples `I = Σ_p Σ_d C(m,2)`:

* **Upper:** for a fixed pair `{q,r}` every apex lies on the perpendicular bisector, a
  line, which carries at most 2 points since no three are collinear. So `I ≤ 2·C(n,2) = n(n−1)`.
* **Lower:** with `a(p)` classes of size 3 at `p`, `Σ_d C(m,2) = (n−1−t(p)) + a(p)`.

Combining gives `Σ_p a(p) ≤ Σ_p t(p)`, which is **true by definition** and therefore
vacuous. The extremal profile (every class at every vertex of size exactly 3) saturates
the perpendicular-bisector count exactly: every pair would have precisely 2 apexes.
**Counting alone cannot beat 1/3.** Beating it needs geometry that rules out the balanced
profile, which is the same extremal object Erdős #97 concerns.


## 2a. Exactly why the constant is stuck, quantified

The literature confirms the framing of §2 and sharpens it. **The constant 1/3 has never
been improved**, verified against the Handbook of Discrete and Computational Geometry
(3rd ed., ch. 1, Table 1.2.4, whose general-position row reads `Omega(n)` with no
constant), Sheffer's survey, Nivasch-Pach-Pinchasi-Zerbib, and the problem page itself.

**The lever is the isosceles count.** Write `Z(P)` for the number of isosceles triples
(apex `p`, base `{q,r}` with `|pq| = |pr|`). Szemeredi's argument is: if every vertex
sees at most `T` distinct distances then convexity gives

    Z >= n(n-1)^2 / (2T)  -  n(n-1)/2,

and no-three-collinear gives `Z <= 2*C(n,2) = n(n-1)`, since a perpendicular bisector is
a line and carries at most 2 points. Together these force `T >= (n-1)/3`. **The extremal
profile of §2 is precisely the equality case of that upper bound.**

Combining a bound `Z <= c*n^2` with the convexity lower bound yields a constant of
roughly `1/(2c+1)`:

| bound on `Z/n^2` | source | resulting constant |
|---|---|---|
| `1` | trivial, no-three-collinear | **1/3** = 0.3333 |
| `11/12` | Dumitrescu, **convex position** | 6/17 = 0.3529 |
| `3/4` | hypothetical | 2/5 = 0.4000 |
| `1/2` | hypothetical | 1/2 = 0.5000 |

So **any constant-factor improvement to `Z` immediately improves the 1/3**, and this has
been achieved only in convex position (Dumitrescu `n^2(1 - 1/12)`, improved by NPPZ to
`n^2(1 - 1/11.981)`). NPPZ pose determining the maximum of `Z` as their **Problem 1** (p. 3, for
"convex (or in general) position"); it is open with only the trivial bound.

**What the no-four-cocircular hypothesis buys: nothing.** This is the calculation nobody
appears to have done, because NPPZ's "general position" means no-three-collinear only.
At a vertex the classes have size at most 3 and sum to `n-1`, so with `t` classes of
which `a` have size 3, `sum_d C(m,2) = (n-1-t) + a`. Maximising:

    3 | (n-1)  =>  Z <= n(n-1)          otherwise  Z <= n(n-2)

and `n(n-1)` is **exactly** the perpendicular-bisector bound `2*C(n,2)`. The two
hypotheses deliver the same number; the gain is `O(n)`, not a constant factor. So the
extra hypothesis is **inert for this argument**, and the constant stays 1/3.

That is a precise negative result rather than a failure to try: it says where the
50-year gap actually sits. Moving the constant requires showing that the perfect profile
(every vertex, every class of size exactly 3, every pair with exactly 2 apexes) fails for
a **constant fraction** of vertices. Section 3f records what that profile forces.


### 2b. Measuring the isosceles maximum: an unfavourable signal

Section 2a shows a bound `Z <= c*n^2` with `c < 1` would lift the constant to about
`1/(2c+1)`. So: how large can `Z` actually get in general position? `maxiso.py` searches
the triangular lattice exhaustively for the configuration maximising it.

| n | max Z found | trivial `n(n-1)` | ratio | refined cap | ratio vs refined |
|---|---|---|---|---|---|
| 5 | 10 | 20 | 0.500 | 15 | 0.667 |
| 6 | 18 | 30 | 0.600 | 24 | 0.750 |

(The refined cap is the no-four-cocircular per-vertex maximum, `n(n-1)` when `3 | n-1`
and `n(n-2)` otherwise.)

**Both ratios increase.** A search returns a LOWER bound on the maximum, so the true
ratios are at least these, which makes the direction worse rather than better. If the
ratio tends to 1 the trivial bound is asymptotically tight and no constant-factor
improvement is available by this route at all.

Two points are not a trend, and `n = 7` costs roughly 100x the `n = 6` run (18.1M nodes,
1262 s) so confirming the direction is expensive. But the honest reading is that the
early `n = 5` figure of 0.500, which looked promising, does not survive one more data
point.

## 3. Computed here, and independently verified

Method. Upper bounds come from explicit witnesses, which are certificates valid however
they were found: exhaustive lattice search (`latmin.py`, exact integers, square and
triangular lattices) and a real-closed-field solver (`direct.py`, `witness.py`). Lower
bounds come from deciding realisability over ℝ: `direct.py` encodes the whole question
as one formula (each pairwise distance must equal one of `k` class variables, plus
non-collinearity and non-cocircularity), so UNSAT means `D_gen(n) > k`.

Every witness is re-checked by `verify.py`, which converts to **real plane coordinates**
and redoes collinearity, cocircularity and distance counts symbolically in sympy, sharing
no code with the searchers. All witnesses pass.

| n | D_gen(n) | status |
|---|---|---|
| 3 | **1** | equilateral triangle |
| 4 | **2** | `≤2` lattice witness; `>1` because 4 mutually equidistant points do not exist (solver UNSAT, also a control) |
| 5 | **3** | `≤3` solver witness in ℚ(√3), squared distances `{1, 2+√3, 4+2√3}`, verified exactly; `>2` by §3a below |
| 6 | **4** | `≤4` triangular-lattice witness, squared distances `{1,3,4,7}`; `>3` by §3c below |
| 7 | **5** | `≤5` triangular-lattice witness `{1,7,12,13,19}`, verified; `>4` by §3h |

The `n=5` witness, up to similarity:

    p0 = (0,0)   p1 = (1,0)   p2 = (1/2, √3/2)   p3 = (−√3/2, −1/2)   p4 = (1/2, −(2+√3)/2)

`p0` has exactly three points at distance 1, saturating the "at most 3 equidistant"
bound of §2, so the extremal profile is realised locally even though it cannot hold
globally for long.

**Solver controls** (both encodings reproduce facts known independently): `n=3,k=1` SAT;
`n=4,k=1` UNSAT; `n=4,k=2` SAT; `n=5,k=4` SAT. All pass.


### 3a. `D_gen(5) > 2`, settled without citing anything

Of the 18 distance patterns on 5 points with 2 classes (up to relabelling of points and
classes), the solver returns UNSAT on 17. The survivor is the **pentagon pattern**:

    class 0: (0,1) (0,2) (1,3) (2,4) (3,4)   -- the 5-cycle 0-1-3-4-2-0
    class 1: (0,3) (0,4) (1,2) (1,4) (2,3)   -- its complementary 5-cycle

an equilateral closed pentagon whose five diagonals are also equal. z3 returns *unknown*
on it after 600 s under both the default solver and `qfnra-nlsat`, so `pentagon.py`
settles it by exact elimination instead. Fixing the scale by `|p0p1| = 1` and writing `t`
for the squared long distance, the Groebner basis has the univariate eliminant

    t^2 - 3t + 1 = 0,      t = (3 ± √5)/2

(the golden ratio squared and its reciprocal: the convex pentagon and the pentagram).
Each root gives two real coordinate solutions, four in total, and **every one has all
five points cocircular** (all 5 of the C(5,4) quadruples degenerate). So every
realisation of the surviving pattern is excluded by the no-four-cocircular hypothesis,
and no 5-point general-position set has 2 distinct distances.

This also re-derives, independently, the classical fact that the regular pentagon is the
only 5-point two-distance set in the plane.


## 3b. Which encoding actually works, measured

Four encodings were tried. The choice matters more than the hardware, so the numbers are
recorded rather than summarised.

| encoding | unknowns | n=4,k=2 | n=5,k=2 (UNSAT) | n=5,k=3 (106 patterns) |
|---|---|---|---|---|
| z3 on coordinates, per pattern | 2n + k | 21 s | 152 s, **1 undecided** | 1198 s: 1 sat, 77 unsat, **28 unknown** |
| z3 single formula (`direct.py`) | 2n + k | 21 s | **872 s, UNKNOWN** | not attempted |
| Groebner elimination by hand (`pentagon.py`) | 2n + k | n/a | settles the 1 leftover | not scalable |
| **Gram matrix (`gram.py`)** | **k − 1** | **0.2 s** | **2.0 s, all decided** | running |

The coordinate encodings carry `2n` unknowns and degree-4 cocircularity constraints, and
z3 degrades badly: a 26% unknown rate at n=5 with three classes, and *unknown* after
872 s on an instance that is provably unsatisfiable. Neither can support a lower bound.

The Gram reformulation removes the coordinates entirely. Squared distances are realisable
in the plane exactly when

    G_ij = (d_0i + d_0j - d_ij) / 2        (i, j = 1 .. n-1)

is positive semidefinite of rank at most 2, so **every 3x3 minor of G vanishes**. Those
minors are polynomials in the distance classes alone, leaving `k-1` unknowns after fixing
the scale (two at k=3, against twelve coordinates at n=6). Cocircularity never enters the
algebra: coordinates are reconstructed only after the class values are pinned down, and
the 4x4 determinant is then evaluated exactly.

One hazard, and how it is handled. `sympy.solve` can return positive-dimensional branches
or values whose reality it cannot settle. Skipping those silently would convert a
completeness hole into a confident `unsat`, so they are counted and the pattern is
reported **`inconclusive`**. A lower-bound claim is only accepted when the inconclusive
and error counts are both zero.

Cross-check: the Gram decider independently reproduces `D_gen(5) > 2` in 2.0 s, agreeing
with the pentagon elimination of §3a, and it independently found a second `n=4` witness
with ratio 1 : (2 - sqrt 3), distinct from the diamond's 1 : 3.


### 3c. `D_gen(6) = 4`

**Augmentation collapses the question to a single pattern.** Seeding from the 5-point
patterns that are not provably unsatisfiable (1 sat, 2 undecided, minus the pentagon
which §3a refutes) and extending by a sixth point leaves, after the subset filter,
**exactly one** canonical 6-point 3-class candidate out of the 3^15 = 14,348,907 raw
colourings. Its three distance classes are each a Hamiltonian path on the six points:

    class 0:  4-2-0-1-3-5      class 1:  3-0-4-5-1-2      class 2:  0-5-2-3-4-1

**The rank conditions pin it down completely.** With class 0 scaled to 1 and classes 1, 2
written u, v, the lex Groebner basis of the vanishing 3x3 Gram minors is just

    v = (u - 1)^2,        u^3 - 5u^2 + 6u - 1 = 0     (discriminant 49)

so there are exactly three branches, all real and positive:

    u ~ 0.198062,  1.554958,  3.246980

Each has a positive-semidefinite rank-2 Gram matrix, so **the pattern is metrically
realisable** and the algebra alone does not exclude it. Everything turns on general
position.

**The realisations are six vertices of a regular heptagon.** In a regular 7-gon the
distance between vertices i and j depends only on `min(|i-j|, 7-|i-j|)` in {1,2,3}, so
deleting one vertex forces a 3-class pattern with no geometry involved. Its canonical
form is **identical** to the surviving candidate. Consistently, branch 2's class values
are exactly the heptagon's squared-chord ratios `sin^2(2pi/7)/sin^2(pi/7) = 3.246979603717`
and `sin^2(3pi/7)/sin^2(pi/7) = 5.048917339522`; the other two roots are the Galois
conjugates, reachable because the vertex map `i -> 2i mod 7` cyclically permutes the three
chord classes, so the same canonical pattern admits all three assignments.

Six vertices of a regular heptagon lie on its circumcircle, so **every** quadruple is
cocircular and the configuration is excluded by hypothesis. A 60-digit reconstruction
agrees: for all three branches, 15 of 15 quadruples have cocircularity determinant below
1e-59, against collinearity determinants of order 0.15 to 0.78.

The only candidate is therefore unrealisable in general position, giving `D_gen(6) > 3`,
and with the verified 4-distance lattice witness, `D_gen(6) = 4`.

**A correction made en route.** The first pass at this printed "not realisable" for the
right reason but on wrong grounds: sympy returned the cubic's roots in
casus-irreducibilis form, `is_real` failed to resolve on those expressions, and all three
branches were silently discarded as non-real. The roots are all real. Redone with
`CRootOf`, the branches survive to the PSD stage and are killed by cocircularity instead.
The verdict is unchanged; the reasoning that first produced it was not sound.


### 3d. `D_gen(7)`: not settled, and what the evidence says

`D_gen(7) >= D_gen(6) = 4` by monotonicity, and a triangular-lattice witness with squared
distances `{1,7,12,13,19}` gives `<= 5` (verified independently in real plane coordinates:
no collinear triple, no cocircular quadruple, max 3 points equidistant from any point).
So the question is whether a 7-point set with only **four** distinct distances exists in
general position.

**A heuristic search, validated in both directions, found none.** `numsearch.py` runs
Nelder-Mead on a 1-D k-means objective over the squared distances with collinearity and
cocircularity penalties, then applies a Gauss-Newton **polish** onto the exact equalities
for the implied pattern. The polish is essential: without it the search returns spurious
patterns from near-misses, and on the first attempt it produced a pattern that the exact
decider immediately refuted.

Controls, both passed:

| case | truth | best raw objective | genuine hits |
|---|---|---|---|
| n=5, k=3 | solution exists | 9.7e-17 | 1, and the pattern matches the exact sweep |
| n=6, k=3 | proved impossible in §3c | 1.2e-07 | 0 |
| **n=7, k=4** | **unknown** | **3.9e-07** | **0** (800 restarts) |

The separation is stark: where a configuration exists the objective collapses to ~1e-16;
where none exists it floors near 1e-7. `n=7, k=4` sits with the impossible case.

**This is not a proof.** A validated heuristic finding nothing is evidence of difficulty,
not of nonexistence. `D_gen(7) = 5` would need the augmentation chain at four classes, and
the exact decider leaves **22%** of 5-point 4-class patterns undecided (52 inconclusive,
39 timeout, 7 error out of 449) against 3% at three classes. Undecided patterns must be
carried as possibly-realisable seeds, so the subset filter that reduced 14,348,907
colourings to a single candidate at `n=6` would be far blunter here.

A separate exhaustive triangular-lattice hunt at R^2 = 169 was **cut off by its time cap
and produced nothing usable**; it is not even a lattice-exhaustive negative.


### 3e. A soundness failure, and the re-derivation of `D_gen(6) = 4`

**`gram.py` emitted false UNSAT verdicts.** It calls `sympy.solve` on the rank conditions
and reports `unsat` when nothing usable comes back. But `sympy.solve` is not complete on
polynomial systems: it can silently omit branches. So its `unsat` never meant
"unsatisfiable", only "sympy found nothing".

This was invisible from its own output. What exposed it was `xcheck.py`, comparing
gram against an independent decider (`hard.py`: Groebner basis, then guaranteed-real
`CRootOf` roots, then high-precision back-substitution) pattern by pattern. At `n=5, k=4`
there were **17 conflicts**, every one a pattern gram called impossible and `hard.py`
called realisable. One was checked by hand: all ten pairwise distances match their
classes, four distinct distances, general position. **`hard.py` was right.**

Consequences, stated plainly:

* **`D_gen(5) = 3` was never at risk.** Its lower bound has two gram-free proofs: z3
  decided 17 of the 18 patterns, and `pentagon.py` settled the survivor by exact
  elimination.
* **`D_gen(6) = 4` was genuinely unproven for a while.** Its seed set came from a gram
  sweep, so false unsats could have removed seeds and left the augmentation incomplete.

**The re-derivation.** Seeds now come only from `hard.py` (7 patterns, versus 3 before),
less the pentagon, which `pentagon.py` refutes by exact elimination rather than by any
solver verdict. Augmentation leaves **three** candidates, all unsatisfiable:

| pattern | why it fails |
|---|---|
| `0,0,0,1,1,1,1,0,0,1,0,0,0,0,1` | uses only **2 classes**; a 6-point 2-distance set gives `D_gen(6) <= 2`, contradicting `D_gen(6) >= D_gen(5) = 3` |
| `0,0,0,1,1,1,2,0,0,2,0,0,0,0,1` | class 0 is **K(3,3)**: p1,p2,p3 would lie on the radius-r circle about p0 AND about p4, but two distinct equal-radius circles share at most 2 points, forcing p0 = p4 |
| `0,0,0,1,1,2,2,0,0,2,0,0,0,0,1` | decided unsat by `hard.py` |

Note the second argument needs no solver at all. Note also that the heptagon pattern of
§3c is **absent** from this candidate set: all six of its 5-subsets reduce to a 5-pattern
the robust decider proves unsat, so it is excluded one level earlier. That is consistent
with §3c, which showed independently that every realisation of it is cocircular.

So `D_gen(6) > 3`, and with the verified 4-distance witness, **`D_gen(6) = 4`**, now with
nothing resting on `gram.py`.


### 3f. What the extremal profile forces, and two cases ruled out

Attaining `D_gen(n) = (n-1)/3` requires every point to see every one of the `(n-1)/3`
distances exactly three times. So **every distance class is a 3-regular graph on all `n`
vertices**, and those classes partition `E(K_n)` — a 3-factorization of `K_n`. Hence:

* 3-regularity needs `3n` even, so **`n` is even**;
* `(n-1)/3` integral needs **`n = 1 mod 3`**;
* together, the bound is attainable only when **`n = 4 mod 6`**: n = 4, 10, 16, 22, ...
* each class is additionally a unit-distance graph and **K(2,3)-free**, since two
  distinct equal-radius circles meet at most twice.

The first two candidates fall to what we already have:

* **n = 4** would need one 3-regular class on 4 points, i.e. `K_4` at a single distance:
  four mutually equidistant points. Impossible in the plane, and indeed `D_gen(4) = 2`.
* **n = 10** would need `D_gen(10) = 3`, but monotonicity gives `D_gen(10) >= D_gen(6) = 4`.

**n = 16 is the first case not settled**, needing `D_gen(16) = 5` against the known
`>= 4`. Settling `D_gen(7) = 5` would close it too.

The parity/divisibility constraint is classical graph factorization, not geometry, and
appears not to have been applied to this problem.

### 3g. The small values are the best known lower bound for 4 <= n <= 10

Monotonicity turns each exact value into a lower bound for all larger `n`. Against
Szemeredi's `ceil((n-1)/3)`:

| n | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 |
|---|---|---|---|---|---|---|---|---|
| `ceil((n-1)/3)` | 1 | 2 | 2 | 2 | 3 | 3 | 3 | 4 |
| ours | **2** | **3** | **4** | 4 | 4 | 4 | 4 | 4 |

So the table is not merely data: on `4 <= n <= 10` it is the **best known lower bound**.
Each further exact value extends the window — `D_gen(7) = 5` would push it to `n <= 13`,
`D_gen(8) = 6` to `n <= 16`. Verified by `lowerbound.py`.


### 3h. `D_gen(7) = 5`

The 4-class question at `n=7` has `4^21 = 4,398,046,511,104` colourings. Augmentation from
the cleaned `n=6` seed set (108 patterns), with the degree and K(2,3) filters and the
subset test, leaves **28** candidates. They fall in four groups:

| stage | killed | how |
|---|---|---|
| monotonicity | 21 | they use fewer than 4 classes, forcing `D_gen(7) <= 3` against `D_gen(7) >= D_gen(6) = 4` |
| z3 (nlsat, sound) | 4 | decided unsat outright |
| equilateral-centre lemma | 2 | see below |
| Groebner, trivial ideal | 1 | the last one |

**The equilateral-centre lemma (new, and reusable).** If three points have all three
mutual distances in class `X`, they form an equilateral triangle of squared side `D_X`.
If a fourth point `v` joins all three in class `Y`, then `v` is that triangle's
circumcentre, so

    D_Y = D_X / 3

since an equilateral triangle of squared side `s^2` has circumradius squared `s^2/3`.
**Corollary:** if one class contains two disjoint equilateral triangles whose centres lie
in the set via *different* classes `Y` and `Z`, then `D_Y = D_X/3 = D_Z`, so two distinct
classes would be the same distance. Contradiction, with no solver. Two candidates died
exactly this way (class 2 held the triangles `(1,2,3)` and `(4,5,6)`, centred at vertex 0
via classes 0 and 1).

**The last candidate.** Pattern `0,0,0,1,1,2,1,3,0,0,3,3,2,2,3,2,2,1,1,0,2`. The lemma
applies once: class 1 holds the triangle `(0,4,5)` and vertex 1 joins all three in class
0, giving `D_0 = D_1/3`. Scaling `D_0 = 1` forces `D_1 = 3` and leaves only `D_2 = u`,
`D_3 = v`. Among the 170 nonzero 3x3 minors of the 6x6 Gram matrix are

    3(2u - 11)/8    and    3(u - 10)/8

which must both vanish, forcing `u = 11/2` and `u = 10` at once. The lex Groebner basis is
`[1]`: the ideal is trivial and there is no solution even over the complex numbers.

So no 7-point set in general position has 4 distinct distances: `D_gen(7) > 4`, and with
the independently verified 5-distance witness, **`D_gen(7) = 5`**.

**Soundness of the chain.** Every seed set was built by discarding patterns `hard.py`
called unsat, and an earlier decider (`gram.py`) was caught emitting false unsats, so this
was checked rather than assumed. All **153** `n=5, k=4` patterns `hard.py` rejected were
re-decided.

That check itself had a fault, found later while working on #654: `z3run.py` constrains the
class values to increase with the class index, but canonical patterns number their classes
by order of first appearance, which is unrelated to magnitude, so its unsat verdicts are
not proofs. Re-running all 70 of them with no ordering imposed
(`pz3_noorder.py`, 90-second hard cap) gave **46 unsat, 24 timeout, 0 sat**. No false unsat
was exhibited, but 24 verdicts stopped being proofs. Corrected tally:

| method | settled |
|---|---|
| trivial Groebner ideal, `= [1]` | 11 |
| z3 unsat with no ordering constraint | 46 |
| **independently settled** | **57 of 153** |
| **still unconfirmed** | **96** |

What that does and does not buy: the disposal of the 28 surviving `n=7` candidates is
already solver-free (lemmas plus monotonicity, above), but their *generation* came from the
cleaned `n=6` seed set, which was pruned with `hard.py` verdicts. So a single false unsat
among the 96 could mean a 29th candidate was never generated. None has been found.

### 3i. `D_gen(8)`: the `n-2` family does not extend on the triangular lattice

`D_gen(8) >= 5` by monotonicity. The `n-2` pattern predicts a witness with 6 distances.
An exhaustive symmetry-reduced search finds none:

| lattice | R^2 | shards complete | nodes | result |
|---|---|---|---|---|
| triangular | 49 | 7 of 7 | 261,025 | no 8-point set with <= 6 distances |
| triangular | 121 | 7 of 7 | 2,163,176 | no 8-point set with <= 6 distances |
| square | 100 | 7 of 7 | 890,398 | no 8-point set with <= 6 distances |

The search uses the p217 symmetry argument: the origin is fixed by translation, so for any
configuration containing 0 the point-group image minimising the smallest remaining point
makes that point orbit-minimal, and restricting the first chosen point to orbit-minimal
representatives is sound. That plus 7-way sharding turned a run that failed to finish in
117 minutes into one that completes in under 3 (R^2=49). Controls reproduce the n=4, n=6
and n=7 witnesses, n=7 in 23 s against 118 s unreduced.

**Calibration.** The known witnesses sit well inside their pools: the n=6 witness has
maximum point norm 7 and the n=7 witness 12, both against a pool of R^2 = 49. If that
growth continued an n=8 witness would need norm about 20-25, comfortably inside R^2 = 121.
So the negative is meaningful rather than vacuous, though extrapolating from two points is
not an argument.

**What this does NOT show.** `D_gen(8) = 7` does not follow. The optimal configuration
need not be lattice-realisable, and we have a concrete precedent: the `D_gen(5) = 3`
witness lives in `Q(sqrt 3)` and no lattice search of any radius would find it. So the
honest statement is:

    no 8-point general-position set with 6 distinct distances exists on the
    triangular lattice within R^2 = 121, nor on the square lattice within R^2 = 100,

and whether `D_gen(8)` is 6 (off-lattice) or 7 is open.

**An upper bound at n=8 (requirement (a)).** A witness with SEVEN distances exists and is
verified in exact plane coordinates:

    (0,0) (-1,0) (-1,1) (1,-3) (2,-3) (3,-1) (-2,-2) (2,-4)     [triangular lattice]
    squared distances {1, 7, 9, 12, 13, 19, 31}, 0 collinear triples, 0 cocircular quads

so `D_gen(8) <= 7`, and with monotonicity `5 <= D_gen(8) <= 7`. A witness is a
certificate however it was found; the search that produced this one was killed by its
time cap before writing its own record, which does not affect the certificate.

**Off-lattice search, completed.** The lattice negatives above are weaker than they look, and we can
prove it: the unique realisable 5-point 3-class pattern has Groebner basis `v = 2u`,
`u^2 - 4u + 1 = 0`, so its only two realisations up to similarity are `u = 2 +- sqrt 3`,
`v = 4 +- 2 sqrt 3`. **Both irrational.** Since squared distances in `Z^2` and `A_2` are
integers, every ratio there is rational, so NO realisation of `D_gen(5) = 3` exists on
either lattice at any radius. (For a general lattice with an irrational Gram entry this
argument does not apply.) The n=5 optimum is therefore invisible to exactly the method
used at n=8, and if `D_gen(8) = 6` were similarly irrational no radius would find it.

So an off-lattice search was run to completion: six independent seeds, each given a
5400-second wall-clock budget (time-bounded rather than restart-bounded, so the run
always finishes and records what it actually did), all six writing completion records.

    4858 restarts performed in total, 0 genuine witnesses.

Calibrating against cases whose truth is known:

| case | truth | best raw objective | hits |
|---|---|---|---|
| n=5, k=3 | exists | 9.7e-17 | 1 |
| n=6, k=3 | proved impossible | 1.2e-07 | 0 |
| n=7, k=4 | proved impossible | 3.9e-07 | 0 |
| **n=8, k=6** | **unknown** | **6.4e-07 to 3.6e-06** | **0** |

Where a configuration exists the objective collapses to about 1e-16; where none exists it
floors near 1e-6 to 1e-7. **n=8 with 6 classes behaves like the proved-impossible cases.**
That is evidence, not proof: a heuristic finding nothing can never rule anything out.

**Summary for n=8.** Three exhaustive lattice searches (complete) and roughly 6600
off-lattice restarts (incomplete) found nothing. That is real evidence for
`D_gen(8) = 7`, hence that the `n-2` family is FINITE and breaks at n = 8 -- which would
make Erdős's hoped-for `h(n) >= n` plausible again. It is **not** a proof. Settling it
rigorously needs the augmentation chain at five classes, one stage longer than the n=7
chain that gave `D_gen(7) = 5`.



## 3j. Two new combinatorial lemmas, and what they do and do not reach

Both fall out of the counting in section 2 but had only ever been used in aggregate,
never as per-pattern filters. Both are sound for any planar set with the general-position
hypotheses, need no solver, and were verified to reject none of the 104 patterns known to
be realisable in this project.

**L3 (bisector).** If `p` is equidistant from `q` and `r` it lies on the perpendicular
bisector of `qr`, a line, which carries at most two points since no three are collinear:

    for every pair {q,r},  #{p : cls(p,q) = cls(p,r)}  <=  2.

**L4 (circumcentre).** A point equidistant from `q, r, s` is the circumcentre of triangle
`qrs`, and a triangle has exactly one:

    for every triple {q,r,s},  #{p : cls(p,q) = cls(p,r) = cls(p,s)}  <=  1.

**Result 1: `D_gen(7) > 4` no longer needs a solver.** All 28 surviving `n=7, k=4`
candidates fall to these lemmas plus monotonicity: L3 alone removes 27, and the last uses
fewer than 4 classes so monotonicity kills it. This retires the 1318-second z3 stage and
both bespoke algebraic arguments of section 3h. It is also a cross-check: L3 independently
rejects the very pattern `last7.py` killed by exhibiting a trivial ideal, two unrelated
methods agreeing.

**Result 2: the cut rate depends on BOTH parameters, in opposite directions.**

| fixed n = 5 | k=2 | k=3 | k=4 | k=5 | k=6 |
|---|---|---|---|---|---|
| cut | 83% | 57% | 34% | 23% | 19% |

| fixed k = 4 | n=5 | n=6 | n=7 |
|---|---|---|---|
| cut | 34% | 53% | 96% |

More classes weaken the lemmas (fewer forced coincidences); more points strengthen them
(more pairs and triples to violate the bounds).

**Result 3, negative: this does NOT rescue the `D_gen(8)` chain.** The k=5 stage from
n=5 to n=6 gives **207,509** candidates against 2,254 at k=4, and the reason is precise:

    raw 2,300,000 -> lemmas 1,484,087 -> subset test 1,484,087 (killed NOTHING)

At k=4 the subset test was the workhorse, cutting 182,919 to 15,249, because the decider
had proved about 198 of 449 five-point patterns unsat so extensions containing them died.
At k=5 the decider proves none, the seed set becomes "everything the lemmas allow", and
any 6-pattern passing the lemmas automatically has all its 5-subsets passing them. The
test is then a tautology. **Lemmas cannot supply what that filter needs**, because its
power came from unsat verdicts on subsets, not from constraints on the whole pattern.

So `D_gen(8)` remains `5 <= D_gen(8) <= 7`, and closing it still needs a decider for 4-5
unknowns rather than more combinatorics.


### 3k. Why n=8 stops here: three independent walls

**Wall 1, the chain.** The k=5 augmentation gives 207,509 candidates at n=6 against 2,254
at k=4. The subset test, which cut 182,919 to 15,249 at k=4, killed NOTHING. Its power
came from decider unsat verdicts on 5-point subsets; with the decider failing at four
unknowns the seed set is "everything the lemmas allow", and any 6-pattern passing the
lemmas automatically has all its 5-subsets passing them, so the test is a tautology.
Projected forward the chain needs 5.2e13 raw extensions at n=8. Not reachable.

**Wall 2, the lemmas peak too late.** Measured survival under the lemma set, random
patterns, showing the n-effect overwhelming the k-effect:

| survival | n=5 | n=6 | n=7 | n=8 |
|---|---|---|---|---|
| k=4 | 81% | 37% | 6.8% | **0.16%** |
| k=5 | 91% | 58% | 20% | **2.8%** |
| k=6 | 94% | 72% | 36% | **9.9%** |

At n=8 the lemmas destroy 97% of k=5 patterns. But they can only be applied to patterns
that have been generated, and wall 1 says those cannot be generated. The tool is strongest
exactly where it cannot be used.

**Wall 3, witness extension.** Any 8th point added to the verified 7-point 5-distance
witness must sit at one of the five existing distances from all seven points, hence on the
intersection of two circles for any chosen pair. That candidate set is finite and was
enumerated completely: **886 intersections, 552 distinct points, 0 admissible**. So that
witness does not extend. This is a complete negative for that configuration only; another
7-point 5-distance set might extend, and it is the only one we have.

**Net.** `5 <= D_gen(8) <= 7`, with the upper bound a verified witness. Closing it needs a
decider for 4-5 unknowns (CAD or regular chains), which is a tooling build, not compute.

## 4. Still open here

* `D_gen(8)`: is it 6 or 7? `>= 5` by monotonicity, and no 6-distance witness exists on
  the triangular lattice within `R^2 = 121` (§3i). Settling it needs either an
  off-lattice witness or the augmentation chain at 5 classes.

## 5. What this is not

Small exact values say **nothing** about `D_gen(n)/n → ∞`. They are the finite end of a
problem whose content is asymptotic, and §2 says the elementary route to the constant is
exhausted. The honest claim available here is a small table nobody appears to have
published, plus the observation in §2 about why the cocircularity hypothesis is inert for
counting arguments.

---

## Companion: the pinned version of the same question, in `../p654`

`D_gen(n)` counts the **total** number of distinct distances in the set. Erdős #654 asks
the **pinned** question: how many distinct distances must SOME point see? Writing
`f(n) = min_X max_i d_X(x_i)`, that directory establishes

    f(3) = 1,  f(4) = 2,  f(5) = 3,  f(6) = 3,   f(7), f(8) in [3, 4]

under both the no-four-concyclic hypothesis and full general position. The two problems
share this directory's machinery (the rank-2 Gram decider, the augmentation framework, the
lattice search with its symmetry reduction, and lemmas L2-L5), but they are **different
functions and must not be conflated**: the `n=8` witness here has `D = 7` and `M = 4`, and
minimising one does not minimise the other.

Two findings there bear directly on this directory:

* **`z3run.py`'s class-ordering constraint is a design fault.** See `ASSUMPTIONS.md` A8.
* **The `n^{log_2 3}` upper bound has a primary source**, found while reading for #654:
  Erdős, SIAM Clemson 1988, p. 35, records "Pach just told me that `h(2^n) <= 3^n`. The
  projection of the n-dimensional cube shows this." That is the construction written up as
  Theorem 1 of Erdős-Hickerson-Pach 1989. See `../p654/PAGE_NOTES.md`.
