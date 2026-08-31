# Reproducing the #217 results

Every command below was run from a fresh copy of this directory on 2026-08-31, on
Windows 10. The outputs quoted are what it actually printed.

Requirements: Python 3 with `sympy` for the audit and the verifier; a C compiler for
the search. The build below used MinGW-W64 gcc 16.1.0 (`gcc.exe (MinGW-W64
x86_64-ucrt-posix-seh, built by Brecht Sanders, r4) 16.1.0`); any C99 compiler will do.
Nothing else is needed. There is no floating point anywhere in the search or in either
verifier.

## Which claim comes from which file

| claim | where |
|---|---|
| every checkable claim, re-derived independently | `audit217.py` |
| the same, by the earlier independent verifier | `verify.py` |
| the searched region and what exhaustiveness means | `audit217.py` check 6 |
| the values in the thread are not already published | `audit217.py` check 8 |
| the search itself | `crescent2.c` |

## 1. The whole note, independently re-derived

    python audit217.py

Shares no code with `crescent.c`, `crescent2.c` or `verify.py`. Ends:

    ALL CHECKS PASSED

Four of its checks are the ones that could have falsified the work rather than
confirmed it, and they are worth reading in the output:

* **check 1** puts the problem-page statement and Burt et al.'s Definitions 1.1 and 1.2
  side by side and confirms they are the same problem.
* **check 2** takes Palasti's PUBLISHED n = 8 coordinates (from arXiv:1509.07220
  Figure 1, not from anything here) and confirms they are a crescent configuration in
  exact arithmetic.
* **check 4** confirms the search rediscovers that published configuration: the first
  n = 8 solution stored here is Palasti's set scaled by 7 in squared distance, with the
  identical multiplicity assignment.
* **check 5** confirms the verifier REJECTS a Palasti point moved by 1/7, and rejects
  five collinear points (which satisfy the multiplicity condition and are excluded only
  by general position). Without these the acceptance tests would be vacuous.

## 2. Build the search

    gcc -O3 -march=native -o crescent2.exe crescent2.c

Printed nothing; exit 0.

## 3. Reproduce the published 91-point search, in seconds

Burt et al. report "over 900 hours of computation" for the 91-point hexagonal region.
That region is the R^2 = 25 rung here (`audit217.py` check 6 confirms the two point
sets are identical, not merely the same size):

    ./crescent2.exe 9 25 out25.txt 0 1

printed

    n=9 R2=25 points=91 shard 0/1
    n=9 R2=25 shard 0: nodes=16636430 solutions=0 2.67s

so the negative result on their own region reproduces in under three seconds.

## 4. The positive control: the search must FIND things

    ./crescent2.exe 8 49 out8.txt 0 1

printed

    n=8 R2=49 shard 0: nodes=161595043 solutions=156 15.29s

and `out8.txt` contains 156 `SOLUTION` lines. A search that finds nothing everywhere
proves nothing; this is the run that shows the program works.

Check the stored controls against the definition:

    python verify.py sol_n4.txt      # verified 5, failed 0 (of first 5)
    python verify.py sol_n8.txt      # verified 5, failed 0 (of first 5)

`verify.py` shares no code with the search and re-derives collinearity, concyclicity,
the distance count and the multiplicity multiset from the definitions.

## 5. The full n = 9 ladder

`super217.py` is the driver. It runs the shards as independent OS processes (no
multiprocessing pool, and no shell, so there is nothing to misresolve), and records a
health checkpoint; the sweep is exhaustive only if every shard reaches COMPLETED, and
the driver reports that. Verified from a clean clone:

    python super217.py 9 2 25

printed

    R2=25: launched 2 shards
      R2=25 60s alive=0 done=2/2 nodes=1.664e+07 (+1.66e+07) sols=0 healthy=True
    R2=25 COMPLETE: nodes=16636430 solutions=0 in 60s

Note the node total on 2 shards is 16,636,430, identical to the 1-shard run in step 3.
The shard counts add up exactly, which is what makes the union-of-shards argument for
exhaustiveness checkable rather than merely asserted.

The full ladder is

    python super217.py 9 5 100 144 196 256 324 400

`ladder.sh` is a small single-process alternative for the cheap rungs:

    ./ladder.sh 25 64

printed

    n=9 R2=25 shard 0: nodes=16636430 solutions=0 2.65s
    n=9 R2=64 shard 0: nodes=1391779545 solutions=0 160.92s

both matching the recorded ladder exactly. A single rung can also be run directly:

    ./crescent2.exe 9 100 out100.txt 0 1

The full ladder to R^2 = 400 took 43,203 s (12.0 h) on 5 cores and about 3.07e12 search
nodes. The records are in `results/`: `LADDER_217.json` (rungs 100 to 400),
`ladder.log`, the per-shard heartbeats `hb_9_400_*.json`, and `STATUS_217.json`.
`audit217.py` check 7 re-reads `LADDER_217.json` and confirms every rung COMPLETED with
zero solutions.

The `results/c2_n9_R*.txt` files are the n = 9 solution outputs. **They are empty, and
their emptiness is the result.**

## 6. What the exhaustiveness actually covers

`audit217.py` check 6 states and checks this, and it is the part most easily
overstated. The search pins one point at the origin and takes the rest at strictly
increasing indices, so it is complete for every subset of the pool CONTAINING the
origin. Distances are translation invariant, so translating any point of a
configuration to the origin puts every other point within the squared diameter of it.
Therefore the sweep is exhaustive for every configuration of **squared diameter at most
R^2**, which is the claim to quote and is stronger than "fits inside the disc".
Configurations of squared diameter between 400 and 1600 are partly covered but not
exhaustively, and nothing is claimed about them.

## Regression test after the MAXP fix

`crescent2.c` had a silent pool truncation above 2048 points (see NOTE.md). After
raising MAXP to 8192 and making the overflow fatal, both reference runs reproduce
digit for digit:

    ./crescent2.exe 9 25 f25.txt 0 1
    n=9 R2=25 shard 0: nodes=16636430 solutions=0 2.72s      (pre-fix: 16636430, 0)

    ./crescent2.exe 8 49 f8.txt 0 1
    n=8 R2=49 shard 0: nodes=161595043 solutions=156 15.48s  (pre-fix: 161595043, 156)

Run these two after any change to the search; they are fast and they pin both the
negative and the positive behaviour.

## Fixed while testing this file against a clean clone

`ladder.sh` began with `source "../tools/env.sh"`, a MinGW/nauty PATH setup from the
author's machine. That file is not in this repository, so the script failed with exit 2
for anyone who cloned it, while `REPRODUCE.md` named it as a driver. It is now
self-contained, checks for the binary, and exits 1 with a build hint if it is missing.
`super217.py` was unaffected: it invokes the binary directly through subprocess with no
shell.

## Standing limits

Nothing here settles n = 9 in the plane. A crescent configuration need not have lattice
coordinates, and a lattice configuration of larger diameter is not excluded. Palasti's
n = 8 coordinates are taken from Burt et al. rather than from Palasti's own papers,
which were not obtained; their correctness as a crescent configuration is verified here
but their attribution is secondhand. See `REFERENCES.md`.
