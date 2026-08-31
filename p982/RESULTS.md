# Erdős problem #982 — attack report

**The question.** Take a convex polygon with `n` corners. Stand on one corner and measure
the distance to each of the other `n-1` corners; some of those distances repeat. Erdős
conjectured (1946) that in *every* convex polygon there is at least one corner that sees at
least `floor(n/2)` *different* distances. A counterexample would be a convex `n`-gon in
which *every* corner sees at most `floor(n/2) - 1` different distances.

The regular `n`-gon sees exactly `floor(n/2)` at every corner, so there is no slack at all:
a counterexample has to beat the regular polygon.

**No counterexample was found.** What was established is below. Every claim carries a
status label, and every object claimed is in `artifacts/` and is re-checked by a verifier
that shares no code with the search.

---

## 0. The verifier, first

`python verify_machinery.py` → `ALL VERIFIER CHECKS PASSED`. Among other things it confirms
the per-vertex counter returns exactly `floor(n/2)` for the regular `n`-gon for `n = 3..40`
(computed exactly by index arithmetic in `Z_n`, because a regular `n`-gon is not a lattice
polygon), and again independently at 60 decimal digits; that the convex-position test
accepts convex polygons and rejects interior points, duplicates and collinear boundary
points; and that Harborth's 8-point set — the counterexample to the neighbouring problem
#1082 — is correctly *rejected* here, on convexity.

`python verify_artifacts.py` is a second, independent verifier, sharing no code with any
search script. It establishes convex position by **two** different exact characterisations
and requires them to agree: Carathéodory (no point inside a closed triangle of three others,
no three collinear, `O(n⁴)`, used for `n ≤ 24`) and the halfplane test (`p` is a hull vertex
iff the other points seen from `p` lie in one open halfplane, `O(n³)`, cross-product only,
used for all `n`). It re-counts distances from the definition. Final run:
**41 objects, 0 problems, 0 disagreements, 0 counterexamples** (`logs/verify_all_final.log`).

The exact-integer style (orientation by 2×2 integer cross product, squared distances as
integers, no floats in any certification path) is carried over from the validated `p1082`
machinery, as is the "guard against degenerate configurations in a parameter scan" lesson —
which was needed again here, see §7.

---

## 1. Prior art — `CITED` (details and verbatim quotes in `LITERATURE.md`)

* **No computational attack on #982 has ever been reported, at any size, by anyone.** The
  #982 comment thread holds one comment (a bibliographic correction, Quanyu Tang, Oct 2025)
  and one proof claim (Scott Duke Kominers, July 2026) which improves the *lower bound*, not
  a search.
* The two counterexamples in this neighbourhood — Harborth's 8 points, and `eigensolver`'s
  42 points (two concentric regular 21-gons) — refute the **second question of #1082**, a
  stronger statement about arbitrary point sets. **Both are non-convex**, so neither touches
  #982; BorisAlexeev says so explicitly in that thread.
* AlphaEvolve (arXiv:2511.02864 §6 item 33) did attack a convex-polygon problem in this
  family, but it is **#97** ("no other 4 vertices equidistant"), not #982.
* Best proved lower bound `(13/36 + 1/22701)n - O(1) ≈ 0.3611n` (Nivasch–Pach–Pinchasi–
  Zerbib 2013), against the conjectured `0.5n`.

So this search is not a repeat of published work.

---

## 2. The exact `n` certified — `VERIFIED`

> **For every real convex `n`-gon with `n ≤ 7`, some vertex sees at least `floor(n/2)`
> distinct distances. No counterexample exists at those sizes.**

This is "no such polygon exists in the plane", not "no lattice counterexample" and not
"I did not find one".

| `n` | budget | method | result | run |
|---|---|---|---|---|
| 3 | 0 | trivial (every vertex sees ≥ 1 distance) | holds | — |
| 4 | 1 | `decide2.py` — one z3 formula, no enumeration | UNSAT | 0.0 s, COMPLETED |
| 5 | 1 | `decide2.py` — one z3 formula, no enumeration | UNSAT | 0.0 s, COMPLETED |
| 6 | 2 | `decide.py` — 316 patterns | 316/316 UNSAT, 0 unknown | 67.1 s, 16 workers, COMPLETED |
| 6 | 2 | `decide.py … noaltman` — 1834 patterns, no cited theorem used | 1834/1834 UNSAT, 0 unknown | 899.8 s, 3 workers, COMPLETED |
| 7 | 2 | `decide.py` + `retry_unknown.py` — 5354 patterns | 5354/5354 UNSAT, 0 unknown | 465 s (16 workers) + 51 s retry (6 workers), COMPLETED |

**Method.** A counterexample's distance function colours the edges of `K_n` (same colour =
same length), and the counterexample condition says at most `k = floor(n/2)-1` colours meet
each vertex. `patterns.py` enumerates every such colouring up to colour renaming and the
dihedral symmetry of the vertex cycle; `decide.py` then asks z3's `nlsat` whether real
points exist that are in strictly convex position **and** satisfy that colouring's
equalities. Only equalities are imposed, never disequalities, so a polygon whose distances
coincide accidentally is still covered — its own coarser colouring is itself an enumerated
pattern. Hence all patterns UNSAT ⟹ no counterexample. `nlsat` is a complete decision
procedure for polynomial arithmetic over the reals, so UNSAT answers are proofs.

**The Altman dependency was removed.** The enumerator originally used Altman's 1963
total-distance theorem as a prune (316 pattern classes at `n=6`). Re-running without it
gives 1834 classes, all UNSAT. The `n=6` certification therefore rests on nothing but the
problem statement. (The `n=7` run still uses the Altman prune — `CONDITIONAL` on Altman's
theorem, which is published and standard.)

**Controls** (`python control_decide.py`, `logs/control_decide_clean.log`). A prover that
answers UNSAT to everything proves nothing, so the encoding was checked to admit models
*without using z3's search at all*: four convex lattice polygons substituted into every
constraint exactly over the rationals, and the regular 5-, 7- and 9-gons at 80 decimal
digits. All 7 pass. Negative controls ("all pairwise distances equal", impossible for
`n ≥ 4`) return UNSAT for `n = 4..8`.

**A real limitation, stated plainly.** z3 frequently returns UNKNOWN rather than SAT on
these systems — it could not construct the regular pentagon's configuration, nor a convex
lattice hexagon's, even though rational models exist. That is a weakness in *finding*
counterexamples, not in refuting them. It does not weaken the result above, because every
single pattern came back UNSAT and none came back UNKNOWN; had any pattern been satisfiable
it would not have returned UNSAT.

**Independent re-checks, and how far they go.** Three of them, each covering a different
failure mode:

1. *Is the encoding vacuous?* Control A above answers no, exactly, without z3.
2. *Is the pattern enumeration right?* The `noaltman` run enumerates a strict superset
   (1834 classes instead of 316) and gets UNSAT on all of them. If the Altman filter had
   been dropping a live pattern, the superset run would have found it.
3. *Is the formula right?* `decide_alt.py` re-decides the same 316 `n=6` patterns with a
   different formula — equalities through an explicit level variable per colour instead of
   chained to a class representative, and every pattern fed in its reversed vertex
   labelling. Result (`decide_alt_n6.json`, COMPLETED, 296.6 s, 8 workers, 15 s per-pattern
   budget): **207 UNSAT, 0 SAT, 109 UNKNOWN.** So the second formula re-confirms 207 of the
   316 patterns and **contradicts none**; the remaining 109 exceeded its (deliberately
   small) time budget and are simply not re-checked by it. This is *encoding*-independent,
   not solver-independent — both use z3.

An earlier, unbounded attempt at (3) with a free scale variable was **KILLED** after its
worker pool hung, and a second was **KILLED** when the shared machine starved it; neither
contributed anything and both are recorded as killed.

**What is not covered.** `n ≥ 8` for general real polygons. The pattern enumeration passes
3 million raw colourings at `n=8`, and the enumeration-free single-formula version times out
at `n=6`. Nothing here certifies `n ≥ 8`.

---

## 3. Points on a circle can never work — `VERIFIED`

If the points lie on a common circle, two chords from the same point `v` are equal exactly
when their far endpoints are mirror images in the diameter through `v`. So every distance
class at `v` has size at most 2, and `v` sees at least `ceil((n-1)/2) = floor(n/2)` distinct
distances. **Every concyclic convex polygon satisfies the conjecture, for every `n`.**

Checked exhaustively over all `2 095 589` subsets of regular `m`-gons for `m ≤ 20` with exact
index arithmetic in `Z_m`: no violation, and no distance class of size 3 anywhere.

This deletes the whole "subsets of a regular `m`-gon" family in one line, and says where a
counterexample must live: off any single circle, with three vertices equidistant from every
vertex.

---

## 4. What a counterexample must look like — `CITED` (Erdős's own remark)

With `c ≤ k = floor(n/2)-1` distance classes covering `n-1` other vertices, the class sizes
must overshoot 2: total excess `Σ max(0, size-2) ≥ 1` for even `n`, `≥ 2` for odd `n`. In
particular **every** vertex needs three others equidistant from it. This is the
contrapositive of the implication already printed on the #982 page; it is not new, and is
used here only as a search prune (arithmetic checked for all `n ≤ 200`).

---

## 5. The concentric-polygon family — `ASSERTED` (exhaustive over the family; float64 screen)

`eigensolver`'s refutation of #1082 is two concentric regular 21-gons. Its convex analogue
is two concentric regular `m`-gons *staggered* by half a step, `T(m, r)` with `n = 2m`; the
radially-aligned version is never convex, since the inner ring sits inside the hull.

Convex position holds exactly when `cos(π/m) < r < 1/cos(π/m)`.

Every vertex lies on a mirror axis, so each vertex automatically sees exactly `m` distinct
distances; a counterexample needs one coincidence on the outer ring *and* one on the inner
ring. Each single coincidence is a quadratic in `r`, so all candidate radii are enumerable.

`python tworing_par.py 3 400 14` (1.8 s, COMPLETED) and a single-process extension to
`m = 1200` (580 s, COMPLETED): for **all 1198 values of `m` from 3 to 1200 the best
achievable maximum is `m` — exactly one too many, every time. Zero counterexamples.**

The reason is structural. Convexity pins `r` to an interval of width `≈ π²/m²` around 1, so
for large `m` the two rings are squeezed onto the same circle and the configuration
degenerates to the regular `2m`-gon; only 2 to 4 candidate radii land inside the convex
window at each `m`. The #1082 construction needs `r ≈ 0.445`, three orders of magnitude
outside the convex window at `m = 21`. That is exactly why it does not carry over.

Caveats, both in the safe direction for a null result:

* The screen is float64 with relative tolerance `1e-9`. A root sitting within that tolerance
  of the convex window's boundary could be misclassified. The distinct-distance count with a
  tolerance can only *merge* values, i.e. only *under*count, so a genuine counterexample
  would still have been flagged; the tolerance cannot hide one.
* The `artifacts/tworing_m*_best.json` objects were rendered at 60 digits from a **float64**
  radius, so their intended coincidence is only accurate to `~1e-17` and the independent
  verifier (tolerance `1e-40`) correctly reports `m` distinct distances rather than `m-1`.
  The trustworthy objects are the `artifacts/nearmiss_tworing_m*.json` of §7, whose radii
  were computed in mpmath and whose coincidences verify with gaps of 0.1–0.8.

**High-precision cross-check of the float64 screen** (COMPLETED): every candidate radius the
float64 screen produced for `m ≤ 39` and for `m = 50, 75, 100, 150, 200` was re-evaluated in
mpmath at 60 digits — 128 candidates at tolerance `1e-25` — and separately the 40 mpmath-root
candidates for `m ≤ 29` at tolerance `1e-40`. **Zero counterexamples in either pass**, so the
null result is not an artefact of the float64 tolerance.

Objects: `tworing_m3_400.json`, `tworing_m3_1200.json` (best radius, tags and counts for
every `m`).

---

## 6. Lattice pools — `ASSERTED` (exhaustive over the stated pool ONLY)

Exhaustive over *all* strictly convex `n`-gons with vertices in `{p : |p| ≤ R}` in the square
lattice `Z²` or the triangular lattice `A2`, pruned by the counterexample budget. **This
certifies nothing about general real polygons.**

| n | lattice | R | pool | nodes | counterexamples | run |
|---|---|---|---|---|---|---|
| 6 | Z2 | 6 | 113 | 4 474 348 | 0 | 41 s, COMPLETED |
| 8 | A2 | 6 | 127 | 7 271 174 | 0 | 100 s, COMPLETED |
| 8 | Z2 | 7 | 149 | 13 647 872 | 0 | 168 s, COMPLETED |
| 8 | A2 | 7 | 175 | 26 467 094 | 0 | 454 s, COMPLETED |
| 9 | Z2 | 6 | 113 | 4 433 822 | 0 | 36 s, COMPLETED |
| 9 | A2 | 6 | 127 | 7 249 593 | 0 | 75 s, COMPLETED |
| 10 | Z2 | 6 | 113 | 46 132 254 | 0 | 283 s, COMPLETED |
| 10 | A2 | 6 | 127 | 84 946 833 | 0 | 687 s, COMPLETED |
| 11 | Z2 | 5 | 81 | 8 038 701 | 0 | 32 s, COMPLETED |
| 11 | A2 | 5 | 91 | 15 130 413 | 0 | 74 s, COMPLETED |
| 12 | Z2 | 5 | 81 | 33 113 080 | 0 | 85 s, COMPLETED |
| 12 | A2 | 5 | 91 | 72 251 921 | 0 | 277 s, COMPLETED |

Objects: `lattice_*_b*.json` (each records its own pool definition and node count), plus the
run log `lattice_batch_log.json`: **10 of 10 planned runs COMPLETED, 0 counterexamples**.
Earlier runs at `R = 8`/`R = 9` were started and **KILLED** before completing;
they contribute nothing and are recorded as killed in `tasks/lessons.md` and in the
validation index. (`n ≤ 7` is already settled for *all* real polygons by §2, so the lattice
runs matter only for `n ≥ 8` — where the pools reached are small.)

A control confirms the enumerator reaches complete polygons and reproduces ground truth: run
with the budget raised to `floor(n/2)`, it finds the regular hexagon in `A2` (max per-vertex
3) and convex lattice octagons in `Z²` with max per-vertex 4 — both exactly the conjectured
bound. Those objects are saved (`artifacts/lattice_*_near*.json`) and independently verified.

---

## 7. Best near-miss found — `VERIFIED` (objects re-checked independently)

The best possible near-miss is a convex `n`-gon with maximum per-vertex count exactly
`floor(n/2)` — one more than the counterexample budget. The regular `n`-gon does that. The
interesting question is how much of a polygon can be pushed *below* it.

> **For every `m` from 3 to 14 there is a convex `2m`-gon in which exactly half the vertices
> — `m` of the `2m` — see only `floor(n/2) - 1` distinct distances, i.e. they already meet
> the counterexample budget. The other half see exactly `floor(n/2)`.**

These are the staggered two-ring polygons `T(m, r)` with `r` chosen as a root of an
outer-ring coincidence quadratic. Independently verified by `verify_artifacts.py`
(`artifacts/nearmiss_tworing_m3.json` … `m14.json`, plus
`artifacts/nearmiss_hexagon_exact.json`). Sample:

| n | r | per-vertex range | budget | vertices at budget | min gap between distinct squared distances |
|---|---|---|---|---|---|
| 6 | 0.732050807568877… (`= √3 − 1`) | 2 … 3 | 2 | 3 / 6 | 0.8038 |
| 10 | 0.902113032590307… | 4 … 5 | 4 | 5 / 10 | 0.5730 |
| 14 | 0.949855824363647… | 6 … 7 | 6 | 7 / 14 | 0.3435 |
| 20 | 1.024926402959837… | 9 … 10 | 9 | 10 / 20 | 0.1993 |
| 28 | 1.012654648103713… | 13 … 14 | 13 | 14 / 28 | 0.1012 |

The `n = 6` case is available **exactly**, coordinates in `Q(√3)`: two concentric
equilateral triangles staggered by 60°, radii 1 and `√3 − 1`. Three of its six vertices see
only 2 distinct distances — the counterexample budget — and the other three see 3. By §2 no
hexagon can do better, so this object is extremal. The other rows are high-precision (60
digits) with the separation margins quoted above, all more than 39 orders of magnitude above
the `1e-40` tolerance used.

**Continuous measure.** Define
`rho = (largest within-cluster spread of any vertex's distance set, when its n-1 distances
are optimally split into floor(n/2)-1 clusters) / (shortest side of the polygon)`. `rho = 0`
is exactly a counterexample. Over the staggered two-ring family, scanning the whole convex
window (`tworing_rho.py 3 24`, COMPLETED):

| n = 2m | best rho in family | at r | regular `n`-gon rho |
|---|---|---|---|
| 6 | 0.16723316 | 1.70502409 | 0.26794919 |
| 10 | 0.14080823 | 1.22050157 | 0.15838444 |
| 14 | 0.10665156 | 0.90358091 | 0.11267294 |
| 18 | 0.08473101 | 0.94063883 | 0.08748866 |
| 20 | 0.07870400 | 0.99999928 | 0.07870171 |
| 42 | 0.03720708 | 0.98886230 | 0.03741736 |
| 48 | 0.03273688 | 0.99999997 | 0.03273661 |

so the family beats the regular polygon for odd `m` and reduces to it (`r → 1`) for even
`m` — but never gets close to zero, and the margin shrinks as `n` grows. Object:
`tworing_rho_3_24.json` (m = 3..24, COMPLETED, 20001 radii per m, float64).

**Free-form numerical search** (`nsearch.py`, cluster-and-fit with Levenberg–Marquardt,
random restarts, seed0 = 12345, all runs COMPLETED): the optimum found equals the regular
`n`-gon's `rho` to 7 significant figures for `n = 7, 8, 9, 10, 12, 16, 20`. For `n = 6` it
lands on a two-ring hexagon (`rho = 0.210661`, radius ratio 0.54932) — better than the
regular hexagon, though not as good as the 0.16723 the dedicated 1-D family scan finds, so
the free-form search converged to a nearby local optimum there. **No restart at any `n` ever
produced `rho` below `1e-10`.**

| n | trials | best rho found | regular `n`-gon rho |
|---|---|---|---|
| 6 | 3000 | 0.210661 | 0.267949 |
| 7 | 3000 | 0.445042 | 0.445042 |
| 8 | 600 | 0.198912 | 0.198912 |
| 9 | 600 | 0.347296 | 0.347296 |
| 10 | 600 | 0.158384 | 0.158384 |
| 12 | 600 | 0.131653 | 0.131653 |
| 16 | 600 | 0.098491 | 0.098491 |
| 20 | 600 | 0.078702 | 0.078702 |

A degeneracy guard was necessary and is worth flagging: without a floor on the shortest side
the optimiser drove `rho` to `6e-4` by collapsing several vertices onto each other (min
pairwise distance `3.6e-5` against diameter `4.57`). Those numbers were discarded; every
figure above comes from the guarded version, and each saved object records its
min-side/diameter ratio.

---

## 8. Was a counterexample found?

**No.** `ASSERTED` for `n ≥ 8`; for `n ≤ 7`, `VERIFIED` that none exists.

---

## 9. What remains unsearched

* **All real convex `n`-gons for `n ≥ 8`.** This is the big gap. The pattern-enumeration
  method dies at `n = 8` (over 3 million raw colourings) and the enumeration-free
  formulation dies at `n = 6`. Closing `n = 8` would need the pairwise-intersecting
  structure of the per-vertex colour sets turned into a proper covering-design enumeration.
* Symmetric families other than the two-ring dihedral one. A heuristic argument (not a
  proof) says that a convex polygon with a mirror axis through every vertex must *be* a
  staggered two-ring configuration, which §5 rules out — but the halving of a vertex's
  distance count only needs a local pairing, not a global symmetry, so this is not closed.
* Everything outside the lattice pools of §6 and the random restarts of §7.
* The two-ring scan beyond `m = 1200`, and any exact (rather than float64) certification of
  that family.
