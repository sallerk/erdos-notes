# References for #831

Provenance marked per item: [READ] = I or an agent working for me read the primary
text; [SECONDHAND] = seen only as a citation or an abstract; [NOT OBTAINED].

* **The problem.** P. Erdos, *Some problems on elementary geometry*, Austral. Math.
  Soc. Gaz. **2** (1975), 2-3. Renyi archive item 1975-41,
  https://users.renyi.hu/~p_erdos/1975-41.pdf **[READ]**
  It defines h(n) and states NO bound and NO value. Two things on the same page matter:
  - the opening remark, quoted verbatim: "Mrs. E. Szekeres observed that there always
    is a unique point x4 so that x1, x2, x3, x4 are not on a circle and so that the
    radii of the four circles determined by the four triples ... are the same. It
    suffices to choose x4 as the orthocentre of the triangle x1, x2, x3." This is
    h(4) = 1, though Erdos does not say so.
  - a SECOND question the erdosproblems page does not carry: "How does h(n) get
    modified if we only assume that not all our points are on a circle?"
  Also on the page: f(n), the number of unit circles through three of n points, which
  is erdosproblems #104, and g(n), the number of triples whose circumcircle has unit
  radius. Erdos poses the three together and relates none of them.

* **The second citation on the page.** P. Erdos, *Some unsolved problems in geometry,
  number theory and combinatorics*, Eureka **52** (1992), 44-48. **[NOT OBTAINED]**
  Eureka is not in the Renyi archive, which ends at 1990. What this paper says about
  h(n) is unknown to me. Note that the #104 page attributes a GBP 100 prize in the same
  paper to #104, not to #831.

* **f(n), used for the lower bound.** OEIS **A003829**, "Maximal number of unit circles
  through n points in plane, each circle containing 3 of the points", offset 3, values
  1, 4, 4, 8, 12, 16 for n = 3..8, keyword `more`. **[READ]**
  Sources cited there: H. Harborth and I. Mengersen, *Point sets with many unit
  circles*, Discrete Math. **60** (1986) 193-197 **[SECONDHAND]**; H. Harborth,
  *Einheitskreise in ebenen Punktmengen*, 3. Kolloquium ueber Diskrete Geometrie,
  Salzburg 1985, 163-168, PDF linked from the OEIS entry **[READ by agent]**, which
  establishes a(8) = 16.

* **The only bound anywhere on h(n).** A single forum comment, user SamKorsky,
  04:34 on 16 Jun 2026, https://www.erdosproblems.com/forum/thread/831 **[READ]**
  It gives (n-2)/2 <= h(n) <= n^2 exp(O(sqrt(log n))), states its lower bound is "the
  same simple double-counting lower bound from #104", and discloses partial GPT-5.5
  assistance. The site prints "comments are not verified for correctness". Since
  C(n,3)/(n(n-1)/3) = (n-2)/2 identically, that comment already contains the reduction
  used in NOTE.md section 3; only the substitution of exact A003829 values is added
  here.

* **The nearest published relative, and a different function.** L. Martinez and
  E. Roldan-Pensado, *Points defining triangles with distinct circumradii*, Acta Math.
  Hungar. **145** (2015); arXiv:1402.6276 **[READ by agent]**
  This solves Erdos's Ramsey-type n_k (the least n such that some k of any n points in
  general position have all C(k,3) circumradii distinct), NOT h(n): n_k = O(k^9),
  n_4 <= 9, n_5 <= 37. It also records that Erdos's 1978 proof that n_k exists has a
  gap. They define general position as "no four on a line or circle". Three citations
  on Semantic Scholar, none about h(n).

* **Erdos's 1978 follow-up**, *Some more problems on elementary geometry*, Austral.
  Math. Soc. Gaz. **5** (1978) no. 2, 52-54, Renyi item 1978-44 **[READ by agent]**
  solves the n_k question, not h(n); h(n) is never mentioned again.

* **Not obtained, and a gap in the novelty check:** Erdos-Purdy, *Extremal problems in
  combinatorial geometry*, Handbook of Combinatorics ch. 17, pp. 847-848 (cited by
  A003829), and Brass-Moser-Pach, *Research Problems in Discrete Geometry*. Both could
  carry a statement relating f and h. **[NOT OBTAINED]**

## Two things to raise with the page maintainers, separately from any result

1. The page's statement omits Erdos's second question, quoted above.
2. Erdos writes "in general position"; the page renders that as "no three on a line and
   no four on a circle", while Martinez and Roldan-Pensado, working on the same family
   of questions from the same paper, read general position as "no four on a line or
   circle". The two readings give different functions.
