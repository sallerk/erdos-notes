# Reproducing p831

Python 3.13, numpy, scipy, sympy, z3. No compiled dependency. Run from this directory.

## Fast, exact, no search (seconds)

    python lemmas.py        # Lemmas 1-4 in exact rational arithmetic
    python lemma6.py        # Lemma 6 symbolically in the four circle centres
    python verify.py        # audits every claim in NOTE.md against results/

`verify.py` reads the witnesses back out of `results/` and re-derives them from the
definitions in sympy, sharing no code with the searches. It exits non-zero on any
failure and prints the bound table.

## Pattern enumeration (seconds)

    python penum.py 5 1     # 0 patterns  -> h(5) >= 2 with no external input
    python penum.py 5 2     # 1 pattern, class size 5 > f(5)=4 -> h(5) >= 3
    python penum.py 5 3     # 15 patterns, 12 of them also within f(5)=4

## Upper bounds by search (minutes)

    python lath.py 4 6 6 4          # positive control: must return h = 1
    python lath.py 5 11 11 5        # returns 4
    python beam.py 8 13 13 30000    # beam over a 13x13 grid, n up to 8

`lath.py` is an exhaustive DFS over subsets of the integer grid with an admissibility
test and a monotone prune on the running radius count; `beam.py` is a heuristic. Both
use exact integer arithmetic, so any configuration they report is genuinely admissible
and its radius count is exact. Neither proves anything about h(n): a lattice is a
restriction, and a beam is not a search.

## The n = 5 case analysis (minutes to hours)

    python ctrlA.py         # control: 4 equations in 4 unknowns ARE solvable, 5 are not
    python caseA.py 150 2   # orthocentric size-4 class: best residual 7e-8
    python orthobranch.py   # the orthocentric branch of (4,4,2): 0 admissible solutions
    python obstruction433.py# the residual floor as a function of the degeneracy margin
    python typeIII.py 10 10 # sweep of the common-point family
    python pscreen.py 5 3 500 99      # all 15 patterns, with a positive control
    python pdecide.py 5 3 1800000     # z3 nlsat, 30 minutes per pattern

Run `ctrlA.py` and read the control line of `pscreen.py` before believing any negative
from this directory. A search that cannot find a known solution cannot report an
absence.

## What was actually run for the numbers in NOTE.md

| claim | produced by | artifact |
|---|---|---|
| h(4) = 1 | lath.py 4 6 6 4, re-verified in sympy | results/lath_n4_6x6.json |
| h(5) <= 4 | lath.py 5 11 11 5 | results/lath_n5_11x11.json |
| h(6) <= 6 | lath.py 6 11 11 7, exhaustive over that grid | results/lath_n6_11x11.json |
| bound table | verify.py, from A003829 | printed |
| 15 patterns | penum.py 5 3 | results/penum_n5_k3.json |
| Case A negative | caseA.py, with ctrlA.py as control | results/caseA_n5.json, results/ctrlA.json |
| s^2 obstruction | obstruction433.py | results/obstruction433.json |
| parallelogram branch empty | orthobranch.py | results/orthobranch.json |

Screens that were still running when this was written are marked as such in NOTE.md
and are not claims.

## The harder control (added during the audit)

    python ctrlB.py

Builds an admissible configuration whose pattern has four classes and whose six
constraint equations have Jacobian rank five, then checks that `pscreen`'s optimiser
recovers it. Writes results/ctrlB.json. This is the control that matters; the one
printed by `pscreen.py` itself is exactly determined and therefore too easy.

## Corrections after the audit of 2026-09-07

Read `AUDIT_SUMMARY.md` first. The following supersede entries above.

* **`ctrlA.py` and `caseA.py` are superseded by `caseA2.py`.** The old control
  normalised by the mean of all six radii while constraining only some, and dropped
  equations in an order that violates Lemma 1; the old search had no degeneracy guards
  at all. Run `python caseA2.py 300` instead. Its artifact is `results/caseA2.json`.
* **`pscreen.py`'s headline is superseded, and so is `tausweep.py`'s.** The screen's
  margin is a parameter now, but sweeping one margin while holding the others fixed just
  relocates the problem: the class-separation guard turned out to be active at almost
  every optimum of the sweep. Do not read TRACKS-TAU or FLAT-IN-TAU as an obstruction.
  **The decisive test is `python r2check.py`**, which drops every guard, finds the exact
  roots of the equalities, and shows that all of them, for all fifteen patterns, put four
  points on a circle. That is the evidence; the sweeps are a record of how floors move.
* **`orthobranch.py` is vacuous** and is retained only as a record. Do not cite it.
* **`gridsweep433.py`** supplies the global grid sweep that NOTE.md previously asserted
  without an artifact. Run `python gridsweep433.py 140`.
* **`enc_test.py`** now writes `results/enc_test.json`.
* **Artifact names carry the search target**: `lath_n5_17x17_t4.json`, not
  `lath_n5_17x17.json`. Two runs at different targets are different experiments and the
  old naming let one silently overwrite the other.
* **The 17x17 run** missing from the table above is `python lath.py 5 17 17 4`, and it is
  the command behind the headline exhaustive statement in NOTE section 4.
* `results/typeIII_n5.json` is a PARTIAL run (3 of 10 splits). The complete treatment of
  that branch is `gridsweep433.py` plus `obstruction433.py`.

## The clean run (2026-09-07, after remediation)

    python lemmas.py        # ALL CHECKS PASSED   (Lemmas 1, 2, 3, 4, 4a, exact)
    python lemma6.py        # ALL CHECKS PASSED   (Lemma 6, symbolic)
    python AUDIT_SELF.py    # 0 defects
    python verify.py        # ALL CHECKS PASSED

`verify.py` now re-derives every recorded witness from the definitions rather than
reading a flag, excludes checkpoint files, and enforces that the write-up discloses the
weaknesses the audit found rather than that those weaknesses are absent. Where a
limitation cannot be removed, the check asserts that NOTE.md states it.
