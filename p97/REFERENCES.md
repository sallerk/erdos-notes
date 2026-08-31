# References for the #97 note

## Erdős's own minimality question

* **P. Erdős**, "On some problems of elementary and combinatorial geometry",
  Ann. Mat. Pura Appl. (4) **103** (1975), 99-108. Page 100, verbatim:

  > "Finally I conjectured that every convex polygon always has a vertex which does
  > not have three vertices equidistant from it. DANZER to my great surprise disproved
  > this conjecture. In fact be showed that to every k there is a convex polygon of n_k
  > vertices so that every vertex has k other vertices equidistant from it. **Danzer's
  > example is not yet published. It would be of interest to determine or estimate the
  > smallest possible value of n_k.**"

  Transcribed as printed. "In fact be showed" is a typo in the original. The
  subscripts are n_k in both places, not n; an earlier draft of this note quoted the
  last sentence as "smallest possible value of n", which was wrong. n_k is the least
  number of vertices of a convex polygon in which every vertex has k others
  equidistant from it, so the k = 3 case is exactly what this note bounds below.

  Scan: https://users.renyi.hu/~p_erdos/1975-25.pdf
  *[VERIFIED AT SOURCE: PDF text layer extracted and read 2026-08-31]*

  Note the wider claim in that passage, that Danzer settled **every** k. This is
  already known to the site and already discounted there. The #97 page says, verbatim:
  "In [Er75f] Erdős claimed that Danzer proved that this false for every constant - in
  fact, for any k there is a convex polygon such that every vertex has k vertices
  equidistant from it. Since this claim was not repeated in later papers, presumably
  Erdős was mistaken here."  [Er75f,p.100] is already in the page's citation list, so
  locating this passage is not a new observation.

  The reasoning for "mistaken" is circumstantial rather than proved: Erdős re-posed the
  k = 4 question in [Er90], [Er92e], [Er95] and [Er97e], which he would not have done
  had Danzer settled every k. No general-k construction of Danzer's has ever surfaced,
  and no proof that one cannot exist has either.

  The **minimality** sentence is a separate claim in the same paragraph, and the page
  does not mention it. It is well-posed for k = 3 regardless of the "every k" question,
  since Danzer's k = 3 construction is not in doubt; that is the only case this note
  addresses.

  The same page also states, of the first of the three conjectures, "This conjecture
  was proved by ALTMAN", the conjecture being that a convex n-gon determines at least
  floor(n/2) distinct distances IN TOTAL. This is the Altman result relied on in the
  #982 and #1082 notes. The full reference is in the same paper's bibliography:
  "E. ALTMAN, On a problem of P. Erdos, Amer. Math. Monthly, 70 (1963), pp. 148-157".
  Note that the SECOND of the three conjectures on the same page, max_i d_2(x_i) >=
  n/2, which Erdos there calls "not yet settled", is problem #982; the total-distance
  result and problem #982 are neighbours in one paragraph.
  *[VERIFIED AT SOURCE: PDF text layer extracted and read 2026-08-31]*

* **P. Erdős**, "Some combinatorial and metric problems in geometry", Intuitive
  Geometry (Siófok 1985), Colloq. Math. Soc. J. Bolyai **48**, North-Holland (1987),
  167-177. **p. 175** is where Danzer's construction is written out, as Figure 5 plus
  three distance relations for the convex nonagon A1 B1 C1 A2 B2 C2 A3 B3 C3 of
  threefold rotational symmetry:

  > "This conjecture was disproved by Danzer, his example appears in Fig.5. This is a
  > convex nonagon A1B1C1A2B2C2A3B3C3 of threefold rotational symmetry, satisfying
  > A1A2 = A1A3 = A1B3, B1B2 = B1C2 = B1B3, C1C2 = C1A3 = C1C3."

  No coordinates are printed. The artifact in this directory satisfies exactly those
  three relations; `audit.py` checks that correspondence explicitly rather than only
  checking that all nine counts are 3. Danzer appears never to have published the
  construction himself: Erdos says so outright in 1975, and Er87b carries no Danzer
  entry in its reference list. So it is published, but by Erdos on Danzer's behalf.

  **p. 176** of the same paper, immediately after, has Erdos posing the k = 4 question:

  > "Perhaps in every convex polygon there is a vertex which does not have four other
  > vertices equidistant from it."

  That is direct evidence for the problem page's "presumably Erdős was mistaken here"
  about the 1975 all-k claim; by 1987 he is treating k = 4 as open.
  Scan: https://users.renyi.hu/~p_erdos/1987-27.pdf
  *[VERIFIED AT SOURCE: page images read 2026-08-31]*

## The non-convex analogue

* **P. Erdős and P. Fishburn**, "Minimum planar sets with maximum equidistance counts",
  Comput. Geom. **7** (1997), 207-218, doi:10.1016/0925-7721(95)00050-X. Defines the
  smallest n for which n planar points each have k others equidistant, and proves the
  values 3, 6, 8 for k = 2, 3, 4 and an upper bound 16 for k = 5.

  This is the same question **without** convexity, so it does not settle Erdős's n_k,
  which is about convex polygons. The novelty check that matters: their k = 3 realiser
  is two similarly-oriented equilateral triangles of side d translated by a vector of
  length d, and if that set were in convex position then n_3 = 6 and the bound n_3 >= 7
  proved here would be false. `audit.py` check 7 confirms in exact arithmetic that the
  set does have the k = 3 property and is **not** in convex position, for all six unit
  translations, with controls showing the convexity test accepts a scrambled convex
  hexagon and rejects a dented one. The translation DIRECTION is free, so the
  realisers are a one-parameter family and six exact cases do not cover it; the same
  check therefore also sweeps all 3600 directions numerically, finding the k = 3
  property in every one and convex position in none. So their value 6 and the bound n_3 >= 7 proved here are
  consistent, and convexity costs at least one point. (Their symbol g(k) is NOT the
  g(k) of the #1082 note, which is the largest set with at most k distinct distances;
  the two are unrelated and the symbol is avoided here.)
  *[secondary: abstract only for the paper itself; the realiser's non-convexity is
  VERIFIED here in exact arithmetic]*

## Prior work on the k = 4 question

* **AlphaEvolve**, arXiv:2511.02864, Problem 6.53: reached k = 3 but not k = 4.
  *[secondary]*
* **mysticflounder**, Lean formalisation in progress,
  https://github.com/mysticflounder/erdos-97-96-formalization  *[secondary]*
* **Fishburn and Reeds**, "Unit distances between vertices of a convex polygon",
  Comput. Geom. **2** (1992), 81-91. Proves n = 20 minimal for a *different*,
  cut-restricted single-common-distance variant.  *[secondary: full text not obtained]*
* **Brass, Moser and Pach**, Research Problems in Discrete Geometry (2005), Sec. 5.6,
  p. 218.  *[secondary]*

## Artifacts here

`REPRODUCE.md` (step-by-step, with the output each command actually printed),
`RESULTS.md`, `COMMENT_FULL.md`, `artifact_danzer9_t0.json` (exact Danzer coordinates),
`audit.py` (standalone re-derivation of every checkable claim, sharing no code with the
searches), `verify_p97.py`, `theorem_alt.py`, and `k3-minimality/` holding the
n = 4, 5, 6 exclusion, including the incomplete n = 7 run recorded honestly as
incomplete.
