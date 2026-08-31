# Reproducing the #982 results

Every command below was run from a fresh copy of this directory on 2026-08-31, on
Windows 10 with Python 3.12.9, numpy 2.1.3, scipy 1.15.2, sympy 1.13.1, mpmath 1.3.0
and z3-solver 5.1.0 (`pip install numpy scipy sympy mpmath z3-solver`). The outputs
quoted are what it actually printed. The machine was not idle, so timings are upper
bounds, not benchmarks.

## Which claim comes from which script

| claim in the note | script |
|---|---|
| every checkable claim, re-derived independently | `audit.py` |
| the search machinery is correct before it is trusted | `verify_machinery.py` |
| the encoding admits models, so the search is not vacuous | `control_decide.py` (see the caveat below) |
| the conjecture holds for n <= 5 | `decide2.py 4`, `decide2.py 5` |
| the conjecture holds for n = 6 (316 classes) | `decide.py 6 60000 16` |
| n = 6 without the Altman prune (1834 classes) | `decide.py 6 60000 16 noaltman` |
| the conjecture holds for n = 7 (5354 classes) | `decide.py 7 30000 16` then `retry_unknown.py` |
| the extremal hexagon, exact in Q(sqrt3) | `audit.py` check 3, `nearmiss.py 3 14` |
| the two-ring family stalls at exactly half | `tworing_par.py`, `nearmiss.py` |

## 1. The whole note, independently re-derived

    python audit.py

Shares no code with `patterns.py`, `decide.py` or any search script. Re-derives the
tightness of floor(n/2) for regular polygons, the concyclic multiplicity lemma on exact
roots of unity, the extremal hexagon in exact Q(sqrt3) arithmetic (strict convexity over
all C(6,3) orientations, and the counts 2,3,2,3,2,3), the run records, and the two-ring
sweep. Ends:

    ALL CHECKS PASSED

## 2. Validate the machinery before believing any search

    python verify_machinery.py

Recovers known values using the same code the searches use: the regular n-gon gives
exactly floor(n/2) per vertex for n = 3..40 (exact index arithmetic, then again at 60 dps
via mpmath), the convex-position test accepts convex polygons and rejects interior
points, duplicates and collinear boundary points, Harborth's H_8 comes out with
per-point count 3 and 4 distances in total and is correctly reported as not convex, and
concyclic sets never beat floor(n/2). Ends:

    ALL VERIFIER CHECKS PASSED

## 3. The controls, and the one that fails

    python control_decide.py

**This script exits non-zero, reporting `CONTROLS FAILED: 3`. That is the true current
state and is not a setup error on your part.** What passes and what does not:

* **Control A passes.** It takes explicit convex polygons, puts them through the same
  normalisation, and evaluates every constraint of the encoding on them, in exact
  rational arithmetic for the lattice polygons and exact Q(sqrt5)/Q(sqrt3) arithmetic
  for the regular pentagon and hexagon. No solver search is involved. This is the
  control that rules out the failure mode that matters, namely an encoding that is
  accidentally self-contradictory and therefore unsatisfiable for a trivial reason.
* **Control C passes.** "All pairwise distances equal" is correctly UNSAT for n >= 4.
* **Control B fails on 3 of its 4 cases.** It feeds z3 the colouring induced by a convex
  lattice polygon, which after normalisation has a rational model and so must be SAT.
  The lattice pentagon comes back SAT; the hexagon, heptagon and octagon come back
  `unknown` at the script's 60 s budget. Raising the budget does not rescue it: re-run
  at 900 s per instance, the results were

      lattice hexagon      n=6  -> unknown   900.3s
      lattice pentagon     n=5  -> sat         0.0s
      lattice heptagon     n=7  -> unknown  1033.6s

  so this is a genuine wall at n >= 6, not an unlucky 60-second cutoff. (The heptagon
  overran its own 900 s budget by two minutes; z3 checks the timeout only at certain
  points, so treat the budget as approximate.)
* Control D is informational and expected: z3 returns `unknown` on colourings whose only
  models are irrational.

What Control B's failure does and does not mean. It does **not** undermine the n <= 7
result. z3's nlsat is a complete decision procedure for the existential theory of the
reals, so an UNSAT answer is a proof, and every one of the 316 classes at n = 6 and all
5354 at n = 7 came back UNSAT rather than unknown (the six that initially timed out at
n = 7 were re-run at a larger budget and all resolved to UNSAT, leaving none). What it
does mean is that this pipeline is much better at proving unsatisfiability than at
exhibiting models: had some class been satisfiable, the likely outcome would have been a
timeout rather than a SAT answer. The result is therefore conclusive because everything
resolved to UNSAT, not because the solver was independently shown able to find models at
n >= 6. Treat Control A, not Control B, as the non-vacuity evidence.

## 4. The certification

    python decide2.py 4 60000          # UNSAT
    python decide2.py 5 60000          # UNSAT
    python decide.py 6 60000 16        # 316 patterns, all UNSAT   (~67 s, 16 workers)
    python decide.py 7 30000 16        # 5354 patterns, 5348 UNSAT + 6 timeouts (~465 s)
    python retry_unknown.py 7 2400000 6    # the 6 timeouts, all UNSAT

Independent of Altman (drops the one cited theorem used as a prune, at the cost of 1834
classes instead of 316):

    python decide.py 6 60000 16 noaltman

Encoding-independent re-check (level variables, free scale, reversed vertex labelling):

    python decide_alt.py 6 120000 6

The run records shipped here are `decide_n6.json`, `decide_n6_noaltman.json`,
`decide_n7.json`, `decide2_n4.json`, `decide2_n5.json` and `decide_alt_n6.json`;
`audit.py` check 5 re-reads them and confirms the counts quoted in the note.

## 5. The two-ring family

    python tworing_par.py 3 400 14
    python tworing_rho.py 3 24
    python nearmiss.py 3 14

`tworing_m3_1200.json` is the full sweep to m = 1200 (1198 rows, m = 3..1200 with no
gaps). `audit.py` check 6 confirms `best_max - target` equals 1 in every row, i.e. the
family never reaches the budget, and that `nearmiss_3_14.json` has exactly half the
vertices at budget for every even n from 6 to 28.

## 6. Lattice pools and the numerical search

    python run_batch.py lat      # -> lattice_*.json ; W=<workers> env var
    python run_batch.py ns       # -> nsearch_n*.json

These are exhaustive over their pool only, not over the reals, and the note says so.

## Standing limits

`audit.py` verifies the deduction, not the literature. The Altman attribution is verified
at source (Erdős 1975, p. 100, read from the Rényi scan) but the Altman paper itself was
not obtained; see `REFERENCES.md`, where it is marked accordingly. The n <= 7
certification is a solver result over an exhaustive pattern enumeration and has not been
re-derived by a second independent implementation. `decide_alt.py` is a re-encoding, not
a second implementation, and covers only n = 6.
