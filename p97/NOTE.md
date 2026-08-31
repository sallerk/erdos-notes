# Erdos #97 (four equidistant vertices of a convex polygon)

Problem page: https://www.erdosproblems.com/97

This is the full note. The forum comment is a summary of it. Bibliography with provenance for every reference is in `REFERENCES.md` alongside.

A theorem ruling out the symmetric families, and exact coordinates for Danzer's construction.

Context, so as not to repeat spent work: AlphaEvolve attacked this numerically (Problem 6.53 of arXiv:2511.02864) and reached $k = 3$ but not $k = 4$, so I worked the exact and symmetric side instead. Nothing below contradicts TheAbandonedThinker's $n \ge 7$ or mysticflounder's programme; those bound the size of a counterexample, this restricts its symmetry, and it holds for every $n$.

First a triviality worth recording. On a single circle $|v_\alpha - v_\beta| = 2R|\sin((\alpha-\beta)/2)|$, so two vertices are equidistant from $v$ exactly when they are symmetric about the diameter through $v$. Hence every distance from a vertex of a cyclic polygon has multiplicity at most $2$: even $k = 3$ needs at least two radii.

THEOREM. No counterexample has dihedral symmetry $D_m$, $m \ge 2$, with all of its vertices on mirror lines.

Proof. A line through the centre meets a convex curve twice, so each mirror carries at most $2$ vertices and $n = m$ or $n = 2m$. The case $n = m$ is a regular $m$-gon, dead by the paragraph above. The case $n = 2m$ forces the alternating $2m$-gon $v_l = \rho_l e^{i\pi l/m}$ with $\rho_l = 1$ for $l$ even and $\rho_l = b$ for $l$ odd, which is in convex position exactly when $\cos(\pi/m) < b < 1/\cos(\pi/m)$. For every $m$ and every $b$ in that window the distances $|v_0 - v_l|$, $l = 0, \dots, m-1$, are strictly increasing. For $l$ even the step reduces to the upward parabola $b^2 - 2c_{l+1}b + 2c_l - 1$ (writing $c_i = \cos(i\pi/m)$), whose larger root lies below $\cos(\pi/m)$ exactly when $2\sin((l+1)\pi/m)\sin(\pi/m) - \sin^2(\pi/m) > 0$; that holds because $\sin((l+1)\pi/m) \ge \sin(\pi/m)$ for $1 \le l+1 \le m-1$. For $l$ odd the roles of the radii swap and the requirement becomes $b^2 - 2c_l b + 2c_{l+1} - 1 < 0$ across the window, which follows from negativity at both ends: at the lower end the value is $-\sin(\pi/m)(\sin(\pi/m) + 2\sin(l\pi/m))$, negative automatically, and at the upper end it is $-\sin(\pi/m)(2\sin((l+1)\pi/m)\cos(\pi/m) - \sin(\pi/m))$ after scaling, negative exactly when $2\cos(\pi/m) > 1$, i.e. $m \ge 4$. The case $m = 3$ is the one degenerate point: there the parabola is $(b-2)(b+1)$ and the upper endpoint $b = 2$ is exactly a root, but the convexity window is open, so the step is still strict on it. So each distance from $v_0$ is attained at most twice among $v_1, \dots, v_{m-1}$ and their mirror images, plus at most once at the antipode $v_m$; maximum multiplicity $3$, never $4$. The $l = m$ step is the one that can drop, and that is exactly the loophole leaving room for $3$. That argument is stated at an even vertex; the odd vertices need no separate work, because $w_l = v_{l+1}/b$ is the alternating $2m$-gon with radii $(1, 1/b)$ rotated by $\pi/m$, and the convexity window is invariant under $b \mapsto 1/b$, so the odd-vertex case of $(1,b)$ is the even-vertex case of $(1,1/b)$.

Why $k = 4$ is hard. Under any finite symmetry a vertex gets at most $2$ equidistant partners for free, from its stabiliser and from its own orbit. So $k = 3$ costs one equation per orbit and $k = 4$ costs two. Against parameters: a $C_m$ configuration with $c$ orbits has $2c-2$ of them, a $D_m$ configuration with $a$ mirror and $g$ generic orbits has $a+2g-1$. For $k = 3$ under $C_3$ with $c = 3$ that is three equations in four unknowns, a one-parameter family; which is exactly Danzer. For $k = 4$ every symmetric family is overdetermined: by $2$ under $C_m$, by $1$ under $D_m$. The theorem also blocks the cheap escape, since two phase-aligned $C_m$ orbits form an alternating $2m$-gon and so can never supply the matching pair.

The least overdetermined survivor is $D_m$ with one mirror and one generic orbit, $n = 3m$, where two of the three ways to place the extra pair die for every $m$. A dense grid over $m = 3, \dots, 8$ found nothing. Converting that last step to an exact resultant over $\mathbb{Q}(e^{2\pi i/m})$ is small (two unknowns, low degree); and would close the family outright. That is the concrete next step, and I did not run it.

An artifact others may want. Danzer's theorem is usually cited without coordinates, so: a constructive $C_3$-symmetric convex $9$-gon with equilateral orbits, six of its vertices at $(1,0)$, $(-1/2, \sqrt{3}/2)$, $(-1/2, -\sqrt{3}/2)$, $(-1/2+\sqrt{3},\ \sqrt{3}/2)$, $(-\sqrt{3}/2-1/2,\ 3/2-\sqrt{3}/2)$, $(1-\sqrt{3}/2,\ -3/2)$, the other three in a field of degree at most $4$ over $\mathbb{Q}$. All nine vertices have maximum equidistant count exactly $3$, verified in exact arithmetic, and every one is exactly one short of $k = 4$. The full coordinates, exact, are in `artifact_danzer9_t0.json` in this directory, and `verify_p97.py` re-checks them.

The theorem was checked symbolically and numerically at 50 digits for $m \le 60$, and against an independent screen to $m = 200$; which initially disagreed, and the theorem is what exposed the bug in it. The search results are searches, not proofs, and are stated as such.

Disclosure: the searches, symbolic checks and the drafting of this note were done with AI assistance.

## The k = 3 minimality question

Erdos raised this alongside the k = 4 question in "On some problems of elementary and
combinatorial geometry", Ann. Mat. Pura Appl. (4) 103 (1975), 99-108, at p. 100:

> "Danzer's example is not yet published. It would be of interest to determine or
> estimate the smallest possible value of n."

(That passage also contains a wider claim, that Danzer settled every k, which the
problem page already discounts as a presumed error since Erdos never repeated it. See
`REFERENCES.md`. The minimality question is well posed for k = 3 regardless.)

**Result: the smallest n for the k = 3 property is at least 7, and at most 9 by Danzer.**

No strictly convex 4-gon, 5-gon or 6-gon has every vertex with three other vertices
equidistant from it.

| n | patterns | how decided | outcome |
|---|---|---|---|
| 4 | 1 | brute force over every pattern, no pruning | no configuration |
| 5 | 1,024 | brute force over every pattern, no pruning | no configuration |
| 6 | 66 classes | z3 over the reals, full convex position | all unsatisfiable |

The n = 4 and n = 5 cases use no pruning at all, so they depend on nothing but the
encoding. For n = 6 an independent numerical search (`numsearch.py`, sharing no code
with the solver path) agrees: 0 of 66 classes are realisable as a strictly convex
hexagon.

Two soundness checks on the pruning used at n = 6, both in `k3-minimality/`:
Danzer's real 9-gon pattern survives the prune at every depth (a prune that rejected a
realisable pattern would invalidate every conclusion), and 300 randomly chosen
prune-rejected patterns were handed to z3, which agreed all were unsatisfiable
(298 unsat, 2 timeouts, 0 satisfiable).

**n = 7 is NOT settled.** That run was stopped at 5.27% coverage, with 9,539 of
184,424 pattern classes decided and no configuration found. Finding nothing in 5% of a
space rules out only that 5%. The honest statement stops at n <= 6; see
`k3-minimality/STATUS_n7_AT_STOP.json`.

A trap worth recording: requiring only consecutive-triple orientations to be positive
is not convex position, since it also admits winding-2 star polygons. Under that weaker
constraint z3 reported 19 satisfiable patterns at n = 6, all of which vanish under the
correct all-triples constraint.


## Files in this directory

* `COMMENT_FULL.md`
* `REFERENCES.md`
* `RESULTS.md`
* `artifact_danzer9_t0.json`
* `k3-minimality`
* `theorem_alt.py`
* `verify_p97.py`
