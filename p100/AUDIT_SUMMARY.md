# Audit of p100: what was checked, what changed

Two companion files hold the detail: AUDIT_MATH.md for the mathematics and the draft
comment, AUDIT_CODE.md for the programs. This file is the short version.

## The verdict

No number in the table is wrong. The exact values at n = 3 through 9 stand, including the
three that answer Erdos's own question, and the brackets at n = 10 through 13 stand.
Nothing had to be withdrawn.

Three claims were being made a little more strongly than the evidence allowed, and all
three have been reworded rather than removed:

1. The floor delta(10) >= 6 depends on identifying a figure in Wei's paper, because the
   paper gives that configuration only as a drawing. NOTE.md now says so, and a sweep of
   the whole family the phrase can mean is included as evidence. The weaker floor of 5
   there is unconditional.
2. The count of fifteen 8-point 4-distance sets is implied by Shinohara's theorem, not
   stated by him. The comment now says "the fifteen sets that Shinohara's theorem allows".
3. The comment said that neither Erdos-Fishburn nor Erdos's 1995 survey mentions the
   other's construction. Only half of that was checked, so the comment now claims only
   the half that was: Erdos and Fishburn do not mention Piepmeyer.

One argument was correct in its conclusion but sloppy as written: the reason the one-point
extension in `ext3.py` misses nothing. Its docstring now carries the case analysis that
actually proves it, including the two cases the old wording skipped.

## The independent evidence

`AUDIT_RECHECK.py` re-derives 56 claims and imports nothing from the directory. Every
witness in it is rebuilt from the mathematical description: the six 4-point two-distance
sets from their two possible short-edge graphs, Piepmeyer's nine points from the sentence
in Erdos's survey, the Erdos-Fishburn nine points from their distance rules (whose radii
the script solves for rather than copies), and the lattice sets from a fresh enumeration
in the Eisenstein integers whose similarity reduction is complete, unlike the one in
`lat.py`. It agrees on every count and every value.

`AUDIT_EXTRA.py` answers the two questions the first script cannot: it sweeps the pentagon
family behind finding 1 above, and it checks that the exact solver never returned the same
solution twice, which is the one way its completeness certificate could have been fooled.
Neither found a problem.

The first run of `AUDIT_RECHECK.py` failed three checks, and all three were bugs in the
audit script itself: a wrongly built witness, two constants typed with truncated digits,
and a wrong list of the units of the Eisenstein integers. They are written up in
AUDIT_CODE.md because they are the reason to believe the checks that passed.

## What this audit is not

The two subagents sent to audit this work independently were both cut off by a usage limit
before writing anything, so the reading below is the same session's, which is weaker than
an outside one. The strongest guard against that is the re-derivation just described, plus
the fact that the load-bearing counts (34, 9, 2, 20, 8, 15, 42, 4, 3, 1) each match a
published classification obtained from a primary source.

Three gaps remain and are recorded in NOTE.md and REFERENCES.md rather than papered over:
Brass's 1996 paper on this exact quantity could not be obtained anywhere; Wei's 2011 paper
was read from a scan by eye; and the thirty-four five-point three-distance sets found here
were compared with Shinohara's count, not with his figures one at a time.
