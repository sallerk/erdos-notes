# Audit of p831 — consolidated result

Three passes on 2026-09-07: an adversarial mathematical audit (`AUDIT_MATH.md`), an
adversarial audit of computational method (`AUDIT_CODE.md`), and my own pass
(`AUDIT_SELF.py`). Totals as reported: **2 FATAL, 11 SERIOUS, 20 MINOR, 8 WORDING.**

Both FATAL defects were re-checked from scratch by me before being accepted
(`AUDIT_RECHECK.py`, `results/audit_recheck.json`). Both reproduce. Nothing below is
taken on an auditor's word.

---

## 1. What survived, and how hard it was attacked

These are the claims that are now MORE trustworthy than before the audit, because
someone tried to break them with independently written code and failed.

| claim | how it was re-checked |
|---|---|
| **h(4) = 1**, witness (0,0),(0,3),(1,1),(2,1) | exact rational arithmetic, permutation-expansion determinant sharing no code with this directory |
| **h(5) ≤ 4**, **h(6) ≤ 6** | same; class profiles [4,2,2,2] and [8,4,2,2,2,2] confirmed |
| **h(5) ≥ 2** and **h(5) ≥ 3** | pattern counts 0 / 1 / 15 reproduced by two independently written enumerators |
| the four lemmas | all survived; a symbolic recheck of Lemma 6 and the parallelogram argument found no error |
| the lower-bound proposition and its table | sound under **both** readings of the A003829 definition |
| **the exhaustive lattice runs** | an independently written C brute force reproduced every node count to the last digit (17×17 n=5 → 8,514,906; 11×11 n=6 → 7,968,042), and the prune was validated against prune-free enumeration of all 198,792,594 subsets at 11×11 n=5 and all 324,540,216 at 9×9 n=6 |
| **the s²/2 obstruction law** | reproduced to six significant figures using a hard nonlinear constraint with no penalty term at all |
| floating point | 50-digit recomputation puts rounding noise 4 to 7 orders below every quoted residual |

The lattice work and the obstruction law are the strongest evidence in the directory
and they came through untouched.

## 2. The two FATAL defects, both confirmed by my own re-check

**F1. The Case A control was inverted.** `ctrlA.py` divided each residual by the mean
of all six radii while constraining only some of them. The optimiser drove an
unconstrained radius to about 1e15 by flattening one triangle, inflating the
denominator and dividing the residual away. Rungs reported SOLVED at 1e-14 were
violating their own equations by 61%, 33% and 2.6%; the only rung that genuinely held
was the one printed as NOT SOLVED. My re-check reproduces this exactly. **Consequence:
the Case A negative had no control, so it was never evidence.** The file is rewritten to
measure each equation against its own two radii, with explicit guards.

**F2. Two of the fifteen screened residuals measured a hard-coded constant.** In
`pscreen.py` the concyclicity guard is a fixed margin tau = 1e-6, and for two patterns
the optimum sits exactly on it. Sweeping tau across four decades moves the "negative"
with it, roughly linearly. So those two patterns are realisable to any accuracy asked
for, arbitrarily close to a four-concyclic configuration; the screen reported the
distance at which its own penalty stopped it. **Consequence: the phrase "0 leads,
a gap of eight orders of magnitude" was measuring the constant 1e-6, not the geometry.**
`tausweep.py` replaces it with the honest test: fit the floor against tau and classify
each pattern. **Superseded by round 2, see section 8.** The sweep classified 13 of 15 as
OBSTRUCTED, but it swept only tau and left the class-separation guard fixed at 1e-3, and
that guard turns out to be active at twelve of the thirteen. The verdict was measuring
the unswept constant.

Both outcomes still mean no ADMISSIBLE realisation was found. The difference is that
one is a scaling law and the other is a floor, and only the second is a clean negative.

## 3. The serious defects that change what is claimed

* **The "harder" control was not harder.** `ctrlB.py`'s Jacobian rank is 4, not 5: it
  used one-sided differences at eps = 1e-6 against an absolute tolerance, and the two
  smallest singular values fall as eps², the signature of exact zeros. Worse, the
  inference ran backwards — a larger rank deficiency means a bigger solution set, which
  random restarts find MORE easily. Measured hit rates: 47/500 for the "harder" control
  against 51/500 for the one it replaced. Statistically identical.
* **The false-negative rate is not bounded.** On the only realisable overdetermined
  instance available in this directory (the n=6 witness pattern), the same optimiser has
  a 0.33% per-restart hit rate, giving roughly a 19% chance that 500 restarts miss a
  solution that exists. The screened patterns are less overdetermined than that, but
  nothing here bounds their rate.
* **`orthobranch.py` was vacuous.** Its parametrisation forces the four points to be a
  parallelogram, and this directory proves no parallelogram is orthocentric. So the
  constraint it searched for is unsatisfiable by construction and all 80,000 restarts
  were guaranteed to fail. Reporting it as "independent confirmation" was wrong; a
  search with a bug would have produced the identical artifact.
* **`verify.py`'s check of the headline exhaustive claims was vacuous.** It tested only
  the `completed` flag and the `target` field, never `best` or `witness`, so a doctored
  artifact claiming a 5-point set with ONE radius would have passed.
* **Numbers with no artifact.** The Case A figure 7e-8, a "110³ grid" that was never
  run at that size, and a three-encoding benchmark that wrote no file. The 110³ claim
  appears to be true (an independent 180³ grid agrees) but was unsupported here.
* **`f(n) = o(n²) is equivalent to h(n) = ω(n)` is false.** Only one direction follows;
  the converse needs an upper bound on h in terms of f, which does not exist here.
* **Lemma 1 was presented as proved here without attribution.** It is the standard
  unit-circle double count already stated on the #104 page.

## 4. Where that leaves the results

Unchanged and verified: **h(4) = 1**, **h(5) ∈ {3,4}** with **h(5) ≤ 4** and
**h(5) ≥ 3**, **h(6) ≤ 6**, the four lemmas, the parallelogram structure, the
lower-bound table, and the exhaustive lattice statements.

Weakened, then partly restored: the case for h(5) = 4. Before the audit it rested on
three legs — the Case A negative, the fifteen-pattern screen, and the s²/2 obstruction.
My Case A instrument is gone, but the mathematical auditor redid that search correctly
and reached the same conclusion, so the leg stands on their run (section 6). The screen
is now a scaling-law statement rather than a clean negative. The obstruction survives
intact, as does the lattice exhaustion over the 17×17 grid, which an independent
implementation reproduced exactly.

**Honest status: h(5) is 3 or 4. The evidence points to 4 but is thinner than the
pre-audit note claimed.**

## 5. Two things the audit ADDED

* **Monotonicity, which the note had missed.** h is non-decreasing, because both
  hypotheses are hereditary and deleting a point cannot add a circumradius. So h(5) >= 3
  gives h(6) >= 3 and h(7) >= 3 with no need for f(6) or f(7), and h(8) >= 4 gives
  h(n) >= 4 for every n >= 8 — the only statement here that reaches past the range where
  f is known. It does not beat the forum bound, which overtakes 4 at n = 11.
* **h(5) >= 3 does not really need the published f(5) = 4.** The mathematical auditor
  attacked that external input directly: there are exactly two orbits of size-5 radius
  classes with pair-degree at most 2, both are realisable, but every one of about 7,600
  roots found carries four concyclic points, usually all five on one circle. So no
  admissible 5-set has a size-5 class. That is a numerical finding, so the proved route
  remains the one through f(5) = 4, but it shows the citation is doing real work rather
  than papering over a gap.

## 6. The Case A branch, rescued

The Case A negative lost its instrument, but not its conclusion. The mathematical
auditor redid the search independently, with the concyclicity, distinctness and
class-separation penalties that `caseA.py` lacks, over a 200x200 grid of triangle shapes
crossed with a 241x241 grid of fifth-point positions plus 4000 restarts per split, and
found 0 admissible roots in all nine splits. The branch is supported; it is simply
supported by that run rather than by anything in `results/`.

---

# 7. Remediation, 2026-09-07

Every defect either fixed, or explicitly withdrawn where no fix is possible.

## Fixed in code

| defect | fix |
|---|---|
| ctrlA normalised by the mean of all six radii (FATAL) | `caseA2.py` measures each equation against its own two radii; `ctrlA.py`/`caseA.py` superseded |
| the control ladder dropped equations in an order Lemma 1 forbids | the new ladder draws its equations from an admissible split, so every rung is a legal relaxation |
| caseA had no concyclicity, distinctness or class-separation guard | all three present in `caseA2.py`, with the margins as parameters |
| pscreen's degeneracy margin was a hidden constant (FATAL) | it is now an argument, and `tausweep.py` fits the floor against it and reports the slope |
| pscreen had no minimum-distance guard | added |
| pscreen's restart box was 2.8e-9 of the permitted volume | widened, and the box is a parameter |
| verify.py checked only metadata on the headline exhaustive runs | it now re-derives the recorded witness from the definitions |
| verify.py and fgp.py globbed checkpoint files as if complete | `.ck.json` excluded |
| two lath runs wrote the same filename | artifact names now carry the search target |
| pdecide wrote no completion flag; its timeout is advisory | flag added, and the advisory nature recorded in the artifact |
| penum renamed the note's Lemma 4 as "Lemma 5" | numbering aligned, and Lemma 1 attributed to the #104 page |
| lemmas.py did not test Lemma 1's content and covered three lemmas of six | rewritten: Lemma 1 tested by counting real centres at d < = > 2r, Lemma 2 uniqueness by solving the full system, plus Lemmas 3, 4 and 4a |
| beam.py justified its seeding "by translation invariance" | corrected; the restriction is stated, not justified |
| orthobranch was cited as confirmation | marked vacuous at the top of the file, claim withdrawn everywhere |

## Artifacts created for numbers that had none

* `results/gridsweep433.json` — the global sweep. Over a 140³ grid, the 1,576,784 points
  with centre separation above 0.25 contain no point with both residuals below 0.02, and
  the minimum there is 3.92e-2. The note previously asserted a 110³ grid that was never run.
* `results/enc_test.json` — the three-encoding z3 benchmark, with the explicit caveat
  that a thirty-second budget cannot distinguish hard algebra from a short budget.
* `results/caseA2.json` — Case A rebuilt. Result: 0 admissible solutions across all
  nine splits, and the ladder reaches only 1 equation of 4 at machine precision, so the
  rebuilt instrument is itself weak and says so. The branch rests on the auditor's
  independent grid-based search, not on this.
* `results/tausweep_n5_k3.json` — the margin sweep, complete: 13 obstructed, 2
  degenerate-only.

## Fixed in the write-up

The false equivalence between the #104 conjecture and h growing superlinearly; the
"support 5" error; "three lemmas" where there are six; the citation of Lemmas 1, 3, 5 for
a result that needs Lemma 1 alone; 15 patterns where the document's own use of f(5) = 4
leaves 12; the non sequitur about thirty-second timeouts; the missing disclosure that 7
of 12 patterns rest on the screen alone; the unhedged claim that no other bounds exist
anywhere, when two sources could not be obtained; the unhedged prize attribution; the
missing degenerate cases in the proofs of Lemmas 1 and 2; the missing admissibility
clause in Lemma 5, without which it is false as literally written; and LESSONS P3 and P9,
both of which drew the wrong conclusion from a broken instrument.

## Not fixable, and stated as such

The positive control for the pattern screen is one equation easier than the systems it
validates, and no control of the right difficulty can be built at n = 5, because a
realisable 3-class pattern there is exactly what is in question. The false-negative rate
of the screen is not bounded. Both limits are now stated in NOTE.md rather than implied.


---

# 8. Round-2 audit, same day: the fix was defective in the same way

`AUDIT_R2_SELF.py` asked one question of the remediated directory: is the new
OBSTRUCTED verdict the old defect wearing a different hat? It is.

`tausweep.py` sweeps tau, the flatness and concyclicity margin. Its objective also
contains a class-separation guard at 1e-3, a minimum-distance guard at 1e-2 and a span
guard, none of which it sweeps. Decomposing the thirteen OBSTRUCTED optima:

* the **separation guard is active at 12 of 13**, its margin sitting on 1e-3 to two digits;
* sweeping the separation margin moves the floor by a factor of **396 across three
  decades** (pattern 2: 1.33e-3, 2.14e-4, 3.26e-5, 3.36e-6), i.e. nearly proportionally;
* sweeping the minimum-distance margin over the same range moves it by **0.78x**, so
  that guard is inert and is not the cause.

So the floor was the separation constant. The corrected reading is that all fifteen
patterns are degenerate-only, in two flavours: two approach four concyclic points, and
thirteen approach a merger of two radius classes. Both are inadmissible, the second
because a merged configuration has at most two distinct circumradii and h(5) >= 3
forbids that. The conclusion h(5) has no 3-class realisation survives; the claim that
thirteen patterns were "genuinely obstructed" does not.

**The general lesson, now recorded as LESSONS P15.** Fixing "the residual sits on guard
A" by sweeping guard A does not work when guards B, C and D are still fixed. The test
has to sweep every active constraint, or report which constraint is active at the
optimum. Both the first fix and the original defect failed the same way.

---

# 9. Round-2 external audit: 1 FATAL, 7 SERIOUS, 10 MINOR, 2 WORDING

Ten previously-reported defects were re-checked and confirmed genuinely fixed. Three
new findings matter.

**R1 (FATAL). Only the prose retracted the verdict.** I corrected NOTE.md and
AUDIT_SUMMARY.md but left `tausweep.py` defining OBSTRUCTED as "the equalities themselves
cannot be satisfied", left thirteen `"verdict": "OBSTRUCTED"` records in its artifact,
and left REPRODUCE.md telling the reader to run it. A retraction that lives only in prose
is not a retraction. Fixed: the labels are now TRACKS-TAU and FLAT-IN-TAU, the docstring
says neither means obstruction, and the artifact is regenerated.

**R2 (SERIOUS), and it improves the result.** With every guard removed the equality
systems have on the order of a thousand exact roots, and **every one is four-concyclic**
(largest margin about 1e-12). My "2 concyclic, 13 class-merge" table was a false
dichotomy: concyclicity is what forces the merger and it is present in all fifteen. I
re-derived this myself in `r2check.py`. The conclusion is now a single clean statement
and no longer leans on h(5) >= 3.

**R5 (SERIOUS). My Case A ladder was internally impossible.** Four equations came back
"solved" one to two orders better than three on all four splits, which cannot happen: a
3-equation system is a relaxation of the 4-equation one. Solving each rung with
independent random restarts allowed a rung to miss a point another rung had found, so
`ladder_top = 1`, the number NOTE.md offered as its honest self-assessment, was restart
noise. Fixed: every point found at any rung is now evaluated at every shorter prefix, and
an assertion enforces monotonicity.

**Two smaller ones, both mine.** AUDIT_SUMMARY said tausweep's objective contains a
minimum-distance guard; it does not, so my round-2 decomposition measured a slightly
different function (the finding survived, and was re-confirmed against the real objective
by the auditor). And my active-guard counter tallied only the first active guard per row,
reporting separation twice where its own rows showed twelve.

**Confirmed sound under this attack:** the three witnesses and the 0/1/15/12 counts in
exact arithmetic, the 1,3,3,3,4 table at the correct A003829 offset, the f_gp argument,
the direction of monotonicity, the s^2/2 law (replicated to seven figures by a
hard-constrained independent method), Lemma 5's parametrisation, and lath.py's prune
(re-validated by prune-free enumeration of all 198,792,594 subsets at 11x11).

## 9a. Late additions from the round-2 auditor

**R5 got stronger, and my fix holds.** The ladder was non-monotone at 300 restarts as
well as at 40, so it was not a small-sample effect. After the fix - every point evaluated
at every shorter prefix, plus an assertion - all four sampled splits are monotone. A
second point stands unfixed and is now disclosed: the absolute Case A residuals are
budget-dependent, moving by a factor of 2.6 for a 7.5x increase in restarts, so none of
them is converged.

**R6 reverses the reading of the ladder's low reach, in our favour.** The auditor's first
probe reported no three-equation roots; that was a threshold artifact. They do exist, but
at minimum pairwise distance about 1e-11, concyclicity determinant about 1e-13, and
squared area exactly zero - coincident points on a line, nine orders outside the guards.
So the guards are not too tight, there are no admissible three-equation solutions, and
the ladder's failure to climb is a fact about the geometry rather than a weakness of the
optimiser. The corollary is that the ladder cannot act as a control above rung two, since
a control must be able to succeed.

**The decisive test, re-run to completion here.** `r2check.py`: 577 exact roots across
all fifteen patterns, largest concyclicity margin anywhere 2.65e-12. Every exact root is
four-concyclic.