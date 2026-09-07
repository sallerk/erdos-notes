# AUDIT_CODE.md - adversarial audit of the COMPUTATIONAL METHOD in p831

Auditor: independent agent. Date 2026-09-07, ~11:40 MDT.
Everything below was produced by probes written from the definitions, not by re-running
the directory's own scripts and believing the output. Probe sources are in the session
scratchpad (`bf.c`, `caseA_ladder.py`, `tausweep.py`, `hitrate.py`).

**Moving target.** `NOTE.md`, `LESSONS.md`, `REPRODUCE.md`, `verify.py` were rewritten
and `ctrlB.py`, `fgp.py`, `AUDIT_SELF.py` were added at 10:27-10:30 today, i.e. *during*
this audit. All findings below refer to the state at 11:40. Defects D1, D6, D9, D12
were already present in the pre-10:27 version and survived the self-audit rewrite.

Count: **2 FATAL, 6 SERIOUS, 8 MINOR, 5 WORDING.**

---

## PART A - what survived the attack

State these first, because the defect list is long and most of the arithmetic is sound.

**A1. `lath.py`'s DFS is correct and its exhaustive claims reproduce exactly.**
I wrote an independent C brute force (`bf.c`) from the definitions, with the 4x4
concyclicity determinant expanded along a *different* column from `lath.py`'s. Node
counts agree to the last digit on every run in `results/`:

| run | lath.py nodes | independent C nodes | result |
|---|---|---|---|
| n=4, 6x6, target 4 | 732 | 732 | best 1, same witness |
| n=5, 7x7, target 6 | 189,075 | 189,075 | best 5, same witness |
| n=5, 11x11, target 5 | 651,094 | 651,094 | best 4, same witness |
| n=5, 17x17, target 4 | 8,514,906 | 8,514,906 | none |
| n=6, 11x11, target 7 | 7,968,042 | 7,968,042 | best 6, same witness |
| n=6, 11x11, target 6 | 7,967,782 | 7,967,782 | none |

So the det4 sign convention does not matter (it is only tested against zero), the
`start = chosen[-1]+1` ordering does cover every subset, and there is no integer
overflow (int64 in C suffices at 17x17 and matches Python bignums).

**A2. The prune `if len(merged) >= best[0]: continue` is sound, and I verified it by
brute force rather than by argument.** The radius set only grows along a branch and
every prefix of an admissible set is admissible, so no witness can be cut. Checked
against prune-free full enumerations:

* 11x11, n=5: all **198,792,594** subsets enumerated, 147,902,768 admissible,
  minimum distinct radii **4**, attained by 80 sets, **none below 4**. Same witness
  `(0,0),(0,7),(2,6),(4,3),(6,9)`.
* 9x9, n=6: all **324,540,216** subsets, minimum **7**, identical to the pruned DFS's
  answer and witness.
* 6x6, n=4: minimum 1 (200 sets); 6x6, n=5: minimum 5.

Admissibility is applied to every generated triple and quadruple: when point `P` is
added at depth `k`, `circ2` covers all `C(k,2)` new triples and `det4` all `C(k,3)` new
quadruples, and everything else was checked at a shallower depth. The prune runs
*before* the concyclicity test, which can only discard nodes early, never keep bad ones.

**A3. The three witnesses are exact.** Re-derived in `fractions.Fraction` with a
permutation-expansion determinant sharing no code with the directory:

| n | points | admissible | distinct R^2 | class sizes |
|---|---|---|---|---|
| 4 | (0,0),(0,3),(1,1),(2,1) | yes | 1 | [4] |
| 5 | (0,0),(0,7),(2,6),(4,3),(6,9) | yes | 4 | [4,2,2,2] |
| 6 | (0,0),(0,7),(2,6),(4,3),(6,2),(6,9) | yes | 6 | [8,4,2,2,2,2] |

All six `beam_13x13` witnesses also check out exactly (n=3..8, h = 1,1,4,6,12,16, all
admissible, all inside the declared grid).

**A4. `penum.py` reproduces.** Independent re-enumeration over all `k^10` colourings:
0 / 1 / 15 canonical patterns at k = 1/2/3; 35 at k=3 under Lemma 1 alone; profiles
(4,3,3)x7, (4,4,2)x5, (5,3,2)x2, (5,4,1)x1; 12 within f(5)=4. Matches
`penum_n5_k3.json` exactly. A003829 = 1,4,4,8,12,16 confirmed from `A003829.txt`.

**A5. `obstruction433.py`'s s^2/2 law is real and the penalty weight is NOT distorting
it.** I re-ran the minimisation with a *hard* nonlinear inequality constraint (SLSQP,
no penalty term at all) and with an independent 180^3 vectorised grid:

| s | obstruction433.json | my hard-constraint min | s^2/2 | ratio | 180^3 grid |
|---|---|---|---|---|---|
| 0.35 | 6.246153e-2 | 6.246153e-2 | 6.125e-2 | 1.0198 | 7.55e-2 |
| 0.25 | 3.157056e-2 | 3.157056e-2 | 3.125e-2 | 1.0103 | 3.95e-2 |
| 0.15 | 1.129196e-2 | 1.129196e-2 | 1.125e-2 | 1.0037 | 1.53e-2 |
| 0.08 | 3.203408e-3 | 3.203408e-3 | 3.200e-3 | 1.0011 | 5.49e-3 |
| 0.03 | 4.500675e-4 | 4.500675e-4 | 4.500e-4 | 1.0002 | 6.09e-4 |

Six significant figures of agreement with no penalty at all. The minimum sits on the
constraint boundary (`sep = smin` to 1e-9) in all five cases. This is the strongest
piece of numerical evidence in the directory and it holds up.

**A6. Nothing is hidden under floating-point noise.** Recomputing R^2 at each reported
optimum in 50-digit `mpmath` and comparing with the float64 value gives an evaluation
error of 8e-15 (patterns 0,1) to 7e-11 (pattern 11, min pairwise distance 0.004) -
four to seven orders of magnitude *below* the residuals being quoted. The residual is
locally Lipschitz with slope ~6 (measured by perturbing the exact n=5 witness by delta
= 1e-12 ... 1e-1 and reading the residual back), so a reported residual r corresponds to
a distance ~r/6 from a solution if one existed there. The condition number of
`R^2 = a2 b2 c2 / S` is bad only when `S/scale^2` is small, and at the reported optima
`S/scale^2` is 2.2e-3 down to 3.6e-7, giving a rounding floor of ~1e-13 at worst.
**A genuine solution is not hiding below the noise at any configuration the searches
actually reported.**

---

## PART B - defects

### D1. FATAL - `ctrlA.py`, the positive control for the whole Case A negative, does not solve the equations it reports as solved

`ctrlA.res_k` normalises by `sc = float(np.mean(r))` where `r` is **all six**
P-triple radii, but constrains only `k` of them. The optimiser drives an
*unconstrained* radius to ~1e15 by making one triple near-collinear, inflating `sc` by
14 orders of magnitude, and the residual divides away to nothing. Evaluating the stored
solutions in `results/ctrlA.json`:

| k | reported residual | verdict printed | radii it claims are equal | true relative error |
|---|---|---|---|---|
| 1 | 0.0 | SOLVED | 1.262864, 1.262864 | 0 (genuine) |
| 2 | 1.94e-14 | SOLVED | 2.3107, **9.4071**, 2.3108 | **3.07** (307%) |
| 3 | 7.73e-15 | SOLVED | 14.90, 21.59, 24.52, **29.76** | **0.64** (64%) |
| 4 | 6.00e-14 | SOLVED | 148.02, 141.33, 140.45, 141.83, 141.02 | **0.054** (5.4%) |
| 5 | 1.34e-08 | **NOT SOLVED** | all six equal to 9 digits | **1.34e-08** |

The sixth radius at k=2,3,4 is 2.2e15, 1.2e16, 7.6e14 respectively, because
`cross(P,C,H)` is 3.5e-8, 7.8e-7, 6.9e-6 - point P is sitting on the line CH.
**The ladder is inverted:** the rungs labelled SOLVED are violated by 5% to 307%, and
the rung labelled NOT SOLVED is the only one that actually satisfies its equations.

Consequences. `NOTE.md` section 5: "best relative residual 7e-8, against a control
(`ctrlA.py`) that solves four equations of the same family to 6e-14. **No solution
found.**" - the comparison is with a number that measures nothing.
`REPRODUCE.md`: "`python ctrlA.py` # control: 4 equations in 4 unknowns ARE solvable,
5 are not" and "Run `ctrlA.py` ... before believing any negative from this directory" -
this instructs the reader to validate the directory against a broken instrument.
`LESSONS.md` P3 records the broken ladder as the lesson that controls must be able to
fail. And P2 records the mean-R^2 normalisation as the *fix* for an earlier problem;
it is the mechanism of this one.

Note also that the equations are not "of the same family": `PAIRS[:4]` imposes
r0=r1=r2=r3=r4, a class of size **5** among the six P-triples, which `caseA.splits()`
itself excludes (it admits only (4,2) and (3,3)).

### D2. FATAL - `pscreen.py`'s two smallest residuals measure its own hard-coded constant, not the geometry

For patterns 0 and 1, the optimum sits *exactly* on the concyclicity margin:
`min |det4| / scale^1.5 = 1.000000e-06`, which is the hard-coded threshold `tau = 1e-6`
in `make_residual`. Re-running `pscreen`'s own optimiser with `tau` swept:

| tau | pattern 0 residual | min|det4|/sc^1.5 | pattern 1 residual | min|det4|/sc^1.5 |
|---|---|---|---|---|
| 1e-4 | 3.844e-05 | 1.000e-04 | 1.278e-05 | 1.000e-04 |
| 1e-5 | 6.789e-06 | 1.000e-05 | 1.302e-06 | 1.000e-05 |
| **1e-6** | **1.481e-07** | 1.000e-06 | 8.882e-07 | 1.000e-06 |
| 1e-7 | 9.835e-08 | 1.000e-07 | 6.786e-08 | 1.000e-07 |
| 1e-8 | 3.440e-09 | 1.000e-08 | 2.717e-09 | 1.000e-08 |

The residual tracks `tau` over four decades (roughly 0.1-1 x tau) and the constraint is
active at every value. Replicated at a different restart count (120 instead of 200):
pattern 0 reproduces to the digit (3.844e-05, 6.789e-06, 1.481e-07, 9.835e-08,
3.440e-09); pattern 1 gives 1.278e-05, 1.302e-06, 1.065e-06, 2.030e-07, 2.030e-08,
i.e. `residual / tau` pinned at 2.03 for the last two decades - linear tracking of the
constant, not convergence to a floor. Pattern 0's configuration is a near-rectangle
`(0,0),(1,0),(~0,3.437),(~1,3.437)` - four concyclic points - with the fifth on the
symmetry axis. **These patterns are realisable to any accuracy you ask for, arbitrarily
close to a degenerate configuration; `pscreen` reports the distance at which its own
penalty stops it and calls that a negative.** Because the achievable residual is
~1e-7 at `tau=1e-6`, the screen's `lead` test `c < 1e-12` can *never* fire for such a
pattern, at any number of restarts.

`NOTE.md`: "0 leads, every residual between 1.5e-7 and 1.0e-3 against a control that
recovers a known-realisable pattern at 6.7e-16, **a gap of eight orders of magnitude**"
- the gap is a property of the constant 1e-6. This is exactly the structure that
`obstruction433.py` documents honestly for the (4,3,3) branch (a floor sitting on the
non-degeneracy constraint), but here it is presented as a clean negative. The other
13 patterns are not affected (their `min|det4|/sc^1.5` is 2.4e-5 to 4.9e-4, well clear
of `tau`), so their residuals of 4e-4..1e-3 stand.

### D3. SERIOUS - `verify.py`'s audit of the two headline exhaustive claims is vacuous

Section 4b checks `bool(d['completed']) and d['target'] == tgt`. It never looks at
`best` or `witness`. I copied `results/`, set
`lath_n5_17x17.json: best = 1` (a 5-set with ONE radius, flatly contradicting the
claim) and `lath_n6_11x11.json: best = 99`, and re-ran:

```
[PASS] no admissible 5-set on the 17x17 grid has <= 3 radii (completed=True, 8514906 nodes)
[PASS] the 11x11 grid minimum at n=6 is exactly 6 (completed=True, 7968042 nodes)
...
ALL CHECKS PASSED
```

`REPRODUCE.md` says `verify.py` "audits every claim in NOTE.md against results/" and
"exits non-zero on any failure". For the two exhaustive statements it checks that the
file exists and that a command-line argument was echoed back. (The claims themselves
are true - see A1/A2 - but nothing in the directory establishes that.)

### D4. SERIOUS - `ctrlB.py`'s rank is 4, not 5, and the "harder" control is not harder

`ctrlB.py` builds its Jacobian with **one-sided** differences at `eps = 1e-6` and calls
`np.linalg.matrix_rank(Jc, tol=1e-6)` - an *absolute* singular-value cut. Recomputing
with central differences in `pscreen`'s own gauge:

```
eps=1e-3  sv = [1.661e+01 1.423e+00 1.119e+00 3.530e-01 6.608e-04 5.442e-06]
eps=1e-4  sv = [1.658e+01 1.423e+00 1.119e+00 3.531e-01 6.605e-06 5.442e-08]
eps=1e-5  sv = [1.658e+01 1.423e+00 1.119e+00 3.531e-01 6.604e-08 5.519e-10]
```

The last two singular values fall as eps^2 - the signature of exact zeros contaminated
by truncation error. The rank is **4**, with two dependent equations, not 5 with one.
(This is what the geometry says: the three class-1 equations cut the 6-dimensional
gauge space down to the 3-dimensional type-III family, Lemma 6 makes two more equations
identities on that family, and R(014)=R(023) removes one more dimension. Solution set:
**2-dimensional**.) `ctrlB.py`'s own docstring says "only four independent ones"; its
artifact and `NOTE.md` say five. The one-sided Jacobian's fifth and sixth singular
values are 3.3e-5 and 4.8e-7, straddling the absolute tolerance 1e-6 - move the
tolerance one decade either way and you get 6 or 4.

Worse, the inference is backwards. A *larger* rank deficiency means a
*higher-dimensional* solution set, which random restarts find *more* easily. Measured
per-restart hit rate under `pscreen`'s own optimiser, 500 restarts each:

| control | hits / 500 | rate | P(500 restarts all miss) |
|---|---|---|---|
| original pscreen control (n=5 witness, k=4) | 51 | 0.102 | 4e-24 |
| `ctrlB` "harder" control | 47 | **0.094** | 4e-22 |

Statistically indistinguishable, point estimate slightly *easier*. `NOTE.md`
("`ctrlB.py` narrows the gap ... the optimiser demonstrably finds solutions that live
on a degenerate subvariety, which is precisely the ability the n=5 negative needs"),
`LESSONS.md` P9, `REPRODUCE.md` ("This is the control that matters") and `verify.py`'s
new check all rest on this.

### D5. SERIOUS - 500 restarts is not demonstrably enough, and the directory's own numbers can show it

The brief asked for the false-negative probability, honestly. Using `pscreen`'s own
`make_residual` and `least_squares` settings:

* **Exactly-determined, realisable** (the current control, 6 equations / 6 unknowns):
  hit rate **10.2%** per restart -> P(500 restarts all miss) ~ **4e-24**. Safe, but this
  is the easy case.
* **Overdetermined, realisable, admissible, from this directory's own artifacts**
  (the n=6 witness pattern: k=6, 20 triples, 14 equations in 8 unknowns, overdetermined
  by 6): hit rate **0.33%** (2 hits in 600) -> P(500 restarts all miss) ~ **19%**.

So on an overdetermined-but-consistent instance the same code has a ~1-in-5 chance of
producing a false negative at 500 restarts. The screened n=5 patterns are overdetermined
by one, between the two; nothing in the directory bounds their hit rate. (The n=6 test
is in 8 dimensions rather than 6, so it is an indication, not a matched control - but it
is the only realisable overdetermined instance available here, and it is 30x harder than
the control actually used.)

Related: `pscreen` draws restarts from `uniform(-2.0, 2.5)^6` while its span penalty
permits `|coord| < 60`. The restart box is **2.8e-9** of the permitted volume, and one
of the 15 recorded optima has a coordinate of 19.5 - outside the box the search starts
in. `caseA.py` has the same shape of problem (start box is 3.3e-6 of `big < 40`).

### D6. SERIOUS - the Case A negative has no working control at any rung, not just at k=4

Beyond D1: I built a proper ladder on `caseA`'s *own* system - same splits, same
unknowns, equations dropped one at a time, with a scale-free residual
`(r_a - r_b)/(|r_a|+|r_b|)` and a minimum-distance guard (which `caseA.py` lacks
entirely, as it lacks any concyclicity penalty). 120 restarts per rung:

```
split [2,3,4] | [0,1,5]     1 eq: 6.27e-17   2 eq: 1.09e-05   3 eq: 2.47e-06   4 eq: 2.94e-05
split [2,3]   | [0,1,4,5]   1 eq: 0.00e+00   2 eq: 2.23e-16   3 eq: 2.11e-05   4 eq: 6.70e-06
split [1,2,3,4]|[0,5]       1 eq: 7.02e-17   2 eq: 7.52e-06   3 eq: 1.87e-05   4 eq: 3.03e-05
```

The ladder is **non-monotone** - 3 equations solved better than 2, 4 better than 3 -
and it stalls at 1e-5 on systems that are *underdetermined* (2 equations in 4 unknowns).
The failing rungs land on the penalty cliffs (`|cy| = 0.05` exactly, `mindist = 0.01`
exactly). Whatever the reason, a search that cannot reliably solve 2 of 4 equations
carries no information when it fails to solve 4. `caseA`'s residuals are otherwise
honest - the mean-R^2 exploit of D1 does not bite there, because all six radii are
constrained (I measured max/min radius ratio = 1.00-1.01 at every optimum, and the
scale-free residual agrees with the reported one to within a factor of 2).

I did reproduce the 7e-8 figure: 150 restarts gives best 7.25e-08 on split `[2,3,4]`.
It is a real number; it just has no control behind it.

### D7. SERIOUS - `orthobranch.py` searches for something the directory itself proves impossible, and this is reported as independent confirmation

`orthobranch.points(th4)` is Lemma 5's parametrisation, under which
`P1 + P4 = P2 + P3` **identically** - the four points are always a parallelogram.
`NOTE.md` Lemma 6 then proves no parallelogram is orthocentric. So the constraint
`H(P_a,P_b,P_c) = P_which` that `orthobranch` imposes is unsatisfiable *by construction*,
for every one of the 80,000 restarts. The run tests nothing about the optimiser, the
geometry, or the pattern; a search with a bug that made it always fail would produce the
identical artifact.

`NOTE.md`: "`orthobranch.py` separately confirms the other branch is empty: 0
admissible solutions in 80,000 restarts, as the parallelogram argument predicts." It is
not separate and it does not confirm. `results/orthobranch.json` records only
`{"found": [], "completed": true}` - no residuals, no restart count, no per-branch
data - so the artifact cannot distinguish this run from a crashed one. (Its `.err` log
shows divide-by-zero warnings inside `ortho`.) There is also no positive control.

### D8. SERIOUS - several quoted numbers have no artifact behind them

Checked every number in `NOTE.md` against `results/`:

| claim | where | artifact |
|---|---|---|
| Case A "best relative residual 7e-8" | NOTE 5, REPRODUCE | **none** - `caseA_n5.json` records only `hits: []`; there is no `logs/caseA*` |
| "A 110^3 grid over the region with separation above 0.25 contains no point with both residuals below 0.02" | NOTE 5 | **none** - no 110^3 sweep exists; `typeIII.py` was run at 10^3 |
| "Three encodings were benchmarked first ... all three timed out at thirty seconds" | NOTE 5 | **none** - `enc_test.py` writes no JSON and has no log |
| "the published extremal configurations at n=7,8 ARE degenerate (a collinear triple and a concyclic rectangle at n=7, three collinear triples at n=8)" | NOTE 3a | **none** - attributed to "a literature agent", absent from `REFERENCES.md` |
| orthobranch's per-branch best residuals (3.1e-7, 1.2e-7, 1.4e-7, 2.4e-7) | `logs/` only | not in `orthobranch.json` |
| obstruction433 ratios 1.0198 / 1.0103 / ... | derived | not stored (I recomputed them; they are right) |

My own 180^3 grid is *consistent* with the 110^3 claim (minimum 3.95e-2 at sep >= 0.25,
above 0.02), so the statement appears true - it just is not supported by this directory.

### D9. MINOR - `NOTE.md`'s "Its size-4 class has support 5" is false; the support is 6

Exact computation on the n=6 witness. The size-4 class is R^2 = 65/2, triples
`(0,1,5),(0,4,5),(1,2,3),(2,3,4)`, support `{0,1,2,3,4,5}` - all six points. The
conclusion drawn (that it is not an orthocentric quadruple) holds a fortiori, so only
the number is wrong. Full profile: `[8, 4, 2, 2, 2, 2]` with supports 6, 6, 4, 4, 4, 4.

### D10. MINOR - `results/typeIII_n5.json` is an incomplete run and its most interesting number is unreported

`typeIII.splits()` returns **10** splits; the artifact holds **3** and says
`"completed": false`. Its first entry records `best = 8.978e-10` for split
`[[0,1],[2,3,4,5]]` - two orders of magnitude *below* the 7e-8 that `NOTE.md` quotes as
the directory's closest approach in Case A - and nothing anywhere mentions it.
`REPRODUCE.md` lists `python typeIII.py 10 10` as part of the case analysis.

### D11. MINOR - checkpoint files are consumed as completion artifacts

`verify.py` and `fgp.py` both glob `results/lath_n*.json`, which matches
`lath_n6_11x11.ck.json` (`"completed": false`). `verify.py`'s witness table duly lists
it as a source. Here the checkpoint carries the same correct witness so nothing breaks,
but the mechanism means a half-finished run is indistinguishable from a finished one to
the audit script.

### D12. MINOR - an artifact was silently overwritten by a second run

`logs/n6_11.log` records a completed `lath.py 6 11 11 6` run (`best=none`, 7,967,782
nodes) and `logs/n6_11_t7.log` a completed `lath.py 6 11 11 7` run (`best=6`, 7,968,042
nodes). Both wrote `results/lath_n6_11x11.json`; only the second survives. Nothing in
`results/` records the target-6 run. (The target-7 run does establish the minimum on its
own, so the claim is unaffected - only the record is.)

### D13. MINOR - `pdecide` exceeded its own timeout and its artifact has no completion flag

Pattern 0 took 2336.52 s against a 1,800,000 ms limit (+30%), pattern 1 1871.76 s,
pattern 3 1910.75 s. `pdecide_n5_k3.json` has no `completed` key, unlike every other
artifact. All 15 verdicts are `unknown`; `NOTE.md` now reports that honestly.

### D14. MINOR - `pscreen.py` has no minimum-distance penalty

Its side conditions are span, flatness, class separation and concyclicity. Two
coincident points are not excluded. Recorded optimum 11 has min pairwise distance
**0.0041** and optimum 5 has **0.036**; those are not 5-point configurations in any
meaningful sense, and restarts that fall into such basins are wasted. `typeIII.py`
does have the penalty; `pscreen.py` and `caseA.py` do not.

### D15. MINOR - `beam.py`'s seeding justification is wrong

`run()` keeps only seed triples with `pts[i] == (0,0)`, i.e. containing the grid corner,
justified in the docstring "by translation invariance". Translation normalises a set so
that `min x = 0` and `min y = 0`, which does not put any *point* at `(0,0)`. The
restriction is a real (unstated) narrowing of the beam. Harmless for the claims - a beam
gives upper bounds only - but the n=7 and n=8 witnesses that `fgp.py` reads come from it.

### D16. MINOR - `REPRODUCE.md`'s "what was actually run" table omits the 17x17 run

The table lists `lath.py 5 11 11 5` and `lath.py 6 11 11 7` but not
`lath.py 5 17 17 4`, which is the command behind the headline exhaustive statement in
NOTE section 4.

### D17. WORDING - `LESSONS.md` P3 misdiagnoses the ctrlA k=4 configuration

"the k=4 control solution is itself geometrically inadmissible - it has four concyclic
points". It does not: `min |det4| = 3.66` at coordinates of size ~12. The actual
pathology is a near-collinear triple (P on line CH, `cross = 6.9e-6`) sending one
circumradius to 7.6e14. The stated reason is wrong and the real one is the reason the
control fails (D1).

### D18. WORDING - "four equations of the same family" (NOTE 5) is doubly wrong

Not the same family (it is a size-5 class, excluded by `caseA.splits()`), and not solved
(5.4% relative error). Same sentence in `REPRODUCE.md` and `LESSONS.md` P3.

### D19. WORDING - the rank-deficiency inference in NOTE 5 / LESSONS P9 is a non sequitur

"the optimiser demonstrably finds solutions that live on a degenerate subvariety, which
is precisely the ability the n=5 negative needs". What the negative needs is the ability
to find an *isolated* solution of an *overdetermined* system. A rank deficiency does the
opposite: it enlarges the solution set. Measured, `ctrlB` is not harder (D4).

### D20. WORDING - `penum.py`'s docstring renames NOTE's Lemma 4 as "LEMMA 5"

`quad_ok`'s docstring says "LEMMA 5 (proved in NOTE.md): if three of the four triples of
a 4-set have the same circumradius..."; in `NOTE.md` that is Lemma 4 and Lemma 5 is the
type-III parametrisation. Cross-checking the filters against the write-up requires
noticing this.

### D21. WORDING - `NOTE.md` section 1 is not synchronised with the completed runs

The table still reads "h(5) = 4 | NOT ESTABLISHED. 15 patterns remain to be decided",
which is right, but section 5's prose was updated for the finished `pscreen`/`pdecide`
runs while `REPRODUCE.md` still says "Screens that were still running when this was
written are marked as such in NOTE.md and are not claims" - there are no longer any
running screens. Minor drift between the three documents.

---

## PART C - what I would do first

1. Delete or rewrite `ctrlA.py`. Normalise by the mean of the radii *being compared*,
   or use the scale-free form `(r_a - r_b)/(|r_a| + |r_b|)` that `target433.py` already
   uses, and add a degeneracy guard. Then re-run and see whether the ladder survives.
   Until then, remove the Case A negative from `NOTE.md` section 5 or mark it
   uncontrolled.
2. Replace `pscreen`'s hinge penalties with a report of *both* numbers - the equation
   residual and the achieved degeneracy margin - and sweep the margin. A pattern whose
   residual tracks the margin is realisable-on-the-boundary, which is a different (and
   more interesting) finding than "no lead". Patterns 0 and 1 are of that kind.
3. Make `verify.py` section 4b check `d['best'] is None` / `d['best'] == 6`. It takes
   one line each and would have caught a real regression.
4. Record the per-split and per-branch best residuals in `caseA_n5.json` and
   `orthobranch.json`. Both currently record an empty list and nothing else.
5. Fix the `ctrlB` rank (central differences, relative tolerance) and drop the claim
   that it is a harder control; the honest statement is that no matched control exists
   at n=5, which `AUDIT_SELF.py` already says.
