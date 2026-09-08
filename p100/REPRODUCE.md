# Reproducing p100

Python 3.13 with numpy, scipy, sympy. Run from this directory.

## Exact, seconds

    python piepmeyer.py     # Piepmeyer's 9 points, two independent derivations, exact
    python verify.py        # audits every claim in NOTE.md against results/

`piepmeyer.py` rebuilds the set from Erdos's verbal description and separately from the
closed-form coordinates, checks the two agree as exact distance multisets, and reports
the four distances, the three gaps and which gap binds. `verify.py` re-reads every
artifact and fails on a missing one.

## The proved values, minutes

    python patterns.py 4 2 200      # all 5 two-distance patterns on 4 points -> 2.0731321850
    python patterns.py 5 2 300      # all 17 on 5 points; exactly one realisable -> phi^2

These are exhaustive over every canonical colouring of the pairs, with every distinct
realisation shape collected per pattern. They are what "PROVED" means in NOTE.md.

## The bracketed values, minutes to an hour each

    python seeded.py 6 3 4          # -> 3.4142135624
    python seeded.py 9 4 4          # CONTROL: must report 4.6639024601 from "Piepmeyer first 9"
    python seeded.py 10 5 4

`seeded.py` starts from structured configurations and polishes each. Read the hit rate
it prints; a run whose n = 9 control does not recover Piepmeyer may not be quoted. The
subset bounds come from

    python -c "..."                 # the block in the session that wrote results/piepmeyer_subsets.json

and are re-derived by `verify.py` from the exact coordinates.

## Two instruments kept for the record, not for use

* `search.py` minimised delta over coordinates with a penalty on the integer class count.
  It cannot work (the penalty is a step function) and reported no 2-distance set on four
  points. Kept because the failure mode is instructive.
* `fewdist.py` is the solver that `seeded.py` uses; run on its own with random starts its
  hit rate is under 1%, which is why `seeded.py` exists.

## What each artifact supports

| claim | artifact |
|---|---|
| delta(4) = 2.0731321850, proved | results/patterns_n4_k2.json |
| delta(5) = phi^2, proved; pentagon unique | results/patterns_n5_k2.json |
| delta(6) <= 2+sqrt2 | results/seeded_n6_k3.json, results/piepmeyer_subsets.json |
| delta(7), delta(8) <= 4.6639 | results/piepmeyer_subsets.json |
| delta(9) <= 4.6639, Piepmeyer exact | results/piepmeyer.json |
| the n = 9 control | results/seeded_n9_k4.json |
