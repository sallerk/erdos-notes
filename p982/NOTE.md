# Erdos #982 (distinct distances from a vertex of a convex polygon)

Problem page: https://www.erdosproblems.com/982

This is the full note. The forum comment is a summary of it. Bibliography with provenance for every reference is in `REFERENCES.md` alongside.

The conjecture holds for every convex $n$-gon with $n \le 7$, and a near-miss family that gets exactly halfway.

Two remarks, one certification and one construction. Both concern small $n$, so they are orthogonal to the asymptotic line of work; Moser's $\lceil n/3 \rceil$, through Erdős-Fishburn and Dumitrescu, to the published record of Nivasch, Pach, Pinchasi and Zerbib at $(13/36 + 1/22701)n - O(1)$, and to the improvement claimed on the proof-claims tab by Kominers, which raises the coefficient from 13/36 + 1/22701 to 13/36 + 3/5270 and which as far as I know has not yet been examined. Nothing below depends on which of those is current. I could not find a previous computational attack on the small-$n$ cases; that is a negative search result over public sources, not a claim that none exists, and the Kominers claim shows the problem is actively being worked on.

First, small $n$ is settled over the reals. Writing the conjecture in the contrapositive, a counterexample on $n$ points is a convex $n$-gon in which every vertex sees at most $\lfloor n/2 \rfloor - 1$ distinct distances. I encoded that as a decision problem over the reals (vertices as real coordinates, convex position as strict sign conditions on $2 \times 2$ determinants, and the per-vertex distance pattern as an equality-and-inequality system on squared distances); and discharged it with an SMT solver over an exhaustive enumeration of the possible patterns. Every instance came back unsatisfiable.

A note on provenance, since it bears on the Altman dependency below. The problem page cites [Er75f, p.100], and that page states three conjectures of Erdős about convex polygons in one paragraph: the first, that a convex $n$-gon determines at least $\lfloor n/2 \rfloor$ distances in total, which Erdős there records as "proved by ALTMAN"; the second, $\max_i d_2(x_i) \ge n/2$, which he calls "not yet settled" and which is this problem; and the third, the equidistance conjecture that is problem [97]. So the theorem used as a prune here and the problem being attacked are neighbours in a single paragraph of the cited source.

One convention should be stated, since it is live on the neighbouring problem [97]: "convex polygon" is read here as strict convex position, so interior points, repeated points and collinear boundary triples are all excluded. Allowing redundant $180^\circ$ boundary vertices would need a separate degenerate-case reduction, which I have not done.

> For every $n \le 7$, every convex $n$-gon in the plane has a vertex with at least $\lfloor n/2 \rfloor$ distinct distances to the other vertices.

This is over the reals, not over a lattice or a finite pool. The cases $n = 4, 5$ need a single formula; $n = 6$ took $316$ pattern classes and $n = 7$ took all $5354$, with no unknowns left. As a guard against the encoding being vacuously unsatisfiable I also substituted explicit polygons into every constraint by hand, without the solver, and confirmed the constraints are the intended ones. The obstruction to going further is combinatorial rather than the solver: the pattern enumeration passes three million colourings at $n = 8$.

One dependency should be declared. The enumeration prunes using Altman's theorem (the vertices of a convex $n$-gon determine at least $\lfloor n/2 \rfloor$ distinct distances in total (Altman, "On a problem of P. Erdős", Amer. Math. Monthly 70 (1963), 148-157)); to bound the number of distance classes a pattern may use. Dropping that filter multiplies the enumeration by about fifteen: $1834$ classes instead of $316$ at $n = 6$, and $81278$ instead of $5354$ at $n = 7$. I ran the unfiltered enumeration at $n = 6$ and all $1834$ classes are likewise unsatisfiable, so $n \le 6$ is unconditional; $n = 7$ rests on Altman's theorem, which is of course not in doubt, but the reader should know the statement is not self-contained.

Second, a structural observation and the family that comes closest. No set of points on a single circle can ever be a counterexample: for concyclic points $|v_\alpha - v_\beta| = 2R|\sin((\alpha-\beta)/2)|$, so two vertices are equidistant from $v$ exactly when they are symmetric about the diameter through $v$, and hence every distance from a vertex has multiplicity at most $2$. So a counterexample needs at least two radii, and the natural next family is two concentric rings.

That family gets exactly halfway and no further. Take two staggered concentric regular $m$-gons (outer radius $1$ at angles $2\pi k/m$, inner radius $b$ at the interleaved angles); giving a convex $2m$-gon. For every even $n = 2m$ with $6 \le n \le 28$ there is a choice of $b$ for which exactly half the vertices reach the counterexample budget of $\lfloor n/2 \rfloor - 1$, and the other half miss it by one. The failure is always the same half, so it is structural rather than an artefact of the search.

The smallest case is exact and worth writing down. Two staggered concentric triangles with inner radius $b = \sqrt{3} - 1$ give a convex hexagon whose six vertices have distinct-distance counts $2, 3, 2, 3, 2, 3$ in cyclic order, against a budget of $\lfloor 6/2 \rfloor - 1 = 2$. Three of the six vertices are already at the budget. By the $n = 6$ certification above this is extremal: no convex hexagon does better. Sweeping the same two-ring family out to $m = 1200$ never improves on half.

So the picture at small $n$ is that the conjecture is not close to failing; the best structured family stalls at half the vertices, and the exhaustive check closes $n \le 7$.

On what is verified and what is not, since some of this is machine work. The hexagon above is exact in $\mathbb{Q}(\sqrt{3})$: convex position from exact determinant signs, distance counts from exact squared distances, no floating point. The concyclic remark is a two-line proof. The $n \le 7$ certification is a solver result over an exhaustive pattern enumeration, checked for non-vacuity as described but not independently re-derived by a second implementation, and unconditional only up to $n = 6$; I would treat it accordingly.

One control fails and the reader should know which. The non-vacuity control that matters (substituting explicit convex polygons into every constraint in exact arithmetic, with no solver involved) passes. But the positive solver control, which hands z3 the colouring of a convex lattice polygon and requires SAT because a rational model exists, returns `unknown` for the lattice hexagon, heptagon and octagon, at a 60-second budget and equally at 900 seconds; only the pentagon comes back SAT, and it does so instantly. So the wall is at n >= 6 and is not an artefact of the cutoff. That does not undermine the result, because nlsat is complete for the existential theory of the reals and so an UNSAT answer is a proof, and every one of the 316 classes at $n = 6$ and all 5354 at $n = 7$ resolved to UNSAT rather than to unknown. What it does mean is that this pipeline proves unsatisfiability far more readily than it exhibits models: a satisfiable class would most likely have shown up as a timeout rather than as SAT. The conclusion rests on everything having resolved, not on the solver having been shown able to find models at $n \ge 6$. See `REPRODUCE.md`. The two-ring sweep to $m = 1200$ is a search, not a proof, and rules out only that family.

Disclosure: the searches, computations and the drafting of this note were done with AI assistance.

## Files in this directory

Documentation: `REPRODUCE.md` (step-by-step, with the actual output of each command),
`REFERENCES.md`, `RESULTS.md`, `LITERATURE.md`.

Verification, none of which shares code with the searches: `audit.py` (standalone
re-derivation of every checkable claim), `verify_machinery.py`, `verify_artifacts.py`,
`control_decide.py` (the controls, including the failing one discussed above).

Search and decision: `patterns.py` (enumeration), `decide.py`, `decide2.py`,
`decide_alt.py`, `retry_unknown.py`, `core.py`, `run_batch.py`, `lattice.py`,
`nsearch.py`, `tworing.py`, `tworing_par.py`, `tworing_rho.py`, `nearmiss.py`,
`artifact.py`, `export_artifacts.py`.

Run records: `decide_n6.json`, `decide_n6_noaltman.json`, `decide_n7.json`,
`decide2_n4.json`, `decide2_n5.json`, `decide_alt_n6.json`, `tworing_m3_1200.json`,
`tworing_rho_3_24.json`, `nearmiss_3_14.json`.
