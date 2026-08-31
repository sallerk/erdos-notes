# Erdos-Gyarfas Conjecture -- Literature Review (compiled 2026-08-28)

## 1. The statement

**Conjecture (Erdos & Gyarfas, 1995).** Every finite simple graph with minimum degree
at least 3 contains a (simple) cycle whose length is a power of 2.

Since a simple graph has no cycles of length 1 or 2, the relevant lengths are
`4, 8, 16, 32, 64, ...`. The user's phrasing in the task matches the literature exactly.

Sources:
- https://en.wikipedia.org/wiki/Erd%C5%91s%E2%80%93Gy%C3%A1rf%C3%A1s_conjecture
- http://dwest.web.illinois.edu/openp/2powcyc.html  (West's open problem page:
  "Every graph with minimum degree 3 has a cycle whose length is a power of 2.")
- https://mathweb.ucsd.edu/~erdosproblems/erdos/newproblems/PowerOfTwoCycles.html

The conjecture was posed at a 1995 conference and appeared in print in 1997.
It is open in general. A weaker variant due to Yair Caro asks only for a cycle of
length a nontrivial perfect power.

## 2. Proved special cases (all cited)

| Result | Author(s) | Year | Source |
|---|---|---|---|
| K(1,m)-free graphs with min degree >= m+1, or max degree >= 2m-1 | Shauger | 1998 | Proc. 29th SE Conf. Comb. Graph Th. Comput. (via West's page) |
| Planar claw-free graphs | Daniel & Shauger | 2001 | Proc. 32nd SE Conf. (via West's page) |
| 3-connected cubic planar graphs | Heckman & Krakovski | 2013 | Wikipedia |
| Claw-free graphs (further work) | see cyberleninka survey | -- | https://cyberleninka.org/article/n/196992 |
| P8-free graphs | -- | 2022 | via emergentmind summary |
| P10-free graphs | -- | 2024 | https://www.sciencedirect.com/science/article/abs/pii/S0012365X24003066 |
| P13-free graphs (long induced paths) | -- | 2024/25 | https://arxiv.org/abs/2410.22842 |
| Diameter-2 graphs contain a C4 or C8 | Carr | 2025 | https://arxiv.org/pdf/2508.19302 |

## 3. Prior COMPUTATIONAL bounds -- this is where my search must start

**(a) Royle & Markstrom (c. 2004).** Computer search.
- Any counterexample (min degree >= 3) has **>= 17 vertices**.
- Any **cubic** counterexample has **>= 30 vertices**.
- Markstrom found four 24-vertex cubic graphs whose only power-of-2 cycle length is 16
  (36 edges, radius 5, diameter 6, girth 3, |Aut| = 3; one of them planar).
- Source: Wikipedia article; also cited in arXiv:2605.22844.
- **VERIFIED**: the user's recollection of "17 vertices / cubic 30 vertices" is correct.

**(b) Bipartite (2011 experimental).** Reports vary between n >= 30 and n >= 32.
- https://www.researchgate.net/publication/312286036_An_Experimental_Result_on_the_Erdos-Gyarfas_Conjecture_in_Bipartite_Graphs

**(c) 2026 SAT / SAT-Modulo-Symmetries computation (ArjunBalaji79).**
- https://github.com/ArjunBalaji79/erdos-gyarfas-min-degree-3
- Verified n = 17..31 all UNSAT under min-degree-3 + no C4/C8/C16.
- **Certified bound: any min-degree-3 counterexample has >= 32 vertices.**
- Method: SAT Modulo Symmetries (SMS) with the Glasgow Subgraph Solver for
  forbidden-subgraph propagation. Independent cross-check by a plain CEGAR-SAT solver
  reached only **n = 19** (this is an important calibration datapoint: plain CEGAR-SAT
  without dynamic symmetry breaking dies around n ~ 19-20).
- n <= 31 is exactly the range where C4, C8, C16 are the only admissible power-of-2
  lengths; C32 first fits at n = 32.
- **This is the current general frontier: n >= 32.** It subsumes the cubic >= 30 bound.

**(d) arXiv:2608.02675 -- "A 60-Vertex Lower Bound for Cubic Bipartite
Counterexamples to the Erdos-Gyarfas Conjecture", Julius Tranquilli, 2 Aug 2026.**
- https://arxiv.org/abs/2608.02675 , https://arxiv.org/html/2608.02675
- **Theorem 1**: every simple cubic bipartite graph G with |V(G)| <= 58 contains a cycle
  of length 4, 8, or 16.
- **Corollary 2**: any cubic bipartite counterexample has **>= 60 vertices**.
- Method: cubic bipartite graphs = Levi graphs of linear symmetric v_3-configurations;
  Moore-bound Lemma 8 (nonbacktracking cubic tree from an edge reaches
  1+2+4+8+16 -> 62 vertices, so below 62 vertices a cubic bipartite graph avoiding
  C4 and C8 must contain a C6); the C6 becomes a Berge triangle; two rooted extensions
  up to symmetry; restricted-growth search on <= 29 points.
- **Explicitly unsearched: v = 30 (i.e. exactly 60 vertices).**
- **VERIFIED** -- the paper exists and the user's recollection is correct.

**(e) arXiv:2605.22844 -- "Every Minimal Counterexample to the Erdos-Gyarfas
Conjecture is Predominantly Cubic", Avery Carr, 13 May 2026.**
- https://arxiv.org/abs/2605.22844 , https://arxiv.org/html/2605.22844v1
- **Definition.** A *minimal counterexample* is a graph G with delta(G) >= 3 containing
  no power-of-2 cycle, chosen with **minimum possible order** and, subject to that,
  **minimum possible size**.
- **Lemma 0.1**: for a minimal counterexample G, every proper subgraph H has delta(H) <= 2.
- **Corollary 0.1(1)**: every vertex of G is adjacent to a vertex of degree exactly 3.
- **Corollary 0.1(2)**: the set of vertices of degree >= 4 is an independent set.
- **Corollary 0.2**: any *regular* minimal counterexample is cubic.
- **Theorem 0.1**: at least **4/7** of the vertices of a minimal counterexample have
  degree exactly 3.
- **VERIFIED** -- the paper exists and the user's recollection is correct.

## 4. Structural constraints legitimately usable for pruning

Derived from the above (each is cited, none is my own unproven guess):

- **[C1]** (Carr, Cor. 0.1(2)) In a minimal counterexample the degree->=4 vertices form
  an independent set.
- **[C2]** (Carr, Thm 0.1) >= 4/7 of the vertices have degree exactly 3.
- **[C3]** (Carr, Cor. 0.1(1)) Every vertex is adjacent to a degree-3 vertex.
- **[C4]** (Carr, Cor. 0.2) A regular minimal counterexample is cubic.
- **[C5]** (Carr, Lemma 0.1) Every proper subgraph of a minimal counterexample has
  minimum degree <= 2.
- **[C6]** (Moore bound, standard; the version used in Tranquilli's Lemma 8) A cubic
  graph with no cycle of length <= 8 (girth >= 9) has >= 1 + 3(2^4 - 1) = 46 vertices.
  Hence a cubic graph on < 46 vertices with no C4 and no C8 contains a cycle of
  length 3, 5, 6 or 7. (Cubic Moore bound for odd girth g = 2r+1: n >= 1 + 3(2^r - 1).)
- **[C7]** (trivial, mine) A cubic counterexample on exactly 32 vertices must be
  non-Hamiltonian, since a Hamiltonian cycle would have length 32 = 2^5.

> **IMPORTANT: none of [C1]-[C7] was actually used.** I considered them as pruning
> rules, then did not need them: the plain "cubic + connected + no forbidden cycle in
> the partial graph" search was already fast enough. The certified results in
> RESULTS.md are therefore unconditional and do not depend on any of the papers above.
> The two facts I *do* rely on are proved in the code: (a) every connected cubic graph
> has a BFS labelling of the canonical form the generator enumerates, and (b) a partial
> graph is a subgraph of every completion.

## 4b. THE KEY REFERENCE I ALMOST MISSED -- Exoo, arXiv:1403.5636

**"Three Graphs and the Erdos-Gyarfas Conjecture", Geoffrey Exoo (Indiana State),
Dec 2013 / arXiv Mar 2014.** https://arxiv.org/abs/1403.5636

Defines `f(k)` = order of a **smallest cubic graph with no 2^m-cycle for any m <= k**.
Final table of the paper, verbatim:

```
  k    f(k)
  2    10
  3    24
  4    54 - 78
  5    <= 450
```

with these attributions in the text:
- `f(2) = 10`: three cubic graphs of order 10 have no 4-cycle (one is Petersen), none smaller.
- `f(3) = 24`: **"Markstrom [3] showed that f(3)=24, and listed all four minimal graphs."**
- `f(4) >= 54`: **"The lower bound for f(4) is an unpublished result of Markstrom."**
  I.e. no cubic graph on <= 53 (hence <= 52, order being even) vertices avoids C4, C8 and C16.
- `f(4) <= 78`: Exoo's G78, built from the Petersen graph via a vertex-replacement
  gadget H7 (Petersen -> G12 by expanding one vertex to a triangle, then replace 11 of
  the 12 vertices by H7).
- `f(5) <= 450`: G450, built from the girth-8 Tutte-Coxeter graph with a 15-vertex
  replacement gadget H15, with u placed on the chord edge to kill 32-cycles.
- Also: G420, a 3-connected cubic **planar** graph of order 420 with no 4-, 8- or
  16-cycle, built from the buckyball C60 with the H7 gadget. This shows the m <= 7
  bound of Heckman-Krakovski cannot be lowered below m = 5.

**Consequence for the conjecture.** A cubic counterexample on n vertices must in
particular avoid C4, C8 and C16 whenever n >= 16, so **any cubic counterexample has
at least 54 vertices** by Markstrom's (unpublished) f(4) >= 54.  This is much stronger
than the widely-quoted published "cubic >= 30", and it is the real target for any new
exhaustive computation over cubic graphs.

## 5. Where the frontier is, as of 2026-08-28

| Class | Lower bound on a counterexample | Who | Status |
|---|---|---|---|
| min degree >= 3, general | **>= 32 vertices** | 2026 SMS/SAT computation | public repo |
| cubic, published/citable | >= 30 | Royle & Markstrom c.2004 | published |
| cubic, real state of the art | **>= 54 vertices** | Markstrom, via Exoo arXiv:1403.5636 | *unpublished* result, cited |
| cubic bipartite | **>= 60 vertices** | Tranquilli 2026 | arXiv 2026 |

Related extremal facts (Exoo): smallest cubic graph with no C4 is order 10;
with no C4 and no C8 is order **24** (exactly four such graphs);
with no C4, C8, C16 has order between 54 and 78;
with no C4, C8, C16, C32 has order at most 450.

**No result newer than 2608.02675 (2 Aug 2026) was found.**

## 6. Consequences for my own computation

- Anything at n <= 31 is already done and is only useful as a **correctness check** on my code.
- The genuinely open frontier for a general/cubic counterexample starts at **n = 32**.
- n = 32 is the first order at which C32 is a forbidden length, so the constraint set
  changes there (C4, C8, C16, C32).
- Cubic graphs have even order, so the cubic frontier is n = 32, 34, 36, ...
- Calibration warning from (c): a plain CEGAR-SAT approach (which is all I can build
  here -- no SMS, no nauty, no Glasgow Subgraph Solver, no C compiler) topped out at
  n = 19 in the hands of the 2026 authors. I should not expect to beat n = 32 by SAT.
- Count of connected cubic graphs on 32 vertices is ~1.9e13; on girth >= 5, ~3.5e11.
  Pure-Python exhaustive generation at n = 32 over the unrestricted cubic class is
  not feasible. Any exhaustive claim I make must be over an explicitly restricted class.
