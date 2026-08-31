# Erdos #1082 (no three collinear, distinct distances)

Problem page: https://www.erdosproblems.com/1082

This is the full note. The forum comment is a summary of it. Bibliography with provenance for every reference is in `REFERENCES.md` alongside.

The first question holds for all $n \le 15$.

Every comment on this page so far addresses the second question (must some single point see $\lfloor n/2 \rfloor$ distinct distances?); which Harborth's $8$-point set refutes. This note concerns the first question: must the whole set determine at least $\lfloor n/2 \rfloor$ distinct distances?

A convenient reformulation. Following Erdős and Fishburn, let $g(k)$ denote the largest number of points in the plane determining at most $k$ distinct pairwise distances, and let $h(k)$ denote the same quantity with the additional requirement that no three of the points are collinear. Both are non-decreasing in $k$. A counterexample on $n$ points with $k$ distinct distances needs $k < \lfloor n/2 \rfloor$, that is $\lfloor n/2 \rfloor \ge k+1$, that is $n \ge 2k+2$. Hence the first question is exactly the assertion that $h(k) \le 2k+1$ for every $k \ge 1$.

The reverse inequality is free: a regular $(2k+1)$-gon has $2k+1$ vertices, exactly $k$ distinct distances, and no three vertices collinear, so $h(k) \ge 2k+1$ always. Therefore the first question is equivalent to $h(k) = 2k+1$ for every $k$, i.e. the regular odd polygon is exactly optimal, with no slack at any $k$. That absence of slack seems to me the main obstruction: the bound $\lfloor n/2 \rfloor$ is attained for every $n$, so no counting argument has room to work in.

Reduction to one case. Since $h(k) \le g(k)$, we get $h(k) = 2k+1$ for free whenever $g(k) = 2k+1$. The published values are $g(1),\dots,g(6) = 3, 5, 7, 9, 12, 13$, resolved by Erdős and Fishburn for $k \le 4$ ("Maximum planar sets that determine $k$ distances", Discrete Math. 160 (1996), 115-125), by Shinohara for $k = 5$, and by Wei for $k = 6$ ("A Proof of Erdős-Fishburn's Conjecture for $g(6)=13$", Electron. J. Combin. 19(4) (2012), #P38). Against $2k+1 = 3, 5, 7, 9, 11, 13$, exactly one case fails to close immediately: $k = 5$, where $g(5) = 12 = 2k+2$.

The case $k = 5$. Shinohara proved both that $g(5) = 12$ and that the maximum planar $5$-distance set is unique ("Uniqueness of maximum planar five-distance sets", Discrete Math., 2008); it is the uniqueness that the argument below needs. In the triangular lattice, writing points as Eisenstein integers $a + b\omega$ with $\omega = e^{i\pi/3}$, the squared distance between $(a_1,b_1)$ and $(a_2,b_2)$ is the integer $p^2 + pq + q^2$, where $p = a_1 - a_2$ and $q = b_1 - b_2$. That set is (0,0), (0,1), (0,2), (1,-1), (1,0), (1,1), (1,2), (2,-1), (2,0), (2,1), (3,-1), (3,0), with squared distances $1, 3, 4, 7, 9$, confirming $k = 5$ and $n = 12$. This set contains $18$ collinear triples, for instance $\{(0,0),(0,1),(0,2)\}$ and $\{(0,0),(1,0),(2,0)\}$. So it is not a counterexample, and by uniqueness $h(5) = 11 = 2 \cdot 5 + 1$.

Proposition. Every planar set of $n \le 15$ points with no three collinear determines at least $\lfloor n/2 \rfloor$ distinct distances.

Proof. Suppose an $n$-point set with no three collinear has $k < \lfloor n/2 \rfloor$ distinct distances, with $n \le 15$. Write $m = \lfloor n/2 \rfloor$. Then $k \le m - 1 \le 6$, and $h(k) = 2k+1$ for all $k \le 6$ by the above. The set has $k$ distances and no three collinear, so $n \le h(k) = 2k+1$. Since $k \le m-1$ this gives $n \le 2(m-1)+1 = 2m-1$. Finally $2m-1 \le n-1$ because $2m \le n$, so $n \le n-1$, a contradiction.

It is worth stating what this shows. Without the collinearity hypothesis the inequality is already false at $n = 12$, since $5 < \lfloor 12/2 \rfloor = 6$. Those $18$ collinear triples are the only thing saving the conjecture there; the entire content of the first question is the collinearity condition.

The frontier. A counterexample on $n$ points needs $n \le g(\lfloor n/2 \rfloor - 1)$. Running that against the published $g$ values leaves the smallest conceivable counterexample at $n = 16$ with $7$ distances, and it must be a maximum $7$-distance set, so $g(7) \ge 16$ is a prerequisite. This is open only because $g(7)$ is unknown.

A conditional remark on the triangular lattice. Searching the lattice $A_2$ over a pool of $271$ points (all points of squared norm $\le 75$, restricted to sets of squared diameter $\le 75$, giving $28$ admissible distance values) gives $g_{A_2}(7) = 16$ and $h_{A_2}(7) = 10$. So the lattice does contain a $16$-point $7$-distance set (the counting frontier is live); but the largest with no three collinear has only $10$ points. Hence if the Erdős-Fishburn triangular-lattice conjecture holds at $k = 7$, then $n = 16$ is closed. Unconditionally it remains open. As a check on the search, the same code returns $g_{A_2}(5) = 12$, agreeing with the known value of $g(5)$.

Convex position is already settled, and worth stating explicitly since it does not seem to have been said on this page. Altman ("On a problem of P. Erdős", Amer. Math. Monthly 70 (1963), 148-157) proved that the vertices of any convex $n$-gon determine at least $\lfloor n/2 \rfloor$ distinct distances, with equality for odd $n$ only for the regular $n$-gon. Points in convex position are automatically no-three-collinear, so Altman's theorem is exactly the first question restricted to convex position, and it has been true since 1963. Hence any counterexample must be non-convex. That also subsumes the concyclic case: a set on one circle is in convex position, which is the real reason both known counterexamples to the second question need two concentric circles rather than one.

So the search has to allow non-convex configurations, and the natural place to look is a highly symmetric convex core with extra points inside. Taking the core to be a subset of a regular polygon: every subset $S$ of a regular $m$-gon with $m \le 24$, $|S| \ge 9$ and at most $7$ distinct distances was enumerated (since the distances of $\{\zeta_m^j : j \in S\}$ are the circular differences $\min(d, m-d)$, this is a pure computation in $\mathbb{Z}_m$); giving $656$ subsets up to the dihedral group, none at all for $m = 16, 17, 19, 23$, and $380$ of them subsets of the regular $15$-gon. The regular $15$-gon itself admits no $16$th point anywhere in the plane: it already realises all $7$ chord lengths, so a new point would have to be at a chord distance from all $15$ vertices simultaneously, and none of the $7980$ circle-circle intersections does that.

Natural next step, which I have not done: classify the $(2k+1)$-point, $k$-distance, no-three-collinear configurations at $k = 7$; is the regular $15$-gon the only one? Combined with a circle-intersection extension test, which is complete and pool-free once those sets are known, that would settle $n = 16$ outright. One warning for anyone attempting it by exact algebra: fixing three base points and pinning each further point by its distance triple gives $k^3$ candidates of which $2k-2$ are needed, so the $17{,}550$ four-subsets at $k = 3$ become about $4.6 \times 10^{21}$ twelve-subsets at $k = 7$. A Gröbner-basis search over the $k = 3$ case terminates in about an hour; that route does not reach $k = 7$.

A note on what is verified. The $k = 5$ computation was checked four independent ways, and the lattice and polygon searches above were each re-derived a second time from the definitions, the lattice one against the known $g(5) = 12$ as a control. The $k = 5$ case and the lattice search are exact throughout: collinearity is the sign of an integer $3 \times 3$ determinant and squared distances are integers, so no floating-point value is load-bearing there. The one exception is the $15$-gon extension test, which is high-precision numerical rather than exact; but not close: over all $7980$ intersection points, the best candidate still misses having all $15$ of its distances be chord lengths by more than $0.137$, in a configuration of diameter $2$. That is a gap of a different order from any precision question, though a fully exact version would want algebraic-number arithmetic. The only new mathematical ingredient is $h(5) = 11$; the rest is published $g(k)$ data, elementary deduction, and finite search.

Disclosure: the searches, computations and the drafting of this note were done with AI assistance.

## Files in this directory

* `REFERENCES.md`
* `RESULTS.md`
* `check_two_classes.py`
* `concentric.py`
* `cyclo.py`
* `extend.py`
* `extend_control.py`
* `frontier.py`
* `geo.py`
* `phase1.py`
* `phase2_lattice.py`
* `phase2_z3.py`
* `search.py`
* `verify_machinery.py`
* `verify_set1.py`
* `z3_decisive.py`
