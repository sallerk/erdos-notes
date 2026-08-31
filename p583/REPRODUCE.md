# Reproducing the #583 results

Every command below was run from a fresh copy of this directory on 2026-08-31, on
Windows 10. The outputs quoted are what it actually printed.

## Requirements

* Python 3 with `networkx` (for the planarity test in `coverage.py`). `audit583.py`
  needs nothing but the standard library.
* A C compiler. The build below used MinGW-W64 gcc 16.1.0.
* **nauty**, for `geng`. It is third-party and is deliberately **not** bundled here.
  Install it from https://pallini.di.uniroma1.it/ and either put `geng` on your PATH or
  set `GENG=/path/to/geng`. Both scripts resolve it in that order and, if it is
  missing, exit with those instructions rather than a traceback:

      $ python coverage.py 7
      geng (from nauty) was not found.
        nauty is not bundled with this repository. Install it from
        https://pallini.di.uniroma1.it/ and then either put geng on your PATH,
        or set GENG=/path/to/geng before running this script.

## Which claim comes from which file

| claim | where |
|---|---|
| every checkable claim, re-derived independently | `audit583.py` |
| the published theorems already cover n <= 6 | `coverage.py`, `audit583.py` check 6 |
| the conjecture holds for all connected graphs on n vertices | `run583.py N 7` |
| the n = 12 residual decision is infeasible | `COST.md` |

## 1. The whole note, independently re-derived

    python audit583.py

Needs no C build and no nauty for checks 1, 2, 5 and 6; checks 3 and 4 use `geng`.
Ends:

    ALL CHECKS PASSED

The decisive parts of its output:

* **check 1** separates paths from trails. The bowtie has all degrees even, so one
  closed trail covers it, but it needs two simple paths. A decider that accepted trails
  would answer 1, so this pins down which problem is being solved.
* **check 3** re-decides **every connected graph on 4 to 7 vertices**, 992 of them, with
  a decider written from the definition in Python that shares no code with `decide5.c`,
  and agrees in every case:

      n=4: 6 connected graphs, all decomposable into <= 2 paths
      n=5: 21 connected graphs, all decomposable into <= 3 paths
      n=6: 112 connected graphs, all decomposable into <= 3 paths
      n=7: 853 connected graphs, all decomposable into <= 4 paths

* **check 6** is the novelty check and prints the coverage table below.

## 2. The novelty check

    GENG=/path/to/geng python coverage.py 7

printed

    n= 7  connected=853
            AnBa23   11
            BBB21    22
            BoPe19   583
            CFZ26    40
            Lo68     130
            Py96     31
            NONE     36   <-- settled by NO cited theorem
            first uncovered graph (graph6): FCf^w

`coverage.py 4 5 6 7 8 9 10` regenerates the whole table. n = 10 takes a few minutes.
The recorded run is in `results/coverage_9_10.log`. The headline: every connected graph
on **n <= 6** is settled by a cited theorem, so verification there adds nothing, while
at n = 10 a **majority** (6,666,730 of 11,716,571) is settled by none of them.

## 3. Verify the conjecture at a given n

    gcc -O3 -march=native -o sweep12.exe sweep12.c
    gcc -O3 -march=native -o decide5.exe decide5.c
    GENG=/path/to/geng python run583.py 10 7

printed

    stage 1 done: 11716571 graphs, 4677752 filtered, 2770 hard, 60s, 7/7 shards COMPLETED
    CHECK: swept count equals OEIS A001349(10) = 11716571, so the shard split was an
           exhaustive partition.
    stage 2: deciding the residue on 7 shards
    n=10 COMPLETE: swept=11716571 filtered=4677752 hard=2770 COUNTEREXAMPLES=0 undecided=0
    ==> Erdos-Gallai path decomposition VERIFIED for all 11716571 connected graphs on
        10 vertices.

`python run583.py 11 7` does n = 11 (1,006,700,565 graphs) in a few minutes.

The A001349 line is the guard that matters. `run583.py` refuses to print a verification
unless every shard reaches COMPLETED **and** the swept total equals the known number of
connected graphs. An earlier version had neither check and once printed a verification
after sweeping zero graphs; see NOTE.md.

## 4. What cannot be reproduced quickly

n = 12 stage 1 is 164,059,830,476 graphs and took 17,461 s on 7 cores. It is
reproducible with `python run583.py 12 7`, but the run will then stop: stage 2 is
infeasible, at a measured 2.61 s per residual graph over 35,633,639 of them, with 3.25 %
of them exceeding the decider's node cap. `COST.md` records the measurement. The 476 MB
of residue graphs are not shipped; the command above regenerates them.

## Standing limits

The n <= 11 verification depends on `decide5.c` being correct. The independent Python
decider cross-checks it exhaustively only to n = 7; beyond that the agreement is
untested and the result rests on the C decider plus the A001349 exhaustiveness check.
`coverage.py` implements the six cited theorems from their statements as given on the
problem page; the papers themselves were not read, and are marked accordingly in
`REFERENCES.md`.
