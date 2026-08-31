# Reproducing the #506 results

Every command below was run from a fresh copy of this directory on 2026-08-31, on
Windows 10 with Python 3.12.9 and sympy 1.13.1 (`pip install sympy`). Nothing else is
needed; there is no floating point anywhere in the verification. The outputs quoted
are what it actually printed.

## Which claim comes from which script

| claim in the note | script |
|---|---|
| every checkable claim, re-derived independently | `audit.py` |
| the same claims by a different circle-identification method | `verify_iso.py` |
| the values in the thread are already in the literature | `audit.py` check 6 |

The two verifiers are deliberately not the same computation. `verify_iso.py` treats a
circle or line as the zero set of A(x^2+y^2) + Bx + Cy + D and reads (A,B,C,D) off as
the null vector of the 3x4 matrix with rows [x^2+y^2, x, y, 1], so that A = 0 is
exactly collinearity. `audit.py` instead solves for the centre by Cramer's rule and
keys each circle on (cx, cy, r^2). They agree.

## 1. The whole note, independently re-derived

    python audit.py

Ends:

    ALL CHECKS PASSED

Checks 1 and 2 confirm both eight-point witnesses determine exactly 17 circles and 3
lines with all 56 triples covered once, Wang's over Q in `Fraction`, mzn's over
Q(sqrt 15) in sympy. Check 3 confirms the shared block profile (twelve blocks of size
4, eight of size 3). Check 4 brute-forces all 8! relabellings and finds exactly four
that send lines to lines and circles to circles. Check 5 is the one that decides the
question the note is about:

    [PASS] every isomorphism gives more than one ratio, so none is a similarity
           distinct ratios per isomorphism: [10, 10, 10, 10]

## 2. The novelty check, which is why this note was rewritten

`audit.py` check 6 prints Wang's Theorem 1.2 next to the values reported in the forum
thread:

       n   F(n)   c(n) per Wang
       4     3      3
       5     5      5
       6     9      8
       7    13      11
       8    19      17
       9    25      25

    [PASS] Wang's exceptional values are exactly the forum comment's m(6), m(7), m(8)
    [PASS] so the values reported in the thread are ALREADY in the literature, and
           this note adds the pointer, not the values
    [PASS] Wang also gives c(9) = F(9) = 25, settling the n = 9 case left open there

This check exists because checks 1 to 5 can all pass on a result that is already
known. It is the check that changed what this note claims.

## 3. The earlier verifier

    python verify_iso.py

Ends:

    VERDICT: CONFIRMED - same configuration, one rational and one over Q(sqrt15)

and prints the circle and line blocks for both witnesses, the four
designation-preserving relabellings, and the line correspondence

    Wang (0, 1, 2, 3) -> mzn (0, 1, 2, 3)
    Wang (0, 4, 6)    -> mzn (0, 5, 6)
    Wang (3, 5, 7)    -> mzn (1, 4, 7)

## Not included here

Wang's paper is not redistributed in this repository; it is at arXiv:2608.19844. The
eight coordinates and the list of 17 circles were transcribed from its section 7.3 and
are hard-coded in both verifiers, so the checks above run without it.

## Standing limits

`audit.py` verifies the two witnesses and the relation between them. It verifies **no
lower bound**: whether c(8) = 17 is minimal is Wang's Theorem 1.2, and I have not
checked his proof. The search scripts in this directory (`circles.py`, `designs.py`,
`gridsearch.py`, `anneal.py`) are exploratory and are not part of any claim; they have
no controls and their outputs are not cited in the note.
