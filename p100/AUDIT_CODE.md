# Audit of the code of p100

## Summary

No bug was found that changes a result. The exact machinery is sound: the polynomial
system in `pexact.py` really does encode "all points distinct", the completeness
certificate it prints really does certify completeness, and the stored solution lists
contain no duplicates (which is the one way that certificate could have been fooled).

Two things are weaker than they look and are now written down: the similarity reduction
in `lat.py` is not complete, and several scripts decide "these two distances are equal"
with a fixed numerical tolerance. Neither affects a published number, and both now have
an independent check behind them. `AUDIT_RECHECK.py` re-derives 56 claims without
importing anything from the directory; `AUDIT_EXTRA.py` answers the two questions it
could not.

## Findings

**1. OK. The Groebner setup in `pexact.py` is correct.** The gauge puts the first point
at the origin and the second at (1,0), which fixes translation, rotation, reflection and
scale, and forces the distance class containing that pair to the value 1. Every other
class gets its own variable for the squared distance. The extra equation
`t * (product of the other class values) = 1` has a solution exactly when none of those
values is zero. Since every pair's squared distance is one of the class values, that is
exactly the condition that no two points coincide. A reduced basis equal to [1] therefore
proves that no configuration of distinct points realises the pattern, over the complex
numbers and so also over the reals.

**2. OK. The completeness certificate is sound, and it could not have been fooled.** For
a zero-dimensional ideal, the number of standard monomials (monomials not divisible by
any leading monomial of the reduced basis) equals the number of solutions over the
algebraic closure counted with multiplicity. `pexact.py` compares that number with the
number of solutions sympy returned, and calls the list complete when they agree. That
argument fails if sympy ever returns the same solution twice, because the count would be
inflated while a genuine root was missing. `AUDIT_EXTRA.py` re-reads all 104 stored
solutions across the three artifacts and finds no repeated solution anywhere, and finds
that the stored solutions account for exactly the number of real solutions each pattern
reports. Every feasible pattern in all three files is zero-dimensional and certified.

**3. COULD BE BETTER. The similarity reduction in `lat.py` is not complete.** Two subsets
of the triangular lattice are similar when one is obtained from the other by z -> az + b
or z -> a conj(z) + b with a a nonzero Eisenstein integer. `lat.py` reduces only by the
fixed scalings of norm 4, 3, 25, 7 and 13 (dividing coordinates by 2 or 5, and the
index-3, index-7 and index-13 sublattice maps), so a set living inside a sublattice of
norm 19, 31, 37 or 43 would be reported as a separate class from its image. That would
inflate a count, never change a delta.

`AUDIT_RECHECK.py` therefore re-enumerates the same seven cases in the Eisenstein
integers, where the gcd of the differences can be divided out (the ring is Euclidean),
leaving only the six units and conjugation. That reduction is complete. It returns the
same counts: 20, 8, 2, 15, 3, 1 and 1 for (n,k) = (7,4), (8,4), (9,4), (10,5), (11,5),
(12,5) and (13,6), with every class having the delta the note claims. So no over-counting
happened, and the counts that were compared with the published classifications stand.

**4. SILENT TOLERANCE, now disclosed. Several scripts decide equality of distances
numerically.** `ext2.py`, `ext3.py` and `chain4.py` work at 60 digits and treat distances
within 1e-45 as equal; `e78.py` works at 50 digits with 1e-35; `e9.py` groups at 80
digits and then checks each group exactly. The consequences differ:

* In `ext3.py` and `chain4.py` the tolerance only steers the search, because every set
  that survives is re-decided exactly by a Groebner basis on its own pattern. A tolerance
  error there could only lose a set, not invent one, and the results match the published
  classifications.
* In `e78.py` the tolerance decides how many distinct distances a constructed set has.
  The sets involved have well-separated values (the smallest ratio between two distinct
  distances in any of them is above 1.05), so 1e-35 is not close to deciding anything,
  but the check is numerical and REPRODUCE.md now says so.
* `pexact.py` calls a solution real when its imaginary part is below 1e-50 at 60 digits.
  A root with a genuinely tiny imaginary part would be misread as real and would add a
  spurious shape. None appeared: the shape counts reproduce Shinohara's 34 five-point and
  the nine six-point and two seven-point 3-distance sets exactly.

**5. COULD BE BETTER. `e78.py` deduplicates most families by distance multiset.** Two
non-congruent sets with the same multiset (homometric sets) would be merged and the
family count would come out one short. The lattice families avoid this because they are
keyed by `lat.py`'s canonical form instead, and that is where the one homometric pair in
this data actually lives (among the twenty lattice 7-point sets). Every family count
matches the paper it is compared with, so no merge occurred, but the keying is not
uniform and a future case could hide one.

**6. COULD BE BETTER. The circle pairing uses object identity.** In `ext2.py` and
`ext3.py` the loop over pairs of circles skips a pair when `A is B`, relying on the
centre tuples being the same objects because they come from the same list. It works and
is fast, but it would silently start comparing coordinates if the list were ever rebuilt.

**7. OK. `verify.py` re-derives rather than trusting flags.** It rebuilds the witnesses,
recomputes the deltas from stored coordinates, checks the counts against the published
theorems, and fails on a missing artifact. It passes 65 checks. Two of its assertions are
about the wording of NOTE.md rather than the mathematics, which is deliberate: they are
there so that a claim cannot be quietly strengthened in prose without the audit noticing.

**8. OK. Kept-for-the-record code is labelled.** `search.py` (the failed penalty-based
search) and `ext1.py` (superseded by `ext2.py`) are both documented as such in their
docstrings and in REPRODUCE.md.

**9. Fresh-checkout ordering matters and is now correct in REPRODUCE.md.** `e78.py` reads
`results/chain4.json` if it exists, and uses it to build the two 7-point sets that Lan and
Wei give only by their distance ratios; without it those two sets are carried as ratios
only. `verify.py` requires all 42 to be explicit, so `chain4.py` must run before `e78.py`,
which must run before `verify.py`. That is the order REPRODUCE.md lists.

## Bugs found in the audit scripts themselves

Recorded because they are the reason to trust the checks that passed. The first run of
`AUDIT_RECHECK.py` reported three failures, and all three were mine:

* one of the six 4-point 2-distance witnesses was built as a parallelogram and had three
  distances, not two; the correct pair of witnesses (four short pairs and two short pairs)
  is now derived in the file from the two possible short-edge graphs;
* two expected constants for the regular octagon had been typed with truncated digits and
  are now computed from the closed form 2/(2 - sqrt(2+sqrt2));
* the list of units of the Eisenstein integers was wrong (it contained elements of norm
  3), which the file's own assertion caught.

A fourth was a performance bug rather than a correctness one: the first version of the
pentagon sweep ran at 40 digits over 1.6 million grid cells and had to be killed, then
rewritten with floats and checked in exact arithmetic only at the candidates it found.

## Runtime

`AUDIT_RECHECK.py` takes about 40 seconds, most of it the lattice enumeration at
(13,6). `AUDIT_EXTRA.py` takes about 3 minutes, almost all of it the sweep. Both exit
non-zero on any failure.
