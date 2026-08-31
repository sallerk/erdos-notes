# Erdos #982 (distinct distances from a vertex of a convex polygon)

Full note. The forum comment is a summary of this page.

The conjecture holds for every convex $n$-gon with $n \le 7$, and a near-miss family that gets exactly halfway.

Two remarks, one certification and one construction. Both concern small $n$, so they are orthogonal to the asymptotic line of work — Moser's $\lceil n/3 \rceil$, through Erdős–Fishburn and Dumitrescu, to the published record of Nivasch, Pach, Pinchasi and Zerbib at $(13/36 + 1/22701)n - O(1)$, and to the further improvement of the additive term claimed on this page by Kominers, which as far as I know has not yet been examined. Nothing below depends on which of those is current. As far as I can find, no computational attack on this problem has been reported.

First, small $n$ is settled over the reals. Writing the conjecture in the contrapositive, a counterexample on $n$ points is a convex $n$-gon in which every vertex sees at most $\lfloor n/2 \rfloor - 1$ distinct distances. I encoded that as a decision problem over the reals — vertices as real coordinates, convex position as strict sign conditions on $2 \times 2$ determinants, and the per-vertex distance pattern as an equality-and-inequality system on squared distances — and discharged it with an SMT solver over an exhaustive enumeration of the possible patterns. Every instance came back unsatisfiable.

One convention should be stated, since it is live on the neighbouring problem [97]: "convex polygon" is read here as strict convex position, so interior points, repeated points and collinear boundary triples are all excluded. Allowing redundant $180^\circ$ boundary vertices would need a separate degenerate-case reduction, which I have not done.

> For every $n \le 7$, every convex $n$-gon in the plane has a vertex with at least $\lfloor n/2 \rfloor$ distinct distances to the other vertices.

This is over the reals, not over a lattice or a finite pool. The cases $n = 4, 5$ need a single formula; $n = 6$ took $316$ pattern classes and $n = 7$ took all $5354$, with no unknowns left. As a guard against the encoding being vacuously unsatisfiable I also substituted explicit polygons into every constraint by hand, without the solver, and confirmed the constraints are the intended ones. The obstruction to going further is combinatorial rather than the solver: the pattern enumeration passes three million colourings at $n = 8$.

One dependency should be declared. The enumeration prunes using Altman's theorem — the vertices of a convex $n$-gon determine at least $\lfloor n/2 \rfloor$ distinct distances in total (Altman, "On a problem of P. Erdős", Amer. Math. Monthly 70 (1963), 148–157) — to bound the number of distance classes a pattern may use. Dropping that filter multiplies the enumeration by about fifteen: $1834$ classes instead of $316$ at $n = 6$, and $81278$ instead of $5354$ at $n = 7$. I ran the unfiltered enumeration at $n = 6$ and all $1834$ classes are likewise unsatisfiable, so $n \le 6$ is unconditional; $n = 7$ rests on Altman's theorem, which is of course not in doubt, but the reader should know the statement is not self-contained.

Second, a structural observation and the family that comes closest. No set of points on a single circle can ever be a counterexample: for concyclic points $|v_\alpha - v_\beta| = 2R|\sin((\alpha-\beta)/2)|$, so two vertices are equidistant from $v$ exactly when they are symmetric about the diameter through $v$, and hence every distance from a vertex has multiplicity at most $2$. So a counterexample needs at least two radii, and the natural next family is two concentric rings.

That family gets exactly halfway and no further. Take two staggered concentric regular $m$-gons — outer radius $1$ at angles $2\pi k/m$, inner radius $b$ at the interleaved angles — giving a convex $2m$-gon. For every even $n = 2m$ with $6 \le n \le 28$ there is a choice of $b$ for which exactly half the vertices reach the counterexample budget of $\lfloor n/2 \rfloor - 1$, and the other half miss it by one. The failure is always the same half, so it is structural rather than an artefact of the search.

The smallest case is exact and worth writing down. Two staggered concentric triangles with inner radius $b = \sqrt{3} - 1$ give a convex hexagon whose six vertices have distinct-distance counts $2, 3, 2, 3, 2, 3$ in cyclic order, against a budget of $\lfloor 6/2 \rfloor - 1 = 2$. Three of the six vertices are already at the budget. By the $n = 6$ certification above this is extremal: no convex hexagon does better. Sweeping the same two-ring family out to $m = 1200$ never improves on half.

So the picture at small $n$ is that the conjecture is not close to failing — the best structured family stalls at half the vertices, and the exhaustive check closes $n \le 7$.

On what is verified and what is not, since some of this is machine work. The hexagon above is exact in $\mathbb{Q}(\sqrt{3})$: convex position from exact determinant signs, distance counts from exact squared distances, no floating point. The concyclic remark is a two-line proof. The $n \le 7$ certification is a solver result over an exhaustive pattern enumeration, checked for non-vacuity as described but not independently re-derived by a second implementation, and unconditional only up to $n = 6$; I would treat it accordingly. The two-ring sweep to $m = 1200$ is a search, not a proof, and rules out only that family.

Disclosure: the searches, computations and the drafting of this comment were done with AI assistance.
