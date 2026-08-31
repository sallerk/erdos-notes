# Prior art for Erdős problem #982

**Statement.** If $n$ distinct points in $\mathbb{R}^2$ form a convex polygon, must some vertex
have at least $\lfloor n/2\rfloor$ distinct distances to the other vertices?
Tagged FALSIFIABLE. https://www.erdosproblems.com/982 (accessed 2026-08-29)

A counterexample is a convex $n$-gon in which **every** vertex sees at most
$\lfloor n/2\rfloor - 1$ distinct distances.

---

## 1. The #982 problem page and its comment thread

Fetched 2026-08-29 with `curl -A "Mozilla/5.0 ..."` (WebFetch gets 403 on this host) from
`/982`, `/forum/thread/982` and `/forum/thread/982/proof-claims`. The raw HTML was read and
then deleted; the decisive content is quoted verbatim below.

**Comments: exactly one.** Quanyu Tang, 05:09 on 02 Oct 2025 — a bibliographic
correction only:

> "Currently the best known lower bound is a slight improvement of Dumitrescu's result.
> Nivasch, Pach, Pinchasi, and Zerbib proved that $f(n) \ge (13/36 + 1/22701)n + O(1)$."

**Proof claims: exactly one**, submitted 2026-07-25 by `skominers` (Scott Duke Kominers,
"using GPT 5.6 Sol, Claude Fable 5"). It is a **lower-bound** claim, not a counterexample:

> "Recording a (very slight) strengthening of the lower bound: ... $f(n) \geq
> \left(\frac{13}{36} + \frac{3}{5270}\right)n - O(1)$, improving the additive term in the
> [NPPZ13] coefficient by a factor of roughly 12.92. This is still, of course, quite a long
> way from the conjectured $\lfloor n/2 \rfloor$."

and, in its Notes:

> "no bound beyond $\frac{5}{12}n$ can follow from the isosceles-triangle reduction alone."

**Nothing on the page or in the thread reports any search for a counterexample**, exhaustive
or heuristic, at any size.

The page's own remark, which is the origin of the reduction used below:

> "This would be implied if there was a vertex such that no three vertices of the polygon are
> equally distant to it, which was originally also conjectured by Erdős [Er46b], but this is
> false (see [97])."

## 2. Adjacent threads #1082 and #97

**#1082** (https://www.erdosproblems.com/forum/thread/1082, 21 comments). Its *second*
question — some single point sees $\lfloor n/2\rfloor$ distances, assuming only no-3-collinear
— is a strictly stronger form of #982, and it is **refuted**. Two counterexamples:

* Harborth's 8-point set $H_8$ (square + equilateral triangle erected on each side), first in
  the literature in Erdős–Fishburn, rediscovered in Feb 2026 by a DeepMind prover agent
  (Lean proof, PR google-deepmind/formal-conjectures#2397); attribution corrected in-thread by
  Sharvil Kesarwani, 25 Feb 2026.
* `eigensolver`, 19 Dec 2025: 42 points = two concentric regular 21-gons, radius ratio
  $r_0=\tfrac12(1-\sqrt{5-8\cos\tfrac{2\pi}{7}})$, a root of $x^3-x^2-2x+1$; each point
  determines only 20 distinct distances. Verified in Maple by StijnC and in Lean by llllvvuu.

**Both are non-convex** (in each, points lie strictly inside the hull of the others), so
neither touches #982. BorisAlexeev states this explicitly in-thread, 25 Feb 2026:

> "note that the main conjecture is still open. Both this construction, and the one by
> eigensolver, disprove the second/'stronger' part of the conjecture."

StijnC also reports a **negative** scan of the natural concentric family:

> "take n odd, and two concentric regular n-gons ... Update: checked for odd $n \le 250$, and
> no positive result."

(that scan was for the non-convex, radially-aligned version, and was incomplete — it fixed
$|A_iA_j|=|A_iB_i|$.)

**#97** (https://www.erdosproblems.com/forum/thread/97, 7 comments, $100 prize). "Does every
convex polygon have a vertex with no other 4 vertices equidistant from it?" The 3-equidistant
version is false: Danzer, 9 points; Fishburn–Reeds 1992, 20 points (same distance at every
vertex). The thread is entirely about the $k=4$ question (`mysticflounder`'s Lean descent
program, `TheAbandonedThinker`'s $n\ge 7$ counting bound). **No per-vertex distinct-distance
search appears.**

## 3. Literature

* Moser 1952: $f(n)\ge\lceil n/3\rceil$.
* Erdős–Fishburn, *A postscript on distances in convex $n$-gons*, DCG 11 (1994) 111–117:
  $f(n)\ge\lfloor n/3+1\rfloor$.
* Dumitrescu, *On distinct distances from a vertex of a convex polygon*, DCG 36 (2006):
  $f(n)\ge\lceil(13n-6)/36\rceil$.
* Nivasch–Pach–Pinchasi–Zerbib, *The number of distinct distances from a vertex of a convex
  polygon*, J. Comput. Geom. 4 (2013) 1–12, arXiv:1207.1266: $f(n)\ge(13/36+1/22701)n-O(1)$.
  Fetched; it contains **no** small-$n$ verification and **no** computer search.
* Altman 1963, *On a problem of P. Erdős*, AMM 70, 148–157: the vertices of a convex $n$-gon
  determine at least $\lfloor n/2\rfloor$ distinct distances **in total**. This is the TOTAL
  count and does not settle the per-vertex question. Fishburn later classified the equality
  cases (for even $n\ge 8$: the regular $n$-gon, or a regular $(n{+}1)$-gon minus a vertex).
* Fishburn–Reeds, *Unit distances between vertices of a convex polygon*, Comput. Geom. 2
  (1992) 81–91: the 20-point absolutely-3-uniform convex polygon.

## 4. The one computational attack in the literature is on #97, not #982

Google DeepMind, *Mathematical exploration and discovery at scale*, arXiv:2511.02864,
§6 item 33 "Equidistant points in convex polygons" (p. 59). Verbatim:

> "Is it true that every convex polygon has a vertex with no other 4 vertices equidistant from
> it? ... We instructed AlphaEvolve to construct a counterexample. ... While it managed to
> produce graphs where every vertex has at least 3 other vertices equidistant from it, it did
> not manage to find an example for 4."

That is Erdős #97. The paper does not mention #982 or the per-vertex distinct-distance count
anywhere (searched the full 81-page PDF for `982`, `equidistan`, `convex polygon`,
`distinct distance`).

`gh api search/issues repo:teorth/erdosproblems 982` returns one hit, PR #77, "Add OEIS
cross-links for #6, #13, #977, #982" — bookkeeping only.

## 5. Conclusion of the prior-art pass

**No computational attack on #982 has been reported**, at any size, by anyone. The two
counterexamples in the neighbourhood (#1082 second question) are both non-convex and provably
irrelevant here. AlphaEvolve's convex-polygon work targets #97. So a search is not a repeat of
published work. It is also, on the record above, unlikely to be easy: the community has been
staring at this family since 1946 and the per-vertex bound has moved from $n/3$ to only
$0.3611n$.

## 6. What is *not* new, and must not be presented as new

The reduction "a counterexample must have three vertices equidistant from every vertex" is
**Erdős's own remark**, stated verbatim on the #982 page (quoted in §1). Everything below in
`RESULTS.md` that uses it is using a known implication, not a new one.
