# Reproducing the #98 / D_gen results

`D_gen(n)` is the minimum number of distinct distances among `n` points in the plane with
**no three collinear** and **no four cocircular**. The problem page (Erdős #98) writes it
`h(n)`; Sheffer's survey writes `D_gen(n)`.

**Claimed:** `D_gen(3..7) = 1, 2, 3, 4, 5`.

## Requirements

Python 3 with `sympy`, `z3-solver`, `mpmath`, and (only for the heuristic search)
`numpy` and `scipy`.

```
pip install sympy z3-solver mpmath numpy scipy
```

No compiler, no external tool, no lattice or floating-point step is load-bearing for any
claim. Everything decisive is exact arithmetic.

## READ THIS BEFORE RUNNING THE CHAIN: it no longer reproduces its own intermediates

Two things were found by re-running every command in this file from a clone.

**(a) Four steps have no input as written.** The chain names files that no script in this
directory produces: `sweep_n5_k3_robust.json` (read by `six2.py`), `seeds_n5_k4.json` and
`seeds_n5_k4_lemmaonly.json` (read by `aug.py`), `cand_n7_k4_real.json` and
`cand_n7_stubborn.json` (read by `z3run.py` and `equilateral.py`). They were produced by
intermediate hand steps that were not recorded. All of them are archived in `results/`, so
the chain runs if you stage them first, as described below, but it does not run end to end
from a bare clone.

**(b) `aug.py` has since been strengthened, so its output no longer matches the archive.**
`aug.py` now filters with all five lemmas (`lemmas.survives`), where the archived
intermediates were generated with L1+L2 only. Re-running the documented commands today
gives **1,066** candidates at `n=6, k=4` instead of the archived 2,254, and **1** at
`n=7, k=4` instead of 28. Nothing here is unsound: the new filter is strictly stronger, and
the new output was checked to be a subset of the old. But the archived artifacts and the
current code are from different filter generations, and the note's cut-rate figures in
section 3j are the L1+L2 numbers. Restricting the filter to `l1_degree and l2_k23`
reproduces 2,254 and 28 exactly, set-for-set.

`python audit98.py` is unaffected by all of this: it reads no artifact and re-derives its
checks from scratch, which is why it is the command to run first.

## Where the artifacts live, and how to re-run a step that consumes one

Every JSON this directory produced is archived under `results/`. **The scripts read and
write bare filenames in the current working directory**, not in `results/`, so a command
like

```
python aug.py 5 4 seeds_n5_k4.json cand_n6_k4.json
```

will only find its input if that file is in the working directory. To re-run a middle step
of the chain without regenerating everything before it, copy the input up first:

```
cp results/seeds_n5_k4.json .
python aug.py 5 4 seeds_n5_k4.json cand_n6_k4.json
```

`python audit98.py` needs none of this: it re-derives everything from scratch and reads no
artifact at all, which is why it is the command to run first.

`python lemmas.py` takes well over five minutes: its soundness check over the 104
known-realisable patterns is quick, but the measured-cut-rate table after it enumerates
patterns exhaustively.

Two intermediates are **not** archived because they are large and regenerable:
`cand_n6_k5.json` (23 MB) and `cand_n6_k4_lemmaonly.json` (2.7 MB).


## The one command that checks everything

```
python audit98.py
```

Runs in a couple of minutes and re-derives every claim from scratch in exact arithmetic,
sharing no code with the searches that originally produced them. It verifies:

* all five witnesses, in real plane coordinates: distinct-distance count, no collinear
  triple, no cocircular quadruple;
* monotonicity, by deleting each point of each witness in turn;
* the pigeonhole bound and why combining it with the collinearity bound is vacuous;
* `D_gen(4) > 1` from scratch;
* the pentagon eliminant `t^2 - 3t + 1` for `D_gen(5) > 2`;
* the heptagon identification for `D_gen(6) > 3`;
* the equilateral-centre lemma, its corollary, and the trivial ideal that kills the last
  `n = 7` candidate;
* that the values are the best known lower bound for `4 <= n <= 13`.

It prints `ALL CHECKS PASSED` and exits non-zero on any failure.

## Reproducing each result individually

**Witnesses (upper bounds).** A configuration certifies an upper bound wherever it came
from, so these are re-checked rather than re-found:

```
python verify.py
```

re-derives every witness in real plane coordinates with sympy, sharing no code with the
searchers. To re-find them:

```
python latmin.py 4 13 a2          # D_gen(4) <= 2
python latmin.py 6 49 a2          # D_gen(6) <= 4
python latmin.py 7 49 a2          # D_gen(7) <= 5
python witness.py 5 3             # D_gen(5) <= 3, the Q(sqrt3) witness
```

**`D_gen(5) > 2`.** Two independent routes:

```
python sweep2.py 5 2 60 6         # every pattern decided by the Gram method
python pentagon.py                # the pentagon pattern by exact elimination
```

`pentagon.py` is the load-bearing one: the eliminant is `t^2 - 3t + 1`, and all four real
branches are cocircular.

**`D_gen(6) > 3`.**

```
python sweep2.py 5 3 150 6        # decide the 5-point patterns
python six2.py 6 300              # augment to 6 points and decide
python six_pattern4.py            # the heptagon candidate, in full
```

`six2.py` trusts nothing to `gram.py` (see the caveat below). It leaves three candidates:
one uses only 2 classes and dies to monotonicity, one has class 0 equal to K(3,3) and
dies because two equal-radius circles cannot share three points, one is decided directly.

**`D_gen(7) > 4`.** The chain, in order:

```
python xcheck.py 5 4 60 6                                  # n=5 verdicts, cross-checked
python aug.py 5 4 seeds_n5_k4.json cand_n6_k4.json         # augment to n=6
python dec.py 6 4 cand_n6_k4.json dec_n6_k4.json 90 6      # decide them
python rerun_err.py 6 4 dec_n6_k4.json seeds_n6_k4_clean.json 240 3
python aug.py 6 4 seeds_n6_k4_clean.json cand_n7_k4.json   # augment to n=7  -> 28
python z3run.py 7 4 cand_n7_k4_real.json z3_n7_k4.json 900 3
python equilateral.py cand_n7_stubborn.json                # kills 2
python last7.py                                            # kills the last one
```

`last7.py` is self-contained and needs none of the preceding steps: it takes the final
pattern as a literal and shows its Gram minors include multiples of `(2u - 11)` and
`(u - 10)`, which cannot both vanish. The lex Groebner basis is `[1]`.

## Caveats you should know before trusting anything

**`gram.py` is unsound for negative verdicts and must not be used for lower bounds.** It
calls `sympy.solve` and reports `unsat` when nothing usable comes back, but `sympy.solve`
can silently omit branches. Cross-checking found **17 patterns at n=5, k=4** it called
impossible that are in fact realisable. Use `hard.py` or `pz3_noorder.py` (Groebner plus guaranteed-real
`CRootOf` roots) instead. **Not `z3run.py`:** its class-ordering constraint makes its unsat verdicts non-proofs (see ASSUMPTIONS.md A8). `gram.py` is kept only because `xcheck.py`
documents the discrepancy.

**`hard.py`'s unsat verdicts are validated only partially.** An early 40-pattern sample of
its `n=5, k=4` unsats was re-decided by z3: **22 unsat, 18 unknown, 0 sat**. **That figure
is superseded.** All 153 A8-dependent rejections have since been examined, of which **57
are independently settled and 96 are not** (ASSUMPTIONS.md A8). Note also that the
40-pattern sample used `z3run.py`'s ordered encoding, so most of its 22 "unsat" verdicts
are not proofs either; only verdicts from a trivial Groebner ideal or from
`pz3_noorder.py` count.

**Heuristic searches prove nothing.** `numsearch.py` finds candidate configurations by
optimisation; anything it produces is re-derived exactly before it counts. Its controls
(`n=5,k=3` must be found, `n=6,k=3` must not) both pass, but a negative from it is
evidence of difficulty, not a proof.

**Lattice searches under-estimate.** `latmin.py` and `maxpts.py` search a lattice pool, so
they give valid upper bounds on `D_gen` (a configuration is a certificate) but only lower
bounds on the inverse function. The true `D_gen(5) = 3` witness is not lattice-realisable,
which is why `maxpts.py 3` returns 4 rather than 5.

## What is NOT claimed

Nothing here bears on whether `D_gen(n)/n -> infinity`, which is what Erdős #98 actually
asks. The values are the finite end of an asymptotic problem. `NOTE.md` sections 2,
2a and 2b explain why the elementary route to the constant is exhausted, including a
measurement suggesting the isosceles bound is close to tight.

`D_gen(8)` is open here: `>= 5` by monotonicity and `<= 7` from a witness that is verified
in exact coordinates (`results/witness_n8.json`; `verify.py` checks it). Nothing excludes 5,
and no 6-distance witness was found. An earlier version of this line said "with no witness
found", which contradicted the directory's own artifact.
