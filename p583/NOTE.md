# Erdos #583 (Gallai's path decomposition conjecture)

Problem page: https://www.erdosproblems.com/583

Full note. Bibliography with provenance is in `REFERENCES.md`; step-by-step
reproduction, with the output each command actually printed, is in `REPRODUCE.md`.

## The problem, and that it is the one being solved

The page states, verbatim:

> "Every connected graph on n vertices can be partitioned into at most ceil(n/2)
> edge-disjoint paths."

**Paths, not trails**, and that distinction is the entire difficulty. A connected graph
with 2t > 0 odd-degree vertices decomposes into exactly t trails by an Euler argument,
which would make the conjecture routine. Both deciders here enforce vertex-simplicity:
`decide5.c` with a vertex bitmask (`adj[vend] & ~used`), and the independent decider in
`audit583.py` with its `seen` set. Check 1 of the audit exhibits a graph that separates
the notions: the bowtie (two triangles sharing a vertex) has all degrees even, so a
single closed trail covers it, but it needs two simple paths.

## Result

**The conjecture holds for every connected graph on at most 11 vertices.**

| n | connected graphs | = A001349(n)? | shards | counterexamples | undecided |
|---|---|---|---|---|---|
| 10 | 11,716,571 | yes | 7/7 | 0 | 0 |
| 11 | 1,006,700,565 | yes | 7/7 | 0 | 0 |

The sweep is exhaustive if and only if the shard counts sum to the number of connected
graphs, so that equality is checked against OEIS A001349 before any verdict is printed,
and a mismatch aborts the run.

**n = 12 is NOT verified.** Stage 1 is complete and provably exhaustive:
**164,059,830,476** graphs swept, equal to A001349(12), with all seven shards
COMPLETED, leaving a residue of 35,633,639 graphs
that the greedy heuristic could not decide. Stage 2 was then abandoned. Measured on 400
graphs drawn at random from that residue, the exhaustive decider averages **2.61 s per
graph** (total 1044.88 s, worst single graph 98.5 s), which is about 154 days on 7
cores; and 13 of the 400 exceeded the 5e8-node cap and returned UNDECIDED, projecting
roughly 1.16 million graphs that the decider cannot settle at all. So even a completed
run would not have produced a verification. Details in `COST.md`.

## Why this is not already implied by the literature

This is the check that decides whether the result is worth anything, and it is run by
`audit583.py` check 6 rather than asserted. `coverage.py` implements all six partial
results cited on the problem page and applies them to every connected graph:

| n | connected | settled by no cited theorem |
|---|---|---|
| 4 | 6 | 0 |
| 5 | 21 | 0 |
| 6 | 112 | 0 |
| 7 | 853 | 36 (4%) |
| 8 | 11,117 | 2,058 (19%) |
| 9 | 261,080 | 89,757 (34%) |
| 10 | 11,716,571 | 6,666,730 (57%) |

**Verification at n <= 6 establishes nothing**: every connected graph there is already
covered, mostly by Bonamy-Perrett (maximum degree at most 5) and Lovász. From n = 7 the
uncovered set is non-empty, and by n = 10 it is a majority. That is the honest measure
of what the exhaustive check at n = 7..11 adds, and also of its limits.

## Controls

An independent decider, written from the definition in Python and sharing no code with
`decide5.c`, re-decides **every connected graph on 4 to 7 vertices** (992 graphs) and
agrees in every case. It uses only two elementary bounds, capacity (a simple path on n
vertices has at most n-1 edges) and parity (every odd-degree vertex must end a path, so
at least ceil(odd/2) paths are needed). The audit also checks that the parity bound the
C decider prunes with never over-prunes, and recovers by hand the values for the star
K_{1,5} (3), the 5-cycle (2), a 5-vertex path (1), K_4 (2) and K_5 (3).

## A false positive this project produced, and the guard added because of it

The first n = 12 run printed

    ==> Erdos-Gallai path decomposition VERIFIED for all connected graphs on 12 vertices.

after sweeping **zero graphs**. Three defects combined: the shards were launched with
`subprocess.Popen(['bash','-lc',...])` and `bash` resolved to WSL's, which has no distro
installed, so every shard died instantly; the health field was `delta > 0 or alive == 0`,
so "everything is dead" counted as healthy; and the final gate tested only
`counterexamples == 0`, never that any work had happened.

`run583.py` was rewritten. It launches executables directly with no shell, requires
every shard to reach COMPLETED, and checks the swept total against A001349 before
printing any verdict. The external ground-truth count is the guard that actually works;
the others only catch the failures one thought of in advance.

## A bug in the audit itself, found while writing it

The independent decider normalises edges internally as (min, max) but did not normalise
its input. A 5-cycle written as `[(i,(i+1)%5)]` supplies the edge `(4,0)`, which then
never matched its stored form `(0,4)` and was silently uncoverable, so the decider
reported 5 paths instead of 2. Fixed by normalising on entry. Recorded here because the
symptom was a wrong answer on a graph anyone can check by hand, which is exactly why the
hand-checked controls in section 2 of the audit exist.

## What is claimed, and what is not

Claimed: the conjecture holds for every connected graph on at most 11 vertices, and for
n = 7..11 this covers graphs that no cited partial result reaches.

Not claimed: anything about n = 12 or beyond; any new theory; and any assertion that
this small-n verification is unpublished. I could not find a published exhaustive
computational verification, but that is a negative search over public sources.

Disclosure: the searches, computations and the drafting of this note were done with AI
assistance.

## Files in this directory

Documentation: `REPRODUCE.md`, `REFERENCES.md`, `COST.md`.

Verification: `audit583.py` (standalone, independent decider, includes the novelty
check) and `coverage.py` (the six cited theorems applied to every connected graph).

Search: `sweep12.c` (generate, filter and greedy), `decide5.c` (the exhaustive residual
decider), `run583.py` (the driver, with the guards described above).

Records in `results/`: `STATUS_583.json` and `RESULT_583_n12_ABANDONED.json`,
`coverage_9_10.log`, `audit583.log`, and the n = 11 sweep log. The 476 MB of n = 12
residue graphs are deliberately not shipped; `REPRODUCE.md` says how to regenerate them.
