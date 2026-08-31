# k=3 minimality for Erdos #97 — literature / novelty check

**Date:** 2026-08-30. Novelty check done BEFORE the main compute (lesson L14).

## The question

Erdos #97 asks for a convex polygon in which every vertex has **4** other vertices
equidistant from it. Danzer constructed one with **3** (the k=3 case) on **9** vertices.
Question attacked here: **is 9 the minimum n for the k=3 property?**

## Headline: Erdos posed this exact question as open in 1975, and it was never answered

Erdos, *On some problems of elementary and combinatorial geometry*, Ann. Mat. Pura Appl. (4)
**103** (1975), 99–108, at **p. 100** (scan: https://users.renyi.hu/~p_erdos/1975-25.pdf):

> "Danzer's example is not yet published. It would be of interest to determine or estimate
> the smallest possible value of n."

No later paper, survey, book or note found that resolves or revisits it.  STATUS: `CITED`.

## Source-by-source

| source | finding |
|---|---|
| Danzer's construction | **never published**; personal communication. Written out with a figure only in Erdos, *Some combinatorial and metric problems in geometry*, Intuitive Geometry (Siofok 1985), Colloq. Math. Soc. J. Bolyai **48** (1987), 167–177, at **p. 175** (https://users.renyi.hu/~p_erdos/1987-27.pdf). It is a **one-parameter family** (Reuleaux triangle A1A2A3, then B1 on an arc elongation, second Reuleaux triangle B1B2B3, C1 located by an intermediate-value argument), not a rigid configuration. **No minimality remark.** |
| erdosproblems.com/97 | no minimality claim; only sizes mentioned are Danzer's 9 and Fishburn–Reeds' 20 |
| forum thread /97 (all 7 comments read) | **nothing on k=3 minimality.** TheAbandonedThinker's `n >= 7` is for **k=4** (Cauchy–Schwarz: distinct centres give distinct circles so `|Q_i n Q_j| <= 2`, whence `6n <= n(n-1)`). mysticflounder's Lean bounds (>= 9, >= 10, README >= 12) are all for k=4; his README treats k=3 only as a *positive control* ("For k = 3 the property **is** realizable") |
| AlphaEvolve arXiv:2511.02864 Problem 6.53 (p. 59) | reached k=3, not k=4. Backing notebook `experiments/equidistant_points_in_convex_polygons/` **hard-codes a 9-point solution**; stored k=4 attempts are at n = 15,20,25,30,35,40,45. It **reproduced** 9, it did not establish it |
| `google-deepmind/formal-conjectures` `97.lean` | explicit 9-point witness in Q(sqrt 3) for `three_equidistant`, as *existence*. The only minimality theorem there is Fishburn–Reeds' n=20, a different (cut-restricted, single-common-distance) variant |
| Brass–Moser–Pach, *Research Problems in Discrete Geometry* (2005), §5.6 p. 218 | no minimality statement |
| OEIS | nothing |

## The closest solved analogue — same question WITHOUT convexity

Erdos & Fishburn, *Minimum planar sets with maximum equidistance counts*, Comput. Geom. **7**
(1997), 207–218, doi:10.1016/0925-7721(95)00050-X, define g(k) = the smallest n for which n
planar points each have k others equidistant, and prove

    g(2) = 3,  g(3) = 6,  g(4) = 8,  g(5) <= 16.

That is exactly this question minus convex position, and it is cited on erdosproblems.com/92.
So **g(3) = 6 in the unrestricted plane.**  STATUS: `CITED`.  The convex-position version appears
never to have been attacked.

## Coverage gaps (stated, not papered over)

Not read directly: Fishburn–Reeds 1992 full text (ScienceDirect 403); Erdos–Fishburn 1997 full
text (abstract only); Fishburn, *Distances in convex polygons* (The Mathematics of Paul Erdos II,
284–293); Erdos surveys Er90/Er92e/Er95/Er97e (Renyi archive stops at 1989). If a minimality
statement for the convex k=3 case exists in print, Fishburn–Reeds 1992 §1 or Fishburn's survey
chapter are the likely places. **A library check is warranted before claiming novelty in print.**
