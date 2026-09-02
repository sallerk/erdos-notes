# Erdős #654: exact small values of the pinned distance count

`f(n)` is the largest number such that **every** admissible set of `n` points in the plane
has some point with at least `f(n)` distinct distances to the others:

    f(n) = min over admissible X of  M(X),      M(X) = max_i d_X(x_i)

where `d_X(x)` counts the distinct distances from `x` to the other points of `X`.

Two hypotheses, kept apart throughout:

* **`f_N4`** — no four points on a circle. Collinear points are allowed. *This is the
  quantity on the problem page.*
* **`f_G`** — general position: also no three collinear. *This is Sheffer's `D̂_gen(n)`
  (arXiv:1406.1949 **v2**, p. 6; see the version note in section 1).*

Since every general-position set is in particular free of concyclic quadruples,
`f_N4(n) <= f_G(n)`: a lower bound proved under N4 covers both, and a general-position
witness bounds both from above.

---

## 1. Results

| n | trivial bound `⌈(n−1)/3⌉` | `f_N4(n)` | `f_G(n)` | excess over trivial |
|---|---|---|---|---|
| 3 | 1 | **1** | **1** | 0 |
| 4 | 1 | **2** | **2** | +1 |
| 5 | 2 | **3** | **3** | +1 |
| 6 | 2 | **3** | **3** | +1 |
| 7 | 2 | `[3, 4]` | `[3, 4]` | ≥ +1 |
| 8 | 3 | `[3, 4]` | `[3, 4]` | ≥ 0 |

Every value in the table is the same for both hypotheses; no configuration exploiting
collinearity beats a general-position one at these sizes.

Sheffer, arXiv:1406.1949 **v2** (19 May 2015), p. 6, writes that **no non-trivial bound is
known for `D̂_gen(n)`, neither a lower nor an upper one**, and poses finding its exact value
as his Problem 10. The four exact values above are an answer for `n <= 6`.

*The version matters and must be cited precisely.* The same paragraph is Problem **12** in
v1, and **v3 (2 July 2018, the current arXiv version) removes the `D̂_gen` paragraph and its
problem from the body text**; v3's Problem 10 is about `D_d(n)` in higher dimensions, and
the word "frustrating" does not occur in it at all. A `D̂_gen(n)` row does survive in v3's
Table 1. A reader who checks only the current version will not find the problem.

## 2. The trivial lower bound, and why it is not tight

Fix a point `x`. The other `n-1` points are partitioned by their distance from `x` into
`d_X(x)` circles centred at `x`. A circle centred at `x` carrying four points of `X` would
give four concyclic points, so each circle holds at most 3. Hence `n-1 <= 3 d_X(x)` for
**every** `x`, and so

    f(n) >= ceil((n-1)/3).

This needs only the no-four-concyclic hypothesis. It is what Erdős calls trivial, and
Erdős's question (3) in [Er87b] asks whether it can be improved to `(1/3 + c)n`.

**A conflation to watch for in the literature.** Brass–Moser–Pach render the `(1/3 + c)n`
question in terms of `v_γ(n)`, the minimum **total** number of distinct distances under
condition `γ` (p. 214: "We do not know any argument showing that there exists `ε > 0` such
that `v_no-4-circ(n) >= (1/3 + ε)n`"), whereas the problem page and Erdős's own [Er87b]
statement are about the **pinned** maximum. The two agree at the trivial bound, because the
`⌈(n−1)/3⌉` lower bound for the total count is *derived from* the pinned argument, which is
probably why they get run together. Any claim of the form "no non-trivial bound is known"
should say which of the two functions is meant.

The table shows the bound is **not** tight at `n = 4, 5, 6, 7`: the excess is `+1` at each.
That is weak evidence in the direction of (3), and it is the reason exact small values are
worth having. It is only evidence: a bounded excess is exactly what a negative answer to
(3) would also look like at small `n`.

## 3. Upper bounds: verified witnesses

Every witness is checked from exact plane coordinates (`sympy`, no floating point), for
its pinned counts, its total distance count, no three collinear and no four concyclic.

| n | `M` | configuration | source |
|---|---|---|---|
| 3 | 1 | equilateral triangle | `pinned.py` |
| 4 | 2 | `A_2` points `(0,0), (-1,0), (-1,1), (0,-1)`; also the equilateral triangle plus its centre | `pinned.py` |
| 5 | 3 | the `D_gen(5)` witness, squared distances `{1, 2+√3, 4+2√3}` | `pinned.py` |
| 6 | 3 | `A_2` points `(0,0), (-1,0), (1,1), (-2,3), (1,-3), (3,-2)` | `latM.py`, verified in `witness_n6_M3.json` |
| 7 | 4 | a 7-subset of the `n=8` `D_gen` witness | `subsets.py` |
| 8 | 4 | the `D_gen(8)` witness, `A_2` | `pinned.py` |

**`M` and `D` are different objectives.** The `n=8` witness has `D = 7` but `M = 4`, which
is *better* than the `n=7` `D`-optimal witness's `M = 5`; deleting a point from it then
improved `n=7` from 5 to 4. Witnesses optimised for the total count are not optimised for
the pinned maximum, and the `n=6` entry above (`M=3`, `D=7`) was found by a search whose
objective was changed to `M`.

**Monotonicity.** Deleting a point cannot add a distance at a surviving point, so
`M(X') <= M(X)` for `X' ⊂ X`; hence `f` is non-decreasing and every subset of a witness is
itself a witness at its own size.

## 4. Lower bounds: exhaustive over patterns

A *pattern* colours the `C(n,2)` edges of `K_n`; a colour class is a distance value. The
hypothesis `M(X) <= m` becomes purely local: **at most `m` distinct colours at each
vertex**, and (no four concyclic) **at most 3 edges of one colour at a vertex**. Those two
constraints force `n-1 <= 3m` and cap the palette at `k <= nm/2`, so unlike the #98 setting
the number of classes is derived rather than fixed.

`penum.py` enumerates these by DFS under three reductions: restricted-growth colour
numbering (exact quotient by colour renaming, free); vertex 0's edges required
non-decreasing (sound because vertices `1..n-1` may be relabelled freely, and very strong);
and full canonicalisation under all `n!` relabellings, applied last. It is validated
against brute force on five cases (`python penum.py crosscheck`), agreeing exactly on the
canonical counts every time.

Each surviving pattern is then decided exactly by `pdecide.py`: realisability in the plane
is equivalent to the Gram matrix `G_ij = (d_0i + d_0j - d_ij)/2` being PSD of rank at most
2, so every `3×3` minor vanishes; a lex Gröbner basis triangulates those polynomials in the
`k-1` unknown class values, real roots come from `CRootOf`, and each branch is
reconstructed at high precision and tested geometrically.

| rung | patterns after enumeration | outcome |
|---|---|---|
| `n=4, m=1` | 1 | unsat ⇒ `f(4) > 1` |
| `n=5, m=2` | 14 | 13 unsat; the 14th settled below ⇒ `f(5) > 2` |
| `n=6, m=2` | 11 | all unsat ⇒ `f(6) > 2` |
| `n=7, m=2` | **1** | unsat ⇒ `f(7) > 2` |

All four hold in **both** modes.

### `f(7) > 2` needs no solver at all

The `n=7, m=2` rung collapsing to a single pattern is not an accident, and once one asks
*why*, the whole rung falls to a short argument that uses no algebra. It is worth stating
separately because it is checkable by hand.

Suppose 7 points have `M <= 2`. Each vertex has 6 edges carrying at most 2 colours, and at
most 3 edges of one colour (a 4th would put four points on a circle centred at that
vertex). So every vertex sees **exactly** two colours, each exactly **3** times.

1. Every colour class is therefore 3-regular on the set of vertices it meets. A class with
   support `s` and `e` edges has `3s = 2e`, so **`s` is even**.
2. A 3-regular graph needs at least 4 vertices, and only 7 are available, so each support
   is 4 or 6. The vertex-colour incidences total `7 × 2 = 14`, and the only multiset of
   4s and 6s summing to 14 is **`{4, 4, 6}`**. Edge counts check: `6 + 6 + 9 = 21 = |K_7|`.
3. A 3-regular graph on 4 vertices is `K_4`. The two `K_4`s are edge-disjoint so share at
   most one vertex, and `4 + 4 - |shared| <= 7` forces them to share **exactly** one. The 9
   remaining edges run between the two leftover triples, i.e. form `K_{3,3}`, which is
   indeed 3-regular on 6 vertices.
4. So some colour class is a `K_4`: **four points pairwise equidistant**. Impossible in the
   plane — with every squared distance equal to 1 the Gram matrix is `(I + J)/2`, whose
   eigenvalues are `2, 1/2, 1/2`, so it has rank 3 and cannot be realised in rank 2.

Hence `f(7) > 2`. The argument assumes nothing beyond "at most 3 points on a circle centred
at a point of the set", so it holds in **both** modes, and step 4 is exactly the argument
that gives `f(4) > 1`. `auditM.py` checks each step, and confirms that the single pattern
the enumerator produced does have precisely this shape: classes `K_4` on `{0,1,2,3}`, `K_4`
on `{3,4,5,6}`, and `K_{3,3}` between `{0,1,2}` and `{4,5,6}`.

### The one pattern the Gröbner decider could not triangulate

At `n=5, m=2` the pattern `[0,0,0,1,2,2,0,2,0,0]` returned "basis not triangular". z3's
`nlsat` (a decision procedure for real closed fields, so its verdicts are proofs) returns
**unsat in both modes**. There is also a one-line proof, which is how the lemma below was
found: in that pattern both vertex 0 and vertex 4 are joined to each of 1, 2, 3 in colour 0,
i.e. two distinct points are equidistant from the same three points. Impossible: if 1, 2, 3
span a triangle its circumcentre is unique, and if they are collinear no point at all is
equidistant from all three.

### L4, and why it survives the weaker hypothesis

That argument is `plemmas.py`'s **L4 (circumcentre): at most one point is equidistant from
any triple.** The collinear branch is what makes it valid under N4 alone, where collinear
triples are legal; #98 could ignore that case. L4 also subsumes #98's L2. By contrast **L3
(bisector)** — at most two points equidistant from a pair — needs no-three-collinear and is
therefore available only in mode `g`. Measured on the `n=5, m=3` set: L3 removes 114 of 378
patterns in mode `g`, and L4 removes 2 more; in mode `n4`, where L3 is unavailable, L4
removes 21.

## 5. What is not settled, and the honest limits

* `n = 7` and `n = 8` are open here, both bracketed as `[3, 4]`. Settling them means
  deciding whether `M = 3` is achievable. A single witness would close both (`f(8) = 3`
  would match the trivial bound exactly); a completed `m=3` enumeration would prove `= 4`.
* Lattice searches found no `M = 3` configuration, but **only these sweeps actually
  completed**, and the `n=7` coverage is much thinner than the `n=8` coverage:

  | n | lattice | squared radius | target | shards complete | found |
  |---|---|---|---|---|---|
  | 5 | `A_2` | 49 | `M < 3` | 1/1 | none |
  | 6 | `A_2` | 49 | `M < 3` | 1/1 | none |
  | 7 | `A_2` | 49 | `M < 4` | 2/2 | none |
  | 7 | `A_2` | 121 | `M < 4` | **0/2 — abandoned** | — |
  | 8 | `A_2` | 49 | `M < 4` | 4/4 | none |
  | 8 | `A_2` | 121 | `M < 4` | 3/3 | none |
  | 8 | `Z^2` | 100 | `M < 4` | 2/2 | none |

  So for `n = 7` the lattice statement is only "nothing in `A_2` within squared radius 49",
  with no `Z^2` sweep at all; the wider `R^2 = 121` run was killed to free cores and its
  shards are incomplete. An earlier version of this file said `A_2` had been swept to 121
  at `n = 7`; that was wrong.

  **In any case this is not evidence of nonexistence.** Every squared distance in these
  lattices is an integer, so no configuration with an irrational distance ratio can appear,
  and the `D_gen(5)` optimum is exactly such a configuration (#98 assumption A12).

* The off-lattice search (`numM.py`) found no `M = 3` configuration either, in 12,600
  restarts across `n=7` and `n=8`. **This is worth nothing as evidence, and the
  control is what shows it.** Run the same search at `n=6`, where an `M=3` configuration is
  known and has been verified in exact coordinates: it finds **zero leads in 512 restarts**.
  A method that cannot find a solution known to exist cannot testify to the absence of one
  that might. An earlier version of this file claimed the negative was evidence for
  `f(7) = 4`; that claim was wrong and is withdrawn.

  The reason is structural rather than a tuning failure. At `m = f(n) + 1` solutions are
  abundant (the `n=7`, `m=4` search produces leads at roughly one per 74 restarts); at
  `m = f(n)` exactly they are isolated, which is precisely what makes the value extremal.
  So this style of search is informative only *above* the answer, never *at* it.

* **A false-lead bug, and what it teaches.** The first version of the acceptance test
  checked the Gauss-Newton residual, coincident points, and (in mode `g`) collinear triples.
  It did not check that the polished class values stayed **distinct**, nor that no four
  points became **concyclic**. Both failures are invisible to the residual, because the
  residual only measures the *equalities*; the inequalities that make the pattern
  `k`-class and the configuration admissible are separate conditions. The bug produced an
  apparent `M=3` configuration at `n=7` in mode `n4` with residual `4.4e-16`, in which
  classes 1 and 2 had collapsed to one value and classes 3 and 4 to another (so the six
  classes were really four), and three quadruples were exactly concyclic. The exact decider
  rejected it. **Both** leads the `n=7` mode-`n4` search produced were degenerate in exactly
  this way: one claimed 6 classes and the other 5, both actually had only **4** distinct
  distances, and both had **5** concyclic quadruples. So `f_N4(7) = 3` is *not* established
  by them. Both checks are now in `numM.py`, and the known `n=6` witness passes them with
  room to spare (smallest concyclicity determinant `6.06` against a threshold of
  `7.3e-07`).

* **Even repaired, the numerical leads are not reliable at `n = 7`.** Of the five `m=4`
  leads that survive the tightened test, the exact decider calls **three unsat**, and z3
  times out on all five at a 120-second cap, so the disagreement is unresolved: it could be
  false unsats from the decider's chain enumeration (the same incompleteness as #98's
  assumption A8, and these patterns carry 6 to 10 classes, far beyond the sizes where that
  decider was validated) or near-solutions that a float residual of `1e-15` cannot
  distinguish from solutions. Nothing in the table above depends on these leads.

* None of this bears on the asymptotic question. The problem page states outright that
  #654 "cannot be resolved with a finite computation".

## 6. Reproducing

```
python pinned.py         # pinned counts of the #98 witnesses, exact
python subsets.py        # upper bounds by deletion, exact
python penum.py crosscheck   # enumerator validated against brute force
python pdecide.py selftest   # decider reproduces four known #98 verdicts
python penum.py 7 2      # the single n=7, m=2 pattern
python pdecide.py 7 2 g  # and its refutation
```

---

## Companion: the total-count version, in `../p98`

Erdős #98 asks for `D_gen(n)`, the minimum **total** number of distinct distances among `n`
points in general position, where this note's `f(n)` is the minimum over sets of the
**maximum over points** of the per-point count. That directory establishes
`D_gen(3..7) = 1, 2, 3, 4, 5` with `D_gen(8)` in `[5, 7]`, and supplies the witnesses used
here as upper bounds, the rank-2 Gram decider (`hard.py`, re-implemented as `pdecide.py`
with no class-ordering assumption), the lattice search and its symmetry reduction
(`latmin2.py`, re-aimed at the pinned objective as `latM.py`), and lemmas L2-L5.

The functions actually imported are vendored here in `common.py`, so this directory runs
standalone; `common.py` names the #98 file each block came from.

**They are different functions.** The `n=8` witness has `D = 7` but `M = 4`; the `n=6`
witness found here has `M = 3` and `D = 7`. A configuration optimised for one is not
optimised for the other, which is why the searches had to be re-aimed rather than reused.
