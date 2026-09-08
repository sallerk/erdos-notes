# Erdos #831: how few distinct circumradii can n points have?

*Audited 2026-09-07 by two adversarial passes plus my own; every defect fixed or
explicitly withdrawn. See `AUDIT_SUMMARY.md` for the verdict and `AUDIT_MATH.md` /
`AUDIT_CODE.md` for the raw reports. The verification suite runs clean:
`lemmas.py`, `lemma6.py`, `AUDIT_SELF.py`, `verify.py`.*

`h(n)` is the least number of DISTINCT circumradii among the `C(n,3)` triples, over
n-point planar sets with no three collinear and no four concyclic. Erdos asks for an
estimate. The page carries no bound and no value; there is no OEIS sequence; the only
bounds I could find anywhere are in a single 2026 forum comment. That is a statement
about what was reachable: the Erdos-Purdy Handbook chapter and Brass-Moser-Pach could
not be obtained, and either could carry more (REFERENCES.md records this).

Every number below is reproducible from this directory; see REPRODUCE.md.

## 1. Status of what is established here

| claim | status |
|---|---|
| h(4) = 1, with an exact witness | VERIFIED (exact rational arithmetic) |
| h(5) >= 2 | PROVED, from **Lemma 1 alone**, no external input: a single class holding all ten triples would put the pair {0,1} in three of them |
| h(5) >= 3 | PROVED, using the published f(5) = 4. The audit found that input is not strictly needed: of the two orbits of size-5 classes, both are realisable, but every one of ~7,600 roots found has four concyclic points, so no ADMISSIBLE 5-set has a size-5 class. That is numerical, so the proved route remains the f(5) = 4 one |
| h(6) >= 3, h(7) >= 3, h(n) >= 4 for n >= 8 | PROVED, by monotonicity (Lemma 4a) from h(5) >= 3 and h(8) >= 4 |
| h(5) <= 4 | VERIFIED (exact lattice witness) |
| h(6) <= 6 | VERIFIED (exact lattice witness) |
| h(n) >= ceil(C(n,3)/f(n)) for all n | PROVED, but NOT new: it is the forum comment's own double count. Only the use of exact f(n) values is added |
| h(5) = 4 | NOT ESTABLISHED. Twelve patterns survive the lemmas together with f(5) = 4 (fifteen without it); five have a structural treatment here and seven rest on the numerical screen alone. See AUDIT_SUMMARY.md |

## 2. Six lemmas

Throughout, "admissible" means no three of the points collinear and no four concyclic.
`lemmas.py` checks Lemmas 1, 2, 3, 4 and 4a in exact arithmetic, and `lemma6.py` checks
Lemma 6 symbolically. An earlier draft said "all three lemmas", which was wrong on both
the count and on what the script covered.

**Lemma 1.** In an admissible set no pair of points lies in three triples of the same
radius class.
*Proof.* At most two circles of radius r pass through two given points: with
|ab| = d the centres are (d/2, +- sqrt(r^2 - d^2/4)), so there are two when d < 2r, one
when d = 2r, and none when d > 2r. If {a,b} lay in three triples abc1, abc2, abc3 all of
circumradius r, then two of c1, c2, c3 would share a circle (immediate when d = 2r,
since there is only one), and those two together with a and b would be four concyclic
points. []

Note the bound is not tight for a diametral pair, where the true per-class degree is at
most 1. `penum.py` imposes only degree <= 2, so its surviving list is a SUPERSET of the
truth: "no pattern survives" conclusions stand, and counts like "15 patterns" are upper
bounds.

Consequence: a class of size m satisfies `3m <= 2*C(n,2)`, i.e. `m <= n(n-1)/3`.
**Not new.** This is the standard unit-circle double count, already on the #104 page in
the form "every pair of points determines at most 2 unit circles", with the `n(n-1)/3`
refinement credited there to Harborth and Mengersen. It is written out here because the
enumerator needs the per-class form, not because it is original.

**Lemma 2 (E. Szekeres, quoted by Erdos in [Er75h]).** For any triangle ABC the
orthocentre H is the unique fourth point making all four circumradii equal, and
{A,B,C,H} is admissible when ABC is not right-angled.
*Proof of uniqueness.* A fourth point D with R(ABD) = R(ACD) = R(BCD) = R(ABC) = r
cannot lie on the circumcircle (that would be four concyclic points), so D lies on the
reflection of the circumcircle in AB and on its reflection in AC. Both reflections pass
through A and through H. They are distinct circles, since coincidence would force the
circumcentre onto both lines and hence onto A; two distinct circles meet at most twice,
and D is not A, so D = H. []

Two degeneracies the argument must exclude. If the triangle is right-angled at C then AB
is a diameter, the reflection of the circumcircle in AB IS the circumcircle, and the
system has no solution off the circle at all. If it is right-angled at A or B then H
lands on a vertex and there is no fourth point. Solving the full system exactly for six
triangles confirms it: off the circumcircle the only solution is always H, and the
right-angled rows produce no new point. So h(4) = 1 needs a non-right triangle, and one
exists.
Hence **h(4) = 1**, which is exactly Erdos's own opening remark, though he never
writes it as a value.

**Lemma 3.** If all four triples of a 4-set Q have circumradius r, then every pair of
Q already uses BOTH circles of radius r through it. Hence no further point can form a
triple of radius r with two points of Q.
*Proof.* The pair {a,b} of Q lies in exactly two triples of Q, whose third vertices
must be on different radius-r circles through a,b, or four points of Q would be
concyclic. So both circles are occupied, and a fifth point on either of them would be
concyclic with a, b and an existing point. []

**Lemma 4.** No radius class contains exactly three of the four triples of a 4-set.
*Proof.* If R(ABC) = R(ABD) = R(ACD) = r then, exactly as in Lemma 2, D is the
orthocentre of ABC, so R(BCD) = r as well and the class contains the fourth triple
too. []

Lemma 4 is the strongest of these in practice: at n = 5 it cuts the candidate
patterns from 35 to 15.

**Lemma 4a (monotonicity).** `h` is non-decreasing. Any n-subset of an admissible
(n+1)-set is admissible, since both hypotheses are hereditary, and deleting a point
cannot increase the number of distinct circumradii; so `h(n) <= r(X) <= r(Y) = h(n+1)`
for a minimising Y and any n-subset X. Consequently `h(5) >= 3` already gives
`h(6) >= 3` and `h(7) >= 3` without needing f(6) or f(7), and `h(8) >= 4` gives
`h(n) >= 4` for every n >= 8, which is the only statement here that reaches past the
range where f is known. It does not beat the forum bound: ceil((n-2)/2) overtakes 4
at n = 11. Pointed out by the mathematical audit; the note had missed it.

**Lemma 5 (a parametrisation).** Suppose four triples of an ADMISSIBLE set share a
circumradius and all four contain the same point. The admissibility is needed: the four
triples correspond to four edges on the other four points, and up to isomorphism a
4-edge subgraph of K4 is either a 4-cycle or a paw (a triangle with a pendant edge). The
paw has a degree-3 vertex, which puts a pair in three triples of one class and is
excluded by Lemma 1. So the 4-cycle labelling below is forced, not chosen. Put that point at the origin and the radius at 1. Each
of the four circumcircles then has its centre on the unit circle, say o1..o4, and two
unit circles through the origin with centres o_i, o_j meet again at exactly `o_i + o_j`
(the triangle 0-o_i-o_j is isosceles, so the foot of the perpendicular from 0 to the
line o_i o_j is the midpoint, and reflecting 0 in that line gives the sum). Labelling
the class as {012, 013, 024, 034},

        P0 = 0,   P1 = o1+o2,   P2 = o1+o3,   P3 = o2+o4,   P4 = o3+o4,

so at n = 5 the whole configuration is three angles after fixing the rotation.

**Lemma 6.** In that situation `P1 + P4 = P2 + P3`, i.e. **the other four points form a
parallelogram**. Consequently triangles P1P2P3 and P2P3P4 are congruent, as are
P1P2P4 and P1P3P4, so the four triples on those points contribute exactly two distinct
circumradii - two, not one, because all four equal would make the parallelogram
concyclic (a rectangle, inadmissible) or orthocentric, and **no parallelogram is
orthocentric**: `A + H = B + C` with `H = A+B+C-2O` forces `A = O`, and a point cannot
be its own triangle's circumcentre. `lemma6.py` verifies the two congruences
symbolically; the identity `P1+P4 = P2+P3` is immediate from the parametrisation.

Lemma 6 is what makes n = 5 tractable by hand: it says a class of this shape gives
two coincidences among the remaining six triples for free, and then caps how much
further collapse is possible.

## 3. The lower bound: the same double count, with the exact values

**Novelty, stated first.** The reduction below is NOT new. The single forum comment on
the problem page opens "the same simple double-counting lower bound from #104 gives
h(n) >= (n-2)/2", and `C(n,3) / (n(n-1)/3) = (n-2)/2` identically, so that comment IS
this proposition with the Harborth-Mengersen upper bound `f(n) <= n(n-1)/3` substituted
for f(n). What appears not to have been done is to substitute the EXACT values of f(n)
instead, which is what the table below does. Erdos's [Er75h] defines f, g and h in three
consecutive paragraphs and states no relation between them. Caveat: the Erdos-Purdy
Handbook chapter and Brass-Moser-Pach could not be obtained, so the search for prior
statements of the exact-value version is incomplete.

## 3a. The reduction

Let f(n) be the maximum number of unit circles passing through three of n points -
this is exactly erdosproblems #104, and OEIS A003829 records
`f(3..8) = 1, 4, 4, 8, 12, 16` (Harborth-Mengersen 1986; f(8) Harborth 1985).

**Proposition.** `h(n) * f(n) >= C(n,3)`, hence `h(n) >= ceil(C(n,3)/f(n))`.
*Proof.* Fix an admissible X and a radius r. The triples of X with circumradius r are
circles of radius r through exactly three points of X; rescaling X by 1/r turns them
into unit circles, so there are at most f(n) of them. Summing over the h(X) distinct
radii gives C(n,3) <= h(X) f(n) for every admissible X, and h(n) is the minimum of
h(X). []

| n | C(n,3) | f(n) | this bound | the forum bound ceil((n-2)/2) |
|---|---|---|---|---|
| 4 | 4 | 4 | **1** | 1 |
| 5 | 10 | 4 | **3** | 2 |
| 6 | 20 | 8 | **3** | 2 |
| 7 | 35 | 12 | **3** | 3 |
| 8 | 56 | 16 | **4** | 3 |

The two coincide at n = 4 and n = 7 and the reduction wins at n = 5, 6 and 8. Both
are the same double count when f(n) is replaced by the Harborth-Mengersen upper bound
n(n-1)/3; the gain is entirely in using the exact values.

**Can general position sharpen it?** f(n) is a maximum over ALL n-point sets, while
ours are restricted, so the honest input is f_gp(n), the maximum over admissible sets.
Any strict drop would improve the bound. It does not drop for n <= 6, and this
directory can show that from its own artifacts rather than from the literature: a
radius class of size m inside a verified-admissible witness IS m circles of one radius
through three points each, so it certifies f_gp(n) >= m. `fgp.py` reads the witnesses
back and finds largest classes of 1, 4, 4, 8 at n = 3, 4, 5, 6, matching f(n) exactly
each time. So **f_gp(n) = f(n) for n <= 6** and the bound is already the best this route
gives there. At n = 7 and n = 8 our witnesses only reach 8, against f = 12 and 16, so a
drop is possible; a literature agent reports that the published extremal configurations
at those two n ARE degenerate (a collinear triple and a concyclic rectangle at n = 7,
three collinear triples at n = 8), which would make a drop likely, but neither
f_gp(7) < 12 nor f_gp(8) < 16 is proved. f_gp(7) <= 11 would give h(7) >= 4.

Two conditional consequences, stated as implications and not as progress on either
problem: #104's conjecture `f(n) = o(n^2)` **would imply** `h(n) = omega(n)`, and the
prized form `f(n) = O(n^{3/2})` would give `h(n) = Omega(n^{3/2})`. That direction only.
(The #104 page attaches a GBP 100 prize to an `O(n^{3/2})` statement, but the antecedent
there is ambiguous: it may be the general-position question of the preceding sentence
rather than f(n) itself. Treat the attribution as unverified.)
An earlier draft of this note said "is equivalent to", which is false: the converse
would need an UPPER bound on h in terms of f, and nothing here provides one. A set
realising f(n) = Omega(n^2) has one huge radius class, which says nothing about how many
classes it has, and it need not even be admissible.

## 4. Upper bounds: witnesses

All verified in exact arithmetic by `verify.py`, independently of the search that
found them.

| n | h(n) <= | witness |
|---|---|---|
| 4 | 1 | (0,0), (0,3), (1,1), (2,1) - an orthocentric system |
| 5 | 4 | (0,0), (0,7), (2,6), (4,3), (6,9) - class sizes 4,2,2,2 |
| 6 | 6 | (0,0), (0,7), (2,6), (4,3), (6,2), (6,9) |

Two exhaustive lattice statements, both from complete DFS runs with an admissibility
test and a monotone prune (`lath.py`):

* over the **17x17** integer grid (289 points, 8.5M nodes, 29 minutes) **no** admissible
  5-point set has three or fewer distinct circumradii;
* over the **11x11** grid (7.97M nodes) the minimum at n = 6 is exactly **6**.

Neither is a proof about h: a lattice is a restriction, and circumradii of lattice
points are rational, so a lattice cannot see configurations that need irrational
coordinates. They are reported as searches.

The n=5 witness has a class of size 4 = f(5), so it attains the #104 maximum at one of
its radii; the n=6 witness has a class of size 8 = f(6) and so is extremal for #104
there too. Its size-4 class has support 5, so by Lemma 3 it is NOT an orthocentric quadruple.
(The n=6 witness's size-4 class has support 6, not 5 as an earlier draft of this note
said; the conclusion that it is not an orthocentric quadruple holds a fortiori.) The
orthocentric route is a dead end above n = 4 for the SEARCH that starts from it, not as
a theorem about h: see LESSONS.md P4.

## 5. n = 5: the case analysis, and where it stands

**Read AUDIT_SUMMARY.md before this section.** An adversarial audit on 2026-09-07 found
two fatal defects in the instruments that produced the negatives below, and both were
re-checked and confirmed. What follows is the corrected account.

With f(5) = 4 the class sizes must be (4,4,2) or (4,3,3), so **every** 3-class pattern
has a class of size 4. Up to relabelling there are exactly three shapes of size-4 class
(Lemma 4 kills a fourth), and this count was reproduced by two independently written
enumerators.

* **All four triples on four points.** By Lemma 2 those four points are an orthocentric
  system, and by Lemma 3 the class is exactly those four triples, so the remaining six
  all contain the fifth point. That is four equations in four unknowns. The old
  `caseA.py` reached a best relative residual of 7e-8 across the nine admissible splits.
  **That run is not evidence**, for three reasons the audit established: its control
  normalised by the mean of all six radii while constraining only some, so the optimiser
  inflated the denominator with a near-collinear triple and the rungs reported SOLVED
  were violating their equations by up to 61%; that control also dropped equations in an
  order that puts a pair in three triples of one class, which Lemma 1 forbids, so every
  rung was asking for a configuration that forces four concyclic points; and the search
  itself carried no concyclicity, distinctness or class-separation guard at all, the
  failure mode this directory's own LESSONS P7 records.

  **The conclusion rests on two later searches.** The mathematical auditor redid Case A
  independently, with the missing guards, over a 200x200 grid of triangle shapes crossed
  with a 241x241 grid of fifth-point positions plus 4000 restarts per split, and found
  **0 admissible roots in all nine splits**. `caseA2.py` rebuilds it here with every
  guard in place and with a ladder whose equations are drawn from an admissible split,
  so each rung is a legal relaxation. It finds **0 admissible solutions across all nine
  splits** (best equation residuals 1.2e-5 to 6.8e-4), and its ladder reaches only
  **1 equation of 4** at machine precision by the all-splits criterion: two of the four
  sampled splits solve two, none solves three.

  An earlier draft read that as the instrument being weak. The round-2 audit shows it is
  mostly not. Three-equation roots of this system **do** exist, but at a minimum pairwise
  distance of about 1e-11, a concyclicity determinant of about 1e-13 and a squared area
  of exactly zero: coincident points on a straight line, nine orders of magnitude outside
  the guards rather than just outside them. So the guards are not too tight, admissible
  three-equation solutions simply do not exist, and the ladder cannot climb higher
  because there is nothing there to find. That makes the low reach a fact about the
  geometry, but it also means the ladder cannot serve as a control above rung two: a
  control has to be able to succeed.

  Two caveats on the numbers. The ladder was non-monotone until the audit caught it -
  four equations were being "solved" better than three, which is impossible for a
  relaxation - because each rung used its own random restarts; every point is now
  evaluated at every shorter prefix and monotonicity is asserted. And the absolute
  residuals are budget-dependent: a 7.5x increase in restarts moved the rung-2 figures by
  a factor of 2.6, so none of them is converged and none should be quoted as if it were.

  The support for this branch is therefore structural plus the auditor's independent
  grid-based search, not these residuals.
* **Four triples through a common point.** Lemmas 5 and 6 apply. The other four points
  form a parallelogram contributing exactly two radii; the leftover triples 014 and 023
  cannot take the class radius (Lemma 1 on the pair {0,1}) and cannot take the same one
  of the parallelogram's two radii (Lemma 1 on {2,3}). So the only surviving pattern is
  `{012,013,024,034} | {123,234,014} | {124,134,023}`, two equations in three angles,
  which by dimension count should have a one-parameter family of solutions. It does not
  have one away from degeneracy: `obstruction433.py` minimises max(|f1|,|f2|) subject to
  a lower bound s on the angular separation of the four centres and finds the floor
  sitting exactly on that constraint, scaling as

        min max(|f1|,|f2|)  ~  s^2 / 2   (0.0625, 0.0316, 0.0113, 0.0032, 0.00045
                                          at s = 0.35, 0.25, 0.15, 0.08, 0.03)

  so the equations are satisfiable only in the limit where two centres merge, which
  merges two class circles and puts four points on a circle. **This survived the audit
  intact**: an independent implementation reproduced the law to six significant figures
  using a hard nonlinear constraint with no penalty term at all, and confirmed the
  minimiser sits on the boundary in every case.

  A global sweep agrees, and now has an artifact. `gridsweep433.py` evaluates both
  residuals over a 140^3 grid of the three angles: of the 1,576,784 grid points whose
  four centres are pairwise separated by more than 0.25, **not one** has both residuals
  below 0.02, and the minimum of max(|f1|,|f2|) there is 3.92e-2. Relaxing the
  separation to zero drops that minimum to 1.01e-3, the same degenerate-limit behaviour.
  An earlier draft of this note quoted a "110^3 grid" for this; no such run had been
  made, and `results/gridsweep433.json` is the run that was.

  A caution about a companion run. `orthobranch.py` was described in an earlier draft as
  "independently confirming" the other branch. It does not. Its parametrisation forces
  the four points to be a parallelogram, and Lemma 6 proves no parallelogram is
  orthocentric, so the thing it searched for is impossible by construction and its
  80,000 failed restarts were guaranteed. The claim is withdrawn; the underlying
  geometric fact is still proved, just not by that run.
* **The third shape**, in which the four circles have no common point, has no structural
  treatment here and is covered only by the numerical screen.

### The fifteen-pattern screen, and what it actually shows

`pscreen.py` screened all fifteen surviving patterns in six coordinates and returned no
lead. That headline was **overstated**, in a way the audit pinned down precisely. Its
objective contains a hard-coded concyclicity margin tau = 1e-6, and for the two smallest
residuals the optimum sits exactly on that margin. Sweeping tau across four decades
moves those residuals with it, roughly linearly. So the reported "min residual 1.5e-7"
was measuring the constant, not the geometry: those patterns are satisfiable to any
accuracy asked for, arbitrarily close to a four-concyclic configuration.

`tausweep.py` replaces the headline with the honest test. For each pattern it measures
the residual floor at tau = 1e-4 ... 1e-8 and fits the slope in log-log:

* **slope near 1 (DEGENERATE-ONLY)** — the equalities can be met to any accuracy, but
  only by approaching an inadmissible configuration. Still no admissible realisation,
  but the evidence is a scaling law, exactly as in the (4,3,3) branch above.
* **slope near 0 (OBSTRUCTED)** — the equalities themselves resist, independently of the
  guard. This is the only clean form of negative.

**Two rounds of auditing found this test defective, and then found the fix defective in
the same way.** `tausweep.py` sweeps only tau, the flatness and concyclicity margin, and
holds a class-separation guard fixed at 1e-3. That guard is active at essentially every
optimum (an independent auditor measured it pinned to 1.000e-3 at **14 of 15**), and
sweeping it instead moves the floor nearly proportionally, by a factor of about 400
across three decades, while the minimum-distance guard moves it by under 2. So the label
OBSTRUCTED was measuring the unswept constant, exactly as the original headline measured
its own. The verdicts in that artifact are now printed as TRACKS-TAU / FLAT-IN-TAU, and
neither should be read as an obstruction.

**The decisive test drops every guard.** `r2check.py` solves the equalities alone, with
no penalties of any kind, and inspects the exact roots. Across the fifteen patterns it
finds on the order of a thousand roots at residual below 1e-10, and **every one of them
is four concyclic**: the largest concyclicity margin seen anywhere is of order 1e-12,
against a scale of 1. So the correct statement is not a mixture:

> Every exact solution of every one of the fifteen surviving patterns places four of the
> five points on a common circle.

That is a single clean reason, it applies to all fifteen rather than two, and it does not
lean on h(5) >= 3 the way the class-merger reading did. It also supersedes an earlier
draft's "2 concyclic, 13 class-merge" table, which was a false dichotomy: concyclicity is
what forces the merger, and it is present throughout.

Two further limits on the screen, both from the audit and neither fixable by more
compute. Its positive control is a 4-class pattern, six equations in six unknowns and
so exactly determined, while every screened pattern is seven equations in six unknowns;
the control therefore never tests the case that matters. The replacement control
`ctrlB.py` does not fix this: its Jacobian rank is 4, not the 5 an earlier draft
claimed (one-sided differences at eps = 1e-6 against an absolute tolerance, with the
two smallest singular values falling as eps²), and measured per-restart hit rates make
it no harder than the control it replaced, 47/500 against 51/500. And on the only
realisable OVERdetermined instance available in this directory, the n=6 witness pattern,
the same optimiser has a 0.33% per-restart hit rate, so 500 restarts would miss an
existing solution about 19% of the time.

`pdecide.py` re-decided all fifteen with z3 nlsat at 30 minutes per pattern and returned
`unknown` on all fifteen, so the exact decision procedure contributed nothing in either
direction. Three encodings were tried before that run (nine variables at degree six, six at degree
ten, twenty-nine at degree two) and all three failed to decide a single pattern in
thirty seconds; `enc_test.py` now records that in `results/enc_test.json`. An earlier
draft concluded "so the obstacle is the algebra, not the time limit", which does not
follow: a thirty-second budget cannot distinguish the two. What the 1800-second run
shows is that one solver, at one budget, on one encoding family, decides nothing.

### Status

**h(5) is 3 or 4.** Sorting the twelve patterns by the shapes of their size-4 classes,
five have a structural treatment above and **seven rest on the numerical screen alone**.
The evidence points to 4 and consists of: the s^2/2 obstruction in
the common-point branch, which survived independent replication; and an exhaustive
search over the 17x17 integer grid finding no admissible 5-point set with three or fewer
distinct circumradii, whose node count an independently written C implementation
reproduced to the last digit, and whose prune was validated against prune-free
enumeration of all 198,792,594 five-subsets of the 11x11 grid. Neither is a proof about
h(5), because a lattice is a restriction and one branch of the case analysis is
untreated. The pattern screen and the Case A search, which the pre-audit version of this
note also cited, are no longer offered as evidence.

## 6. An attempt to settle one branch by quantifier elimination, and how it ended

The question "is h(5) at least 4" is a sentence about real numbers, so in principle a real
quantifier elimination decides it. In general that is hopeless here: six coordinate
unknowns and equations of degree ten. But one branch is small enough to try. In the
common-point family the class {012, 013, 024, 034} puts all four circles through one
point, so by Lemma 5 the configuration is P1 = o1+o2, P2 = o1+o3, P3 = o2+o4,
P4 = o3+o4 with o1..o4 unit vectors; fixing the rotation leaves three angles, and
Lemma 6 turns two of the six remaining triples into identities, so only two equations
survive. Writing each angle through the tangent half-angle substitution makes every
coordinate rational, and the whole branch becomes a sentence about three real variables.
`mkqe.py` emits it: does there exist (t2, t3, t4) satisfying both equations, with the five
points distinct, no three collinear, no four concyclic, and the three class radii pairwise
different? A `false` would settle this branch; a `true` would hand back a configuration
and prove h(5) = 3.

**It did not finish.** Redlog was run on the sentence twice, once with all eighteen side
conditions (`qe_typeIII.red`) and once with five (`qe_typeIII_lean.red`), the second in
the hope that a smaller input would decompose faster. Virtual substitution refuses the
input at degree three, so both fell through to the cylindrical algebraic decomposition,
`ofsf_cad`. Both completed the projection phase quickly and then stopped producing output
altogether: the full sentence projects to 757 factors (15, 45 and 697 at the three levels)
and the lean one to 210 (9, 21 and 180), after which each printed "Building partial CAD
tree" and nothing more. They were left running for 20.4 and 19.5 hours of
processor time respectively, holding about 2 GB each, and were then stopped. Neither
returned an answer, and the extension phase writes nothing until it completes, so there is
no partial result to report either.

**So this changes nothing.** h(5) is still 3 or 4, on the evidence in section 5. What the
attempt does establish is a cost: the branch is not reachable by a general-purpose CAD on
this input, at least not in a day of one core. Anyone trying again should attack the
projection rather than the machine. The obvious moves are to exploit the symmetry that
permutes o1..o4, to eliminate one variable by hand with a resultant before calling the
decomposition, and to try QEPCAD B, whose projection operators and propagation of
equational constraints are different from Redlog's and may be better suited to a system
that is two equations plus many inequations.
