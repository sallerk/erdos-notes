# Erdos #831: how few distinct circumradii can n points have?

*Audited three times. Two adversarial passes on 2026-09-07 (`AUDIT_MATH.md`,
`AUDIT_CODE.md`, summarised in `AUDIT_SUMMARY.md`), a round-2 pass the same day
(`AUDIT_ROUND2.md`, 20 findings), and a full pass on 2026-09-16 (`AUDIT_2026-09-16.md`,
32 defects). An earlier version of this header said "every defect fixed or explicitly
withdrawn" and named only the first three reports; the 2026-09-16 pass found that claim
false and at least six round-2 findings still open. What that pass found in this file is
fixed here. What it found elsewhere is listed as open in section 7. The verification suite
runs clean: `lemmas.py`, `lemma6.py`, `AUDIT_SELF.py`, `verify.py`, `cp_verify.py`.*

*2026-09-15: Case A of n = 5 decided exactly by computer algebra (section 5a); the third
shape decided modulo primes only, which is evidence and not a proof (section 5b).
2026-09-16: the common-point branch closed exactly, by hand (section 5c), which also
corrects three claims in section 5 and supersedes its case reduction. `verify.py` covers
sections 5a and 5b; `cp_verify.py` covers 5c; section 7 says what neither covers.*

`h(n)` is the least number of DISTINCT circumradii among the `C(n,3)` triples, over
n-point planar sets with no three collinear and no four concyclic. Erdos asks for an
estimate. The page carries no bound and no value; there is no OEIS sequence; the only
bounds I could find anywhere are in a single 2026 forum comment. That is a statement
about what was reachable: the Erdos-Purdy Handbook chapter and Brass-Moser-Pach could
not be obtained, and either could carry more (REFERENCES.md records this).

Most numbers below are reproducible from this directory; see REPRODUCE.md. The exceptions
are listed in section 7 and flagged where they appear. Two matter. `obstruction433.py` cannot
run as shipped, since its third line execs a `target433.py` that is not in the directory, so the
s^2/2 figures in section 5 cannot be regenerated here. And several figures below were measured by
an auditor and have no artifact in this directory; each is marked where it appears.

## 1. Status of what is established here

| claim | status |
|---|---|
| h(4) = 1, with an exact witness | VERIFIED (exact rational arithmetic) |
| h(5) >= 2 | PROVED, from **Lemma 1 alone**, no external input: a single class holding all ten triples would put the pair {0,1} in three of them |
| h(5) >= 3 | PROVED, using the published f(5) = 4. The audit found that input is not strictly needed: of the two orbits of size-5 classes, both are realisable, but every one of about 7,600 roots found has four concyclic points, so no ADMISSIBLE 5-set has a size-5 class. That search was run by the mathematical auditor and left no artifact in this directory, and it is numerical either way, so the proved route remains the f(5) = 4 one |
| h(6) >= 3, h(7) >= 3, h(n) >= 4 for n >= 8 | PROVED, by monotonicity (Lemma 4a) from h(5) >= 3 and h(8) >= 4 |
| h(5) <= 4 | VERIFIED (exact lattice witness) |
| h(6) <= 6 | VERIFIED (exact lattice witness) |
| h(n) >= ceil(C(n,3)/f(n)) for all n | PROVED, but NOT new: it is the forum comment's own double count. Only the use of exact f(n) values is added |
| h(5) = 4 | NOT ESTABLISHED. Twelve patterns survive the lemmas together with f(5) = 4 (fifteen without it); five are now proved impossible (sections 5a and 5c) and the remaining seven are decided only modulo primes (section 5b), which is evidence and not a proof |
| Case A (an orthocentric size-4 class) has no admissible solution | PROVED 2026-09-15 (section 5a): exact Groebner bases over Q for the 3+3 splits, in two coordinate systems; Lemmas 5 and 6 for the 4+2 splits. Does not decide h(5) |
| The common-point branch (patterns 0, 2, 12, 14) has no admissible solution | PROVED 2026-09-16 (section 5c): Lemma 6 alone for 2 and 12, a rectangle argument for 0, and a resultant with a positivity certificate for 14. No computer decision procedure used |
| The third shape (7 patterns) has no admissible solution | NOT PROVED; strong evidence (section 5b): no solution modulo 32003 and 32749 for all seven, and modulo 1073741827 for six, in two programs. No exact decision over Q |

## 2. Six lemmas

Throughout, "admissible" means no three of the points collinear and no four concyclic.
`lemmas.py` checks, in exact arithmetic, the circle count behind Lemma 1 at three distances,
the existence of the orthocentre in Lemma 2 on six test triangles and its uniqueness on three
of them, the class incidence count of Lemma 3, and Lemma 4a. `lemma6.py` checks Lemma 6's two
congruences symbolically in the given labelling; it does not check Lemma 5. An earlier draft
said "all three lemmas", which was wrong on the count, and a later one credited both scripts
with more than they do.

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

**Lemma 2 (E. Szekeres, quoted by Erdos in [Er75h]).** For any triangle ABC that is not
right-angled, the orthocentre H is the unique fourth point making all four circumradii equal,
and {A,B,C,H} is admissible. The hypothesis is needed for the uniqueness as much as for the
admissibility; the right-angled cases are disposed of just below.
*Proof of uniqueness.* A fourth point D with R(ABD) = R(ACD) = R(BCD) = R(ABC) = r
cannot lie on the circumcircle (that would be four concyclic points), so D lies on the
reflection of the circumcircle in AB and on its reflection in AC. Both reflections pass
through A and through H. They are distinct circles, since coincidence would force the
circumcentre onto both lines and hence onto A; two distinct circles meet at most twice,
and D is not A, so D = H. []

Two degeneracies the argument must exclude. If the triangle is right-angled at C then AB
is a diameter, the reflection of the circumcircle in AB IS the circumcircle, and the
system has no solution off the circle at all. If it is right-angled at A or B then H
lands on a vertex and there is no fourth point. (With the right angle at A, the two reflected
circles have centres antipodal about A, so they are tangent at A and meet nowhere else; that is
the one step the uniqueness proof above cannot take, since it assumes D is not A.) `lemmas.py`
solves the full system exactly on three of its six test triangles and finds that off the
circumcircle the only solution is H. None of its six is right-angled, so it does not test that
case; an earlier draft of this note said it solved six and that the right-angled rows produced
no new point, and neither was true. So h(4) = 1 needs a non-right triangle, and one exists.
Hence **h(4) = 1**, which is exactly Erdos's own opening remark, though he never
writes it as a value.

**Lemma 3.** If all four triples of a 4-set Q inside an ADMISSIBLE set have circumradius r,
then every pair of Q already uses BOTH circles of radius r through it. Hence no further point can form a
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
line o_i o_j is the midpoint, and reflecting 0 in that line gives the sum). The four centres
are distinct and no two are antipodal: o_i = o_j would merge two circles of the class, and
o_i = -o_j would put their second meeting point back at the origin. Labelling
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
The bound is a ceiling, so a strict drop does not by itself improve it: at n = 7 the drop must
reach f_gp(7) <= 11 (ceil(35/11) = 4), and at n = 8 it must reach f_gp(8) <= 13, since
ceil(56/15) and ceil(56/14) are both still 4 while ceil(56/13) is 5. f_gp does not drop at all
for n <= 6, and this
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
there too. The n=5 witness's size-4 class has support 5 and the n=6 witness's has support 6,
so by Lemma 3 neither is an orthocentric quadruple. (An earlier draft gave the n=6 figure as 5,
and a later one left the wrong value standing beside its own correction.) The
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
  all contain the fifth point. That is four equations in four unknowns. **This branch
  is now decided exactly; see section 5a.** What follows is the numerical history, kept
  as a record. The old
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
* **Four triples through a common point.** **This branch is now closed exactly; see section
  5c**, which also supersedes the reduction sketched here and corrects the numerics below. The
  sketch is wrong in two ways that section 5c repairs. It reaches only three of the seven ways
  the triples 014 and 023 can be placed. And it cites the wrong pair twice: 014 on the class
  radius is indeed excluded by Lemma 1 on {0,1}, but 023 on the class radius needs {0,2}, and
  putting both on one parallelogram radius needs {2,3} in one case and {1,4} in the other, a
  pair this note never mentions. The conclusion it reaches is right; the route is not.
  What follows is the history, kept as a record.
  Lemmas 5 and 6 apply. The other four points
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

  so the equations are satisfiable only in a degenerate limit. **Three corrections, from the
  2026-09-16 work.** The minimiser the search returns lies, at every one of the five margins, on
  the family th = (0, -pi-s, -s, -2s) up to rotation, reflection and relabelling of the centres,
  where the residual is exactly
  sin^2(s)/(1 + cos^2 s) = s^2/2 + s^4/12 - ..., reproducing every digit quoted above; that this
  family is the GLOBAL minimiser is shown nowhere, and the search behind it is a 1200-restart
  Nelder-Mead. It is not two centres that merge but three (o1, o3 and o4 approach one point with
  o2 antipodal), so three of the four class circles coincide and the five points collapse to two
  locations. And that family is not merely concyclic in the limit: the 4x4 circle determinant of
  P1, P2, P3, P4 vanishes identically along it, so the configuration realising the floor is
  inadmissible at every s. The region being minimised over still contains admissible
  configurations, which is why the floor is a valid bound; it is the family that attains it that
  is not admissible. This paragraph is corroborating numerics only; the branch is proved in
  section 5c. The scaling law was replicated independently, to six significant figures, using a
  hard nonlinear constraint with no penalty term at all, with the minimiser on the boundary in
  every case; that replication left no artifact in this directory, and the round-2 audit (R10)
  corrected the geometric description of the minimiser, which an earlier draft of this note had
  summarised as "this survived the audit intact".

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

* **slope near 1 (DEGENERATE-ONLY)**: the equalities can be met to any accuracy, but
  only by approaching an inadmissible configuration. Still no admissible realisation,
  but the evidence is a scaling law, exactly as in the (4,3,3) branch above.
* **slope near 0 (OBSTRUCTED)**: the equalities themselves resist, independently of the
  guard. This is the only clean form of negative.

**Two rounds of auditing found this test defective, and then found the fix defective in
the same way.** `tausweep.py` sweeps only tau, the flatness and concyclicity margin, and
holds a class-separation guard fixed at 1e-3. That guard is active at essentially every
optimum (an independent auditor measured it pinned to 1.000e-3 at **14 of 15** on tausweep's
own objective, and a re-run on 2026-09-16 reproduced it in `audit_round2/probe1a.json`, while
`results/audit_r2_self.json`, which measures a different objective, shows the guard active in
12 of its 13 rows and its own summary counter under-reports that as 2), and
sweeping it instead moves the floor nearly proportionally, by factors of 396, 399 and 204 in
the three patterns swept, while the minimum-distance guard moves it by 0.78, 1.77 and 1.09. So the label
OBSTRUCTED was measuring the unswept constant, exactly as the original headline measured
its own. The verdicts in that artifact are now printed as TRACKS-TAU / FLAT-IN-TAU, and
neither should be read as an obstruction.

**The decisive test drops every guard.** `r2check.py` solves the equalities alone, with no
penalties of any kind, by least squares from 120 random starts per pattern, and inspects every
solution that converges to residual below 1e-10. Across the fifteen patterns it finds **577** of
them, and **every one is four concyclic**: the largest concyclicity margin seen anywhere is
2.65e-12, against a scale of 1. So the correct reading is not a mixture:

> Every solution this search found, in any of the fifteen surviving patterns, places four of
> the five points on a common circle.

That is a single clean reason, it applies to all fifteen rather than two, and it does not
lean on h(5) >= 3 the way the class-merger reading did. It also supersedes an earlier
draft's "2 concyclic, 13 class-merge" table, which was a false dichotomy: concyclicity is
what forces the merger, and it is present throughout.

**This is a sample, not a theorem, and an earlier version of this note got that wrong.** It
stated the quantified form, "every exact solution of every one of the fifteen surviving
patterns", as an established fact. Read literally that settles the problem: it says no
admissible 5-point set has three circumradii, hence h(5) = 4, which the status table above
correctly reports as not established. 577 numerically converged local solutions are evidence
about these solution sets, not a description of them. The 2026-09-16 audit found the wrong
form in this file, in the published copy and in the draft comment, and ranked it the worst
defect in the directory.

Two further limits on the screen, both from the audit and neither fixable by more
compute. Its positive control is a 4-class pattern, six equations in six unknowns and
so exactly determined, while every screened pattern is seven equations in six unknowns;
the control therefore never tests the case that matters. The replacement control
`ctrlB.py` does not fix this: its Jacobian rank is 4, not the 5 an earlier draft
claimed (one-sided differences at eps = 1e-6 against an absolute tolerance, with the
two smallest singular values falling as eps^2), and measured per-restart hit rates make
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
**five are now proved impossible and seven are not**. The five are the two with an orthocentric
size-4 class (Case A, section 5a) and the four of the common-point shape (section 5c); pattern 0
is in both lists. The other seven, the third shape, are decided modulo primes only
(section 5b); that is strong evidence, not a proof.
The evidence points to 4 and consists of: the proofs of sections 5a and 5c, which close five
of the twelve patterns; the mod-p verdicts of section 5b; and an exhaustive
search over the 17x17 integer grid finding no admissible 5-point set with three or fewer
distinct circumradii, whose node count an independently written C implementation
reproduced to the last digit, and whose prune was validated against prune-free
enumeration of all 198,792,594 five-subsets of the 11x11 grid (that reimplementation was
written by an auditor and left no artifact in this directory). None of the three settles h(5):
the proofs close five of the twelve patterns and say nothing about the other seven, the mod-p
verdicts are evidence and not proofs over Q, and a lattice is a restriction whose circumradii
are all rational. The pattern screen and the Case A search, which the pre-audit version of this
note also cited, are no longer offered as evidence.

## 5a. Case A, decided exactly (2026-09-15)

Case A is the branch of section 5 in which one radius class is all four triples on four
of the points. By Lemma 2 those four points are an orthocentric system A, B, C, H; by
Lemma 3 their class holds exactly those four triples; so the other six triples all
contain the fifth point P and, for h(5) = 3, fall into exactly two classes. Lemma 1 alone
leaves nine ways to split the six (three of shape 4+2, six of shape 3+3); the size bound
f(5) = 4 removes nothing further here.

**Result.** No admissible 5-point set with three circumradii has an orthocentric size-4
class. For the 3+3 splits this is proved by exact computer algebra over the rationals; for
the 4+2 splits it follows by hand from Lemmas 5 and 6, and msolve agrees.

**The algebra.** A triangle with squared sides a2, b2, c2 and cross product K has squared
circumradius rho exactly when a2*b2*c2 = 4*rho*K^2. So "these three triples share one
radius" is three such equations with one common unknown rho, and "H is the orthocentre"
is two linear conditions. (A collinear triple of distinct points cannot satisfy the
equation: K = 0 would force a2*b2*c2 = 0.) Two coordinate systems were used, F1 with
A = (0,0), B = (1,0) and F2 with P = (0,0), A = (1,0); every labelled configuration can be
moved into either by a similarity, so each covers Case A completely.

Degenerate solutions (two points coinciding, a new radius equal to R, the two new radii
equal) are removed by the Rabinowitsch trick: for a quantity g that must be non-zero, add
a variable t and the equation t*g = 1. If the enlarged system has no solution even over
the complex numbers, which a Groebner basis shows by reducing to {1}, then no admissible
configuration exists. Each such condition holds for every admissible configuration, so
imposing only SOME of them still gives a valid refutation. That freedom is what made the
exact computation feasible.

**What was run, and what each run is worth.** Singular 4.3.2 and msolve 0.6.5, in an
Ubuntu 24.04 container (the exact builds are recorded in `results/engine_versions.json`); see
REPRODUCE.md. Every run, including those stopped by hand, is
in `results/caseA_exact.log`.

1. msolve on all 18 full systems (nine splits in each coordinate system, thirteen
   non-degeneracy conditions each): no complex solution in every case, 78 to 245 seconds
   each. msolve decides this from a Groebner basis modulo one large prime. That
   is right with overwhelming probability, but it is not a proof.
2. Controls, so that "no solution" means something. A planted rational configuration,
   with four radii pinned to its values, is recovered among 32 real solutions in each
   coordinate system. The split-4 system itself, with its class constants rescaled to fit
   a planted configuration and two coordinates pinned, returns that configuration in both
   coordinate systems, so neither the encoding nor the non-degeneracy conditions kill
   genuine solutions. And at the best near-solutions of the old numerical search
   (`caseA2.py`) the new equations are of the same order as that search's own residuals,
   split by split, larger by factors of 1.5 to 2.
3. **Exact over the rationals, Singular.** Split 4 in F2, keeping two conditions (P is not
   B; the first new radius is not R), reduces to {1} in 17 seconds. Split 1 in F1, keeping
   six (P differs from each of A, B, C, H; neither new radius is R), reduces to {1} in 8
   minutes. These are proofs, in two independent coordinate systems. Which conditions to
   keep was chosen by a screen modulo a prime, which only chooses. `verify.py` rebuilds
   both systems from the geometry, sharing no code with `caseA_exact.py`, and checks that
   they are the files Singular read and that every condition imposed is one that
   admissibility forces. A certificate independent of Singular's Groebner code (explicit
   polynomials h_i with sum h_i f_i = 1, to be checked with python-flint) was attempted
   for split 4 with `liftstd` and stopped unfinished at its two-hour budget (7232 s); the last
   memory reading for it is 5.7 GB, taken 40 minutes before the stop. So the proof rests on
   Singular's computation, in two coordinate systems, with msolve agreeing.
4. The six 3+3 splits are one case. Relabelling A, B, C, H keeps an orthocentric system
   orthocentric, is covered by either coordinate system, and carries any 3+3 split to any
   other (`verify.py` checks the orbit). So one exact proof covers all six; there are two.
5. The three 4+2 splits are also one case, and Lemmas 5 and 6 dispose of it: the size-4
   class is four triples through P, which makes A, B, C, H a parallelogram, and no
   parallelogram is orthocentric. msolve agrees on all six 4+2 systems.

What did not work, for the record: Singular on the full thirteen-condition systems ran for
1 h 10, 1 h 40 and 2 h 10 without finishing and was stopped; controls built from systems that
HAVE solutions (one equation dropped, or a planted split left unpinned) drove msolve past
5 to 9 GB of memory and were replaced by the pinned ones; and seven exact runs on reduced 4+2
systems (all three splits, both coordinate systems, slimgb throughout and std on one of them)
were at 3.5 to 6.4 GB where a reading was taken, with two of the seven carrying no memory
reading at all, when they were stopped, unfinished, after 6.5 to 33 minutes; two of the seven
were recorded as still growing at the stop. So the 4+2 case has no computer
proof here; it rests on Lemmas 5 and 6, with msolve in agreement.

**What this does not do.** It settles Case A only. h(5) is still 3 or 4: the common-point
branch is closed separately in section 5c, and the third shape (section 5b) is decided only
modulo primes.

## 5b. The third shape, decided modulo primes (2026-09-15); not proved

The third shape is the seven patterns whose size-4 classes are neither all four triples of
a 4-set nor four triples through one point: patterns 5, 7, 8, 9, 10, 11 and 13 of
`results/penum_n5_k3.json` (recomputed and asserted by `third_exact.py` and `verify.py`).

**Result.** Every one of the seven has no solution modulo every prime that returned a
verdict: 32003 and 32749 (Singular) for all seven, 1073741827 (msolve) for six, and 2147483647
for pattern 5. On pattern 11 msolve returned no verdict at 1073741827 in either gauge: in G1
it crashed when enlarging its hash table failed under a 10 GB memory cap, and in G2 it was
stopped by hand at 5.5 GB, as redundant once Singular had decided the pattern.
That is strong evidence that no admissible 5-point set with three circumradii has a
third-shape pattern. **It is not a proof. No exact decision over Q was obtained for any
third-shape pattern.**

**The algebra.** The same method as Case A, with a simpler gauge: P0 = (0,0), P1 = (1,0),
three free points, and one squared radius per class, so ten equations
N_T = 4*r_c*K_T^2 in nine unknowns. Twelve conditions are imposed with the Rabinowitsch
trick: the nine non-trivial squared distances and the three differences r_a - r_b. No
concyclicity condition is needed. In a third-shape pattern no class contains all four
triples of any 4-set (checked), so four concyclic points would force two classes onto one
radius, which is already excluded. A real solution with all twelve conditions non-zero is
therefore exactly an admissible set with three circumradii.

**What a verdict modulo a prime is worth.** If the system had a complex solution outside
the excluded cases, then for all but finitely many primes p it would also have a solution over
the algebraic closure of F_p, so the reduction could not be the unit ideal there. So "no solution modulo p" can be wrong only for finitely many unlucky
primes, which depend on the hypothetical solution and are unknown. Two or three unrelated
primes agreeing makes an error very unlikely, but it cannot be ruled out, which is why
this is evidence and not a proof.

**Controls and checks.**
* Pinned controls, all fourteen (seven patterns, two coordinate systems): each pattern's
  own system, with the class constants rescaled to fit a planted rational configuration
  and one point pinned, returns exactly one real solution, the planted one.
* `verify.py` rebuilds all seven systems from the geometry, sharing no code with
  `third_exact.py`, and checks that a wrong class assignment is rejected. What it compares
  against are the characteristic-zero input files `exact/G1_full<i>.rab.sing` (and `G1_red11`),
  whose own runs all ended unfinished; the mod-32003, mod-32749 and msolve inputs that produced
  the verdicts carry the same polynomial bodies but are not themselves rebuilt.
* Pattern 11, the one msolve could not do, was also examined numerically (`p11diag.py`):
  1348 complex roots from 1500 random starts, every one in an excluded case. The same run
  on pattern 5 found 1394 of 1395 in an excluded case and the last one within 4e-6 of it.

**What did not work.** Exact runs over Q, the step that decided Case A, did not finish.
On reduced systems (fewer conditions) they stalled: pattern 5's ran two hours. On the full
systems, which collapse modulo a prime in seconds, they reached 2.4 to 4.9 GB where a reading
was taken, with their pair queues still growing; the runs for patterns 5 (in both coordinate
systems, at 2 h 13 and 1 h 38) and 9 (at 3 h 24) were stopped for memory, and patterns 7, 8, 10,
11 and 13 ran to their six-hour cap and were killed there, all five still at degree 7 with their
pair queues growing to the end. A certificate route
(cofactors modulo a prime, to be lifted to Q and checked exactly) was too heavy even
modulo a prime. Every run is accounted for in `results/third_exact.log`, with one gap the log
itself records: pattern 8's start and verdict lines were lost when four runners appended in the
same second, so its record in `results/third_exact_singrab.json` is flagged `reconstructed`,
rebuilt from the live output file (which has no RESULT line, so the run did not finish) and from
the process seen at 5 h 28 min and 2.44 GB, with the 21600 s and the returncode 137 inferred.

## 5c. The common-point branch, closed exactly (2026-09-16)

This is the branch in which one radius class is four triples through a single point. It is now
closed by hand. No decision procedure is involved, which is worth stating plainly: the
quantifier elimination of section 6 spent 40 hours of processor time on a question that half a
page of algebra answers.

**Setup (Lemma 5).** Put the common point at P0 = (0,0) and scale the class radius to 1. The
four circumcircles then have their centres o1..o4 on the unit circle; two unit circles through
P0 with centres o_i, o_j meet again at o_i + o_j; and Lemma 1 forces the 4-cycle labelling, so

        P0 = 0,  P1 = o1+o2,  P2 = o1+o3,  P3 = o2+o4,  P4 = o3+o4,

with the class {012, 013, 024, 034}. Write o_j = (cos th_j, sin th_j) and use the
rotation-invariant angles

        alpha = (th3+th4-th1-th2)/2,  beta = (th2+th4-th1-th3)/2,  gamma = (th1+th4-th2-th3)/2,

and A = cos alpha, B = cos beta, C = cos gamma. The map (th) -> (alpha, beta, gamma) is onto,
since th = (0, beta-gamma, alpha-gamma, alpha+beta) inverts it.

**Lemma 7 (closed forms).** With u = o3-o2, v = o4-o1, D1 = |u+v|^2 and D2 = |u-v|^2,

        R^2(012) = R^2(013) = R^2(024) = R^2(034) = 1,
        R^2(014) = D1/(4 sin^2 alpha),             R^2(023) = D2/(4 sin^2 beta),
        R^2(123) = R^2(234) = D2/(4 sin^2 gamma),  R^2(124) = R^2(134) = D1/(4 sin^2 gamma),
        D1 = 4(1 - A*B) + 4*C*(B - A),             D2 = 4(1 - A*B) - 4*C*(B - A).

The four class triples are three points on a unit circle by construction. The rest follow from
the law of sines at P0 (the angle P1-P0-P4 is alpha modulo pi), from the point reflection of the
parallelogram (which gives the two Lemma 6 congruences), and from sum-to-product for the
diagonals.

**Lemma 8 (degeneracy dictionary).**

        cross(P0,P1,P4)^2 = |P0P1|^2 |P0P4|^2 sin^2 alpha,   and likewise 023 with beta,
        cross(P1,P2,P3)^2 = |P1P2|^2 |P1P3|^2 sin^2 gamma,   and likewise 124, 134, 234,
        A - B = -2 sin((th4-th1)/2) sin((th3-th2)/2),  with |P1-P2|^2 = |o3-o2|^2 and
        |P1-P3|^2 = |o4-o1|^2.

So admissibility translates without circularity: 014 non-collinear means |A| < 1, 023
non-collinear means |B| < 1, and P1 distinct from P2 and from P3 means A != B.

Every identity in Lemmas 7 and 8 is verified EXACTLY by `cp_verify.py`, which writes o_j = z_j^2
with |z_j| = 1, so that conjugation is the substitution z -> 1/z and each claim becomes a Laurent
polynomial identity in z1..z4. None of it is numerical. Every [PASS] line of that script is a
computation, including the sign inspection of the positivity certificate below; statements that
only read earlier checks are printed as NOTE lines and not counted. (An earlier version printed
[PASS] on a hard-coded `True` for that sign inspection and four other lines; the 2026-09-16
audit caught it.)

**The seven placements.** By Lemma 6 the points P1..P4 form a parallelogram, so
R(123) = R(234) and R(124) = R(134) identically, and those four triples carry at most two radii:
the D2 radius for {123, 234} and the D1 radius for {124, 134}. That leaves the triples 014 and
023 to place. Each of them can take the class radius, the D1 radius or the D2 radius, which is
nine combinations; adding the further possibility that D1 = D2 merges the two parallelogram
radii makes ten. Grouping them gives seven cases, of which six are excluded:

1. 014 on the class radius: excluded by Lemma 1 on the pair {0,1}.
2. 023 on the class radius: excluded by Lemma 1 on the pair {0,2}.
3. both on the D2 radius: excluded by Lemma 1 on {2,3}.
4. both on the D1 radius: excluded by Lemma 1 on {1,4}.
5. the matched pairing {014,124,134} | {023,123,234}: excluded by Lemma 1 on {1,4}; it does not
   appear among the fifteen patterns at all.
6. 014 and 023 alone as a class, leaving all four parallelogram triples in one class: that needs
   R(123) = R(124), i.e. D1 = D2, i.e. 8*C*(B-A) = 0, i.e. C = 0 once A != B. Equal diagonals
   make the parallelogram a rectangle, so P1..P4 are concyclic. (This is pattern 0 of
   `results/penum_n5_k3.json`, which Case A also decides.)
7. the crossed pairing {014,123,234} | {023,124,134}: no pair lies in three triples of one
   class, so Lemma 1 does not reach it, and the two triples it separates are not the ones
   Lemma 6 makes equal. This case survives, and the rest of this section closes it.

So exactly one pattern survives: {012,013,024,034} | {123,234,014} | {124,134,023}, which is
canonical pattern 14 under the relabelling (1,4,2,3,0). It is the whole of what survives and
not a representative of it: over all eight relabellings that carry pattern 14's size-4 class to
{012,013,024,034}, the remaining six triples split in exactly one way, the one above. An earlier
draft of section 5 listed only cases 1 to 3, and an earlier draft of THIS section said there
were six cases while omitting case 7, the survivor, so that its list excluded everything.

**The two equations.** R(014) = R(123) and R(023) = R(124), after clearing the positive
denominators of Lemma 7, are

        E1 = D1*(1-C^2) - D2*(1-A^2) = 0,        E2 = D2*(1-C^2) - D1*(1-B^2) = 0,

polynomials in A, B, C alone. The pattern's other equalities are the identities of Lemma 7.

**Theorem.** E1 = E2 = 0 has no real solution with |A| < 1, |B| < 1 and A != B. Hence no
admissible five-point set with three distinct circumradii has a radius class consisting of four
triples through one point.

*Proof.* E1 + E2 = 4*G1 and E1 - E2 = 4*(B-A)*G2, where

        G1 = (1-A*B)*(A^2+B^2-2*C^2) + C*(B-A)^2*(A+B),
        G2 = C*(4 - 2*C^2 - A^2 - B^2) - (1-A*B)*(A+B).

If E1 = E2 = 0 and A != B then G1 = G2 = 0, so G1 and G2 share the root C. The leading
coefficient of G2 in C is the constant -2, so sharing a root forces Res_C(G1,G2) = 0. But

        Res_C(G1,G2) = -8*(A^2-1)*(B^2-1)*(A*B-1)*W(A,B),

and with s = A+B and d = A-B,

        16*W = 64*d^2 + 3*s^2*(s^2-4)^2 + 4*d^6 + 11*d^4*s^2 + 32*d^4 + 2*d^2*s^2*(4-s^2).

On |A| <= 1, |B| <= 1 we have 4 - s^2 = 2(1-A^2) + 2(1-B^2) + d^2 >= 0, so with p = d^2,
q = s^2 and u = 4 - s^2 the certificate is 64p + 3qu^2 + 4p^3 + 11p^2q + 32p^2 + 2pqu, a
polynomial with positive coefficients in non-negative quantities; hence W >= 4*d^2, which is
positive when A != B. With |A| < 1 and |B| < 1 the other factors are non-zero as well, since
1 - A*B = [(1-A^2) + (1-B^2) + d^2]/2 > 0. So the resultant is non-zero and no common root
exists. []

The only hypotheses used are that the triples 014 and 023 are not collinear and that P1 differs
from P2 and P3. No-four-concyclic, class separation, sin gamma != 0, D1 != 0 and D2 != 0 are not
needed. A != B is load-bearing and cannot be dropped: (A,B,C) = (0,0,0) is a genuine real
solution of E1 = E2 = 0, and only A != B excludes it.

**A second proof, elementary.** Multiplying the equations gives the ideal identity
D1*D2*[(1-C^2)^2 - (1-A^2)(1-B^2)] = D1*(1-C^2)*E2 + D2*(1-C^2)*E1 - E1*E2, so with D1, D2 != 0,
sin^4 gamma = sin^2 alpha * sin^2 beta. The equations involve only the cosines, so
representatives alpha, beta, gamma in [0,pi] may be chosen, where the sines are non-negative and
the identity becomes sin^2 gamma = sin alpha * sin beta (the minus branch is exactly the extra
component that keeps the complex solution set one-dimensional). Substituting into E1 gives
E1 = sin alpha * (D1 sin beta - D2 sin alpha), and sin alpha != 0, so D1 sin beta = D2 sin alpha.
With m = (alpha+beta)/2, n = (alpha-beta)/2, X = sin^2 m, Y = sin^2 n that reads

        -8 sin(n) * [ (X+Y) cos(m) - 2*C*X*cos(n) ] = 0,

and n lies in [-pi/2, pi/2], so sin n = 0 means alpha = beta, i.e. A = B. Otherwise square the
bracket and use C^2 = 1 - (X - Y):

        (X+Y)^2*(1-X) - 4*X^2*(1-Y)*(1-X+Y) = (Y-X)*[ (4*X^2-X+1)*Y + 3*X*(1-X) ] = 0.

On 0 <= X, Y <= 1 the second factor is a sum of non-negative terms, since 4X^2-X+1 >= 15/16, so
it vanishes only at Y = 0 with X = 0 or 1; Y = 0 is again A = B. The first factor gives Y = X,
i.e. sin alpha sin beta = X - Y = 0, a collinear triple. Squaring only adds solutions, so every
real solution of the original pair is degenerate. [] This route needs the representative choice
and D1, D2 != 0, which is why the resultant proof is given first.

**Patterns 2 and 12 die by Lemma 6 alone.** Over all eight relabellings that put their
common-point class at {012,013,024,034}, every one splits a pair whose radii are identically
equal, which would put two distinct classes on one radius. Pattern 14 splits none. Singular
agrees from the other side: modulo 32003 and modulo 32749 the ordinary 5-point systems of
patterns 2 and 12 are the unit ideal (2 s and 15 s), while pattern 14's has dimension 1 modulo
both primes. That last figure is a statement about the fibres at two primes and not about
characteristic zero; the runs over Q for patterns 2 and 12 were killed at their one-hour cap,
and no dimension was computed over Q anywhere.

The reason no complex-solution method can close pattern 14 does not need that figure. W(A,A) =
12*A^2*(A^2-1)^2 is not identically zero, so the curve W = 0 does not contain the diagonal and
therefore meets it only finitely often; at each of its infinitely many points with A != B the
resultant vanishes, and the leading coefficient -2 is non-zero there, so G1 and G2 have a common
root C. The complex solution set of E1 = E2 = 0 is therefore genuinely positive-dimensional, and
section 5a's method (saturate the degeneracies, hope for the unit ideal) has nothing to find.
What kills the pattern is |A| < 1 and |B| < 1, which is real information and invisible to it.

**What this does not do.** It closes one branch. Five of the twelve patterns are now proved
impossible: 0 and 1 by Case A (section 5a), and 0, 2, 12 and 14 here. The seven third-shape
patterns remain decided only modulo primes (section 5b). **h(5) is still 3 or 4.**

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
input, at degree three in the full sentence and degree four in the lean one, so both fell
through to the cylindrical algebraic decomposition, `ofsf_cad`. Both completed the projection phase quickly and then stopped producing output
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

## 7. What is still open, as of the 2026-09-16 audit

That audit raised 32 defects (`AUDIT_2026-09-16.md`). Everything it found in this file, in
`REPRODUCE.md` and in `cp_verify.py` is fixed. What remains is below, and a reader should know
it before running anything here.

**Reproduction paths that are broken.**

* `obstruction433.py` cannot run: its third line execs a `target433.py` that is in no copy of
  this directory, and the two functions it needs are defined nowhere else. `REPRODUCE.md` says
  so. `results/obstruction433.json` is kept as a frozen record, and `cp_verify.py` checks its
  floors against their exact closed form. Nothing in this note now rests on it; section 5c replaces what it was evidence for.
* `results/target433.json` and `results/slice433.json` have no producing script and are cited
  nowhere.
* No command-line step writes the Singular input files `exact/G1_full*`, `exact/G2_full5` and
  `exact/G1_cp*` that sections 5b and 5c cite. They were written from a Python prompt with
  functions that are in the directory, and `REPRODUCE.md` gives a snippet that regenerates all
  ten byte for byte.
* `qewatch.py` reads the Redlog log from an absolute path inside one session's scratchpad
  directory, so it has to be edited before use anywhere else. (The round-2 probes under
  `audit_round2/` had the same defect and use relative paths since 2026-09-16.)
* `ctrlB.py` still computes its Jacobian rank the withdrawn way and writes its artifact from
  scratch, so re-running it overwrites the corrected `results/ctrlB.json`.

**Artifacts and docstrings that say more than is true.**

* `results/audit_r2_self.json` carries a summary counter its own source now says is wrong
  (separation reported as 2, the rows show 12). The source was fixed and the artifact never
  regenerated, and re-running the script today would overwrite it with a worse one.
* `lath.py`'s docstring still gives its artifact name without the `_t<target>` suffix the
  script actually writes.
* `verify.py` checks the combinatorics of section 5c (the seven placements, pattern 14's single
  splitting, the Lemma 6 kills) but none of its algebra; that is `cp_verify.py`'s job.

**Earlier public versions.** Until 2026-09-16 the public repository carried the version of
this note from 2026-09-08. That version stated the universal four-concyclic claim of section 5
as a fact, made the false header claim about the 2026-09-07 audit and described the s^2/2
minimiser wrongly. Its `REPRODUCE.md` cited three artifact files under names that do not exist
and listed `obstruction433.py` as runnable, and its `AUDIT_ROUND2.md` pointed to an
`audit_round2/` directory that had not been committed. All of that is corrected in this version, which the repository carries from 2026-09-16, together with
the Case A, third-shape and common-point work of 2026-09-14 to 2026-09-16.

**Numbers quoted above that have no artifact here**, each flagged where it appears: the ~7,600
size-5-class roots; the auditor's 200x200 by 241x241 Case A grid; the 0.33% and 19% hit rates;
the C reimplementation of the lattice node counts and the 198,792,594 five-subsets; and the
six-significant-figure replication of the s^2/2 law, whose script `audit_round2/probe_obstr.py`
is here but prints its comparison without writing an artifact.
