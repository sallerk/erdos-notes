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
* **Shinohara**, "Uniqueness of maximum planar five-distance sets", Discrete Math.
  (2008). Gives g(5) = 12 **and** the uniqueness of the extremal set. The argument in
  the note needs the uniqueness, not merely the value.  *[secondary]*
* **Wei**, "A Proof of Erdős-Fishburn's Conjecture for g(6)=13", Electron. J. Combin.
  **19**(4) (2012), #P38.  *[secondary]*

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
