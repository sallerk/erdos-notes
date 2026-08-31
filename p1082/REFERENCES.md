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
