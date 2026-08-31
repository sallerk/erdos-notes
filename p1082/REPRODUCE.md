# Reproducing the #1082 results

Every command below was executed from a fresh copy of this directory on 2026-08-31.
The outputs quoted are what it actually printed.

Requirements: Python 3 with `sympy`. The Phase 2 scripts also want `z3-solver`.
Nothing else.

## Which claim comes from which script

| claim in the note | script |
|---|---|
| every checkable claim, re-derived independently | `audit.py` |
| the search machinery is correct before it is trusted | `verify_machinery.py` |
| g(5) = 12, the extremal set has 18 collinear triples, h(5) = 11 | `phase1.py`, `verify_set1.py` |
| the two Phase 1 extremal classes are the same set up to similarity | `check_two_classes.py` |
| where the first counterexample can live (n = 16, k = 7) | `frontier.py` |
| lattice search of the A2 pool | `phase2_lattice.py`, on `search.py` and `geo.py` |
| the richer non-lattice pool Z[sqrt3] x Z[sqrt3] | `phase2_z3.py`, `cyclo.py`, `z3_decisive.py` |
| concentric regular polygons (numeric screen) | `concentric.py` |
| the regular odd polygons are rigid, so the 15-gon admits no 16th point | `extend.py`, with `extend_control.py` as the positive control |

## 1. The mathematics, independently re-derived

    python audit.py

Re-derives the Eisenstein 12-point set (squared distances 1, 3, 4, 7, 9 and exactly 18
collinear triples), checks the regular (2k+1)-gons for k = 1..7 have exactly k
distances and no collinear triple, checks the g-table and that k = 5 is the only case
below 7 needing the uniqueness argument, checks that n <= 15 is exactly the reach of
the argument, and checks the n = 16 frontier. Shares no code with the search. Ends:

    ALL CHECKS PASSED

## 2. Validate the machinery before believing any search

    python verify_machinery.py

Recovers published values with the same code the searches use. Ends:

    [PASS] g(5) = 12 attained by a lattice set (got 12)
    [PASS] g(6) = 13 attained by a lattice set (got 13)
    ======================================================================
    PASSED 15   FAILED 0

## 3. Phase 1, the decisive case k = 5

    python phase1.py

Printed:

    PHASE 1 VERDICT: every 12-point 5-distance set in the pool contains three collinear points
      max no-3-collinear 5-distance subset of the pool: 9 points
      distances [1, 7, 12, 13, 19], collinear triples 0
      need >= 12 for a counterexample; 2k+1 = 11 is the conjectured max

`verify_set1.py` gives three further independent checks of the same conclusion.

## 4. The frontier

    python frontier.py

Prints, for each n, the number of distinct distances a concyclic set forces from a
single point against floor(n/2), which is where n = 16 with k = 7 comes from.

## 5. Rigidity of the regular odd polygons

    python extend.py

For every regular m-gon with m odd up to 41 it counts points lying at a polygon
distance from all m vertices. The row that matters for n = 16:

       m   k  |D|  extensions  general position
      15   7    7           0                 0

Zero everywhere, so the regular 15-gon admits no 16th point. `extend_control.py` is
the positive control: it demonstrates the finder can locate an extension when one
exists, so the zeros are not a silent failure.

## 6. The lattice and non-lattice pools

    python phase2_lattice.py A2       # triangular lattice
    python phase2_z3.py               # the Z[sqrt3] x Z[sqrt3] pool
    python concentric.py              # concentric regular polygons, numeric screen

These are the slow ones; see `RESULTS.md` sections 6a to 6c for the recorded outputs
and pool sizes.

## What is NOT reproducible here, and was therefore removed

An earlier version of the note reported an enumeration of subsets of regular m-gons
for m <= 24 with specific counts. No script in this directory produces those numbers,
and they do not appear in `RESULTS.md`. Rather than ship a claim whose code is absent,
the claim was cut. The rigidity result from `extend.py` covers the same ground for the
case that matters and is reproducible.

## Standing limits

`audit.py` verifies the deduction, not its inputs. The result rests on g(5) = 12 with
uniqueness (Shinohara), g(6) = 13 (Wei) and Altman 1963, none of which I have read at
source; see `REFERENCES.md`, where each is marked accordingly.
