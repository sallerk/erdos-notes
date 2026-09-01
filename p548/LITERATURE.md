# Prior art for Erdos problem #548 (Erdos-Sos conjecture)

Checked 2026-08-29.  Every quote below was fetched at the URL given.

---

## 0. The headline finding: the target instance in the task brief was wrong

The task brief said the first open instance is **n = 15, >= 46 edges, some tree
on 11 vertices**.  Two things are wrong with that, one arithmetic and one a
convention mismatch in the literature.  Corrected target derived below:

> **n = 15 vertices, >= 61 edges, some tree on 10 vertices.**

### 0a. The edge count (arithmetic)  -- status VERIFIED

erdosproblems.com/548 states the threshold as `(k-1)n/2 + 1` for a tree on
`k+1` vertices.  For a tree on 11 vertices, k = 10 and n = 15:

    (10-1)*15/2 + 1 = 67.5 + 1 = 68.5   ->  at least 69 edges

not 46.  (46 is what that formula gives at k = 7.)  The standard form of the
conjecture, used in every paper cited below, is `e(G) > n(k-1)/2`, giving
**68** edges for that instance.  The brief was off by 22 edges.

### 0b. The convention mismatch  -- status VERIFIED

The comment thread on erdosproblems.com/548 lists the small-case results using
the letter `k` copied from the source papers **without translating it into the
site's own convention**.  The site says "tree on k+1 vertices"; the papers say
"tree of order k".  The comment is internally inconsistent, which is how you
can tell: it says

> "(vii) B. Zhou in [Zh84] has proved the conjecture in the case when graph G
> has a number of vertices k."

Under the site's convention the tree has k+1 vertices, so a graph on k vertices
could not contain it at all -- the statement would be vacuous.  So `k` there is
the **tree order**, as in the source papers.  The primary source settles it.
Yuan and Zhang, arXiv:1403.5430 (PDF, p.1 and p.2):

> "The Erdos-Sos Conjecture states that if G is a simple graph of order n with
> average degree more than k - 2, then G contains every tree of order k. In
> this paper, we prove that Erdos-Sos Conjecture is true for n = k + 4."

> "**Theorem 1.8** Let G be a simple graph of order n with avedeg(G) > k - 2.
> If k >= n - 4, then G contains every tree of order k as a subgraph."

and Tiner's PhD thesis abstract (digitalcommons.uri.edu/oa_diss/2182/):

> "every simple graph with average degree greater than k - 2 contains every
> tree on k vertices as a subgraph" ... "the conjecture holds for all k <= 8"
> ... "the conjecture holds if G has at most k + 3 vertices."

So `k` = **tree order** throughout.  Re-indexing everything by tree order `t`:

| result | covers |
|---|---|
| Eaton-Tiner 2010 [EaTi10] | all trees of order t <= 8, every n |
| Tiner-Tomlin 2022 [TiTo22] | all trees of order t = 9, every n  (see caveat) |
| Zhou 1984 [Zh84] | n = t |
| Slater-Teo-Yap 1985 [STY85] | n = t+1 |
| Wozniak 1996 [Wo96] | n = t+2 |
| Tiner 2010 [Ti10] | n = t+3 |
| Yuan-Zhang 2014/2017 [YuZh17], arXiv:1403.5430 | n = t+4 |

**Consequence.**  At n = 15 every tree order except one is settled:
t <= 9 by Eaton-Tiner + Tiner-Tomlin; t >= 11 because then n <= t+4.
The single open case at n = 15 is **t = 10**.  In particular the brief's
target (n = 15, trees on 11 vertices) is **closed** by Yuan-Zhang Theorem 1.8,
since 15 = 11 + 4.

**Caveat, status CITED-with-ambiguity.**  I could not obtain the Tiner-Tomlin
paper itself, only the erdosproblems comment citing it as [TiTo22].  If its
"k = 9" were instead 9 *edges* (10 vertices), then t = 10 would be closed too
and the first open instance would be n = 16, t = 11, e >= 73.  I searched that
instance as well, so the conclusion does not depend on resolving this.

### 0c. The threshold for the corrected target  -- status VERIFIED

Tree of order t has t-1 edges; average degree > t-2 means

    e(G) > n(t-2)/2 ,  i.e.  e(G) >= floor(n(t-2)/2) + 1 .

    n = 15, t = 10 :  floor(15*8/2) + 1 = 60 + 1 = **61**

This instance is **tight**: an 8-regular graph on 15 vertices has exactly 60
edges and maximum degree 8, so it does not contain the star K_{1,9} (a tree of
order 10).  Such graphs exist (8*15 = 120 is even); the circulant
C_15(1,2,3,4) is one, and my code confirms it misses exactly one of the 106
trees, the star.  So 61 is best possible and a counterexample would have to
live exactly one edge above a tight extremal example.

Other thresholds used: n=15,t=11 -> 68; n=16,t=11 -> 73; n=18,t=10 -> 73
(tight: 2 disjoint K_9 = 72 edges); n=20,t=11 -> 91 (tight: 2 disjoint K_10).

---

## 1. Sources consulted

* **https://www.erdosproblems.com/548** -- problem statement, $100, tagged
  FALSIFIABLE.  Verbatim:
  > "Let $n\geq k+1$. Every graph on $n$ vertices with at least
  > $\frac{k-1}{2}n+1$ edges contains every tree on $k+1$ vertices."

  Listed there: Brandt-Dobson (girth >= 5), Wang-Li-Liu (complement girth
  >= 5), Sacle-Wozniak (C4-free), Yi-Li (complement C4-free); trivial for a
  star; Erdos-Gallai for a path; easy induction at n(k-1)+1 edges.

* **https://www.erdosproblems.com/forum/thread/548** -- the one comment
  (user "Alfaiz", 08:03 on 11 Dec 2025).  It is the source of the small-case
  list; quoted in part above.  It also says:
  > "Plus it seems that a solution was announced for this conjecture by Ajtai,
  > Komlos, Simonovits, and Szemeredi, but it's whereabouts are unknown..."

  and lists Haxell [Ha01] K_{2,s}-free with s = floor(k/18);
  Balasubramanian-Dobson [BaDo07] s < k/12 + 1; Dobson [Do02] complement
  K_{2,4}-free; Sidorenko [Si89] and Eaton-Tiner [EaTi10] leaf-neighbour
  conditions; Fan-Hong-Liu [FHL18] spiders.

* **https://arxiv.org/abs/1403.5430 / .../pdf/1403.5430** -- Yuan, Zhang,
  "On the Erdos-Sos Conjecture for Graphs on n = k+4 Vertices".  Theorem 1.8
  quoted above.  Also quotes, in the same convention:
  > "**Theorem 1.4** [4] Let G be a simple graph with avedeg(G) > k - 2. If
  > delta(G) >= k - 4, then G contains every tree of order k as a subgraph."
  > "**Theorem 1.5** [4] ... If k <= 8, then G contains every tree of order k
  > as a subgraph."
  > "**Theorem 1.3** ... G contains every tree of order k whose diameter does
  > not excess 4 as a subgraph."  (Mclennan 2003)

* **https://digitalcommons.uri.edu/oa_diss/2182/** -- Tiner, PhD thesis
  abstract; convention and the k <= 8 claim, quoted above.

* **https://www.combinatorics.org/ojs/index.php/eljc/article/view/v23i1p52** --
  Goerlich, Zak (2016):
  > "Given an arbitrary integer c>=1, we prove Erdos-Sos conjecture in the case
  > when G has k+c vertices provided that k >= k_0(c) (here
  > k_0(c) = c^12 polylog(c))."

  Does **not** close n = t+5 for t = 10: k_0(5) ~ 5^12 = 2.4e8 >> 10.
  So n = 15, t = 10 is genuinely not covered by it.

* **https://mathweb.ucsd.edu/~erdosproblems/erdos/newproblems/AllTreesSubgraphs.html**
  -- the "graphs problem collection" entry linked from #548.  Same statement,
  same threshold, mentions Komlos-Szemeredi asymptotics (unpublished) and
  caterpillars.

* Heissan & Tiner 2022 (SEICCGTC 2020 proceedings): Erdos-Sos holds for graphs
  of circumference at most k+1.  Found via search; not independently confirmed
  at the publisher.  Status CITED, low confidence.

---

## 2. Has anyone already run this computational search?

**No evidence of one.**  Status: ASSERTED (absence of evidence, not proof of
absence).  Searches run:

* "Erdos-Sos conjecture computer search counterexample exhaustive verification
  small graphs"
* "Erdos-Sos conjecture simulated annealing / computational / computer
  verification trees embedding search"
* "Erdos-Sos conjecture n=k+5 / k+5 vertices proved"
* several author-specific searches (Tiner, Tomlin, Eaton, Yuan, Zhang)

Everything returned is a human proof of a special case.  The one place where
computer search appears in this neighbourhood is the *Erdos-Gyarfas* conjecture
(Royle, Markstrom), a different problem.  Nothing indicates that the
(n = 15, t = 10) instance has been swept, and nothing indicates any use of
metaheuristic search on Erdos-Sos.  I did not find a survey that even names a
"first open instance", which is consistent with nobody having framed it this
way computationally.

---

## 3. Proved facts used to steer the search  (all status CITED)

**Tree-side exclusions** (rule out which tree can be the missing one; they hold
for every n, so they apply to the whole search):

| exclusion | source | trees of order 10 killed |
|---|---|---|
| paths | Erdos-Gallai 1959 | (subsumed) |
| spiders (<= 1 vertex of degree > 2) | Fan-Hong-Liu 2018 [FHL18] | 26 |
| diameter <= 4 | Mclennan 2003 | 26 |
| some vertex with >= ceil(k/2)-2 = 3 leaf-neighbours | Sidorenko 1989, Eaton-Tiner 2010 | 45 |

**42 of the 106 trees on 10 vertices survive all four** (ids listed in
`suspects_10.json`).  105 of the 235 trees on 11 vertices survive.

**Graph-side exclusions** (rule out which graph can be the counterexample):

| a counterexample G must ... | because |
|---|---|
| have min degree <= t-5 = 5 | Eaton-Tiner Thm 1.4: delta >= t-4 forces every tree of order t |
| contain a C4 | Sacle-Wozniak 1997 (C4-free case proved) |
| have girth <= 4 | Brandt-Dobson 1996 (girth >= 5 proved) |
| have a complement containing C4, girth <= 4, and a K_{2,4} | Yi-Li 2004; Wang-Li-Liu 2000; Dobson 2002 |
| contain a path on t+4 = 14 vertices | Eaton-Tiner 2013 (P_{k+4}-free case proved) |
| have circumference >= t+2 = 12 | Heissan-Tiner 2022 (low confidence) |

The min-degree one is the strongest and the cheapest to use: it rules out the
obvious candidate family "8-regular graph plus one edge" outright, since those
have delta = 8 >= 6.  The search carries a bias term rewarding delta <= 5, and
was also run with that term switched off.
