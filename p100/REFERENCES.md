# References for #100

Provenance per item: [READ] = the primary text was read, by me or by an agent whose
report I checked against the source; [SECONDHAND] = seen only as a citation or abstract;
[NOT OBTAINED].

## The problem and its sources

* **Problem page.** https://www.erdosproblems.com/100, fetched 2026-09-07. Cites [Er90],
  [Er92e], [Er95], [Er97f]. Zero comments, nobody flagged as working on it, formalised.
  [READ]

* **The origin, which the page does not cite.** P. Erdos, Problem 856A, Elem. Math. **36**
  (1981) 22; solution H.-J. Kanold, Elem. Math. **37** (1982) 56. Known from Kanold's own
  1981 paper, which opens by quoting the Elem. Math. problem verbatim and restates his
  published solution `delta(M) > (eps/4) n^{3/4}` for n >= 16. The Elem. Math. pages
  themselves sit behind e-periodica's challenge page. [SECONDHAND] for the pages,
  [READ] for Kanold's quotation of them.

* **H.-J. Kanold, *Uber Punktmengen im k-dimensionalen euklidischen Raum*, Abh.
  Braunschw. Wiss. Ges. **32** (1981) 55-65.** Obtained via the Wayback Machine from the
  TU Braunschweig repository (dbbs_mods_00052443); pages 55-56 read from page images
  because the OCR mangles the fractions. [READ]
  What it contains, and what the problem page omits:
  - eq. (8): `delta >= d_1 + (s-1) eps`, with s the number of distinct distances. This is
    the few-distance connection, and it is the source of the bound used in NOTE.md.
  - Satz 2 (plane): if the minimum distance d <= eps then `delta/eps > n/2`; if d > eps
    then `delta/eps > 0.366 n^{3/4}`. The linear bound is therefore already proved in half
    the parameter space, and the page's "Kanold proved >= n^{3/4}" undersells it.
  - closing remark, p. 65: whether the exponents in Satze 2-4 can be improved is open,
    and the proofs use only pigeonhole and the triangle inequality.

* **[Er95]** P. Erdos, *Some of my favourite problems in number theory, combinatorics,
  and geometry*, Resenhas **2** (1995) 165-186. Free PDF at
  https://www.ime.usp.br/~yoshi/resenhas/abstracts/Erdos.pdf. [READ]
  Contains the verbal description of Piepmeyer's 9 points, the value
  `x = (1+sqrt2) sqrt(2-sqrt3)`, the conjecture "perhaps if n > n_0 the diameter is in
  fact >= n-1", and the sentence "It is perhaps not uninteresting to try to determine the
  smallest diameter for each n, but this will already be difficult for n = 9", which is
  the sub-question this directory works on.

* **L. Piepmeyer**, *Punktmengen mit minimaler Anzahl verschiedener Abstande*,
  Dissertation, TU Braunschweig, 1992 or 1993 (the two dates appear in different
  bibliographies). [NOT OBTAINED]. Piepmeyer's own account of the 9-point set is
  presumably here; Erdos's verbal description was what was used.

* **Exact coordinates for Piepmeyer's set** appear in a branch of
  google-deepmind/formal-conjectures (theaustinhatfield, branch
  solve-erdos-100-piepmeyer, FormalConjectures/ErdosProblems/100.lean). [READ]
  They were reproduced independently here from Erdos's sentence and the two agree as
  exact 36-element distance multisets.

## Maximum sizes of k-distance sets, which give the floor k_min(n)

Values used: g(1..6) = 3, 5, 7, 9, 12, 13. Attributions as usually given:
Erdos and Fishburn, *Maximum planar sets that determine k distances*, Discrete Math.
**160** (1996) 115-125, for k <= 4; M. Shinohara for k = 5; X. Wei for k = 6, settling
an Erdos-Fishburn conjecture. [SECONDHAND] for all three. A literature agent sent to
confirm these values and to find whether the 9-point 4-distance sets are classified was
stopped before it reported, because its fetching was opening PDFs in the user's browser.
The values are the standard ones but have not been re-verified at source in this
directory; every "PROVED" entry in NOTE.md is independent of them (it rests on an
exhaustive enumeration at that n), and the "bracketed" floors do depend on them.

* **L. M. Kelly**, the classification of planar 2-distance sets (six 4-point sets, and the
  regular pentagon as the unique 5-point set). [SECONDHAND]. Recovered from scratch here:
  the enumeration at n = 5 realises exactly one of seventeen patterns.

## Not obtained

* Brass, Moser, Pach, *Research Problems in Discrete Geometry*, the distances chapter.
* P. Brass, *Erdos distance problems in normed spaces*, Comput. Geom. **6** (1996), which
  cites Piepmeyer and Kanold and reportedly names the minimum-diameter function.
* Harborth and Piepmeyer, *Three distinct distances in the plane*, Geom. Dedicata **61**
  (1996) 315-327, which would classify 3-distance sets and could turn delta(6) and
  delta(7) into finite checks.
