# Audit of the mathematics of p100 and of the draft comment

## Summary

Every value in the table survives. The exact entries at n = 3 through 9 are supported by
an independent re-derivation (`AUDIT_RECHECK.py`, 56 checks, sharing no code with the
directory) and by a second script for the two questions the first one could not answer
(`AUDIT_EXTRA.py`). Nothing was found to be false.

Two things were being asserted more strongly than the evidence allowed, and both are now
disclosed in NOTE.md: the floor at n = 10 depends on reading a figure in Wei's paper
(finding 4), and the argument for why the one-point extension is complete was stated
loosely (finding 5). Three sentences of the draft comment were reworded (findings 8, 9,
10). The rest of this file records what was checked and what was found.

One honest note about method. The two subagents sent to audit this work were both cut
off by a usage limit before writing anything, so the audit below is mine. That is weaker
than an outside reading. What it does have is an independent re-derivation: every
construction in `AUDIT_RECHECK.py` is rebuilt from the mathematical description rather
than copied, the lattice enumeration there uses a completely different (and strictly
stronger) reduction, and the first run of it failed three checks. All three turned out to
be bugs in the audit script itself (a wrongly built fourth point in one witness, two
constants I had typed with truncated digits, and a wrong list of the units of the
Eisenstein integers); they are recorded here because they are the reason to trust the
other 53.

## Findings

**1. OK. The reduction "delta is at least the number of distinct distances", and every
use of it.** For a set with distinct distances d_1 < ... < d_k and g the smallest of d_1
and the gaps, d_k is at least d_1 + (k-1)g, which is at least kg, so delta = d_k/g is at
least k. The uses are all of the form "the incumbent is below D, so a competitor has
fewer than D distances", and each one was checked separately:

* n = 4 and n = 5: the incumbents are 2.073 and 2.618, both below 3, so a competitor has
  at most 2 distances; a 1-distance set has at most 3 points. Only k = 2 remains, and
  every k = 2 pattern was decided exactly.
* n = 6: the incumbent 3.414 is below 4, so at most 3 distances; k = 2 is impossible at 6
  points because g(2) = 5. The chain settles k = 3.
* n = 7, 8, 9: the incumbent 4.664 is below 5, so at most 4 distances. At 7 points k = 3
  gives only the regular heptagon (5.049) and the hexagon with its centre (7.464), both
  above 4.664; at 8 and 9 points k = 3 is impossible because g(3) = 7. So the competitors
  have exactly 4 distances, and those are the classified lists.
* n = 10, 11, 12: at most 4 distances is impossible because g(4) = 9. See finding 4.

**2. OK. Every theorem quoted in REFERENCES.md matches its primary source.** I checked
each quotation against the text extraction of the paper, not against the retrieval
agent's summary of it. Erdos and Fishburn's Theorem 1 (their page 116) is quoted
correctly, including the words "a 9-point set with exactly four distances must be R9 or
one of the configurations at the top of Fig. 1", and their description of the
three-triangle set on the same page. Shinohara's 2004 Theorems 1 and 2 (thirty four
five-point sets; six maximal six-point sets; two seven-point sets) are correct.
Shinohara's 2008 Theorem 1.2 is correct in both parts. Lan and Wei's Theorem 8 and the
family breakdown in their closing paragraph are correct, and I checked the three distance
ratios of their sets 740, 741 and 742 character by character in the Russian text, where
the radicals are broken across lines. Wei's 2012 Theorem 11 is correct. Wei's 2011
Theorem 13 I read from the scanned page image (page 514), together with the two lemmas on
that page in which he restates the 9-point and 8-point classifications.

**3. OK. Piepmeyer's set and the Erdos-Fishburn "three equilateral triangles" set are the
same set, and the radii are forced by the words, not chosen to fit.** Erdos and Fishburn
give no coordinates. Their rules are that the largest distance is both a side of the big
triangle and the distance from a big vertex to the farthest intermediate vertex, and that
the smallest distance is both a side of the inner triangle and the distance from an inner
vertex to the nearest intermediate vertex. With the big circumradius set to 1 those two
sentences are two equations, sqrt3 = 1 + r_mid and sqrt3 r_in = r_mid - r_in, whose
solutions are r_mid = sqrt3 - 1 and r_in = 2 - sqrt3. The audit script solves them itself
and then checks the remaining rule as a test, namely that the second distance is the side
of a square whose diagonal is the third distance; it is. The resulting nine points have
four distances in ratio 1 : sqrt(2+sqrt3) : 1+sqrt3 : 2+sqrt3, and their 36-element
distance multiset agrees with Piepmeyer's, rebuilt separately from Erdos's sentence in
[Er95], after multiplying by a single scale factor. So the identification is not an
assumption.

**4. UNDISCLOSED DEPENDENCY, now disclosed. The floor delta(10) >= 6 rests on reading a
figure.** Wei's Theorem 11 lists the 10-point 5-distance sets as the nonagon with its
centre, the regular decagon, the 11-gon minus a vertex, "double R5 with the same center
as shown in Figure 2q", and sixteen lattice configurations. The floor of 6 needs every
one of these to have delta at least 6, because a 10-point set with 6 or more distances
automatically has delta at least 6 while a 5-distance set only gives 5. Four of the five
families are explicit and give 8.291, 20.432, 12.344 and 11.196. The fifth exists in the
paper only as a drawing; the text states no parameters. NOTE.md was identifying it as the
regular pentagon together with the five intersection points of its diagonals, which has
exactly five distances and delta 9.216, without saying that this identification is mine.

To put a number on the risk, `AUDIT_EXTRA.py` sweeps the whole two-parameter family that
the phrase can mean, namely the pentagon together with a concentric copy scaled by rho and
turned by phi, on a grid of 8000 by 801 with the values merged at 1e-4, and finds only two
non-degenerate places where the nine candidate values collapse to five: the pentagram one
(delta 9.216) and the regular decagon (delta 20.432). A sweep is evidence, not a proof, so
NOTE.md now says the floor at n = 10 depends on it. Note that the floor of 5 at n = 10 is
unconditional, since it needs only g(4) = 9, and that nothing in the exact part of the
table (n = 3 to 9) touches this question at all.

**5. COULD BE BETTER, now rewritten. The completeness argument for the one-point
extension was stated loosely.** The docstring of `ext3.py` said that a new point not
pinned by two conditions has "at least n-1 new values", which is the right idea but skips
two cases. The sharp statement is a case analysis on t, the number of base points whose
distance to the new point P is an old value:

* t at least 2: P lies on two circles about different base points, so it is one of at
  most two points. Found by the circle-circle intersections.
* t = 1: the other n-1 distances take v values. If two of them coincide, P is on a
  bisector as well as a circle, and is found. If they are all distinct then v = n-1, and
  since the total number of values is k_base + v and must not exceed K, this needs
  n <= K - k_base + 1, which fails for every case used here.
* t = 0: all n distances are new. If some value occurs three times, P is the circumcentre
  of three base points and lies on two distinct bisectors, so it is found. If two values
  each occur twice, P lies on two bisectors, which are distinct unless the two pairs are
  mirror images of each other in the same line; in that case P is not pinned, but then
  the number of values is at most n-2, and combined with k_base this exceeds K in every
  case used here. Working through the four uses (n = 5, 6, 7 with K = 3, and n = 5, 6
  with K = 4 in `chain4.py`) the only surviving possibility with t = 0 is the centre of
  the regular pentagon, which the bisector-bisector intersections do find.

The conclusion is unchanged; only the argument is now correct as written.

**6. OK, after a check that nearly became a finding. The "lower" column of the table is
not the crude floor, and every entry in it is justified.** The crude floor from the
maximum size of a k-distance set alone would read 3 at n = 7 and 5 at n = 10, 11 and 12,
where the table says 4 and 6. An earlier draft of NOTE.md printed the crude row in
section 1 and the improved column in section 2 with nothing to connect them, which would
have been confusing; the crude row is no longer there, and section 2 now derives each
improved entry where it is used (the 4 at n = 7 from the two 7-point 3-distance sets, the
6 at n = 10, 11 and 12 from the 5-distance classifications). The maximum sizes g(1) to
g(6) are still used, and are still attributed, in `core.py` and `verify.py`.

**7. OK. Every closed form checked, symbolically where possible.** The two forms given
for delta(9), namely (2+sqrt3)/(1+sqrt3-sqrt(2+sqrt3)) and sqrt(6+3sqrt3+4sqrt2+2sqrt6),
agree to more than 190 digits and both equal the value computed from the coordinates.
delta(4) = (sqrt6+sqrt2)/(sqrt6+sqrt2-2) equals 2cos15/(2cos15-1). The lattice values
6+3sqrt3 and 6+4sqrt3 equal 3/(2-sqrt3) and 2sqrt3/(2-sqrt3), which is the form in which
they arise. delta(6) = 2+sqrt2 and delta(5) = (3+sqrt5)/2 check out.

**8. COMMENT, OVERSTATED, now fixed. "fifteen at n = 8" attributed a count to Shinohara
that he does not state.** His Theorem 1.2(a) is a structural statement: every 8-point
4-distance set is one of three named sets or an 8-point subset of a 9-point one. The
number 15 is what that theorem implies once the subsets are enumerated, which is my
computation. The comment now says so.

**9. COMMENT, OVERSTATED, now fixed. "neither paper mentions the other".** What I
actually verified is that the words "Piepmeyer" and the number (1+sqrt2)sqrt(2-sqrt3) do
not appear anywhere in Erdos and Fishburn's paper. I have not searched Erdos's 1995
survey for a reference to Erdos and Fishburn, and since the survey is the earlier
publication the claim was in any case a strange one to make in both directions. The
comment now says only that Erdos and Fishburn do not mention Piepmeyer.

**10. COMMENT, COULD BE BETTER, now fixed. "the value is the number quoted on the page".**
The page says Piepmeyer's example has diameter less than 5. Our 4.6639 is consistent with
that and makes it exact; it is not a number the page quotes. Reworded.

**11. OK. The origin of the problem is given as secondhand and is marked as such.** The
1981 Elem. Math. problem and its 1982 solution are known here only through Kanold's own
1981 paper, which quotes them. REFERENCES.md says this. The comment says "appeared as",
not "first appeared as".

**12. OK. The fifteen against sixteen lattice figures.** Wei's Theorem 11 says sixteen
lattice configurations and this directory finds fifteen similarity classes. Three
independent enumerations now agree on fifteen: the integer one in `lat.py`, a float one
with a different canonical key, and the Eisenstein-integer one in `AUDIT_RECHECK.py`,
whose reduction is complete (see the code audit). The retrieval agent's reading of the
figure, that panels 2c and 2h are mirror images of each other, would explain the
difference. NOTE.md reports this as a finding about the figure and not as a claim about
the paper, and no entry of the table depends on it, since all fifteen have the same delta.

**13. OK. Monotonicity.** Deleting a point from an admissible set leaves an admissible set
of no larger diameter, so delta does not decrease with n. The table respects this at every
step, which is a real check: an earlier version of this work reported 5.049 at n = 7, and
monotonicity against delta(8) <= 4.664 is what exposed it.

## What was not done

* The 34 five-point 3-distance sets found here were compared with Shinohara's count, not
  with his figures one by one.
* Brass's 1996 paper, the one dedicated study of this quantity, could not be obtained.
  OpenAlex reports it closed with no repository copy, there is no snapshot of the
  publisher page in the Wayback Machine, and CORE has no record. Whether it already
  contains small exact values is therefore unknown, and both NOTE.md and the comment say
  so rather than claiming priority.
* Wei's 2011 paper was read from a scan without a text layer, so its Theorem 13 was read
  by eye from the page image rather than extracted.
