# References for the #1082 note

## From the problem page (https://www.erdosproblems.com/1082, read 2026-08-31)

Verbatim: "The second stronger question has a negative answer: there is a construction
of 8 points such that each point has exactly three distinct distances to the others.
This first appeared in the literature in a paper of Erdős and Fishburn **[ErFi97b]**,
where they credit the construction to **Harborth**. This configuration is studied in
detail by Fishburn **[Fi02]**."  *[VERIFIED AT SOURCE]*

The page also records that the construction was later rediscovered by DeepMind, and
that an earlier 42-point construction was given in the comments by **Xichuan**.
*[VERIFIED AT SOURCE]*

## The g(k) values the argument uses

* **P. Erdős and P. Fishburn**, "Maximum planar sets that determine k distances",
  Discrete Math. **160** (1996), 115-125. Source of g(k) for k <= 4.  *[secondary]*
* **Masashi Shinohara**, "Uniqueness of maximum planar five-distance sets", Discrete
  Mathematics **308** (2008), 3048-3055, doi:10.1016/j.disc.2007.08.028. Gives
  g(5) = 12 **and** the uniqueness of the extremal set. The argument in the note needs
  the uniqueness, not merely the value.
  *[bibliographic data VERIFIED AT SOURCE via Crossref 2026-08-31; the proof itself
  not read]*
* **Xianglin Wei**, "A Proof of Erdős-Fishburn's Conjecture for g(6)=13", The
  Electronic Journal of Combinatorics **19**(4) (2012), #P38. Abstract verbatim:
  "The 6-distance conjecture of Erdős and Fishburn states that 13 is the maximum
  number of points in the plane that determine exactly 6 different distances. In this
  paper, we prove the conjecture."
  *[VERIFIED AT SOURCE: journal page read 2026-08-31; the proof itself not read]*

  **A definitional point that matters.** The literature defines a k-distance set as
  one with EXACTLY k distances, and g(k) as the largest such set. The note uses g(k)
  for the largest set with AT MOST k distances, which is what the argument needs. The
  two agree for k <= 6 because the values 3, 5, 7, 9, 12, 13 are increasing, so the
  maximum over j <= k is attained at j = k. For larger k this would need re-checking.

A caution on attribution, since it bit me once: **g(5) = 12 is Shinohara's**, not
Erdős-Fishburn's; Erdős and Fishburn resolved k <= 4.

* **E. Altman**, "On a problem of P. Erdős", Amer. Math. Monthly **70** (1963),
  148-157. A convex n-gon determines at least floor(n/2) distinct distances, so, since
  points in convex position are automatically no-three-collinear, this is exactly the
  first question restricted to convex position and any counterexample must be
  non-convex. The attribution to Altman is stated by Erdős himself in the 1975 survey,
  p. 100.  *[secondary for the paper; attribution VERIFIED AT SOURCE via Erdős 1975]*

## Artifacts here

`RESULTS.md` and the search code: `phase1.py`, `phase2_lattice.py`, `phase2_z3.py`,
`search.py`, `extend.py`, `extend_control.py`, `frontier.py`, `concentric.py`,
`cyclo.py`, `geo.py`, `check_two_classes.py`, `z3_decisive.py`, and the verifiers
`verify_machinery.py`, `verify_set1.py`.

## Provenance of the Harborth configuration, from the thread

Moritz Firsching wrote to Heiko Harborth directly and reported the reply on the #1082
thread (20:52, 28 Feb 2026): Harborth found the configuration himself and told Erdos
about it at a conference, and a subset of it already appears as the third of the nine
six-point three-distance configurations in

* **H. Harborth and L. Piepmeyer**, "Three distinct distances in the plane",
  Geometria Dedicata **61** (1996), 315-327, Figure 2.
  *[VERIFIED AT SOURCE that this is what the thread reports; the paper itself not read]*

The configuration is studied in **Fishburn**, Discrete Math. (2002),
https://www.sciencedirect.com/science/article/pii/S0012365X01001340 , whose abstract
begins "I first heard about $H_8$ from Paul Erdos ... who learned about it from Heiko
Harborth."  *[VERIFIED AT SOURCE: quoted in the thread by BorisAlexeev and Firsching]*

BorisAlexeev's description of $H_8$, which I re-derived and checked exactly: take a
square, erect an outward equilateral triangle on each side, and use the four apexes as
the remaining points. With the square at $(\pm 1, \pm 1)$ the apexes are at distance
$1+\sqrt3$ from the centre and the square vertices at $\sqrt2$, so the eight points lie
on exactly **two** concentric circles. Each point sees exactly $3$ distinct distances,
which is fewer than $\lfloor 8/2 \rfloor = 4$, so the second question fails; but the
set determines $4$ distinct distances in total, so the **first** question holds for it.
*[VERIFIED: recomputed exactly in sympy]*


## Novelty check (added 2026-08-31, after the same check overturned the #982 note)

The arithmetic test first, on the bound the problem page states. Sheffer's survey
"Distinct Distances: Open Problems and Current Bounds" (arXiv:1406.1949) records the
published lower bound for this problem as D_no3l(n) >= ceil((n-1)/3), attributed to
Szemeredi and communicated by Erdos, against the conjectured floor(n/2). Evaluating:

     n      4  5  6  7  8  9 10 11 12 13 14 15
     floor(n/2)  2  2  3  3  4  4  5  5  6  6  7  7
     ceil((n-1)/3)  1  2  2  2  3  3  3  4  4  4  5  5

so the published bound settles only n = 5 in this range. The note's n <= 15 therefore
goes well beyond it, unlike the #982 note, whose claimed range turned out to be
entirely covered by published bounds.

Three further checks, all negative for prior art:

* The 21 comments on the forum thread are all about the SECOND question (Harborth's
  H_8, the DeepMind Lean proof, and the attribution to Harborth via Erdos). None
  mentions g(5), g(6), Shinohara, Wei, or 2k+1. BorisAlexeev states there that "the
  main conjecture is still open".
* Sheffer's survey gives no exact small-n values for this problem and remarks that
  "the last progress made for Problem [6] was several decades ago" (survey dated 2014).
* No source found that studies the no-three-collinear maximum h(k) as a quantity in
  its own right.

**Residual uncertainty, stated plainly.** The k = 6 case cannot predate Wei (2012), so
the full n <= 15 statement is at most fourteen years old and is absent from the 2014
survey. But the derivation from published g(k) is short, and a short corollary can be
folklore without ever being written down. This is a negative search over public
sources, not a proof of novelty.