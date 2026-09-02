# Every assumption behind the #98 results, and how each is discharged

Written for the full audit. Each item is either **PROVED** (an argument given here),
**VERIFIED** (checked mechanically, script named), **CITED** (rests on a source, quoted
in `REFERENCES.md`), or **UNRESOLVED** (a real gap, stated as such).

Nothing below is assumed because "we already did that". Every mechanical item is
re-derived by `audit98.py`, which shares no code with the searches that produced the
results.

---

## A1. The object is the right one

`h(n)` on the problem page is "such that any `n` points ... determine at least `h(n)`
distinct distances", and [Er83c] p.54 defines it as the **largest** such integer. The
largest lower bound valid for every configuration is the **minimum over configurations**,
so `h(n) = D_gen(n)` as computed here.
**Status: VERIFIED** against the live page (fetched 2026-09-01) and CITED to [Er83c].
This is the check that catches "solving the wrong problem"; it was done first.

## A2. General position means exactly two conditions

No three collinear, no four cocircular. Both appear verbatim on the page. No further
conditions (convexity, distinctness of coordinates, etc.) are imposed anywhere.
**Status: VERIFIED** against the page text.

## A3. Monotonicity: `D_gen` is non-decreasing

Deleting a point from a general-position set leaves a general-position set (both
conditions are inherited by subsets) and cannot increase the number of distinct
distances. So an exact value at `m` lower-bounds every `n >= m`.
**Status: PROVED**, and spot-VERIFIED by `audit98.py` deleting each point of each witness
in turn and confirming general position and no increase in distance count.

## A4. At most three points equidistant from a given point

Four would lie on a circle centred there, i.e. four cocircular points.
**Status: PROVED**; VERIFIED on every witness (`audit98.py` reports max multiplicity 3).

## A5. At most two points on any perpendicular bisector

The bisector is a line and no three points are collinear.
**Status: PROVED.** This is the basis of lemma L3.

## A6. The witnesses are genuine

Each is checked in **real plane coordinates** with exact arithmetic: the distinct-distance
count, zero collinear triples, zero cocircular quadruples. The lattice witnesses are
converted from `(a,b)` to `(a + b/2, b*sqrt(3)/2)` first, so the check does not happen in
the integer embedding the search used.
**Status: VERIFIED** by `audit98.py` and `verify.py` independently.

## A7. z3's verdicts are sound

z3's `nlsat` is a decision procedure for real closed fields, so both `sat` and `unsat`
are proofs; only `unknown` is uninformative. Used for 4 of the 7 surviving n=7 candidates.
**Status: CITED** (standard property of the algorithm).

## A8. `hard.py`'s unsat verdicts are sound; THE WEAKEST LINK

`hard.py` reports unsat when the Groebner basis is trivial (sound), or when its triangular
chain finds no admissible real branch (sound only if the chain enumeration is complete).
Its predecessor `gram.py` was caught emitting FALSE unsats, so this was tested rather than
assumed. All **153** n=5,k=4 patterns `hard.py` called unsat were re-decided.

**A DESIGN FAULT IN THE CHECK ITSELF, found while working on #654.** `z3run.py` adds
`d_0 < d_1 < ... < d_{k-1}` to its encoding. But the patterns it is fed are CANONICAL
forms, whose classes are numbered by ORDER OF FIRST APPEARANCE along the edge list, which
has nothing to do with the magnitudes of the distances. Canonicalisation quotients by
colour renaming, so each orbit is represented once; testing that one representative with
the values forced into index order asks "is this pattern realisable with its class values
in this particular order", not "is it realisable". A pattern realisable only with its
values in some other order would be reported unsat. **So z3run.py's unsat verdicts are not
proofs**, and the "81 of 153" figure this file previously carried was wrong.

**Re-tested without any ordering** (`pz3_noorder.py`, which requires the classes to be
pairwise distinct but imposes no order, and enforces its per-pattern cap by killing a child
process rather than trusting z3's advisory `timeout`). All 70 patterns that z3run.py had
called unsat, re-decided at a 90-second hard cap:

    46 unsat      24 timeout      0 sat        (results/ordercheck_out.json)

**No false unsat was exhibited.** The fault is real but has not been shown to bite. The
corrected tally for the 153:

| method | settled | sound? |
|---|---|---|
| lex Groebner basis `= [1]` (`gap_trivial.json`) | 11 | yes, no solution even over C |
| z3 unsat with NO ordering constraint (`ordercheck_out.json`) | 46 | yes, nlsat decides RCF |
| **independently settled** | **57** | |
| **still resting on A8** | **96** | 24 that time out unordered, plus the 72 z3 never decided |

**Status: PARTIALLY VERIFIED (57/153).** Weaker than previously claimed. See A13 for what
this does and does not touch: the disposal of the 28 surviving n=7 candidates is
solver-free, but their GENERATION came from seed sets pruned with `hard.py` verdicts, so a
single false unsat among the 96 could mean a 29th candidate was never generated.

*A second caveat on the original runs.* z3's `timeout` is advisory: the residual run burned
87,797 CPU-seconds on 75 patterns against a design ceiling of 75 x 600 = 45,000, so nlsat
overran its cap on many of them. Those `unknown` verdicts do not mean "undecided within
600s"; they mean "undecided within an unbounded amount of time that happened to be spent".

## A9. The augmentation is complete

Every realisable `n+1`-pattern restricts to a realisable `n`-pattern on each of its
`n+1` subsets, so seeding from all non-refuted `n`-patterns and extending by one point
reaches every `n+1`-pattern up to isomorphism. Extending a canonical representative by all
`k^n` colourings suffices because any pattern can be relabelled to match it.
**Status: PROVED** (it is A3 applied per-pattern).

## A10. The combinatorial lemmas are sound

L1 degree, L2 K(2,3), L3 bisector, L4 circumcentre, L5 equilateral-centre. Each is proved
in `lemmas.py`'s docstring from A4, A5, or the uniqueness of a circumcentre.
**Status: PROVED**, and VERIFIED to reject none of the **104** patterns known to be
realisable in this project (all `sat` verdicts plus every verified witness).

## A11. The lattice symmetry reduction is sound

For a configuration containing the origin, the point-group image minimising the smallest
remaining point makes that point orbit-minimal, so restricting the first chosen point to
orbit-minimal representatives loses nothing.
**Status: PROVED**, and VERIFIED by controls reproducing the known n=4, n=6 and n=7
witnesses (`latmin2.py controls`).

## A12. Lattice searches cannot see irrational-ratio configurations

In `Z^2` and `A_2` every squared distance is an integer, so every ratio is rational. The
unique realisable 5-point 3-class pattern has Groebner basis `v = 2u`, `u^2 - 4u + 1 = 0`,
whose only realisations are `u = 2 +- sqrt 3`: **both irrational**. So `D_gen(5) = 3` is
invisible to both lattices at any radius.
**Status: PROVED.** Consequence: no lattice negative is evidence of nonexistence. This
limits what the n=8 lattice results mean, and it is stated wherever they are used.
(A general lattice with an irrational Gram entry is not covered by this argument.)

## A13. `D_gen(7) = 5` — what it actually rests on

Upper bound: a verified witness (A6). Lower bound: 28 candidates, of which 21 use fewer
than 4 classes and die by A3, 4 were decided by z3 (A7), 2 by the equilateral-centre
lemma, and 1 by a trivial Groebner ideal. **Re-derived since:** all 28 fall to the
combinatorial lemmas plus monotonicity alone, with no solver, and L3 independently rejects
the pattern the Groebner argument killed.
**Status: PROVED**, and now independent of A8.

## A14. Novelty

No published table of small `D_gen` values found. Checked: Brass-Moser-Pach section 5.5
(the general-position section, pp. 214-216 — NOT p.200, which is the unrestricted
Erdos-Fishburn table); Sheffer's survey; Handbook Table 1.2.4; Dumitrescu 2008; the
crescent-configuration papers; Erdos-Fishburn 1997 (a DIFFERENT function — minimum sum of
per-point distance degrees, unrestricted); OEIS full-text on "cocircular", "concyclic",
"no four on a circle"; and the single forum comment plus its linked gist, which contains
no small values.
**Status: ~90% confident, resting on searches failing to find them.** Unchecked: four
1990s Erdos surveys the Renyi archive does not carry ([Er90], [Er92b], [Er94b], [Er97e]).

## A15. `D_gen(8)` is NOT claimed

`5 <= D_gen(8) <= 7`. The upper bound is a verified witness; 6 is **unfound, not
excluded**. Three lattice searches and a completed off-lattice run (4858 restarts) found
nothing, and the one 7-point witness provably admits no 5-distance extension (886 circle
intersections, 552 distinct points, 0 admissible) — but A12 says lattice negatives prove
nothing, and a heuristic proves nothing.
**Status: UNRESOLVED, and stated as such everywhere.**

## A16. Nothing here bears on the conjecture

`h(n)/n -> infinity` is asymptotic; small exact values cannot touch it. Sections 2, 2a and
2b give the reasons the elementary routes are exhausted.
**Status: stated, not assumed.**
