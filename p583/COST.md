# Erdos #583 cost-out (Erdos-Gallai path decomposition)

Conjecture: every connected graph on n vertices partitions into at most ceil(n/2)
edge-disjoint PATHS.  A counterexample is one graph.

## Sound filters (each discards graphs covered by a cited theorem)
  Delta <= 5                      -> Bonamy-Perrett [BoPe19]
  <= 1 vertex of even degree      -> Lovasz [Lo68]
  even-degree vertices a forest   -> Pyber [Py96]
  planar                          -> Blanche-Bonamy-Bonichon [BBB21]   (not implemented)
  2-degenerate                    -> Anto-Basavaraju [AnBa23]          (not implemented)
At n=10 the three implemented filters remove 40% of connected graphs.

## Measured (gcc -O3 -march=native, this machine)
  geng generation            7.0e6 graphs/sec
  filters + greedy, 0 restarts   0.291 us/graph,  8.65% need exhaustive search
  filters + greedy, 5 restarts   0.369 us/graph,  0.75% need exhaustive search
  filters + greedy, 40 restarts  0.393 us/graph,  0.040% need exhaustive search

Randomised restarts are the whole game: 359x fewer hard cases for 1.35x the cost.

## VERDICT
n <= 11 is cheap (minutes).  n = 12 is roughly 5 hours on 5 cores for the
generate+filter+greedy sweep, PLUS an exhaustive decider for the ~6.6e7 residual
graphs, which I have NOT built or costed.  If that decider averages 100 us the
residue adds ~2 h on 5 cores; at 1 ms it adds ~18 h; at 10 ms it is dead.

So #583 at n=12 is FEASIBLE-IF the residual decider is fast, and the residual
decider is the entire risk.  Nothing here is a counterexample: every "needs
search" graph is one the heuristic merely failed on.

## Honest value
This is a VERIFICATION, not a likely refutation.  Success looks like "the
conjecture holds for all connected graphs on <= 12 vertices", which is a forum
comment.  The conjecture has stood since 1968 with many confirmatory partial
results, so P(counterexample at n <= 12) is very low.

---

# GATE RESULT (2026-08-30): #583 FAILS. Not started.

The user's gate was "start #583 if the residual decider is faster than 300 us".

Measured on the 2,823 graphs at n=10 that survive the cited-theorem filters and that
40 randomised greedy restarts cannot decompose:

    decided 2823 graphs: decomposable=2823, NOT-decomposable=0, undecided=0
    mean 156,180 us/graph      worst 284,000 us      total 440.9 s

**156 ms, against a 300 us gate — over by a factor of 520.**

Extrapolated to n=12: 6.56e7 residual graphs x 156 ms = 1.02e7 s = 118 days
single-core, ~24 days on 5 cores. Not attemptable. Even a 100x faster decider
(1.5 ms) would still miss the gate by 5x, though it would make n=12 feasible at
about 5.5 h on 5 cores -- so a substantially better decider, not a bigger machine,
is what this problem needs.

## Byproduct actually established

Every connected graph on n <= 10 vertices satisfies the Erdos-Gallai path
decomposition conjecture.  At n=10: 11,716,571 connected graphs, of which
4,677,752 are disposed of by a cited theorem (Bonamy-Perrett Delta<=5;
Lovasz <=1 even-degree vertex; Pyber even-degree-forest), 7,035,996 decomposed by
randomised greedy, and the remaining 2,823 decomposed by exhaustive search.
Zero counterexamples.  Status `VERIFIED` for n <= 10, contingent on the three
cited theorems for the filtered majority.

This is very likely already known and is recorded only so the work is not lost.

---

# MEASURED, 2026-08-31 (supersedes the estimates above for n = 12)

Stage 1 at n = 12 completed: 164,059,830,476 connected graphs swept in 17,461 s on
7 cores, equal to OEIS A001349(12), so the shard split was a verified exhaustive
partition.  Residue after the 40-restart greedy: 35,633,639 graphs (0.0217%).

The residual decider was then MEASURED on 400 graphs drawn at random from the n = 12
residue, rather than extrapolated from n = 11:

    decided 400: decomposable=387 NOT=0 undecided(cap)=13
    total 1044.880s  mean 2.612 s/graph  worst 98.5 s

Two conclusions, both fatal for n = 12 as designed:

  * 2.612 s/graph over 35.6e6 graphs is ~93e6 core-seconds, about 154 days on 7 cores.
    The "VERDICT" section above guessed 100 us to 10 ms and called 10 ms dead; the
    true figure is 261x past that.  An earlier note in this project quoted 2,569 us
    for decide5, which came from the n = 11 residue and does NOT transfer: the n = 12
    residue is 27,000x larger and far harder per graph.
  * 13/400 = 3.25% of the sample exceeds the 5e8-node cap and returns UNDECIDED,
    projecting ~1.16e6 undecided graphs.  So even a completed run would not yield a
    verification.

Stage 2 was abandoned.  n <= 11 is verified; n = 12 is not claimed.

To make n = 12 reachable the lever is the RESIDUE SIZE, not decider speed.  The two
sound filters listed above but never implemented (planar, Blanche-Bonamy-Bonichon;
2-degenerate, Anto-Basavaraju) remove graphs before they reach the decider.  Raising
the greedy restart count also helps but not enough alone: a 10x smaller residue still
leaves ~15 days.
