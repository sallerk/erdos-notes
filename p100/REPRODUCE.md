# Reproducing p100

Python 3.13 with numpy, scipy, sympy, mpmath. Run from this directory. Every script writes
its artifact under `results/`; `verify.py` reads them all back and fails on a missing one.

## Exact, seconds to minutes

    python piepmeyer.py       # Piepmeyer's 9 points, two independent derivations, exact
    python pexact.py 4 2      # all 5 two-distance patterns on 4 points, Groebner-decided
    python pexact.py 5 2      # 17 patterns; 16 proved unrealisable; the pentagon
    python pexact.py 5 3      # 124 patterns; 104 unrealisable; E_5(<=3), ~3 min
    python ext3.py 5 3        # E_6(<=3): nine sets, all certified -> delta(6) = 2+sqrt2
    python ext3.py 6 3        # E_7(<=3) CONTROL: heptagon and hexagon+centre only
    python ext3.py 7 3        # E_8(<=3) CONTROL: empty (g(3) = 7)
    python ext2.py piepmeyer 10   # every 10th point added to Piepmeyer: best 9.903
    python ext2.py nonagon 10     # CONTROL: finds nonagon + centre, 8.2909
    python ext2.py r9plus 12      # no 11th point with delta <= 12
    python lat.py 12 5 100    # CONTROL: the 12-point 5-distance set is unique
    python lat.py 13 6 100    # CONTROL: one 13-point 6-distance lattice set
    python lat.py 10 5 100    # fifteen lattice sets (Wei's figure shows sixteen)
    python lat.py 11 5 100    # the n = 11 witness, delta = 6+3sqrt3
    python lat.py 9 4 100     # the two lattice 9-point 4-distance sets
    python lat.py 7 4 100; python lat.py 8 4 100
    python polygons.py        # delta for R_n, R_n+centre, R_n-vertex, n <= 14
    python e9.py              # the four 9-point 4-distance sets (Erdos-Fishburn) -> delta(9)
    python chain4.py          # E_5(<=3) -> 6 -> 7 points with <= 4 distances; finds Lan-Wei's 741, 742
    python e78.py             # the 42 seven-point and 15 eight-point 4-distance sets -> delta(7), delta(8), ~2 min
    python verify.py          # audits every claim in NOTE.md against results/
    python AUDIT_RECHECK.py   # 56 checks, importing nothing from this directory, ~40 s
    python AUDIT_EXTRA.py     # the pentagon sweep and the duplicate-solution check, ~3 min

Run them in the order above: `e78.py` uses `results/chain4.json` to build the two 7-point
sets that Lan and Wei give only by their distance ratios, and `verify.py` requires all 42
to be explicit.

A note on tolerances. `ext2.py`, `ext3.py` and `chain4.py` work at 60 digits and treat two
distances within 1e-45 as equal; `e78.py` works at 50 digits with 1e-35; `e9.py` groups at
80 digits and then verifies each group exactly. In the extension scripts the tolerance
only steers the search, since every set that survives is re-decided exactly by a Groebner
basis on its own pattern. In `e78.py` it decides how many distances a constructed set has,
on sets whose values are separated by a factor of at least 1.05. AUDIT_CODE.md says more.

`pexact.py` is the authority on what is PROVED: a pattern is unrealisable when its
saturated ideal has Groebner basis [1], and a feasible pattern's solution list is
certified complete when its length equals the quotient-ring dimension. `ext3.py`'s
completeness argument is in its docstring; every set it keeps is re-decided exactly.

## Numerical witness finders, minutes to an hour

    python patterns.py 4 2 200      # numerical realisation of the same patterns (6 shapes)
    python patterns.py 5 2 300
    python seeded.py 6 3 4          # -> 3.4142135624
    python seeded.py 9 4 4          # CONTROL: must report 4.6639024601 from "Piepmeyer first 9"
    python seeded.py 10 5 4         # -> 8.2908593694 (nonagon + centre)
    python seeded.py 11 5 4         # -> 12.3435375197 (regular 11-gon); lat.py does better

`seeded.py` prints its hit rate; a run whose n = 9 control does not recover Piepmeyer may
not be quoted. The subset bounds in `results/piepmeyer_subsets.json` are re-derived by
`verify.py` from the exact coordinates.

## Kept for the record, not for use

* `search.py` minimised delta with a penalty on the integer class count. It cannot work
  (the penalty is a step function) and reported no 2-distance set on four points.
* `fewdist.py` is the solver `seeded.py` uses; on random starts its hit rate is under 1%.
* `ext1.py` is the first extension search (at most one new value); `ext2.py` supersedes it.

## What each artifact supports

| claim | artifact |
|---|---|
| delta(4) = 2.0731321850, proved; the six 2-distance sets | results/pexact_n4_k2.json |
| delta(5) = phi^2, proved; pentagon unique | results/pexact_n5_k2.json |
| E_5(<=3), complete and exact | results/pexact_n5_k3.json |
| delta(6) = 2+sqrt2, proved; the nine 6-point 3-distance sets | results/e6_k3.json |
| E_7(3) = {R_7, R_6+centre}; E_8(3) empty | results/e7_k3.json, results/e8_k3.json |
| delta(9) = 4.6639, proved; three-triangle set = Piepmeyer | results/e9_k4.json |
| delta(7) = delta(8) = 4.6639, proved | results/e78_k4.json, results/lat_n7_k4.json, results/lat_n8_k4.json |
| delta(7), delta(8), delta(9) <= 4.6639 (the witnesses) | results/piepmeyer_subsets.json, results/piepmeyer.json |
| no 10th point on Piepmeyer beats 8.2909 | results/ext2_piepmeyer.json |
| delta(10) <= 8.2909 | results/seeded_n10_k5.json, results/polygons.json |
| delta(11), delta(12) <= 6+3sqrt3; delta(13) <= 6+4sqrt3 | results/lat_n11_k5.json, lat_n12_k5.json, lat_n13_k6.json |
| lattice controls (12-point unique, 13-point unique) | results/lat_n12_k5.json, results/lat_n13_k6.json |
| the n = 9 seeded control | results/seeded_n9_k4.json |
