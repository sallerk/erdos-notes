DRAFT for https://www.erdosproblems.com/forum/thread/98
NOT POSTED.

Novelty checked: no table of small values found in Brass-Moser-Pach section 5.5 (pp.
214-216, the general-position section, accessed via Google Books search-within-volume),
Sheffer's survey, the Handbook Table 1.2.4, Dumitrescu 2008, the crescent-configuration
papers, or OEIS (full-text "cocircular", "concyclic", "no four on a circle" all negative;
A186704 and A131628 are the unrestricted versions). Erdos-Fishburn, Discrete Math. 175
(1997) 97-132, was checked specifically as the likeliest hiding place and is a DIFFERENT
function: per its zbMATH review, the minimum SUM of per-point distance degrees over
unrestricted sets, (Sigma_3..Sigma_8) = (3,6,10,15,19,24). Confidence the values are
unpublished: ~90%, resting on searches failing to find them.

Before posting, note forum Rules 1 and 2. audit98.py re-checks, in exact arithmetic and
sharing no code with the searches that produced them: every witness in real plane
coordinates, monotonicity, the counting arguments of sections 2 and 2a, the pentagon
eliminant, the algebraic steps that dispose of two of the 28 n=7 candidates, and the
lower-bound window. It does NOT re-run the enumerations or the augmentation chain, which is
where the weakest link (assumption A8) lives; REPRODUCE.md gives those commands.

---

Exact small values of $h(n)$, and a lower bound they improve.

Writing $h(n)$ as on this page (Sheffer's survey calls it $D_{gen}(n)$), I get

$$h(3)=1,\quad h(4)=2,\quad h(5)=3,\quad h(6)=4,\quad h(7)=5,$$

so $h(n)=n-2$ throughout the computed range. Each upper bound is an explicit configuration, re-verified in exact plane coordinates: no three collinear, no four cocircular, distance count as claimed. The $n=5$ witness is $(0,0)$, $(1,0)$, $(1/2,\sqrt3/2)$, $(-\sqrt3/2,-1/2)$, $(1/2,-(2+\sqrt3)/2)$, with squared distances $\{1,\,2+\sqrt3,\,4+2\sqrt3\}$; the others are triangular-lattice sets.

The lower bounds are decided over the reals, not on a lattice. Realisability is equivalent to the Gram matrix being positive semidefinite of rank at most $2$, so every $3\times3$ minor vanishes; those minors are polynomials in the distance classes alone, which keeps the systems small. $h(5)>2$ reduces to the pentagon pattern, whose eliminant is $t^2-3t+1$, both roots giving cocircular realisations. $h(6)>3$ reduces to three patterns. $h(7)>4$ reduces $4^{21}$ colourings to $28$, and all $28$ then fall with no solver at all: $27$ die to the observation that at most two points are equidistant from any pair (a perpendicular bisector is a line and no three points are collinear), and the last uses fewer than four classes, so monotonicity against $h(6)=4$ kills it.

For comparison, Erdős–Hickerson–Pach record (Amer. Math. Monthly **96** (1989) 569–575, p. 571) that Szemerédi conjectured $h(n)\ge (n-1)/2$, generalising Altman. Every value above satisfies it, with equality at $n=3$ and a margin rising from $4/3$ at $n=4$ to $5/3$ at $n=7$.

Two consequences seem worth recording. Since $h$ is non-decreasing, these values give a **better lower bound than $\lceil (n-1)/3\rceil$ for $4\le n\le 13$**, that bound not reaching $5$ until $n=14$. And attaining $(n-1)/3$ forces every distance class to be $3$-regular on all $n$ points, so it needs $n\equiv 4 \pmod 6$; $n=4$ and $n=10$ are impossible, and $n=16$ now requires exact equality.

One remark on why the constant is stuck. The no-four-cocircular hypothesis caps each class at $3$ per vertex, giving $Z(P)\le n(n-1)$ isosceles triples, which is *exactly* the perpendicular-bisector bound from no-three-collinear alone. The two hypotheses give the same number, so this hypothesis is inert for the counting argument, and a search for the true maximum of $Z$ found the ratio rising ($0.500$ at $n=5$, $0.600$ at $n=6$). A search gives only a *lower* bound on the maximum, so the true ratios are at least these; two points are not a trend, but the direction is unfavourable, and if the ratio tends to $1$ no constant-factor improvement is available by this route.

One caveat I would rather state than hide. The reduction of $4^{21}$ colourings to $28$ used seed sets pruned by an exact decider whose completeness is an assumption; the *disposal* of the $28$ is solver-free, but their *generation* is not. Of the $153$ borderline rejections that pruning rests on, $57$ have since been re-confirmed by independent sound methods (a trivial Groebner ideal, or z3's nlsat with no ordering imposed on the class values) and $96$ have not. No false rejection has been found, but the possibility that a $29$th candidate was never generated is not excluded.

Nothing here bears on $h(n)/n\to\infty$.

Code, witnesses and a standalone audit:
https://github.com/sallerk/erdos-notes/tree/main/p98

Disclosure: the searches and computations were done with AI assistance.
