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

## Few-distance sets: sizes and classifications

* **X. Wei, *A proof of Erdos-Fishburn's conjecture for g(6) = 13*, Electron. J.
  Combin. 19(4) (2012) #P38.** Open access; PDF downloaded and read in full. [READ]
  Used here for:
  - the introduction's summary of Erdos-Fishburn: "g(1) = 3 which is realized by R_3,
    g(2) = 5 and every 5-point two-distance set is isomorphic to R_5, g(3) = 7 and every
    7-point three-distance set is isomorphic to R_7 or R_6^+, g(4) = 9, and there exists
    9-point subset of L_triangle with 4-distance"; and "Shinohara [5] proved that
    12-point 5-distance set which realized for g(5) = 12 is unique up to similar
    transformation, that is a subset of L_triangle. Shinohara [6] classified 3-distance
    sets with at least five points." The E_7(3) statement is the control for the exact
    chain in NOTE.md section 4, and the 12-point uniqueness is the control for lat.py.
  - Theorem 11: "Every 10-point 5-distance set in the plane is isomorphic to R_9^+,
    R_10, R_11 - 1, double R_5 with the same center as shown in Figure 2q, or one of
    the sixteen 10-point configurations in L_triangle as shown in Figure 2a-2p." The
    sixteen appear only as figures (page 4, rendered and looked at; not compared point
    by point). lat.py finds fifteen up to similarity with diameter <= 10.
  - Figure 1: the 13-point 6-distance lattice set (lat.py finds exactly one).
  - Its reference list, which is where the classification papers below were found.

* **P. Erdos and P. Fishburn, *Maximum planar sets that determine k distances*, Discrete
  Math. **160** (1996) 115-125.** g(k) for k <= 5 and the classification of maximum
  k-distance sets for k <= 4, hence the list of 9-point 4-distance sets that would
  settle delta(9). [NOT OBTAINED]; known through Wei's summary above. A search snippet
  says the 9-point 4-distance sets are the regular nonagon "or one of three other
  configurations"; that phrase was not verified against the paper.

* **M. Shinohara, *Classification of three-distance sets in two dimensional Euclidean
  space*, European J. Combin. **25** (2004) 1039-1058.** Classifies every planar
  3-distance set with at least five points. [NOT OBTAINED]; cited by Wei. The exact
  chain here rebuilds E_5(3), E_6(3), E_7(3) from scratch (35 distinct distance
  multisets with 3 values at n = 5, nine at n = 6, two at n = 7) and could be compared
  with Shinohara's counts if the paper is obtained.

* **M. Shinohara, *Uniqueness of maximum planar five-distance sets*, Discrete Math.
  **308** (2008) 3048-3055.** [SECONDHAND] via Wei; the uniqueness is reproduced by
  lat.py among lattice sets.

* **W. Lan and X. Wei, *Classification of four-distance seven-point sets in the plane*,
  Mathematical Notes 93 (2013).** Would settle delta(7) by a finite check. [NOT
  OBTAINED]; cited by Wei as "[8] ... to appear".

* **X. Wei, *Classification of eleven-point five-distance sets in the plane*, Ars
  Combin. **102** (2011) 505-515.** [NOT OBTAINED]; cited by Wei 2012 as the source of
  its Lemmas 6 and 7.

* **F. Szollosi and P. R. J. Ostergard, *Constructions of maximum few-distance sets in
  Euclidean spaces*, Electron. J. Combin. 27(1) (2020) #P1.23, arXiv:1804.06040.**
  Abstract read; PDF obtained but its text extraction was not examined. Classifies the
  largest 6-distance sets in R^2 by isomorph-free generation plus Groebner bases, the
  same combination used here. [READ] for the abstract only.

* **Maximum sizes used for k_min:** g(1..6) = 3, 5, 7, 9, 12, 13. g(1..4) and the
  values for k = 5, 6 are stated in Wei's introduction and theorem [READ there]; the
  original proofs (Erdos-Fishburn for k <= 4, Shinohara for k = 5, Wei for k = 6) are
  [SECONDHAND] except Wei's. Every "PROVED" entry in NOTE.md is independent of these
  values (each rests on an exhaustive exact computation at that n, and the g(2) = 5,
  g(3) = 7 facts it needs are re-derived by the chain); the "bracketed" floors depend
  on them.

* **L. M. Kelly**, the classification of planar 2-distance sets (six 4-point sets, and
  the regular pentagon as the unique 5-point set). [SECONDHAND]. Recovered from scratch
  here: the exact enumeration finds exactly six distance multisets at n = 4 and exactly
  one realisable pattern at n = 5.

## Not obtained

* Brass, Moser, Pach, *Research Problems in Discrete Geometry*, the distances chapter.
* P. Brass, *Erdos distance problems in normed spaces*, Comput. Geom. **6** (1996), which
  cites Piepmeyer and Kanold and reportedly names the minimum-diameter function.
* Harborth and Piepmeyer, *Three distinct distances in the plane*, Geom. Dedicata **61**
  (1996) 315-327.
