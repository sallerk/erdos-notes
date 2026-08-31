# Erdos #506 — minimum number of distinct circles determined by n points

m(n) = fewest distinct circles determined by n points, not all concyclic and not
all collinear.  Convention (settled in the problem's forum thread): a collinear
triple determines a line, not a circle, and contributes nothing.

Status of the literature check: RUNNING at the time of writing.  Everything below
is my own computation and does not depend on it.

## Tools built (all exact, no floating point anywhere)

| file | what it does |
|---|---|
| `circles.py` | exact circle counter over `Fraction`. A circle/line is `A(x^2+y^2)+Bx+Cy+D=0`; three points give `(A,B,C,D)` as the null vector of the 3x4 matrix of rows `[x^2+y^2, x, y, 1]`, normalised to a canonical integer 4-tuple. `A == 0` means collinear. Two triples are cocircular exactly when their keys match. |
| `gridsearch.py` | exhaustive branch-and-bound over all n-subsets of an integer grid, pruning as soon as the running circle count reaches the incumbent |
| `anneal.py` | simulated annealing on a grid with the same exact objective, for n where exhaustive search does not reach |
| `designs.py` | combinatorial lower bound by exact cover (see below) |

Sanity checks that passed: `n-1` points on a line plus one off it gives exactly
`C(n-1,2)` circles for n = 4..8; the unit square is correctly rejected as
all-concyclic; square-plus-centre gives 5.

## Results

| n | exhaustive grid | annealing | combinatorial lower bound (`designs.py`) | Purdy-Smith formula |
|---|---|---|---|---|
| 5 | **5** | — | **5** (tight) | 5 |
| 6 | **8** (11x11 grid) | 8 | 7 (NOT tight) | 9 |
| 7 | none < 12 on 8x8 | 13 | 7 (very not tight) | 13 |
| 9 | — | — | — | 25 |

**m(6) <= 8 with an integer witness**, found independently and re-verified by the
separate exact checker:

    (0,1), (2,0), (2,3), (3,2), (5,6), (6,3)     -> exactly 8 circles

Its block structure is clean: **3 lines of 3 points, 3 circles of 4 points, 5
circles of 3 points**, and 3 + 3*4 + 5 = 20 = C(6,3) exactly.  The three 4-point
circles are `{0,1,2,3}`, `{0,1,4,5}`, `{2,3,4,5}` — they pair the six points as
`{0,1} {2,3} {4,5}`.

## The Purdy-Smith construction, derived

The formula `C(n-1,2) + 1 - floor((n-1)/2)` comes from: put `n-1` points on a
circle and one further point `P` outside it, arranged so the `n-1` points fall
into `floor((n-1)/2)` pairs each COLLINEAR with `P`.  Then
  * triples inside the circle -> 1 circle;
  * a triple `P,a,b` with `a,b` paired -> a line, free;
  * every other triple `P,a,b` -> its own circle, and these are all distinct
    because a second circle through `P` meets the first in at most 2 points.
Total `1 + C(n-1,2) - floor((n-1)/2)`.  Verified against the formula for n = 5..9.

## The finding that matters: combinatorics alone cannot solve this

`designs.py` computes the best possible block structure ignoring geometry.  Every
triple lies on exactly one block, so the blocks EXACTLY COVER the C(n,3) triples —
which means "two blocks meet in at most 2 points" needs no separate constraint, a
shared triple would be double-covered.  Lines are free but must pairwise meet in
at most ONE point; circles may meet in two.  So the bound is
`min over exact covers of [ #blocks - max sub-family pairwise meeting in <= 1 ]`.

    n=5  ->  5   matches m(5)=5, so the optimal design IS realisable
    n=6  ->  7   but the best realisable is 8
    n=7  ->  7   but the best realisable is 11 or more

At n=7 the optimal design uses **seven 3-point lines on seven points, pairwise
meeting in one point — the Fano plane**, which is famously not realisable over the
reals.  So the combinatorial bound is not merely loose, it is loose for a
well-understood reason.

**Consequence for how to attack #506:** the difficulty is entirely REALISABILITY,
not enumeration.  A purely combinatorial search cannot produce a correct lower
bound; each candidate design has to be decided over the reals.  That is a
real-algebraic-geometry question of exactly the kind handled by the Groebner +
nlsat pipeline developed for #97 in `../k3min/`.

## Not established

Nothing here proves any lower bound on m(n).  `m(6) <= 8` and the n=5 value are
upper bounds from exhibited configurations plus, at n=5, a matching combinatorial
bound.  m(7), m(8), m(9) are untouched by my own work so far.

---

# STOP: #506 is not open. Four independent claimed solutions, 18-20 Aug 2026.

The triage brief that sent me here was STALE. It recorded mzn's 18 Aug 2026 comment
reducing n=9 to two surviving cases (largest block 4 or 5) and being unable to close
them. That was accurate for about two days.

| n | F(n) = 1+C(n-1,2)-floor((n-1)/2) | claimed m(n) |
|---|---|---|
| 4 | 3 | 3 |
| 5 | 5 | 5 |
| 6 | 9 | **8** |
| 7 | 13 | **11** |
| 8 | 19 | **17** |
| >= 9 | F(n) | F(n) — so m(9)=25, m(10)=33, m(11)=41, m(12)=51 |

Claimants, none peer-reviewed, all AI-assisted:
* **Liyan Wang**, arXiv:2608.19844 (20 Aug 2026), OR-Tools CP-SAT + SymPy + Lean 4.29.1.
  Theorem 1.2: `c(n)=F(n)` for all n>=4 except c(6)=8, c(7)=11, c(8)=17. His n=9
  labelled exact-cover model reports the residue INFEASIBLE — precisely mzn's two
  surviving cases.
* **Denis Paliy**, github.com/DenisUkranian/erdos-506-circles v1.0.2, cadical SAT.
* **Rafal Wrona**, Lean 4.30.0 + Mathlib, sorry-free, submitted as the proof claim on
  the site 20 Aug 2026.
* **Stijn Cambie**, claims a shorter paper; nothing public.

Classically proven remains only n > 393 (Elliott 1967, corrected by Purdy-Smith 2010).
erdosproblems.com and `teorth/erdosproblems` are NOT yet updated.

## What this attack did produce: independent exact verification

Nobody asked for it and it is small, but it is real, and it is the one thing here
that is not duplicated work.

**1. Wang's rational 8-point witness is correct.** Verified with `circles.py` in exact
rational arithmetic: exactly **17 circles**, valid, and the block list matches his
paper exactly — eleven 4-point circles, six 3-point circles, one 4-point line
`(0,1,2,3)` and two 3-point lines `(0,4,6)`, `(3,5,7)`.

**2. mzn's Q(sqrt 15) 8-point witness is also correct.** Verified in sympy exact
arithmetic over Q(sqrt 15): exactly **17 circles**, maximal lines
`(0,1,2,3)`, `(0,5,6)`, `(1,4,7)`.

**3. mzn's non-rationalizability claim is FALSE as stated.** mzn wrote:

> "The value u^2=15 is forced. ... The seven-point witness can be rationalized, and
> this one cannot."

But the two configurations are **the same design**. There is a DESIGNATION-PRESERVING
isomorphism — lines to lines, circles to circles — via the permutation

    (0,1,2,3,4,5,6,7) -> (0,2,3,1,5,7,6,4)

found by brute force over all 8! relabellings. So the 17-circle configuration does
admit a rational realisation; Wang exhibits one and it verifies exactly.

Fair caveat: mzn's supporting descent argument is scoped to their own
parametrization ("abscissae in sqrt3 Q, ordinates in R Q with R = sqrt(4a^2+b^2), so
a similarity would require 4a^2+b^2 = 3q^2, impossible by descent mod 3"). That may
well be correct FOR THAT FAMILY. The error is in the generality of the conclusion:
u^2 = 15 is not forced for the configuration, only for that parametrization of it.

**4. m(6) <= 8 reproduced from scratch** with an integer witness found by my own
branch-and-bound, independent of all four claimants.

## Status of every claim in this file

`VERIFIED`  Wang's 8-point rational set determines exactly 17 circles (exact rationals)
`VERIFIED`  mzn's Q(sqrt15) 8-point set determines exactly 17 circles (exact sympy)
`VERIFIED`  the two are isomorphic as designs, respecting the line/circle split
`VERIFIED`  my own 6-point integer witness determines exactly 8 circles
`VERIFIED`  combinatorial exact-cover floors: 5 at n=5, 7 at n=6, 7 at n=7
`CITED`     every value of m(n) above — these are other people's 2026 claims, not mine

---

# CORRECTION TO MY OWN CRITIQUE (2026-08-30)

Before posting, I tested whether Wang's rational configuration and mzn's Q(sqrt15)
configuration are SIMILAR, not merely isomorphic as designs.  Under all four
designation-preserving relabellings the ratio of corresponding squared distances
takes 10 distinct values, never 1.

    perm (0,2,3,1,5,7,6,4) -> 10 distinct ratios
    perm (0,2,3,1,6,4,5,7) -> 10
    perm (1,3,2,0,4,6,7,5) -> 10
    perm (1,3,2,0,7,5,4,6) -> 10

**They are NOT similar.**  They are two non-similar realisations of the same
abstract incidence design, so the design has moduli.

Consequence: my draft comment overreached.  mzn's argument is explicitly about
similarity ("a similarity would require 4a^2+b^2 = 3q^2, which has only the zero
solution by descent mod 3"), and that can be entirely correct for their own
configuration while a rational realisation exists elsewhere in the moduli space.
Claiming mzn was wrong is not supported.

What is supported, and all that should be said:
  VERIFIED  mzn's set determines exactly 17 circles (exact over Q(sqrt15))
  VERIFIED  Wang's set determines exactly 17 circles (exact over Q)
  VERIFIED  the two designs are isomorphic, lines to lines and circles to circles
  VERIFIED  the two point sets are NOT similar
  =>        the 17-circle type is not rigid and does admit a rational realisation;
            "u^2 = 15 is forced" stands within mzn's parametrised family.

NOT VERIFIED: Wang's coordinates were transcribed from a secondary report, not read
from arXiv:2608.19844 directly.  The fact that they reproduce 17 circles with the
expected block profile is strong but indirect evidence of correct transcription.
