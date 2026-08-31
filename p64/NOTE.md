# Erdos #64 (Erdos-Gyarfas powers-of-two cycles)

Problem page: https://www.erdosproblems.com/64

This is the full note. The forum comment is a summary of it. Bibliography with provenance for every reference is in `REFERENCES.md` alongside.

Exhaustive search: no cubic bipartite counterexample on $\le 62$ vertices.

The computational bounds in Alfaiz's comment are Markström [Ma04] (a cubic counterexample needs $\ge 30$ vertices) and Nowbandegani-Esfandiari [NoEs11] (a bipartite one needs $\ge 32$). For the cubic bipartite subclass there is a more recent published bound not yet cited on this page: Julius Tranquilli, "A 60-Vertex Lower Bound for Cubic Bipartite Counterexamples to the Erdős-Gyárfás Conjecture", arXiv:2608.02675, giving $\ge 60$. I have extended that by two steps.

Claim. Let $G$ be a connected cubic bipartite graph on $n$ vertices with $n \le 62$. Then $G$ contains a cycle of length $2^k$ for some $k \ge 2$. Consequently any cubic bipartite counterexample to the Erdős-Gyárfás conjecture has at least $64$ vertices.

Every even $n$ with $4 \le n \le 62$ was covered, with no gaps. In fact nothing in the range survived even the weaker filter: for every even $n \le 62$ there is no connected cubic bipartite graph on $n$ vertices avoiding all three of $C_4$, $C_8$ and $C_{16}$. The $C_{32}$ test was therefore never reached.

How this sits against Tranquilli's method. His argument opens with a Moore-bound observation valid below $62$ vertices (that a cubic bipartite graph with no $C_4$ and no $C_8$ must contain a $C_6$); and then reads $G$ as the Levi graph of a linear symmetric $v_3$-configuration, turning that $C_6$ into a Berge triangle. The case $n = 62$ is therefore just outside the range that observation covers. So the claim above is not only a larger number: it reaches past where the published structural technique applies. It gets there by brute force rather than by extending the structure theory.

Search sizes, in search-tree nodes with wall time on 5 or 10 worker processes: for $n = 58$, $1{,}446{,}651{,}744$ nodes in $1490$ s; for $n = 60$, $3{,}987{,}181{,}668$ nodes in $5535$ s; for $n = 62$, $12{,}184{,}300{,}857$ nodes in $11221$ s. Total over the whole bipartite range, $1.85 \times 10^{10}$ nodes.

Method. Depth-first generation of connected cubic (bipartite) graphs in BFS-canonical labelling, pruning any partial graph that already contains a $C_4$, $C_8$ or $C_{16}$. The pruning is sound because a partial graph is a subgraph of every completion, so a forbidden cycle present at a node is present in every descendant. Survivors are then re-tested from scratch by a separately validated checker covering every power-of-two length.

On the generator. It performs no isomorph rejection, so it over-generates: the same graph may be produced several times. For a non-existence claim this is the safe direction, since duplicates only cost time whereas missing graphs would silently manufacture a false negative. It was written this way only because nauty, geng and genbg were unavailable in the environment used; a standard isomorph-free generator would be considerably faster.

Validation, carried out before any search. (i) The generator reproduces the published connected-cubic counts A002851 exactly for $n = 4, 6, 8, 10, 12$, namely $1, 2, 5, 19, 85$; for the class actually searched here it also matches A006823 (bicubic, that is cubic bipartite, graphs) and A006924 (connected cubic graphs of girth exactly $4$). (ii) It reproduces Markström's four $24$-vertex $C_4/C_8$-free cubic graphs, exactly one of which is planar. (iii) The cycle-length checker was cross-checked against networkx.simple_cycles on $396$ random graphs and $120$ random cubic graphs with zero disagreements; that cross-check caught a genuine bug in an early Hamiltonicity prune.

Caveats. (i) This covers only the cubic bipartite subclass, and does not improve the general bipartite bound of [NoEs11], since a bipartite counterexample need not be cubic. (ii) For the general cubic class my search reached only $n \le 34$, barely past the $\ge 30$ of [Ma04]; I believe that is well behind an unpublished bound of Markström's reported secondhand via Exoo, arXiv:1403.5636, but I have not confirmed that figure at source, so treat it as hearsay. Either way I claim no advance for the general cubic case. (iii) Generator completeness was verified by direct count comparison only up to $n = 12$, so completeness at $n = 62$ rests on the correctness of the algorithm rather than on that test. (iv) The conjecture proper, for graphs of minimum degree $\ge 3$ that are not cubic, is untouched by this. (v) The method is entirely standard (McKay's canonical construction path, Brinkmann's minibaum, snarkhunter, Meringer's GENREG); so this contributes a bound, not a technique.

Code, per-$n$ certificates and the validation suite are in this directory: `RESULTS.md` for the full run table, `LITERATURE.md` for the search record, and `bip_n60_CERTIFIED.txt` and `bip_n62_CERTIFIED.txt` for the two certified runs.

Disclosure: the searches, computations and the drafting of this note were done with AI assistance.

## Files in this directory

* `LITERATURE.md`
* `REFERENCES.md`
* `RESULTS.md`
* `bip_n60_CERTIFIED.txt`
* `bip_n62_CERTIFIED.txt`
