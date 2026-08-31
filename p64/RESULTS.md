# Searching for a counterexample to the Erdos-Gyarfas conjecture

## The words you need

- A **cycle** is a closed walk in a graph that never repeats a vertex; its **length**
  is the number of edges on it (= the number of vertices on it). A triangle has length 3.
- The **degree** of a vertex is how many edges touch it; the **minimum degree** of a
  graph is the smallest degree over all its vertices.
- A graph is **cubic** (3-regular) if *every* vertex has degree exactly 3.
- A graph is **bipartite** if its vertices can be 2-coloured so that no edge joins two
  vertices of the same colour; equivalently, it has no odd-length cycle.

## The conjecture

**Erdos-Gyarfas (1995).** Every finite graph whose minimum degree is at least 3
contains a cycle whose length is a power of 2 (length 4, 8, 16, 32, 64, ...).

A **counterexample** is a single finite graph with minimum degree >= 3 and no cycle of
any of those lengths. None has ever been found, and non-existence has never been proved.

## RESULT: no counterexample was found

**I did not find a counterexample.** That is the expected outcome and I am not dressing
it up. What this run produced is a bound on a region that is certainly empty, plus an
independent re-derivation of two results that previously rested on a single computation
each.

## What is certified

Both statements below were verified by exhaustive search. Every even n in the stated
range was run to completion; no run was truncated (`run.py` asserts on truncation), and
the per-n certificates are in `results/*.json` and `results/TABLE.md`.

**Theorem A.** Every connected cubic graph on at most **34** vertices contains a cycle
of length 4, 8 or 16. Hence no cubic counterexample has <= 34 vertices.

**Theorem B.** Every connected cubic **bipartite** graph on at most **58** vertices
contains a cycle of length 4, 8 or 16. Hence no cubic bipartite counterexample has
<= 58 vertices.

These are the final numbers. **n = 60 was attempted three times and never completed**
(see "Interrupted work"), so it is not claimed.

*Why "connected" suffices:* if a disconnected graph had minimum degree >= 3 and no
power-of-2 cycle, every connected component would too, and each has fewer vertices. So
a smallest counterexample is connected. Cubic graphs exist only on an even number of
vertices, so checking every even n <= N covers everything.

## NOVELTY: the method is NOT new, and most of the numbers are NOT new

I ran the technique check explicitly, and it came back negative for novelty:

- **The technique is standard.** Isomorph-free exhaustive generation of cubic graphs is
  a well-developed area: McKay's *canonical construction path / canonical deletion*
  (`geng`, and `genbg` for bipartite graphs, in nauty), Brinkmann's *minibaum*,
  Brinkmann-Goedgebeur-McKay's *snarkhunter* ("Generation of cubic graphs", DMTCS 2011),
  and Meringer's orderly generation in *GENREG*. My generator is a plain, **weaker**
  member of that family: it enumerates BFS-canonical labellings and does **no** isomorph
  rejection at all (it simply tolerates each graph appearing once per BFS labelling).
  I wrote it only because this environment has no C compiler and no nauty/geng/genbg.
  Nothing about the method is new.
- **Markstrom's original searches used essentially this approach** — exhaustive
  generation plus, in his words as reported, a simple Fortran program testing for
  cycles of length 4, 8 and 16.
- **Theorem A (cubic, 34) is far below the state of the art.** Markstrom has an
  unpublished result, cited in Exoo (arXiv:1403.5636), that the smallest cubic graph
  with no 4-, 8- or 16-cycle has at least 54 vertices. My 34 does not approach it. It
  does exceed the *citable published* cubic bound of 30 (Royle & Markstrom), but that is
  a weaker statement than the best known one.
- **Theorem B (bipartite, 58) exactly reproduces a published theorem.** Tranquilli
  (arXiv:2608.02675, 2 Aug 2026) Theorem 1: *every simple cubic bipartite graph G with
  |V(G)| <= 58 contains a simple cycle of length 4, 8, or 16.* My Theorem B at 58 is
  the same sentence. It is an **independent verification by a different route** (he goes
  through linear symmetric v3-configurations, Berge triangles and a restricted-growth
  search on <= 29 points; I generate the graphs directly), which has value as
  corroboration, but it is **not a new bound**.
- **Nothing in this run is new.** The one value that would have been (n = 60, which
  Tranquilli explicitly leaves unsearched) never finished. Even that would have been a
  2-vertex increment on a three-week-old paper using a standard technique.

**Bottom line on novelty: there is none.** Verified correctness is not novelty. What
this run delivers is independent corroboration — Markstrom's four 24-vertex graphs and
Tranquilli's 58-vertex theorem, both re-derived from scratch by a different route.

## Comparison table

| class | best known bound | this run | new? |
|---|---|---|---|
| min degree >= 3 (the actual conjecture) | >= 32 (2026 SAT/SMS computation) | not attempted | no |
| cubic, published/citable | >= 30 (Royle & Markstrom) | >= 36 | exceeds the citable bound only |
| cubic, true state of the art | >= 54 (Markstrom, *unpublished*, via Exoo) | >= 36 | **no -- well short** |
| cubic bipartite | >= 60 (Tranquilli, Aug 2026) | >= 60 | **no -- reproduces it** |

## How I know the program is right

A wrong search proves nothing, so this is the part that matters.

1. **The cycle checker is exact** — plain depth-first search, deterministic, no
   colour-coding, so there is no error probability to state. Cross-checked against
   `networkx.simple_cycles` (a fully independent implementation) on ~500 random graphs
   and random cubic graphs, for *every* cycle length, plus hand-known spectra
   (Petersen {5,6,8,9}, Heawood {6,8,10,12,14}, K4 {3,4}, K3,3 {4,6}). This caught a
   real bug in my first Hamiltonicity routine (an unsound prune), which I fixed.
2. **The long-cycle counter used for the C32 decision** was cross-checked against the
   validated Hamiltonicity test on 32-vertex cubic graphs — the exact case that matters.
3. **The generator reproduces published enumeration counts exactly**: connected cubic
   graphs (1, 2, 5, 19, 85, 509), girth >= 5 (1, 2, 9, 49), girth >= 6 (1, 1, 5, 32),
   and connected cubic **bipartite** graphs (1, 1, 2, 5, 13, 38 = A006823).
4. **The strongest single check.** Markstrom proved the smallest cubic graph with no
   4-cycle and no 8-cycle has 24 vertices, that there are exactly four of them, and that
   exactly one is planar. Run from scratch, my pipeline found **zero** on <= 22 vertices
   and **exactly four** on 24, **exactly one** planar. That reproduces a published
   enumeration exactly.
5. **Two independent engines** (pure Python and numba) give byte-identical output on 22
   different (n, forbidden-lengths) settings; the 5-way parallel split provably
   reunites to the serial output.
6. **Bipartite mode cross-checked** against the general search filtered by
   `networkx.is_bipartite`, with forbidden cycles active.

## Interrupted work (contributes nothing and is not counted)

Two runs were killed mid-flight and produced **no data at all**. A search killed part
way through contributes nothing — the tree is explored depth-first, so a partial run
rules out nothing — and neither is included in Theorem A or B.

- **cubic n = 36** — killed once, when I reallocated cores to the bipartite search.
  Estimated cost to finish: ~50 min on 5 workers.
- **cubic bipartite n = 60** — attempted **three times**, killed every time (my own
  cleanup; an account spend limit; and a third unexplained termination at ~55 of an
  estimated ~75 minutes). No `results/bip_n60.json` was ever written. Estimated cost:
  ~4.0e9 search-tree nodes, ~75 min on 5 workers.

Had n = 60 completed, Theorem B would have read 60 rather than 58, i.e. a cubic
bipartite counterexample would need >= 62 rather than >= 60 vertices. It did not
complete, so that is **not** claimed.

## What is NOT searched

- **Everything above the certified bounds.** The space of graphs is infinite; no
  computation can exhaust it. This is a bound, not a proof of the conjecture.
- **Non-cubic graphs — i.e. the actual conjecture.** A counterexample only needs
  minimum degree >= 3; vertices may have degree 4, 5, .... I searched only 3-regular
  graphs. The general bound remains n >= 32 from the 2026 SAT/SMS computation, and I
  did not improve or even attempt it.
- **Cubic graphs on 36..52 vertices** (covered by Markstrom's unpublished result, not
  by me) and **beyond 52** (open).
- **Cubic bipartite graphs above 58 (or 60).**
- Exoo constructed a cubic graph on **78** vertices with no 4-, 8- or 16-cycle, and one
  on **450** vertices with no 4-, 8-, 16- or 32-cycle. Near-counterexamples exist; they
  are just large. Nothing here contradicts that.

## Non-exhaustive search (certifies nothing)

For n <= 63 the only power-of-2 lengths that fit are 4, 8, 16, 32, so a cubic graph on
54..62 vertices with none of those cycles would *be* a counterexample. I built a
simulated-annealing search (`anneal.py`, `hunt.py`) over cubic graphs under 2-opt edge
swaps for exactly that window. It found nothing. **A failed heuristic search is not
evidence of non-existence** and is reported only for completeness about what was tried.
The annealer did independently rediscover a 24-vertex cubic graph with no C4 and no C8
in 3 seconds, which is what exposed my own misreading during the run.

## CONDITIONAL RESULTS

**None.** Every pruning rule in the exhaustive search is either a definition (cubic,
connected, bipartite) or this fact, proved in `fastgen.py`: *a partial graph is a
subgraph of every completion of it, and a cycle in a subgraph is a cycle in the whole
graph, so a partial graph already containing a forbidden cycle can be discarded.*
No theorem from the literature was used to prune — I listed candidate structural
constraints from Carr (arXiv:2605.22844) and the Moore bound in `LITERATURE.md`, then
did not need any of them. Theorems A and B are unconditional, modulo code correctness
as addressed above.

## The certificate table

`results/TABLE.md`, regenerated by `python summarize.py` from `results/*.json`.

## How to reproduce

```
python test_cycles.py     # validate the cycle checker (vs networkx + known graphs)
python test_gen.py        # validate the generator vs published enumeration counts
python test_fastgen.py    # prove the fast engine == the reference generator
python run.py 34 20 5     # exhaust all connected cubic graphs on 34 vertices
python run.py 58 24 5 bip # exhaust all connected cubic bipartite graphs on 58 vertices
python summarize.py       # rebuild the certificate table
```

## Files

| file | what |
|---|---|
| `LITERATURE.md` | literature review with URLs and exact theorem statements |
| `cycles.py` / `test_cycles.py` | exact cycle-length checker + its validation |
| `gen.py` / `test_gen.py` | pure-Python reference generator + validation vs published counts |
| `fastgen.py` / `test_fastgen.py` | numba engine (cubic and bipartite modes) + equivalence proof |
| `run.py`, `summarize.py` | production run for one n, and the certificate table |
| `anneal.py`, `hunt.py` | non-exhaustive simulated-annealing search |
| `results/` | one JSON certificate per n, plus `TABLE.md` |
