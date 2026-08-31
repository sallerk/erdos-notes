# References for the #97 note

## Erdős's own minimality question

* **P. Erdős**, "On some problems of elementary and combinatorial geometry",
  Ann. Mat. Pura Appl. (4) **103** (1975), 99-108. Page 100, verbatim:

  > "Finally I conjectured that every convex polygon always has a vertex which does
  > not have three vertices equidistant from it. DANZER to my great surprise disproved
  > this conjecture. In fact he showed that to every k there is a convex polygon of n
  > vertices so that every vertex has k other vertices equidistant from it. **Danzer's
  > example is not yet published. It would be of interest to determine or estimate the
  > smallest possible value of n.**"

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

  The same page also states "This conjecture was proved by ALTMAN", i.e. that a convex
  n-gon determines at least floor(n/2) distinct distances; this is the Altman result
  relied on in the #982 and #1082 notes.  *[VERIFIED AT SOURCE, same read]*

* **P. Erdős**, "Some combinatorial and metric problems in geometry", Intuitive
  Geometry (Siófok 1985), Colloq. Math. Soc. J. Bolyai **48**, North-Holland (1987),
  167-177, p. 175. Where Danzer's construction is written out with a figure; it is a
  one-parameter family, not a rigid configuration. Danzer's construction appears never
  to have been published separately.
  Scan: https://users.renyi.hu/~p_erdos/1987-27.pdf  *[secondary]*

## The non-convex analogue

* **P. Erdős and P. Fishburn**, "Minimum planar sets with maximum equidistance counts",
  Comput. Geom. **7** (1997), 207-218, doi:10.1016/0925-7721(95)00050-X. Defines the
  smallest n for which n planar points each have k others equidistant, and proves the
  values 3, 6, 8 for k = 2, 3, 4 and an upper bound 16 for k = 5. Same question without
  convexity.  *[secondary: abstract only]*

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

`RESULTS.md`, `COMMENT_FULL.md`, `artifact_danzer9_t0.json` (exact Danzer coordinates),
`verify_p97.py`, `theorem_alt.py`, and `k3-minimality/` holding the n = 4, 5, 6
exclusion, including the incomplete n = 7 run recorded honestly as incomplete.
