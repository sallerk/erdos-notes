# AUDIT_ROUND2 — adversarial re-audit of p831 after the remediation pass

Date: 2026-09-07, starting 13:17 local. Everything below was produced by probes I wrote
from the definitions; no script in this directory was treated as evidence for its own
output. **Because R7 and R8 are complaints about unartifacted evidence, my own probes
and their raw logs are in `audit_round2/`** rather than in a scratchpad:

| file | what it establishes |
|---|---|
| `probe_guards.py` | tausweep's exact objective, with every margin recorded at the optimum (R1a) |
| `probe_sep.py` + `sepsweep.log` | the class-separation sweep, 13/13 slopes (R1b) |
| `probe_noguard.py` + `noguard.log` | roots of the equality systems with all guards removed (R2) |
| `probe_caseA_lite.py` + `caseAlite.log` | Case A 2-equation roots with all guards removed (R6) |
| `probe_caseA.py` + `caseA_full.log` | Case A ladder re-run at 300 restarts, guards on and off, and the 3-equation root hunt (R5, R6) |
| `probe_obstr.py` | independent hard-constrained replication of the s²/2 law (C4) |
| `probe_exact.py` | witnesses, pattern counts, bound table, fgp, in `Fraction` arithmetic (C1–C3) |
| `probe_struct.py` | which lemma cuts 35→15, the three size-4 shapes, the 5/7 split (C2) |
| `probe_lath.py` + `lath7.log`, `lath11.log` | prune-free lattice enumeration (C6) |

Run any of them with `python audit_round2/<name>.py`; each `chdir`s to `p831` itself.

## 0. A note on concurrency, because it changes what "the directory" means

**The directory was edited while I was auditing it.** I read `NOTE.md`,
`AUDIT_SUMMARY.md`, `LESSONS.md` and `verify.py` at about 13:20. At 13:17 a new file
`AUDIT_R2_SELF.py` appeared, at 13:33 it wrote `results/audit_r2_self.json`, and at
13:32 `NOTE.md`, `AUDIT_SUMMARY.md` and `LESSONS.md` were rewritten and `verify.py` was
extended. That pass reached, independently and roughly an hour before I could finish
confirming it, the same headline I was sent to look for: the OBSTRUCTED verdict was
measuring the unswept class-separation guard.

I have therefore audited the **post-13:33 state**, and I confirm that finding from my
own code and go further than it does. Where a defect below is in the round-2 fix
itself, I say so.

---

# DEFECTS

## R1. FATAL — the withdrawn OBSTRUCTED verdict is still what the code prints and what the artifact says

**Claim under attack.** `AUDIT_SUMMARY.md` §8 and `NOTE.md` now withdraw the
"13 patterns are genuinely obstructed" verdict. `REPRODUCE.md` still instructs the
reader to `python tausweep.py 60` and "read the slope".

**Why it is wrong.** Only the prose was patched. `tausweep.py` is unchanged since
11:47. Its module docstring still defines

> `OBSTRUCTED : floor is flat in tau. The equalities themselves cannot be satisfied,
> independently of the degeneracy guard.`

its classifier still emits `verdict = 'DEGENERATE-ONLY' if slope > 0.5 else 'OBSTRUCTED'`,
and its final lines still print *"13 are obstructed independently of the degeneracy
guard."* `results/tausweep_n5_k3.json` — which `verify.py` reads and which `NOTE.md`
cites by name — still carries `"verdict": "OBSTRUCTED"` on thirteen records. Anybody
running the command `REPRODUCE.md` prescribes is handed the retracted claim as output.
A retraction that lives only in the prose while the instrument and its artifact keep
asserting the retracted thing is not a retraction.

**Evidence, and it is stronger than the round-2 pass claims.** Two independent probes
of mine:

*(a) guard activity at tausweep's own optimum.* I reimplemented **tausweep's exact
objective** (span 60, flat > tau, sep > 1e-3, det4 > tau; note there is no
minimum-distance term — see R3) and recorded every margin at the optimum, 60 restarts,
tau = 1e-6:

| separation margin at the optimum, in units of the 1e-3 guard |
|---|
| **1.000 at 14 of the 15 patterns** (the exception is pattern 0, at 277) |

The class-separation guard is pinned exactly on its threshold at every OBSTRUCTED
pattern and at one of the two DEGENERATE-ONLY ones. Round 2 reports "12 of 13"; the
true figure on tausweep's own objective is 14 of 15.

*(b) sweeping the separation guard, which nothing in the directory does.* tau fixed at
1e-8 so the flatness/concyclicity guards are inert, sep_tau swept over three decades,
40 restarts, equality residual only (no penalty terms in the reported number):

```
   i  tausweep verdict   sep=1e-2   sep=3e-3   sep=1e-3   sep=3e-4   sep=1e-4   sep=1e-5   slope
   2  OBSTRUCTED         5.314e-03  2.820e-03  5.253e-04  1.909e-04  1.259e-04  1.642e-05  +0.85
   3  OBSTRUCTED         5.454e-03  1.644e-03  6.547e-04  2.007e-04  6.394e-05  1.010e-05  +0.92
   4  OBSTRUCTED         7.700e-03  1.837e-03  8.128e-04  2.110e-04  6.462e-05  1.002e-05  +0.96
   5  OBSTRUCTED         6.037e-03  1.580e-03  1.048e-03  1.767e-04  9.862e-05  1.301e-05  +0.89
   6  OBSTRUCTED         8.953e-03  2.536e-03  7.631e-04  2.793e-04  1.209e-04  9.999e-06  +0.96
   7  OBSTRUCTED         6.545e-03  2.466e-03  7.417e-04  2.813e-04  1.196e-04  1.700e-05  +0.86
   8  OBSTRUCTED         6.682e-03  2.154e-03  6.147e-04  2.087e-04  9.853e-05  1.325e-05  +0.90
   9  OBSTRUCTED         7.786e-03  2.998e-03  8.452e-04  2.183e-04  1.629e-04  2.066e-05  +0.86
  10  OBSTRUCTED         3.732e-03  2.060e-03  7.373e-04  2.296e-04  1.410e-04  1.403e-05  +0.81
  11  OBSTRUCTED         7.030e-03  1.794e-03  1.384e-03  3.297e-04  1.419e-04  1.846e-05  +0.85
  12  OBSTRUCTED         7.071e-03  2.655e-03  1.063e-03  2.602e-04  1.370e-04  2.173e-05  +0.85
  13  OBSTRUCTED         1.113e-03  4.389e-04  9.800e-04  4.032e-04  1.298e-04  1.174e-05  +0.62
  14  OBSTRUCTED         1.571e-03  1.699e-03  6.225e-04  1.630e-04  1.567e-05  1.752e-06  +1.08
```

**Thirteen of thirteen** have slope in the separation margin between +0.62 and +1.08,
against slopes of −0.02 to +0.06 in tau. By tausweep's own +0.5 rule every one of them
is DEGENERATE-ONLY with respect to the guard that was never swept. Round 2 established
"a guard is active"; this establishes the scaling law for all thirteen individually.

**Severity: FATAL** — not because the mathematics is now wrong (the prose has been
corrected) but because the executable claim and the stored artifact still assert the
retracted verdict, and `REPRODUCE.md` still points at them.

**Minimum fix.** Change the verdict strings and the closing print in `tausweep.py`,
regenerate `results/tausweep_n5_k3.json`, or delete the `verdict` field entirely and
keep only the slopes.

## R2. SERIOUS — every root of the equality systems is four-concyclic, so the corrected two-row table is a false dichotomy

**Claim under attack.** `NOTE.md` and `AUDIT_SUMMARY.md` §8 now give the corrected
reading as two disjoint categories:

| what the equalities need | count |
|---|---|
| the configuration approaches four concyclic points | 2 |
| two of the three radius classes merge | 13 |

**Why it is wrong.** The two categories are not alternatives, and the split is inferred
from which penalty happened to be pressed at one optimum rather than from the structure
of the roots. I dropped **every** guard — minimised only the ten equality residuals,
no penalty of any kind, so no constant can be "the thing being measured" — collected
every root with `max|equality residual| < 1e-10` from 400 restarts per pattern, and
then measured degeneracy from the definitions:

```
  i  tausweep verdict  roots  best sep    best min|det4|/scale^1.5   best 16K^2/scale^2  best min pair dist
  0  DEGENERATE-ONLY    134   2.745e-02   1.253e-13                  1.094               1.000
  1  DEGENERATE-ONLY    131   4.878e-01   7.540e-13                  0.970               1.000
  2  OBSTRUCTED         135   6.058e-14   4.044e-14                  1.493               1.000
  3  OBSTRUCTED         225   1.941e-11   1.088e-12                  1.859               1.000
  4  OBSTRUCTED         135   3.223e-12   8.369e-14                  2.606               1.000
  5  OBSTRUCTED         124   3.311e-13   9.447e-15                  1.027               1.000
  6  OBSTRUCTED         125   1.517e-13   6.608e-14                  1.693               1.000
  7  OBSTRUCTED         119   2.655e-12   7.494e-14                  0.734               1.000
  8  OBSTRUCTED         142   1.962e-13   4.077e-14                  1.425               1.000
  9  OBSTRUCTED         130   2.239e-11   2.050e-14                  3.675               1.000
 10  OBSTRUCTED         119   5.789e-13   4.821e-14                  2.678               1.000
 11  OBSTRUCTED         120   1.556e-12   8.084e-14                  0.960               1.000
 12  OBSTRUCTED         120   3.594e-12   2.331e-14                  1.532               1.000
 13  OBSTRUCTED         112   1.220e-13   2.353e-14                  2.871               1.000
 14  OBSTRUCTED         102   9.601e-12   2.409e-13                  0.999               1.000
```
(`best` = the largest value attained over all roots found, i.e. the least degenerate
root there is.)

Three things follow that the table does not say.

1. **The equality systems have exact roots.** Not near-misses — residual below 1e-10,
   between 102 and 225 of them per pattern, 1,973 in total over the fifteen. The
   screen's original framing ("no lead") was about the guarded objective, not about the
   equations.
2. **Every one of those 1,973 roots has four concyclic points** — min |det4| normalised
   by scale^1.5 never exceeds 1.1e-12 anywhere in the set, in either category. So
   "approaches four concyclic points" is true of all fifteen patterns, not of two.
3. **No root is near-collinear and no root collapses points** (16K²/scale² of order 1,
   minimum pairwise distance exactly 1, the gauge maximum). The degeneracy is
   concyclicity, full stop.

There is a structural reason the table cannot be a dichotomy. Four concyclic points give
their four triples one common circumradius. By Lemma 4 a 4-set's triples are never split
3+1, so they are either all in one class or spread over at least two — and in the second
case **concyclicity forces those classes to merge**. The two rows are one phenomenon seen
from two sides, not two alternatives to be counted against each other.

Separately, the table says 13 where the artifact it cites, and `NOTE.md`'s own preceding
sentence, say 12: `results/audit_r2_self.json` shows pattern 7's optimum with
`separation` ratio 1.189 and `min_dist` active instead. So the row labelled 13 is
unsupported for one of its members even on the directory's own evidence.

## R3. SERIOUS — the round-2 decomposition audits a different function from the one it is auditing

**Claim under attack.** `AUDIT_SUMMARY.md` §8: *"`tausweep.py` sweeps tau... Its
objective also contains a class-separation guard at 1e-3, **a minimum-distance guard at
1e-2** and a span guard, none of which it sweeps."* and then *"sweeping the
minimum-distance margin over the same range moves it by 0.78x, so that guard is inert
and is not the cause."*

**Why it is wrong.** `tausweep.py`'s objective contains **no minimum-distance guard at
all**. Its residual vector is `len(TRI) + 3 + len(QUADS)` = 10 equalities + span + flat
+ separation + 5 concyclicity terms = 18 components. `pscreen.py` has the
minimum-distance term (that was the earlier remediation); `tausweep.py` dropped it;
`AUDIT_R2_SELF.py` puts it back (19 components). So:

* the sentence misdescribes the function under audit;
* the "0.78x, so the guard is inert" finding sweeps a guard that is not in tausweep;
* more seriously, `AUDIT_R2_SELF.floor()` recomputes the optima with that extra
  constraint **and** from a different restart box, `uniform(-8, 8)` against tausweep's
  `uniform(-2.0, 2.5)`. The numbers it decomposes are therefore not tausweep's optima.
  Compare pattern 7: `audit_r2_self.json` reports floor 2.179e-3, `tausweep_n5_k3.json`
  reports 9.732e-4 at the same tau.

The conclusion survives — my probe R1(a), run on tausweep's *actual* objective, finds
the separation guard active at 14 of 15 — but the artifact offered as the evidence for
it does not establish it. This is the same class of error as the defect it is fixing:
measuring one thing and reporting it as another.

Also worth stating plainly: **three different objectives are all reported as "the
screen"** — pscreen (4 penalties), tausweep (3, no min-distance), AUDIT_R2_SELF (4,
different box). `AUDIT_SUMMARY.md` §7's remediation row "pscreen had no minimum-distance
guard | added" is true of `pscreen.py` and false of the objective that produced the
headline.

## R4. SERIOUS — `AUDIT_R2_SELF.py`'s summary counter under-reports the separation guard six-fold, and `verify.py` prints the wrong number under a PASS

**Claim under attack.** `verify.py` prints, and passes,
`active guards: {'flat': 10, 'concyclic': 1, 'min_dist': 0, 'separation': 2, 'none': 0}`.
Read literally that says the flatness guard, not the separation guard, sets the floor —
the opposite of the section's own conclusion.

**Why it is wrong.** In `AUDIT_R2_SELF.py`:

```python
hot = [g for g, r in ratios.items() if r < 1.05]
active[hot[0] if hot else 'none'] += 1
```

`ratios` is built in the order flat, concyclic, min_dist, separation, so a row whose
active set is `['flat','separation']` is tallied only as `flat`. The per-row data in the
same artifact shows `separation` in the active list of **12 of the 13 rows**; the
counter reports 2.

**Evidence.** `results/audit_r2_self.json`, `rows[*].active`: `['flat','separation']`
appears 6 times, `['separation']` twice, `['flat','concyclic','separation']` 3 times,
`['concyclic','separation']` once, `['flat','min_dist']` once. Separation: 12.
The `active` dict in the same file: `separation: 2`.

## R5. SERIOUS — `caseA2.py`'s control ladder does not report minima; its own artifact is internally inconsistent

**Claim under attack.** `NOTE.md`: *"its ladder reports honestly that **it reaches only
1 equation of 4** at machine precision: two of the four sampled splits solve two
equations, none solves three. So this instrument is weak."* `verify.py` has a dedicated
check that this weakness is disclosed.

**Why it is wrong.** The ladder's rung-k number is
`min over the feasible set of max|e_1 … e_k|`, and the feasible set (the guards, and
`solve`'s post-hoc rejection) does not depend on k. Adding an equation can only raise
that minimum. **The recorded floors fall instead, for all four splits:**

| split | 1 eq | 2 eq | 3 eq | 4 eq |
|---|---|---|---|---|
| `[2,3]｜[0,1,4,5]` | 0.0 | 2.06e-16 | **1.445e-04** | **6.50e-06** |
| `[0,2,3]｜[1,4,5]` | 7.04e-17 | 1.740e-04 | **1.835e-04** | **2.97e-05** |
| `[1,2,3]｜[0,4,5]` | 2.20e-16 | 4.888e-05 | **1.318e-04** | **2.36e-05** |
| `[1,4]｜[0,2,3,5]` | 3.35e-16 | 3.31e-16 | **2.426e-04** | **6.73e-06** |

Four equations are solved one to two orders of magnitude *better* than three, which is
impossible for true minima. The artifact refutes itself: the point that achieves
max|e₁…e₄| = 6.50e-06 on split 0 also achieves max|e₁…e₃| ≤ 6.50e-06, so the recorded
rung-3 value 1.445e-04 is wrong by a factor of 22 *on the artifact's own witness*. The
floors are restart noise, not floors, and `ladder_top = 1` is a property of the random
seed, not of the instrument. The sentence `NOTE.md` offers as its honest
self-assessment, and the `verify.py` check that guards it, both rest on a number the
artifact itself refutes.

**Re-running the ladder at 300 restarts confirms both halves** (`caseA_full.log`). The
non-monotonicity does not go away — every split still solves four equations better than
three (2.88e-06 vs 3.24e-05; 1.85e-05 vs 2.30e-05; 1.89e-05 vs 5.27e-05; 2.24e-06 vs
6.53e-05) — and the rung-2 numbers move a long way with the budget: split
`[0,2,3]|[1,4,5]` goes 1.740e-04 → 6.80e-05 and split `[1,2,3]|[0,4,5]` goes
4.888e-05 → 1.85e-05, factors of 2.6 and 2.6 for a 7.5× larger budget. Every recorded
Case A number is budget-dependent in a way neither the artifact nor `NOTE.md` records
(compare R17).

Direction of the error: it *understates* the instrument, so the Case A negative is not
invalidated. But "the ladder reaches only 1 equation of 4" is not a fact, and neither is
the inference "so this instrument is weak".

## R6. MINOR — `caseA2`'s own guard margins are active at its two best points and are never swept (but they are NOT what blocks the ladder — probe below)

**Claim under attack.** `AUDIT_SUMMARY.md` §7: *"caseA had no concyclicity, distinctness
or class-separation guard | all three present in `caseA2.py`, with the margins as
parameters"*, offered as the fix for LESSONS P11 ("a residual that sits on your own
penalty margin is measuring the margin").

**Why it is wrong.** Making a margin a parameter is not the same as measuring its
influence, and `caseA2.py` never varies MIND, CONC or SEP; `results/caseA2.json` records
one triple of margins and nothing else. At the two smallest residuals in that artifact —
1.246e-05 on split `[2,3]|[0,1,4,5]` and 1.302e-05 on `[1,4]|[0,2,3,5]`, the two the
note quotes as the low end of its range — the recorded margins are

```
  min_dist 0.011688  against the guard 1e-2   (17% above it)
  min_dist 0.012158  against the guard 1e-2   (22% above it)
  min_16K2 5.68e-07 / 6.53e-07                (the orthocentre nearly on AB)
```

with `cy` ≈ 31.4 and 30.4, i.e. the optimiser has run the triangle out to where the
orthocentre H approaches the line AB and H approaches a vertex-distance of the guard.
The best points are pressed against the distance guard. `solve` then discards, after
convergence, any restart whose point violates a guard (`continue`), so the reported best
is conditioned on the guard exactly as LESSONS P11 warns. No artifact shows what the
Case A floors do as MIND or CONC move, so P11's rule is unapplied here.

**But the stronger version of this attack fails, and I record that.** The question the
audit brief put is whether roots of 2 and 3 of the equations exist *just outside* the
guards, which would mean the search never explored the admissible region properly. They
do not. With **every guard removed** — pure equations, no penalty, no post-hoc
rejection:

*Two equations* (150 restarts, `caseA_lite.log`): splits `[2,3]|[0,1,4,5]` and
`[1,4]|[0,2,3,5]` give 63 and 32 roots below 1e-11, sitting *deep inside* the admissible
region — minimum pairwise distance **1.000** against a guard of 1e-2, |det4|/scale³ up to
**0.768** against 1e-4, 16K² up to 40.8 — and 60 of 63 and 32 of 32 pass every guard.
Splits `[0,2,3]|[1,4,5]` and `[1,2,3]|[0,4,5]` give none, matching `caseA2.json`'s ladder
exactly.

*Three equations* (900 restarts, threshold 1e-10, `caseA_full.log`): roots do exist, but
they are not "just outside" the guards, they are nine orders of magnitude outside them.

```
 split                roots  best min_dist (guard 1e-2)  best min_det4 (guard 1e-4)  passing all guards
 [2,3]|[0,1,4,5]        3     1.293e-11                   4.604e-13                   0
 [0,2,3]|[1,4,5]        1     1.589e-10                   9.386e-13                   0
```

and the guard-free ladder's best 3-equation points have `min_dist` ≈ 1e-10 to 1e-13,
`min_det4` ≈ 1e-11 to 1e-16 and `16K²` **exactly 0** — coincident points on a straight
line. Relaxing MIND from 1e-2 to 1e-11 to admit them would be geometrically meaningless.

*Rejection bias.* `solve`'s post-hoc `continue` discards 41 to 53 of every 300 restarts
(253, 247, 248, 259 accepted on the four splits), i.e. 14–18%. Real but modest; it does
not explain the ladder's behaviour.

So the guards are not too tight, the `continue` is not biasing the verdict, and the
Case A negative is not an artifact of its guards. What is unsound is only the two quoted
low residuals (above) and the ladder's rung numbers (R5).

## R7. SERIOUS — load-bearing numbers still have no artifact, including the ones offered as the evidence for h(5)=4

**Claim under attack.** `AUDIT_SUMMARY.md` §7 heading: *"Artifacts created for numbers
that had none."* Four were created.

**Why it is incomplete.** `grep` over `results/` finds none of the following, all of
which are quoted as fact in `NOTE.md` or `AUDIT_SUMMARY.md`:

| number | where quoted | what it supports |
|---|---|---|
| prune-free enumeration of **198,792,594** 5-subsets (11×11) and **324,540,216** 6-subsets (9×9) | NOTE §Status, SUMMARY §1 | validation of `lath.py`'s prune — offered in the *Status* paragraph as part of the case for h(5)=4. (Both equal C(121,5) and C(81,6) exactly; I re-ran the 11×11 one myself, see C6, and it holds — but nothing in `results/` records either.) |
| the Case A grid, **200×200 × 241×241 + 4000 restarts per split**, 0 roots in 9 splits | NOTE §5, SUMMARY §6 | NOTE says outright *"The real support for this branch is the auditor's independent grid-based search"* |
| **~7,600** roots, all four-concyclic, for the size-5 class orbits | NOTE §1 table | the claim that f(5)=4 is "not strictly needed" |
| **47/500 vs 51/500** hit rates; **0.33%** per-restart and **19%** miss probability | NOTE §5, SUMMARY §3 | the stated bound on the screen's false-negative behaviour |
| "an independent implementation reproduced the [s²/2] law to **six significant figures**" | NOTE §5 | the strongest surviving leg |
| `caseA.py` "reached a best relative residual of **7e-8**" | NOTE §5 | `results/caseA_n5.json` records only `hits: []`; there is no `best` field |

Two of these I was able to check myself and they hold (the s²/2 replication, C4, and the
198,792,594 enumeration, C6). The rest are the same defect the remediation says it
closed, still open on the items that matter most — including the one `NOTE.md` calls
"the real support" for the Case A branch.

## R8. SERIOUS — `obstruction433.py` cannot be run: the file it executes is not in the directory

**Claim under attack.** `REPRODUCE.md` lists `python obstruction433.py` under "the n=5
case analysis", and the s²/2 obstruction is described as the strongest surviving
evidence for h(5)=4.

**Evidence.** Line 3 of `obstruction433.py` is
`exec(open('target433.py').read().split('if __name__')[0])`. There is no `target433.py`
in `p831`; `ls` fails, and the only other mentions of it are in `AUDIT_MATH.md`
(complaining that REPRODUCE never mentions it) and `AUDIT_CODE.md`. The script raises
`FileNotFoundError` immediately. `results/obstruction433.json` therefore cannot be
regenerated from this directory.

Mitigated by C4 below: I replicated the law independently, so the *result* is sound.
The *reproducibility* claim in `REPRODUCE.md` ("Every number below is reproducible from
this directory") is false for this file.

## R9. SERIOUS — "no pattern has an admissible realisation" is an absence claim drawn from a finite local search

**Claim under attack.** `NOTE.md`, corrected screen section: *"So the conclusion stands
— **no pattern has an admissible realisation with three genuinely distinct radii** — but
it stands by running into the degeneracies."* `AUDIT_SUMMARY.md` §8: *"The conclusion
h(5) has no 3-class realisation survives."*

**Why it is unsupported.** Three reasons, two of them the document's own.

1. Everything behind it is a residual trend from `least_squares` with 30–60 restarts.
   The same section states that on the only realisable overdetermined instance available
   the optimiser has a 0.33% per-restart hit rate and 500 restarts would miss an
   existing solution about 19% of the time. An instrument with an unbounded
   false-negative rate cannot produce "no pattern has".
2. If it were sound it would settle h(5) = 4, which the same document lists as NOT
   ESTABLISHED two hundred lines earlier. The two statements cannot both be right.
3. The supporting argument is also confused. *"a configuration whose classes have merged
   has at most two distinct circumradii, and h(5) >= 3 rules that out"* invokes
   h(5) ≥ 3 needlessly: a configuration with zero class separation does not realise a
   3-class pattern **by definition**, no external theorem required. And the observation
   being explained is not "roots require merging"; it is "the best residual the search
   found scales with the guard", which is weaker.

The defensible statement is quantified and much smaller: *no configuration was found
with relative class separation above 1e-5 and equality residual below about 3·sep.*

## R10. MINOR — the s²/2 minimiser is a rectangle at every separation, which the note does not say

**Claim under attack.** `NOTE.md`: *"`obstruction433.py` minimises max(|f1|,|f2|)
subject to a lower bound s on the angular separation of the four centres and finds the
floor sitting exactly on that constraint... so the equations are satisfiable only in the
limit where two centres merge, which merges two class circles and puts four points on a
circle."*

**What I found.** At every reported minimiser in `results/obstruction433.json` the
quadruple (P1,P2,P3,P4) is already **exactly concyclic**:

```
  s=0.35  |det4(1,2,3,4)| = 1.36e-13     s=0.08  4.78e-14
  s=0.25                    3.05e-14     s=0.03  3.47e-13  (and triple 013 collinear, 16K^2=2.9e-09)
  s=0.15                    1.18e-13
```

By Lemma 6 those four points are a parallelogram, and a concyclic parallelogram is a
rectangle — at s = 0.15 the minimiser is literally the axis-aligned rectangle
(1.98877, ±0.14944), (−0.01123, ±0.14944). So the "floor" is a minimum over a region
that contains inadmissible configurations and is attained on them, at *every* s
including 0.35. The conclusion survives a fortiori (a minimum over a larger set is a
lower bound for the minimum over the admissible subset), but the note presents the
number as a floor over the family of interest, and it is not.

Two further imprecisions in the same sentence: at the reported minimisers **three**
centres merge as s → 0, not two, and the limit puts **all five** points on one circle,
not four. And the reason given elsewhere for why this is not a proof — *"because a
lattice is a restriction and one branch of the case analysis is untreated"* — is the
wrong reason: it is not a proof because it is a numerical global minimisation over a
3-torus.

## R11. MINOR — `LESSONS.md` P9 was not corrected and now contradicts P12 in the same file

**Claim under attack.** `AUDIT_SUMMARY.md` §7, "Fixed in the write-up": *"...and LESSONS
P3 and P9, both of which drew the wrong conclusion from a broken instrument."*

**Evidence.** P3 carries an explicit `CORRECTION (audit, 2026-09-07)` block. P9 does
not, and still reads: *"The fix was to build a control with a KNOWN rank deficiency
(ctrlB.py: six equations, **Jacobian rank five**, admissible by construction); the screen
finds it at 8.5e-16 from 100 restarts."* The rank-five claim is withdrawn in
`AUDIT_SUMMARY.md` §3, in `results/ctrlB.json` (`"rank": 4`, `"rank_note": "...Claim
withdrawn."`), in `NOTE.md`, and in P12 nine lessons later, which says in terms that a
larger rank deficiency makes a control *easier*. P9 and P12 now assert opposite things
about the same file.

## R12. MINOR — `NOTE.md` still states the "support 5" error it corrects in the next sentence

**Evidence.** Lines 217–219:

> Its size-4 class has support 5, so by Lemma 3 it is NOT an orthocentric quadruple.
> (The n=6 witness's size-4 class has support 6, not 5 as an earlier draft of this note
> said; the conclusion ... holds a fortiori.)

The wrong sentence was never edited, only annotated. Exact recomputation (Fraction
arithmetic, my own code) of the n=6 witness `(0,0),(0,7),(2,6),(4,3),(6,2),(6,9)`:
classes of sizes 8, 4, 2, 2, 2, 2 with supports 6, **6**, 4, 4, 4, 4. Also the inference
does not need Lemma 3: support > 4 already means the class is not the four triples of a
4-set.

## R13. MINOR — `penum.py` still prints "Lemma 5" for what its own docstring and `NOTE.md` call Lemma 4

**Claim under attack.** `AUDIT_SUMMARY.md` §7: *"penum renamed the note's Lemma 4 as
'Lemma 5' | numbering aligned"*.

**Evidence.** `penum.py` line 153:
`print('  (filters: Lemma 1 pair-degree<=2, Lemma 5 no exactly-3-of-a-4-set,')`
while `quad_ok`'s docstring twelve lines above says `LEMMA 4 (NOTE.md numbering...)`.
The docstring was fixed; the output line was not.

## R14. MINOR — `REPRODUCE.md`'s "what was actually run" table names three artifacts that do not exist

**Evidence.** Rows 51–53 cite `results/lath_n4_6x6.json`, `results/lath_n5_11x11.json`,
`results/lath_n6_11x11.json`. The files are `lath_n4_6x6_t4.json`,
`lath_n5_11x11_t5.json`, `lath_n6_11x11_t7.json`. The corrections section at the bottom
of the same file announces the rename; the table above it was not updated.

## R15. MINOR — `results/pdecide_n5_k3.json` has neither the completion flag nor the advisory note the remediation says it carries

**Claim under attack.** `AUDIT_SUMMARY.md` §7: *"pdecide wrote no completion flag; its
timeout is advisory | flag added, and the advisory nature recorded in the artifact"*.

**Evidence.** `pdecide.py` does write both `completed` and `timeout_note`. The artifact
in `results/` has keys `n, k, timeout_ms, results` only — it was written at 09:38, the
code was edited at 12:44, and it was never regenerated. `verify.py` reads this file and
does not check `completed`, so nothing catches it.

## R16. MINOR — `verify.py` still has vacuous checks and one whose label does not match its condition

**Claim under attack.** LESSONS P14: *"Write the audit check against the CONTENT of the
artifact, not its flags."*

**Evidence.** Parsing `verify.py`'s AST, three `ck(...)` calls have the literal `True`
as their condition (lines 81, 187, 246). Line 246 asserts a claim about the write-up —
*"the ctrlB rank claim is withdrawn, not relied on"* — without reading any document. And
the new round-2 check reads

```python
ck('the separation guard, not the geometry, sets the floor', act.get('none', 0) == 0,
   'no optimum has zero active guards, so no floor here is a clean obstruction')
```

whose condition is "some guard was active at every optimum". It would pass unchanged if
the separation guard were never active anywhere — which, given R4, is exactly the
scenario the summary counter creates.

Separately, the headline exhaustive negative is still audited by metadata alone: for
`lath_n5_17x17_t4.json` the check tests `completed`, `target`, `best is None`,
`witness is None`. `nodes` is printed and never checked. Unavoidable from the artifact
for a negative — which is why I validated the method instead (C6).

## R17. MINOR — `results/caseA2.json` was produced at 40 restarts; `REPRODUCE.md` prescribes 300

**Evidence.** `"restarts": 40` in the artifact against *"Run `python caseA2.py 300`
instead"* in `REPRODUCE.md`. `NOTE.md` quotes the artifact's residuals ("1.2e-5 to
6.9e-4") without stating the budget. Given R5, the budget is exactly what is in
question.

## R18. MINOR — `tausweep.py` records no optimum, so the question round 2 had to answer could not be answered from `results/`

`results/tausweep_n5_k3.json` stores floors, equality values, the minimum determinant
and the slope — but not the argmin. Which guard was active therefore could not be read
off the artifact and had to be recomputed (badly, see R3). LESSONS P15, added in the
same pass, states the rule *"before reporting any floor, report WHICH constraint is
active at the optimum"*; `tausweep.py` is unchanged since 11:47 and does not implement
it.

## R19. WORDING — the monotonicity consequence is never stronger than the forum bound at any n

**Claim under attack.** `NOTE.md` Lemma 4a: *"`h(8) >= 4` gives `h(n) >= 4` for every
n >= 8, which is the only statement here that reaches past the range where f is known.
It does not beat the forum bound: ceil((n-2)/2) overtakes 4 at n = 11."*

**Check of the direction, which is correct.** For a minimising admissible (n+1)-set Y
and any n-subset X: X is admissible (both hypotheses are hereditary), the triples of X
are a subset of those of Y so r(X) ≤ r(Y), and h(n) ≤ r(X) by minimality. Hence
h(n) ≤ h(n+1). Not backwards.

**What the wording understates.** ceil((n−2)/2) = 3, 4, 4, 5, 5 at n = 8, 9, 10, 11, 12.
So the monotonicity consequence h(n) ≥ 4 is the *hypothesis* at n = 8 (the f-table gives
it directly), *equals* the forum bound at n = 9 and n = 10, and is *beaten* from n = 11.
It is therefore never strictly better than the forum bound anywhere. "Does not beat"
is true but reads as though it merely fails to improve at large n.

Related: `lemmas.py`'s Lemma 4a block tests "every 3-subset of an admissible 4-set is
admissible with no more radii" on three triangles. That is a demonstration of a special
case, not a test of the lemma, and unlike the file's stated policy it is not labelled
as one.

## R20. WORDING — Lemma 6's "no parallelogram is orthocentric" proof covers one of four cases

`NOTE.md` writes *"`A + H = B + C` with `H = A+B+C-2O` forces `A = O`"*, which is the
case where the orthocentre is one end of a diagonal. The other three assignments
(H being either of the other two vertices, or the fourth) each also reduce to "some
vertex is the circumcentre of its own triangle", so the lemma is true as stated — I
checked all four — but the written proof does one of them.

---

# CONFIRMED SOUND (attacked and survived)

**C1. The three witnesses, in exact `Fraction` arithmetic with my own determinant and
circumradius code.** All admissible (0 collinear triples, 0 concyclic quadruples).
n=4 `(0,0),(0,3),(1,1),(2,1)`: one radius, r² = 5/2. n=5 `(0,0),(0,7),(2,6),(4,3),(6,9)`:
4 radii, profile **[4,2,2,2]**, r² ∈ {1625/162, 1625/18, 25/2, 65/2}. n=6 adding (6,2):
6 radii, profile **[8,4,2,2,2,2]**. h(4)=1, h(5)≤4, h(6)≤6 all stand.

**C2. Pattern counts 0 / 1 / 15 / 12, re-enumerated from the lemma statements in fresh
code.** k=1: 0. k=2: 1, profile (5,5), outside f(5)=4. k=3: 35 under Lemma 1 alone, **15**
under Lemmas 1+4, **12** also within f(5)=4, profiles {(4,4,2): 5, (4,3,3): 7} plus the
three f-illegal ones. Lemma 3's saturation clause removes nothing beyond Lemma 1, so
`NOTE.md`'s attribution of the 35 → 15 cut to Lemma 4 is right. The "five structural /
seven screen-only" split also reproduces exactly: of the 12, one has an all-on-a-4-set
size-4 class, two have a common-point class, one has both, one has a common-point and a
no-common-point class, and **seven** have only no-common-point classes.

**C3. The lower-bound chain.** A003829 offset is 3 and `S = 1,4,4,8,12,16`, so
f(3..8) = 1,4,4,8,12,16 — the `F104` dicts in `penum.py`, `verify.py` and `fgp.py` use
the right offset. ceil(C(n,3)/f(n)) = **1, 3, 3, 3, 4** for n = 4..8 against forum
1, 2, 2, 3, 3: better at 5, 6, 8, tied at 4 and 7. The `fgp` argument is sound: in an
admissible set two distinct triples of one class cannot share a circle (that would be
four concyclic), so a class of size m is m distinct circles of one radius each through
exactly three points, and rescaling gives f_gp(n) ≥ m. I re-verified every witness in
`results/fgp.json` from the definitions; largest classes 1, 4, 4, 8 at n = 3, 4, 5, 6
equal f(n), so no sharpening is available there. The bound is also valid under either
reading of the OEIS name, since max over sets of "exactly 3" ≤ max over sets of "at
least 3".

**C4. The s²/2 obstruction replicates exactly.** Independent implementation, SLSQP with
a **hard** nonlinear constraint `sep(θ) ≥ s`, 400 restarts:

```
   s      my min max(|f1|,|f2|)    obstruction433.json     ratio to s^2/2
  0.35    6.246153e-02             6.246153e-02            1.0198
  0.25    3.157056e-02             3.157056e-02            1.0103
  0.15    1.129196e-02             1.129196e-02            1.0037
  0.08    3.203408e-03             3.203408e-03            1.0011
  0.03    4.500675e-04             4.500675e-04            1.0001
  0.01    5.000084e-05             (not in the artifact)    1.0000
```

Seven significant figures, and the law extends to s = 0.01. This leg is real.

**C5. Lemma 5's parametrisation is validated against a real exact witness — a check
nobody in the directory has run.** The n=5 witness's size-4 class is
{012, 013, 124, 134}, which has point 1 in all four triples, so it *is* the common-point
shape. Putting P0 = (0,7) at the origin and scaling by r = sqrt(25/2), the four
circumcentres come out at |o_i| = 1.000000000 exactly, and all four of Lemma 5's
identities hold to machine precision:

```
  P1 = o1+o2 = (0, -1.979899)      P2 = o1+o3 = ( 0.565685, -0.282843)
  P3 = o2+o4 = (1.131371, -1.131371)  P4 = o3+o4 = ( 1.697056,  0.565685)
```

The remaining four points also satisfy P1+P4 = P2+P3 (Lemma 6's parallelogram) in exact
integers: (0,−7)+(6,2) = (2,−1)+(4,−4) = (6,−5). And Lemma 6's prediction that the four
triples on them give exactly two radii is what the witness's class profile shows
({023,234} and {024,034} as two size-2 classes). The family the grid sweep and the
obstruction search explore is the right one and is not vacuous.

**C6. `lath.py`'s DFS, admissibility test and monotone prune, validated by my own
prune-free enumeration — including the 198,792,594 figure that has no artifact.**

* 7×7, n=5: all C(49,5) = **1,906,884** subsets enumerated with no prune whatsoever,
  1,027,968 admissible, minimum distinct circumradii **5**, witness
  `(0,0),(0,1),(1,3),(1,4),(2,2)` — identical value *and* identical witness to
  `results/lath_n5_7x7_t6.json`.
* 11×11, n=5: all C(121,5) = **198,792,594** subsets, no prune, 147,902,768 admissible,
  minimum **4**, witness `(0,0),(0,7),(2,6),(4,3),(6,9)` — identical to
  `results/lath_n5_11x11_t5.json`. 400 s, exact integer arithmetic throughout.

So the count `NOTE.md` and `AUDIT_SUMMARY.md` quote without an artifact is right, and
the prune and admissibility test are correct at that size. (The 17×17 negative itself is
C(289,5) ≈ 2.1e9 and I did not enumerate it; the method behind it is now checked at two
sizes.)

**C7. The classification threshold is not doing hidden work.** Task item 2: the tau
slopes are −0.02, −0.01, 0.01, 0.01, 0.01, 0.01, 0.03, 0.03, 0.05, 0.05, 0.05, 0.06,
0.06 | 0.95, 1.14. The 0.5 cut sits in an empty gap of width 0.89 and no pattern is near
it. The threshold is fine; it is the *thing being classified* that was wrong (R1).

**C8. FATAL F1 from the first audit is genuinely fixed.** `caseA2.py` measures each
equation as `(r_a − r_b)/(|r_a| + |r_b|)`, against its own two radii. No unconstrained
quantity can inflate the denominator, so the ctrlA pathology cannot recur. (Its ladder
is broken for a different reason — R5.)

**C9. `orthobranch.py` is genuinely withdrawn.** The file opens with
`"""VACUOUS - RETAINED ONLY AS A RECORD. DO NOT CITE THIS RUN.` and the reasoning; the
claim is gone from `NOTE.md` and `REPRODUCE.md` cites it only as a record.

**C10. `verify.py`'s check of the n=6 exhaustive claim is genuinely fixed.** It now
re-derives the recorded witness in sympy (`re-derived: admissible=True, 6 distinct
radii`) instead of reading `completed`. Checkpoint `.ck.json` files are excluded from
the globs in both `verify.py` and `fgp.py`. `lath.py` artifact names now carry the
target. `beam.py`'s "by translation invariance" justification is corrected to a stated
restriction.

---

# COUNTS

| severity | count | items |
|---|---|---|
| FATAL | 1 | R1 |
| SERIOUS | 7 | R2, R3, R4, R5, R7, R8, R9 |
| MINOR | 10 | R6, R10, R11, R12, R13, R14, R15, R16, R17, R18 |
| WORDING | 2 | R19, R20 |

Total 20.

Previously-reported defects re-checked and found genuinely fixed, one line each:

* **F1, ctrlA's mean-of-six normalisation** — fixed; `caseA2.py` measures each equation
  against its own two radii and the pathology cannot recur (C8).
* **the Case A ladder drawing equations in an order Lemma 1 forbids** — fixed; the nine
  splits are exactly the (4,2) and (3,3) partitions with per-vertex degree ≤ 2, and I
  re-enumerated them independently: 9.
* **orthobranch cited as confirmation** — fixed; the file is headed
  "VACUOUS — DO NOT CITE THIS RUN" and the claim is gone from `NOTE.md` (C9).
* **`verify.py` checking only metadata on the n=6 exhaustive run** — fixed; it now
  re-derives the witness in sympy (C10). (Still metadata-only for the n=5 negative, R16.)
* **`verify.py`/`fgp.py` globbing `.ck.json` checkpoints as complete** — fixed, both
  globs exclude them.
* **two `lath` runs writing the same filename** — fixed, names carry `_t<target>`.
* **`beam.py`'s "by translation invariance"** — fixed; the seeding restriction is now
  stated, not justified.
* **`pscreen` having no minimum-distance guard** — fixed in `pscreen.py` (but not in
  `tausweep.py`, which is the file that produced the headline; R3).
* **`penum.py`'s Lemma-numbering** — fixed in the docstring, not in the output (R13).
* **"h(4)=1, h(5)≤4, h(6)≤6" and the pattern counts** — all reproduce exactly in
  independent exact arithmetic (C1, C2).

# WHAT THE DIRECTORY CAN STILL SAY

Unchanged and independently re-verified here: **h(4) = 1**, **h(5) ≤ 4**, **h(6) ≤ 6**,
**h(5) ≥ 2** and **h(5) ≥ 3**, the lemmas, the lower-bound table, monotonicity, and the
lattice searches.

The case for h(5) = 4 is now down to one leg with an artifact and one without. The
fifteen-pattern screen contributes **nothing**: its equality systems have hundreds of
exact roots, all of them four-concyclic, and every verdict it has ever printed —
"no lead", "13 obstructed" — was a measurement of one of its own constants. The
s²/2 obstruction holds and I reproduced it to seven figures, but it covers one pattern
of twelve and is a numerical global minimisation, not a proof. The 17×17 lattice
exhaustion holds and its method checks out at 7×7 and 11×11, but a lattice is a
restriction. The Case A branch rests, by `NOTE.md`'s own sentence, on a run that is not
in this directory.
