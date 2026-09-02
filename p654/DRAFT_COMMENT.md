DRAFT for https://www.erdosproblems.com/forum/thread/654
NOT POSTED.

Novelty checked. No published small values found: OEIS has nothing (all 31 full-text
"distinct distances" sequences enumerated; A186704 and A131628 are the unrestricted
total-count versions, and the #654 page's own OEIS field reads "Possible"); Brass-Moser-Pach
section 5.5 (pp. 214-216) is asymptotic with no table; Sheffer's survey is asymptotic in
every version; the Aletheia construction is defined only for n >= 40. Erdos-Fishburn,
Discrete Math. 175 (1997) 97-132, was checked as the likeliest hiding place and is a
DIFFERENT function: per zbMATH review Zbl 0894.52007 it is the minimum SUM of per-point
distance degrees over UNRESTRICTED sets, (Sigma_3..Sigma_8) = (3,6,10,15,19,24). Confidence
~90%, resting on searches failing to find them; its full text is behind a 403 and only the
zbMATH review was read, and Brass-Moser-Pach was readable only in snippet view.

Before posting, note forum Rules 1 and 2. audit654.py re-derives, in exact arithmetic and
sharing no code with the searches that produced them: every witness and its pinned counts,
monotonicity, the trivial bound, $f(4)>1$, and the whole structural argument for $f(7)>2$;
it prints ALL CHECKS PASSED. It does NOT re-derive $f(5)>2$ and $f(6)>2$, which rest on the
pattern enumeration and the exact decider (with one pattern settled by z3); those are
reproduced by the commands in REPRODUCE.md instead.

---

Exact small values of $f(n)$.

Writing $f(n)$ as on this page, and $d(x_i)$ for the number of distinct distances from
$x_i$, I get

$$f(3)=1,\quad f(4)=2,\quad f(5)=3,\quad f(6)=3,\qquad f(7),\,f(8)\in\{3,4\}.$$

The same values hold under the stronger hypothesis of full general position (no three
collinear as well), which is the quantity Sheffer's survey calls $\hat D_{gen}(n)$. Worth
noting for anyone checking the reference: that discussion is in **v2** of arXiv:1406.1949
(19 May 2015, p. 6), where it is Problem 10 and where he writes that "no non-trivial bound
is known for $\hat D_{gen}(n)$ (neither a lower nor an upper bound)". It is Problem 12 in
v1, and **v3 (2 July 2018, the current version) drops the paragraph and the problem from
the body text**, keeping only a row in Table 1.

Every upper bound is an explicit configuration re-verified in exact plane coordinates, and
each happens to be in general position, so it bounds both versions at once. The $n=6$
witness is the triangular-lattice set $(0,0)$, $(-1,0)$, $(1,1)$, $(-2,3)$, $(1,-3)$,
$(3,-2)$, in the basis $(a,b)\mapsto\bigl(a+\tfrac b2,\ \tfrac{\sqrt3}{2}b\bigr)$; its
squared distances are $1,3,7,12,16,25,27$. It has $M=3$ but **seven** distinct distances in
total, which is the point: minimising the per-point maximum is a genuinely different
problem from minimising the total count. The $n=8$ set that is optimal for the total count
has $D=7$ and $M=4$, which beats the $M=5$ of the total-optimal $n=7$ set.

The lower bounds come from enumerating distance patterns. The hypothesis $\max_i d(x_i)\le
m$ is purely local on the pattern: at most $m$ colours at each vertex, and at most $3$
edges of one colour there, since a fourth would put four points on a circle centred at that
vertex. That forces $n-1\le 3m$, which is the trivial bound, and caps the palette at
$k\le nm/2$, so the number of classes is derived rather than assumed. Each surviving
pattern is then decided exactly, via the rank-$2$ Gram condition.

Two of the rungs are short enough to state. **$f(4)>1$:** if every point of a $4$-set saw
one distance, all six distances would be equal, and the Gram matrix of four pairwise
equidistant points is $(I+J)/2$, with eigenvalues $2,\tfrac12,\tfrac12$, hence rank $3$ and
not planar. **$f(7)>2$:** if $7$ points had $M\le 2$ then every vertex would see exactly two
colours, each exactly three times, so every colour class is $3$-regular on its support;
supports are even, lie in $\{4,6\}$, and must total $7\cdot 2=14$, so they are $\{4,4,6\}$
with $6+6+9=21$ edges. A $3$-regular graph on four vertices is $K_4$, so some class is a
$K_4$ and we are back to four pairwise equidistant points. No solver is needed for either,
and neither uses no-three-collinear, so both hold for $f$ as stated on this page.

One thing the table shows: the trivial bound $\lceil (n-1)/3\rceil$ is **not** tight, and
the excess is $+1$ at each of $n=4,5,6$ and at least $+1$ at $n=7$. That is the direction of
[Er87b, p. 168] (3), $\max_i d(x_i) > (1+c)n/3$, though small $n$ cannot distinguish a
growing excess from a bounded one.

Two remarks on sources, from reading for this. The at-most-2 condition on this page appears
in Erdős, *Some old and new problems in combinatorial geometry*, p. 35, question (6) — but
there it is attached to $(1+c)n/2$, not to $(1-o(1))n$, and it carries a \$25 prize. And the
neighbouring problem #655 omits the "no four on a circle" hypothesis that Erdős states in
that same question, where he also writes that it is needed "since otherwise the regular
polygon gives a counterexample" — which is the counterexample #655 was later disproved by.
Details in `PAGE_NOTES.md` in the repository below.

Nothing here bears on the asymptotics, and this page notes that the problem cannot be
resolved by a finite computation.

Code, witnesses and a standalone audit:
https://github.com/sallerk/erdos-notes/tree/main/p654

Disclosure: the searches and computations were done with AI assistance.
