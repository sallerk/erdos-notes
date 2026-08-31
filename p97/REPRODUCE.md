# Reproducing the #97 results

Every command below was run from a fresh copy of this directory on 2026-08-31, on
Windows 10 with Python 3.12.9, sympy 1.13.1, mpmath 1.3.0 and z3-solver 5.1.0
(`pip install sympy mpmath z3-solver`). The outputs quoted are what it actually
printed. The machine was not idle, so timings are upper bounds.

## Which claim comes from which script

| claim in the note | script |
|---|---|
| every checkable claim, re-derived independently | `audit.py` |
| the Danzer nonagon is convex and every count is exactly 3 | `verify_p97.py` |
| the nonagon satisfies the three relations Erdős prints in [Er87b, p.175] | `audit.py` check 4 |
| the D_m theorem: symbolic reduction plus numeric cross-check | `theorem_alt.py` |
| k = 3 needs n >= 7: the n = 4 and n = 5 brute force | `k3-minimality/verify_prune.py brute N` |
| k = 3 needs n >= 7: the n = 6 pattern classes | `k3-minimality/enum2.py 6` |
| n = 6 independent numerical agreement | `k3-minimality/numsearch.py 6` |
| the prune does not reject a realisable pattern | `k3-minimality/control.py` |
| n = 7 is not settled | `k3-minimality/STATUS_n7_AT_STOP.json` |

## 1. The whole note, independently re-derived

    python audit.py

Shares no code with `theorem_alt.py`, `verify_p97.py` or any search script. Re-derives
the concyclic lemma on exact roots of unity, both algebraic reductions behind the
theorem, the two inequalities the proof of the theorem rests on (779 of them, every
m = 3..40 and every l, both parities), the degenerate m = 3 parabola, the convexity
window, the nonagon (convexity over all 84 orientations and all nine equidistant sets
in exact arithmetic), the correspondence with Erdős's printed relations, the
counting-bound comparison, and the Erdős-Fishburn novelty check. Takes about 25
minutes. Ends:

    ALL CHECKS PASSED

Three checks in it are worth singling out, because they are the ones that would catch a
wrong claim rather than confirm a right one:

    [PASS] the equidistant sets are EXACTLY the three relations Erdos prints in
           [Er87b, p.175]   cyclic order [0, 3, 6, 1, 4, 7, 2, 5, 8]
    [PASS] the counting bound gives n >= 7 at k = 4 (the forum result) but only
           n >= 4 at k = 3, so n >= 7 at k = 3 does not follow from it
    [PASS] and it is NOT in convex position, for any of the 6 unit translations, so
           it does not contradict n_3 >= 7 for convex polygons

The last of those is the novelty check. Erdos and Fishburn (Comput. Geom. 7 (1997),
207-218) determined the least n with every point having 3 others equidistant to be 6,
without any convexity requirement. Had their realiser been in convex position, n_3 >= 7
would be false. Check 7 confirms it has the k = 3 property and is not convex, and
carries its own controls: a regular hexagon handed over in scrambled order must still
be detected as convex, and a hexagon with one vertex pushed to the centre must not.
Those controls matter because the all-triples orientation test is only meaningful once
the points are sorted into cyclic order; without the sort it would report "not convex"
for every set and the check would be vacuous.

The middle check re-derives the bound along the argument actually posted in the thread
(Cauchy-Schwarz on the incidence degrees d(v), using that two distinct circles meet at
most twice). An earlier version of NOTE.md described that argument as a
perpendicular-bisector count. That is a valid proof of the same inequality but it is
not the argument in the thread; the misattribution is corrected in NOTE.md.

## 2. The nonagon, checked by the separate verifier

    python verify_p97.py artifact_danzer9_t0.json

`verify_p97.py` was written before `audit.py` and is independent of it. Prints:

    n=9  convex=True  min multiplicity=3  exact=True
         methods=['is_zero', 'minimal_polynomial', 'minpoly+bound', 'syntactic']
    per-vertex max equidistant counts: [3, 3, 3, 3, 3, 3, 3, 3, 3]
    => satisfies k=3 version: True ;  k=4 version: False
    VERDICT: VERIFIED

## 3. The theorem

    python theorem_alt.py --mmax 60 --bsteps 200

Printed, in 12 seconds:

    symbolic reduction identities (sympy, exact): {'A_identity': True, 'B_identity': True}
    numeric cross-check m=2..60, 199 b-values each:
       maximum equidistant count seen anywhere: 2
       violations of monotonicity or mult>=4:   0

One thing to understand about that "2". The theorem's conclusion is that the
multiplicity is **at most 3**, and the grid here reports 2. Those are consistent:
multiplicity 3 requires the antipodal distance to coincide with one of the mirror-paired
distances, which is one equation in b and so happens only at isolated algebraic values
that a 199-point grid misses. `audit.py` solves that equation exactly and confirms 3 is
attained inside the window, for instance at m = 3, b = sqrt(3) - 1 (which is the same
alternating hexagon that is the extremal near-miss for problem 982). So 3 is a real
ceiling, not a vacuous bound, and the grid is not evidence against it.

## 4. The k = 3 minimality bound

From `k3-minimality/`:

    python verify_prune.py brute 4      # n=4 BRUTE: sat=0 unsat=1 unknown=0 / 1
    python verify_prune.py brute 5      # n=5 BRUTE: sat=0 unsat=1024 unknown=0 / 1024
    python enum2.py 6                   # n=6 NT=10 raw=1,000,000 nodes=4,451 classes=66
    python numsearch.py 6 120           # n=6: 0/66 classes numerically realisable
                                        #      as a STRICTLY CONVEX 6-gon
                                        # (120 restarts is what numsearch_n6.json
                                        #  records; 40 gives the same 0/66 faster)

`verify_prune.py brute` uses no pruning at all, so n = 4 and n = 5 depend on nothing but
the encoding. `numsearch.py` shares no code with the solver path.

Soundness of the n = 6 prune:

    python control.py

Prints, confirming a known-realisable pattern survives the prune:

    Danzer 9-gon, ccw-reordered: min cross = 0.21314352  strictly convex = True
    [Danzer9] obtuse-middle lemma: HOLDS (0 violations)
    [random] convex-quadrilateral diagonal-crossing check on 400 random polygons: 0 violations

and `python verify_prune.py rejected 6 300` samples 300 prune-rejected patterns and hands
them to z3 (recorded result: 298 unsat, 2 timeouts, 0 satisfiable).

## 5. What is NOT settled

`k3-minimality/STATUS_n7_AT_STOP.json` is the n = 7 run at the point it was stopped:
9,539 of 184,424 pattern classes processed, **9,496 decided** (5,489 by a unit Gröbner
ideal, 4,007 unsat), 43 z3-unknown, 171 skipped as over budget, 0 satisfiable. That is
5.15% of the space. n = 7 is open and the note says so.

## Fixed while writing this file

`k3-minimality/control.py` opened `../p97/artifact_danzer9_t0.json`, which is the path in
the author's working tree, not the path in this repo (where `k3-minimality/` sits inside
`p97/`). Following the instructions above produced a `FileNotFoundError`. It now searches
the plausible locations. This is the only script that failed to run from a clean copy.

## Standing limits

`audit.py` verifies the deduction, not the literature. The Erdős 1975 and 1987 passages
were read from the Rényi Institute scans and are quoted in `REFERENCES.md`; the Altman
paper itself and the Fishburn-Reeds paper were not obtained and are marked secondary
there. The n = 6 result depends on z3 returning unsat correctly, and has an independent
numerical cross-check but no second symbolic implementation.
