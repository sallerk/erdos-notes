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
    sixteen appear only as figures. lat.py finds fifteen up to similarity; extracting
    the dot coordinates of Figure 2 from the PDF (the agent's computation) shows panels
    2c and 2h are mirror images, so the figure holds one duplicate. The double R_5 is
    the regular pentagon with its five diagonal intersections (the only concentric
    doubling of R_5 with five distances; my computation and the agent's agree).
  - Figure 1: the 13-point 6-distance lattice set (lat.py finds exactly one).
  - Its reference list, which is where the classification papers below were found.

The five papers below were obtained in full text by a retrieval agent restricted to
curl and WebFetch (no browser); each theorem quoted here was then checked by me against
the text extraction of the PDF. Copies are kept outside the repository.

* **P. Erdos and P. Fishburn, *Maximum planar sets that determine k distances*, Discrete
  Math. **160** (1996) 115-125.** Wayback Machine copy of the CORE mirror of the
  Elsevier open-archive PDF (web.archive.org/web/20190320071006id_/https://core.ac.uk/
  download/pdf/82120885.pdf). [READ]
  Theorem 1: "g(2) = 5, g(3) = 7, g(4) = 9 and g(5) = 12. R5 is the only 5-point set with
  exactly two interpoint distances; the only 7-point sets that determine three
  distances are R7 and R6+; a 9-point set with exactly four distances must be R9 or one
  of the configurations at the top of Fig. 1". Fig. 1 top: "Three 9-point
  configurations that determine 4 distances": two lattice sets and one "composed of
  three equilateral triangles with the same center and a horizontal edge", with the
  distance rules on p. 116 that fix its radii (used verbatim in e9.py). That set is
  Piepmeyer's set; the paper does not mention Piepmeyer. Also p. 117: it "is a
  curiosity in that it is the only verified or conjectured realizer of a g(k) that is
  not an Rn or Rn+ or subset of L_triangle".

* **M. Shinohara, *Classification of three-distance sets in two dimensional Euclidean
  space*, European J. Combin. **25** (2004) 1039-1058.** Wayback copy of the CORE
  mirror (web.archive.org/web/20240708032538id_/https://core.ac.uk/download/pdf/
  82573075.pdf). [READ]
  Theorem 1: "There are thirty four three-distance sets having five points in R2 to
  within isomorphism." Theorem 2: no 3-distance set has more than seven points; two
  maximal ones with seven points (R_7, R_6^+); six maximal ones with six points;
  sixteen maximal ones with five points. The exact chain here finds 34 five-point,
  9 six-point and 2 seven-point 3-distance sets, in agreement (the nine are the six
  maximal ones plus the three 6-point subsets of R_7 and R_6^+).

* **M. Shinohara, *Uniqueness of maximum planar five-distance sets*, Discrete Math.
  **308** (2008) 3048-3055.** Wayback copy of the CORE mirror
  (web.archive.org/web/20240414142032id_/https://core.ac.uk/download/pdf/82675961.pdf).
  [READ]
  Theorem 1.2: "(a) Every 8-point four-distance set in R2 is isomorphic to R8, R7+,
  Fig. 1(e) or an 8-point subsets of a 9-point four-distance set. (b) The configuration
  given in Fig. 1(d) is the only 12-point five-distance set in R2." Fig. 1(e) is a
  square with an equilateral triangle erected on each side; Fig. 1(d) is the lattice set
  lat.py finds. Used in e78.py for delta(8).

* **W. Lan and X. Wei, *Classification of seven-point four-distance sets in the plane*,
  Mat. Zametki **93**:4 (2013) 492-508 (Russian; English in Math. Notes 93 (2013)
  510-522).** Russian original from mathnet.ru (mzm10172). [READ] in Russian.
  Theorem 8: up to isomorphism there are exactly 42 seven-point four-distance sets
  (Fig. 4). The closing paragraph (pp. 507-508) identifies them by family: four R_9 - 2,
  R_7^+ - 1, R_8 - 1, nine subsets of the three-triangle 9-set, twenty lattice sets, two
  subsets of the square-with-apexes 8-set, two "R_5 plus two points" inside the doubled
  R_5, and three more given by their distance ratios 1 : sqrt2 : 2 : sqrt5,
  1 : sqrt(2+sqrt3) : sqrt(4+2sqrt3) : sqrt(5+2sqrt3), 1 : sqrt2 : sqrt(2+sqrt3) :
  sqrt(4+sqrt3). e78.py rebuilds every family with the stated counts.

* **X. Wei, *Classification of eleven-point five-distance sets in the plane*, Ars
  Combin. **102** (2011) 505-515.** Scanned PDF from combinatorialpress.com, read from
  page images. [READ]; page 514 checked by me on the page image: Lemma 11 restates the
  Erdos-Fishburn 9-point classification (Figure 3a-3c), Lemma 12 restates Shinohara's
  8-point one (Figure 3d is the square with four apexes), and Theorem 13 reads "There
  are four 11-point 5-distance sets in the plane to within isomorphism, that are R11
  and the three configurations given in Figure 4." lat.py finds exactly three lattice
  ones, all subsets of the 12-point set.

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

* **P. Brass, *On the Erdos-diameter of sets*, Discrete Math. **150** (1996) 415-419.**
  The one dedicated paper on the planar problem. Publisher abstract [SECONDHAND]: "Let
  delta(n) denote the minimum diameter of a set of n points in the plane in which any
  two positive distances, if they are different, differ by at least one. Erdos
  conjectured that for n sufficiently big delta(n) = n - 1, the extremal configuration
  being n equidistant points on a line. We prove an asymptotic version of this
  conjecture for the special case of sets which lie in a parallel half-strip." Full
  text [NOT OBTAINED]: OpenAlex lists it as closed with no repository copy, there is no
  Wayback snapshot of the ScienceDirect page and no CORE record. Whether it contains
  exact values of delta(n) for small n is therefore unknown; the draft comment names
  the paper and does not claim priority for the table.
* Brass, Moser, Pach, *Research Problems in Discrete Geometry*, the distances chapter.
* P. Brass, *Erdos distance problems in normed spaces*, Comput. Geom. **6** (1996), which
  cites Piepmeyer and Kanold.
* Harborth and Piepmeyer, *Three distinct distances in the plane*, Geom. Dedicata **61**
  (1996) 315-327.
