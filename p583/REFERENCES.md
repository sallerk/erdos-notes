# References for the #583 note

## The problem statement

* **erdosproblems.com/583**, read 2026-08-31, verbatim:

  > "Every connected graph on n vertices can be partitioned into at most ceil(n/2)
  > edge-disjoint paths."

  Page citation `#583: [Er71,p.101]`, status FALSIFIABLE, described there as "A problem
  of Erdős and Gallai".
  *[VERIFIED AT SOURCE]*

  **Paths, not trails.** This is the whole difficulty and is worth stating explicitly,
  because the trail version is easy: a connected graph with 2t > 0 odd-degree vertices
  decomposes into exactly t trails by an Euler argument. `decide5.c` enforces
  vertex-simplicity with a vertex bitmask (`adj[vend] & ~used`), and the independent
  decider in `audit583.py` does the same with its `seen` set. Check 1 of the audit
  exhibits a graph separating the two notions: the bowtie has all degrees even, so one
  closed trail covers it, but it needs two simple paths.

## The partial results, used here as filters and as the novelty baseline

All six are quoted from the site's own bibliography, read 2026-08-31.
*[VERIFIED AT SOURCE for the bibliographic data; none of the proofs were read]*

* **[Lo68]** Lovász, L., "On covering of graphs", Theory of Graphs (Proc. Colloq.,
  Tihany, 1966) (1968), 231-236. (MR 233723) Implies the conjecture when G has at most
  one vertex of even degree.
* **[Py96]** Pyber, L., "Covering the edges of a connected graph by paths",
  J. Combin. Theory Ser. B (1996), 152-159. (MR 1368522) Proves it when the subgraph
  induced by the even-degree vertices is a forest.
* **[BoPe19]** Bonamy, Marthe and Perrett, Thomas J., "Gallai's path decomposition
  conjecture for graphs of small maximum degree", Discrete Math. (2019), 1293-1299.
  Maximum degree at most 5.
* **[BBB21]** A. Blanché, M. Bonamy, and N. Bonichon, "Gallai's path decomposition in
  planar graphs", arXiv:2110.08870 (2021). Planar graphs.
* **[AnBa23]** Anto, Nevil and Basavaraju, Manu, "Gallai's path decomposition for
  2-degenerate graphs", Discrete Math. Theor. Comput. Sci. (2023), Paper No. 16, 11.
  2-degenerate graphs.
* **[CFZ26]** Chu, Yanan and Fan, Genghua and Zhou, Chuixiang, "Gallai's conjecture and
  the path number of odd semi-cliques", Discrete Math. (2026), Paper No. 114725, 6.
  The page states this as: the subgraph induced by the vertices of even degree is K_m
  for some m <= 15, and n is odd.

Also on the page but not used here: **[Ch78]** Chung (decomposition into ceil(n/2)
edge-disjoint TREES, a different statement), **[DeKo00]** Dean and Kouider
(ceil(2n/3) paths always suffice, a weaker bound that does not settle any n), and
**[Fa02]** Fan (the version without the edge-disjoint condition).

## OEIS

* **A001349**, the number of connected graphs on n nodes. Used as the exhaustiveness
  check on every sweep: the shard counts must sum to it exactly, or the run is
  rejected. Values relied on: 11,716,571 at n = 10; 1,006,700,565 at n = 11;
  164,059,830,476 at n = 12.

## Novelty

The check that matters is not "has anyone run this code" but "do the theorems above
already settle every connected graph at these n". `coverage.py` implements all six and
runs them over every connected graph from `geng`:

| n | connected | settled by no cited theorem |
|---|---|---|
| 4 | 6 | 0 |
| 5 | 21 | 0 |
| 6 | 112 | 0 |
| 7 | 853 | 36 |
| 8 | 11,117 | 2,058 |
| 9 | 261,080 | 89,757 (34%) |
| 10 | 11,716,571 | 6,666,730 (57%) |

So **verification at n <= 6 establishes nothing**; every connected graph there is
already covered, mostly by [BoPe19] and [Lo68]. From n = 7 the uncovered set is
non-empty and grows to a majority by n = 10. That is what makes the exhaustive check at
n = 7..11 worth stating, and it is also the honest limit on how much it is worth.

I found no published exhaustive computational verification of the conjecture for small
n. That is a negative search over public sources, not proof that none exists; small-n
verification is the sort of thing that gets done and not written up.

**What is NOT claimed.** n = 12 is not verified. Its sweep is complete and provably
exhaustive (164,059,830,476 graphs, equal to A001349(12), all seven shards COMPLETED),
but the residual decision was abandoned: measured at 2.61 s per residual graph over
35,633,639 of them, that is about 154 days on 7 cores, and 3.25 % of a random sample
exceeded the decider's node cap, so even a completed run would have left roughly 1.16
million graphs undecided and produced no verification. See `COST.md`.
